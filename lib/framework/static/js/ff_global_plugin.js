///////////////////////////////////////
// 자주 사용하는 플러그인에 전용 명령

function pluginRcloneLsjson(remote_path) {
  var url = '/rclone/ajax/config/command';
  globalSendCommandByUrl(url, "ls", remote_path);
}
  
