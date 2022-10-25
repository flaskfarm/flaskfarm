// global socketio
$(document).ready(function(){
  ResizeTextArea();
});
  
$(document).ready(function(){
  $('.loading').hide();
})
.ajaxStart(function(){
  $('.loading').show();
})
.ajaxStop(function(){
  $('.loading').hide();
});

var protocol = window.location.protocol;
var frameSocket = io.connect(protocol + "//" + document.domain + ":" + location.port + "/framework");
console.log(frameSocket);

frameSocket.on('notify', function(data){
  $.notify({
    message : data['msg'],
    url: data['url'],
    target: '_self'
  },{
    type: data['type'],
    z_index: 2000,
  });
});

frameSocket.on('modal', function(data){
  m_modal(data.data, data.title, false);
});

frameSocket.on('loading_hide', function(data){
  $('#loading').hide();
});

frameSocket.on('refresh', function(data){
  console.log('data')
  window.location.reload();
});


$('#command_modal').on('hide.bs.modal', function (e) {
  //e.preventDefault(); 있으면 동작 안함.
  console.log("ff global command_modal hide.bs.modal CATCH")
  $.ajax({
    url: `/global/ajax/command_modal_hide`,
    type: 'POST',
    cache: false,
    data: {},
    dataType: 'json'
  });
});





///////////////////////////////////////
// Global - 버튼
///////////////////////////////////////

$("body").on('click', '#globalOpenBtn', function(e) {
  e.preventDefault();
  url = $(this).data('url')
  window.open(url, "_blank");
});

$("body").on('click', '#globalLinkBtn', function(e) {
  e.preventDefault();
  url = $(this).data('url')
  window.location.href = url;
});

// global_link_btn 모두 찾아 변경

$("body").on('click', '#globalSettingSaveBtn', function(e){
  e.preventDefault();
  globalSettingSave();
});

function globalSettingSave() {
  var formData = getFormdata('#setting');
  $.ajax({
    url: '/' + PACKAGE_NAME + '/ajax/setting_save',
    type: "POST", 
    cache: false,
    data: formData,
    dataType: "json",
    success: function (ret) {
      if (ret) {
        $.notify('<strong>설정을 저장하였습니다.</strong>', {
          type: 'success'
        });
      } else {
        $.notify('<strong>설정 저장에 실패하였습니다.</strong>', {
          type: 'warning'
        });
      }
    }
  });
}

$("body").on('click', '#globalEditBtn', function(e) {
  e.preventDefault();
  file = $(this).data('file');
  console.log(file);
  $.ajax({
    url: '/global/ajax/is_available_edit',
    type: "POST", 
    cache: false,
    data: {},
    dataType: "json",
    success: function (ret) {
      if (ret.ret) {
        window.open('/flaskcode?open=' + file, ret.target);
      } else {
        notify('편집기 플러그인을 설치해야 합니다.', 'warning');
      }
    }
  });
});

$("body").on('click', '#globalCliboardBtn', function(e) {
  e.preventDefault();
  window.navigator.clipboard.writeText($(this).data('text'));
  notify("클립보드에 복사하였습니다.", "success");
});


// 사용 on / off
$("body").on('change', '#globalSchedulerSwitchBtn', function(e) {
  e.preventDefault();
  var ret = $(this).prop('checked');
  $.ajax({
    url: '/'+PACKAGE_NAME+'/ajax/' + MODULE_NAME + '/scheduler',
    type: "POST", 
    cache: false,
    data: {scheduler : ret},
    dataType: "json",
    success: function () {}
  });
});

$("body").on('change', '#globalSchedulerSwitchPageBtn', function(e) {
  var ret = $(this).prop('checked');
  $.ajax({
    url: '/'+PACKAGE_NAME+'/ajax/' + MODULE_NAME + '/' + PAGE_NAME + '/scheduler',
    type: "POST", 
    cache: false,
    data: {scheduler : ret},
    dataType: "json",
    success: function () {}
  });
});

$("body").on('click', '#globalOneExecuteBtn', function(e) {
  e.preventDefault();
  $.ajax({
    url: '/'+PACKAGE_NAME+'/ajax/' + MODULE_NAME + '/one_execute',
    type: "POST", 
    cache: false,
    data: {},
    dataType: "json",
    success: function (ret) {
      if (ret=='scheduler' || ret=='thread') {
        $.notify('<strong>작업을 시작하였습니다. ('+ret+')</strong>', {
          type: 'success'
        });
      } else if (ret == 'is_running') {
        $.notify('<strong>작업중입니다.</strong>', {
          type: 'warning'
        });
      } else {
        $.notify('<strong>작업 시작에 실패하였습니다.</strong>', {
          type: 'warning'
        });
      }
    }
  });
});

