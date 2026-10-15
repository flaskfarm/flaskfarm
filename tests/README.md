# Subprocess lifecycle regression tests

Run the standard-library suite without initializing FlaskFarm, Redis, plugins, or user configuration:

```sh
python3 -m unittest discover -s tests -v
```

To exercise the same monkey-patched subprocess/threading path used by a gevent Celery worker, install gevent in an isolated test environment and run:

```sh
FF_TEST_GEVENT=1 python3 -m unittest discover -s tests -v
```

`FF_SUBPROCESS_SOURCE=/path/to/sub_process.py` can select an installed copy or another revision for comparison. The suite loads only that helper using a synthetic package logger; it does not import the application.

Coverage includes repeated and concurrent jobs, full burst output and an unterminated final line, literal `<END>` output, chunk callbacks, interactive stdin, callback exceptions, spawn/worker-start failures, timeout cleanup, idempotent cancellation, cancellation while `Popen` is still returning, and concurrent registry removal. Repeated-job tests retain the job objects and check both worker lifetime and Linux `/proc/self/fd`, so passing does not depend on eventual garbage collection. Descriptor assertions are omitted on systems without `/proc/self/fd`.

Jobs are registered before process creation. Cancellation intent is retained until the child is assigned, and registry snapshots/removal are synchronized. `all_process_close()` stops the jobs in its current snapshot, including jobs still creating a child; later starts remain independent. Stopping jobs stay registered until their cleanup finishes, and `get_list()` returns a snapshot rather than the mutable registry.

Async callbacks retain `START` and `LOG`. Exactly one terminal callback is emitted **after output delivery and pipe cleanup**: `END` for a completed or explicitly stopped command, or `ERROR` for a spawn/read/wait failure (including a timeout). A nonzero child exit remains an `END`, matching the existing behavior; callers can inspect their own results. Cancellation still targets only the direct child, not unrelated processes or new process groups.
