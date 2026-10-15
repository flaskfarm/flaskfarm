"""Run with unittest; set FF_TEST_GEVENT=1 to match a gevent Celery worker."""
import os

if os.environ.get('FF_TEST_GEVENT') == '1':
    from gevent import monkey
    monkey.patch_all()

import gc
import importlib.util
import logging
from pathlib import Path
import subprocess
import sys
import threading
import time
import types
import unittest
from unittest import mock


# Load the real helper without initializing Flask, Redis, plugins, or user data.
package = types.ModuleType('_subprocess_test_support')
test_logger = logging.getLogger('subprocess_test')
test_logger.addHandler(logging.NullHandler())
test_logger.setLevel(logging.CRITICAL)
setattr(package, 'logger', test_logger)
sys.modules[package.__name__] = package
source = Path(os.environ.get('FF_SUBPROCESS_SOURCE',
    str(Path(__file__).resolve().parents[1] / 'lib/support/base/sub_process.py')))
spec = importlib.util.spec_from_file_location(package.__name__ + '.sub_process', source)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SupportSubprocess = module.SupportSubprocess


def descriptor_count():
    path = Path('/proc/self/fd')
    return len(list(path.iterdir())) if path.is_dir() else None


class SubprocessLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the gevent hub before measuring descriptors or workers.
        SupportSubprocess.execute_command_return([sys.executable, '-c', 'pass'])
        gc.collect()

    def setUp(self):
        self.jobs = []

    def tearDown(self):
        # Only test-owned children are eligible for cleanup, including failures.
        for job, _, _ in self.jobs:
            process = job.process
            if process is not None:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=3)
                for stream in (process.stdin, process.stdout, process.stderr):
                    if stream is not None:
                        stream.close()
        self.jobs.clear()
        gc.collect()

    def start_job(self, code, *, callback_line=True, timeout=None, callback=None,
                  command=None):
        events = []
        done = threading.Event()

        def receive(call_id, mode, data):
            events.append((mode, data))
            if mode in ('END', 'ERROR'):
                done.set()
            if callback is not None:
                callback(mode, data)

        job = SupportSubprocess(
            command or [sys.executable, '-u', '-c', code],
            timeout=timeout, stdout_callback=receive, callback_line=callback_line)
        self.jobs.append((job, events, done))
        job.start(join=False)
        return job, events, done

    def finish(self, item):
        job, events, done = item
        self.assertTrue(done.wait(5), 'terminal callback did not arrive')
        job.thread.join(5)
        self.assertFalse(job.thread.is_alive(), 'execution worker did not finish')
        return events

    def assert_terminal(self, events, expected='END'):
        self.assertEqual([mode for mode, _ in events if mode in ('END', 'ERROR')],
                         [expected])
        self.assertEqual(events[-1][0], expected)

    def test_repeated_jobs_release_pipes_and_callback_workers(self):
        before_threads = set(threading.enumerate())
        before_fds = descriptor_count()
        for _ in range(12):
            events = self.finish(self.start_job('pass'))
            self.assert_terminal(events)
        time.sleep(0.05)
        gc.collect()
        if before_fds is not None:
            self.assertEqual(descriptor_count(), before_fds)
        self.assertEqual(set(threading.enumerate()), before_threads)
        self.assertEqual(SupportSubprocess.get_list(), [])
        self.assertTrue(all(job.process is None for job, _, _ in self.jobs))

    def test_burst_output_and_unterminated_tail_precede_end(self):
        for count in (10, 1000, 5000):
            with self.subTest(lines=count):
                code = ("import sys; [print('ROW:'+str(i).zfill(5)) "
                        f"for i in range({count})]; sys.stdout.write('TAIL')")
                events = self.finish(self.start_job(code))
                logs = [data for mode, data in events if mode == 'LOG' and data]
                expected = ['ROW:' + str(i).zfill(5) for i in range(count)] + ['TAIL']
                self.assertEqual(logs, expected)
                self.assert_terminal(events)

    def test_literal_end_marker_is_output_not_a_control_message(self):
        events = self.finish(self.start_job("print('<END>'); print('after marker')"))
        self.assertIn(('LOG', '<END>'), events)
        self.assertIn(('LOG', 'after marker'), events)
        self.assert_terminal(events)

    def test_chunk_callbacks_preserve_output(self):
        events = self.finish(self.start_job(
            "import sys; sys.stdout.write('alpha'+chr(10)+'omega')",
            callback_line=False))
        output = ''.join(data for mode, data in events if mode == 'LOG')
        self.assertEqual(output, 'alpha\nomega\n')
        self.assert_terminal(events)

    def test_timeout_kills_and_reaps_child_before_error(self):
        item = self.start_job("import time; print('ready'); time.sleep(2)", timeout=0.15)
        job = item[0]
        deadline = time.monotonic() + 2
        while job.process is None and time.monotonic() < deadline:
            time.sleep(0.005)
        process = job.process
        self.assertIsNotNone(process)
        assert process is not None
        events = self.finish(item)
        self.assert_terminal(events, 'ERROR')
        self.assertIsNotNone(process.poll(), 'timed-out child is still running')
        self.assertEqual(process.returncode, -9 if os.name == 'posix' else 1)
        self.assertIn(('LOG', 'ready'), events)
        self.assertIsNone(job.process)
        self.assertTrue(process.stdin.closed)
        self.assertTrue(process.stdout.closed)

    def test_explicit_stop_is_idempotent_and_reaps_child(self):
        ready = threading.Event()
        item = self.start_job("import time; print('ready'); time.sleep(2)",
                              callback=lambda mode, data: ready.set()
                              if mode == 'LOG' and data == 'ready' else None)
        self.assertTrue(ready.wait(3))
        job = item[0]
        process = job.process
        job.process_close()
        job.process_close()
        events = self.finish(item)
        self.assert_terminal(events)
        self.assertIsNotNone(process.poll())
        self.assertTrue(process.stdin.closed)
        self.assertTrue(process.stdout.closed)
        job.process_close()

    def test_spawn_failure_has_one_error_and_no_registered_instance(self):
        item = self.start_job('', command=['/missing-command-for-subprocess-test'])
        events = self.finish(item)
        self.assert_terminal(events, 'ERROR')
        self.assertEqual(SupportSubprocess.get_list(), [])
        self.assertIsNone(item[0].process)

    def test_cancel_during_process_creation_is_not_lost(self):
        self.check_cancel_during_process_creation(stop_all=False)

    def test_stop_all_includes_jobs_still_creating_their_process(self):
        self.check_cancel_during_process_creation(stop_all=True)

    def check_cancel_during_process_creation(self, stop_all):
        created = threading.Event()
        release = threading.Event()
        children = []
        real_popen = subprocess.Popen

        def delayed_popen(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            children.append(process)
            created.set()
            release.wait(3)
            return process

        with mock.patch.object(module.subprocess, 'Popen', delayed_popen):
            item = self.start_job('import time; time.sleep(2)')
            try:
                self.assertTrue(created.wait(3))
                if stop_all:
                    SupportSubprocess.all_process_close()
                else:
                    item[0].process_close()
            finally:
                release.set()
            events = self.finish(item)
        self.assert_terminal(events)
        self.assertNotEqual(children[0].returncode, 0, 'creation-time cancel was lost')
        self.assertTrue(children[0].stdin.closed)
        self.assertTrue(children[0].stdout.closed)

    def test_concurrent_registry_removals_do_not_restore_removed_jobs(self):
        class Entry:
            def __init__(self, value):
                self.value = value

            @property
            def timestamp(self):
                # Force a context switch inside the old unlocked list filter.
                time.sleep(0.005)
                return self.value

        first, second = Entry(1), Entry(2)
        SupportSubprocess._SupportSubprocess__instance_list.extend([first, second])
        barrier = threading.Barrier(3)

        def remove(entry):
            barrier.wait()
            SupportSubprocess.remove_instance(entry)

        threads = [threading.Thread(target=remove, args=(entry,))
                   for entry in (first, second)]
        try:
            for thread in threads:
                thread.start()
            barrier.wait()
            for thread in threads:
                thread.join(3)
                self.assertFalse(thread.is_alive())
            self.assertEqual(SupportSubprocess.get_list(), [])
        finally:
            SupportSubprocess.remove_instance(first)
            SupportSubprocess.remove_instance(second)

    def test_output_or_callback_worker_start_failure_cleans_up(self):
        real_start = threading.Thread.start
        for fail_on in (2, 3, 4):
            with self.subTest(worker=fail_on):
                calls = 0

                def fail_start(thread):
                    nonlocal calls
                    calls += 1
                    if calls == fail_on:
                        raise RuntimeError('synthetic worker start failure')
                    return real_start(thread)

                with mock.patch.object(threading.Thread, 'start', fail_start):
                    item = self.start_job('pass')
                    events = self.finish(item)
                self.assert_terminal(events, 'ERROR')
                self.assertIsNone(item[0].process)
                self.assertEqual(SupportSubprocess.get_list(), [])

    def test_callback_exception_does_not_prevent_cleanup(self):
        def fail_log(mode, data):
            if mode == 'LOG':
                raise RuntimeError('synthetic callback failure')

        item = self.start_job("print('hello')", callback=fail_log)
        events = self.finish(item)
        self.assert_terminal(events)
        self.assertIsNone(item[0].process)

    def test_interactive_input_is_preserved(self):
        item = self.start_job('print(input())')
        job = item[0]
        deadline = time.monotonic() + 2
        while job.process is None and time.monotonic() < deadline:
            time.sleep(0.005)
        self.assertIsNotNone(job.process)
        job.input_command('synthetic input')
        events = self.finish(item)
        self.assertIn(('LOG', 'synthetic input'), events)
        self.assert_terminal(events)

    def test_concurrent_jobs_finish_without_registered_instances(self):
        items = [self.start_job(f"print('job-{index}')") for index in range(8)]
        for index, item in enumerate(items):
            events = self.finish(item)
            self.assertIn(('LOG', f'job-{index}'), events)
            self.assert_terminal(events)
        self.assertEqual(SupportSubprocess.get_list(), [])


if __name__ == '__main__':
    unittest.main()