$("body").on('click', '#globalOneExecutePageBtn', function(e) {
  e.preventDefault();
  $.ajax({
    url: '/'+PACKAGE_NAME+'/ajax/' + MODULE_NAME + '/' + PAGE_NAME + '/one_execute',
    type: "POST", 
    cache: false,
    data: {sub:sub},
    dataType: "json",
    success: function (ret) {
      if (ret=='scheduler' || ret=='thread') {
        $.notify('<strong>작업을 시작하였습니다. ('+ret+')</strong>', {
          type: 'success'
        });
      } else if (ret == 'is_running') {
        $.notify('<strong>작업중입니다.</strong>', {
          type: 'warning'
        });
      } else {
        $.notify('<strong>작업 시작에 실패하였습니다.</strong>', {
          type: 'warning'
        });
      }
    }
  });
});
  
$("body").on('click', '#globalImmediatelyExecuteBtn', function(e){
  e.preventDefault();
  $.ajax({
    url: '/'+PACKAGE_NAME+'/ajax/' + MODULE_NAME + '/immediately_execute',
    type: "POST", 
    cache: false,
    data: {},
    dataType: "json",
    success: function (ret) {
      if (ret.msg != null) notify(ret.msg, ret.ret);
    }
  });
});

$("body").on('click', '#globalImmediatelyExecutePageBtn', function(e){
  e.preventDefault();
  $.ajax({
    url: '/'+PACKAGE_NAME+'/ajax/' + MODULE_NAME + '/' + PAGE_NAME + '/immediately_execute',    
    type: "POST", 
    cache: false,
    data: {},
    dataType: "json",
    success: function (ret) {
      if (ret.msg != null) notify(ret.msg, ret.ret);
    }
  });
});

  
$("body").on('click', '#globalDbDeleteBtn', function(e){
  e.preventDefault();
  document.getElementById("confirm_title").innerHTML = "DB 삭제";
  document.getElementById("confirm_body").innerHTML = "전체 목록을 삭제 하시겠습니까?";
  $('#confirm_button').attr('onclick', "globalDbDelete();");
  $("#confirm_modal").modal();
  return;
});
    
function globalDbDelete() {
  $.ajax({
    url: '/'+PACKAGE_NAME+'/ajax/' + MODULE_NAME + '/reset_db',
    type: "POST", 
    cache: false,
    data: {},
    dataType: "json",
    success: function (data) {
      if (data) {
        $.notify('<strong>삭제하였습니다.</strong>', {
          type: 'success'
        });
      } else {
        $.notify('<strong>삭제에 실패하였습니다.</strong>',{
          type: 'warning'
        });
      }
    }
  });
}
  
$("body").on('click', '#globalDbDeletePageBtn', function(e){
  e.preventDefault();
  document.getElementById("confirm_title").innerHTML = "DB 삭제";
  document.getElementById("confirm_body").innerHTML = "전체 목록을 삭제 하시겠습니까?";
  $('#confirm_button').attr('onclick', "globalDbDeletePage();");
  $("#confirm_modal").modal();
  return;
});
    
function globalDbDeletePage() {
  $.ajax({
    url: '/'+PACKAGE_NAME+'/ajax/' + MODULE_NAME + '/' + PAGE_NAME + '/reset_db',    
    type: "POST", 
    cache: false,
    data: {sub:sub},
    dataType: "json",
    success: function (data) {
      if (data) {
        $.notify('<strong>삭제하였습니다.</strong>', {
          type: 'success'
        });
      } else {
        $.notify('<strong>삭제에 실패하였습니다.</strong>',{
          type: 'warning'
        });
      }
    }
  });
}



///////////////////////////////////////
// Global - 함수
///////////////////////////////////////

function globalSendCommand(command, arg1, arg2, arg3, modal_title, callback) {
  console.log("globalSendCommand [" + command + '] [' + arg1 + '] [' + arg2 + '] [' + arg3 + '] [' + modal_title + '] [' + callback + ']');
  console.log('/' + PACKAGE_NAME + '/ajax/' + MODULE_NAME + '/command');

  $.ajax({
    url: '/' + PACKAGE_NAME + '/ajax/' + MODULE_NAME + '/command',
    type: "POST", 
    cache: false,
    data:{command:command, arg1:arg1, arg2:arg2, arg3},
    dataType: "json",
    success: function (ret) {
      if (ret.msg != null) notify(ret.msg, ret.ret);
      if (ret.modal != null) showModal(ret.modal, modal_title, false);
      if (ret.json != null) showModal(ret.json, modal_title, true);
      if (callback != null) callback(ret);
    }
  });
}

function globalSendCommandPage(command, arg1, arg2, arg3, modal_title, callback) {
  console.log("globalSendCommandPage [" + command + '] [' + arg1 + '] [' + arg2 + '] [' + arg3 + '] [' + modal_title + '] [' + callback + ']');
  console.log('/' + PACKAGE_NAME + '/ajax/' + MODULE_NAME + '/command');

  $.ajax({
    url: '/' + PACKAGE_NAME + '/ajax/' + MODULE_NAME + '/' + PAGE_NAME + '/command',
    type: "POST", 
    cache: false,
    data:{command:command, arg1:arg1, arg2:arg2, arg3},
    dataType: "json",
    success: function (ret) {
      if (ret.msg != null) notify(ret.msg, ret.ret);
      if (ret.modal != null) m_modal(ret.modal, modal_title, false);
      if (ret.json != null) m_modal(ret.json, modal_title, true);
      if (callback != null) callback(ret);
    }
  });
}

function shutdown_confirm() {
  $("#confirm_title").html("종료 확인");
  $("#confirm_body").html("종료 하시겠습니까?");
  $('#confirm_button').attr('onclick', 'window.location.href = "/system/shutdown";');
  $("#confirm_modal").modal();
}




///////////////////////////////////////
// 리스트 화면 기본
///////////////////////////////////////


function globalRequestSearch(page, move_top=true) {
  var formData = getFormdata('#form_search')
  formData += '&page=' + page;
  $.ajax({
    url: '/' + PACKAGE_NAME + '/ajax/' + MODULE_NAME + '/web_list',
    type: "POST", 
    cache: false,
    data: formData,
    dataType: "json",
    success: function (data) {
      current_data = data;
      if (move_top)
        window.scrollTo(0,0);
      make_list(data.list)
      make_page_html(data.paging)
    }
  });
}



function make_page_html(data) {
  str = ' \
    <div class="d-inline-block"></div> \
      <div class="row mb-3"> \
        <div class="col-sm-12"> \
          <div class="btn-toolbar" style="justify-content: center;" role="toolbar" aria-label="Toolbar with button groups" > \
            <div class="btn-group btn-group-sm mr-2" role="group" aria-label="First group">'
  if (data.prev_page) {
    str += '<button id="gloablSearchPageBtn" data-page="' + (data.start_page-1) + '" type="button" class="btn btn-secondary">&laquo;</button>'
  }

  for (var i = data.start_page ; i <= data.last_page ; i++) {
    str += '<button id="gloablSearchPageBtn" data-page="' + i +'" type="button" class="btn btn-secondary" ';
    if (i == data.current_page) {
      str += 'disabled';
    }
    str += '>'+i+'</button>';
  }
  if (data.next_page) {
    str += '<button id="gloablSearchPageBtn" data-page="' + (data.last_page+1) + '" type="button" class="btn btn-secondary">&raquo;</button>'
  }

  str += '</div> \
    </div> \
    </div> \
    </div> \
  '
  document.getElementById("page1").innerHTML = str;
  document.getElementById("page2").innerHTML = str;  
}



$("body").on('click', '#gloablSearchPageBtn', function(e){
  e.preventDefault();
  globalRequestSearch($(this).data('page'), false);
});

$("body").on('click', '#globalSearchSearchBtn', function(e){
  e.preventDefault();
  globalRequestSearch(1, false);
});

$("body").on('click', '#globalSearchResetBtn', function(e){
  e.preventDefault();
  $("#order").val('desc');
  $("#option1").val('all');
  $("#option2").val('all');
  $("#keyword").val('');
  globalRequestSearch(1, false);
});



///////////////////////////////////////
// 파일 선택 모달
///////////////////////////////////////

var select_local_file_modal_callback = null;

function globalSelectLocalFile(title, init_path, func) {
  _selectLocalFileModal(title, init_path, false, func);
}

function globalSelectLocalFolder(title, init_path, func) {
  _selectLocalFileModal(title, init_path, true, func);
}

function _selectLocalFileModal(title, init_path, only_dir, func) {
  if (init_path == '' || init_path == null)
    init_path = '/';
  document.getElementById("select_local_file_modal_title").innerHTML = title;
  document.getElementById("select_local_file_modal_path").value = init_path;
  document.getElementById("select_local_file_modal_only_dir").value = only_dir;
  select_local_file_modal_callback = func;
  $("#select_local_file_modal").modal();
  listdir(init_path, only_dir);
}

$("body").on('click', '#global_select_local_file_load_btn', function(e) {
  e.preventDefault();
  let current_path = $('#select_local_file_modal_path').val().trim();
  only_dir = $('#select_local_file_modal_only_dir').val().trim();
  listdir(current_path, only_dir);
});

$("body").on('click', '#select_local_file_modal_confirm_btn', function(e) {
  e.preventDefault();
  if (select_local_file_modal_callback != null)
    select_local_file_modal_callback($('#select_local_file_modal_path').val().trim());
  $("#select_local_file_modal").modal('toggle');
});


let listdir = (path = '/', only_dir = true) => {
  $.ajax({
      url: `/global/ajax/listdir`,
      type: 'POST',
      cache: false,
      data: {
          path: path,
          only_dir : only_dir
      },
      dataType: 'json'
  }).done((datas) => {
    console.log(datas)
      if (datas.length == 0) {
        return false;
      }
      let new_obj = ``;
      const path_spliter = (path.indexOf('/')>=0)?'/':'\\';
      $('#select_local_file_modal_list_group').empty();
      for (let dt of datas) {
          tmp = dt.split('|');
          new_obj += `<a href='#' class="list-group-item list-group-item-action item_path" data-value="${tmp[1]}">${tmp[0]}</a>`;
      }
      $('#select_local_file_modal_list_group').append(new_obj);
      $('.item_path').off('click').click((evt) => {
          
          let new_path = '';
          /*
          if ($(evt.currentTarget).text() === '..'){
              let split_path = '';
              split_path = path.split(path_spliter);
              split_path.pop();
              new_path = split_path.join(path_spliter);
              if (new_path.length === 0){
                  new_path = path_spliter
              }
          } else {
              //new_path = (path !== path_spliter) ? path + path_spliter + $(evt.currentTarget).text() : path + $(evt.currentTarget).text();
              new_path = $(evt.currentTarget).data('value');
              console.log(new_path)
              console.log(evt)

          }
          */
          new_path = $(evt.currentTarget).data('value');
          $('#select_local_file_modal_path').val(new_path);
          listdir(new_path, only_dir);
          
      });
  }).fail((datas) => {
      $.notify('<strong>경로 읽기 실패</strong><br/>${add_path}', {type: 'danger'});
  });
  return false;
}
// 파일 선택 모달 End
///////////////////////////////////////


///////////////////////////////////////
// Command MODAL
///////////////////////////////////////

frameSocket.on('command_modal_add_text', function(data){
  document.getElementById("command_modal_textarea").innerHTML += data ;
  document.getElementById("command_modal_textarea").scrollTop = document.getElementById("command_modal_textarea").scrollHeight;
});

frameSocket.on('command_modal_input_disable', function(data){
  $('#command_modal_input').attr('disabled', true);
});

frameSocket.on('command_modal_show', function(data){
  command_modal_show(data)
});

frameSocket.on('command_modal_clear', function(data){
  document.getElementById("command_modal_textarea").innerHTML = ""
});

function command_modal_show(title) {
  ClientHeight = window.innerHeight
  document.getElementById("command_modal_title").innerHTML = title
  $("#command_modal").height(ClientHeight+50);
  $("#command_modal_textarea").height(ClientHeight-380);
  $("#command_modal").modal({backdrop: 'static', keyboard: false}, 'show');
  $('#command_modal_input').attr('disabled', false);
}

$("body").on('click', '#command_modal_input_btn', function(e) {
  e.preventDefault();
  $.ajax({
    url: '/global/ajax/command_modal_input',
    type: "POST", 
    cache: false,
    data: {cmd:$('#command_modal_input').val()},
    dataType: "json",
    success: function (ret) {
      $('#command_modal_input').val('');
    }
  });
});


$(window).resize(function() {
  ResizeTextArea();
});


function ResizeTextArea() {
  ClientHeight = window.innerHeight
  $("#command_modal").height(ClientHeight-100);
  $("#command_modal_textarea").height(ClientHeight-380);
}

///////////////////////////////////////

