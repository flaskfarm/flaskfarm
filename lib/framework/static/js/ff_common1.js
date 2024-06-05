var tmp = window.location.pathname.split('/');
if (tmp.length == 2) {
  var PACKAGE_NAME = tmp[1];
  var MODULE_NAME = "";
  var PAGE_NAME = "";
} else if (tmp.length == 3) {
  var PACKAGE_NAME = tmp[1];
  var MODULE_NAME = tmp[2];
  var PAGE_NAME = "";
} else if (tmp.length > 3){
  var PACKAGE_NAME = tmp[1];
  var MODULE_NAME = tmp[2];
  var PAGE_NAME = tmp[3];
}
var current_data = null;
var current_page = null;
console.log("NAME: [" + PACKAGE_NAME + '] [' + MODULE_NAME + '] [' + PAGE_NAME + ']');

$(window).on("load resize", function (event) {
  var $navbar = $(".navbar");
  var $body = $("body");
  $body.css("padding-top", $navbar.outerHeight());
});  

$('#command_modal').on('show.bs.modal', function (event) {
})

///////////////////////////////////////
// 사용 미확인
///////////////////////////////////////


// 알림
$.notify({ 
  // options
  icon: 'glyphicon glyphicon-ok',
  title: 'APP',
  message: '',
  url: '',
  target: '_blank'
},{
  // settings
  element: 'body',
  position: null,
  type: "info",
  allow_dismiss: true,
  newest_on_top: false,
  showProgressbar: false,
  placement: {
      from: "top",
      align: "right"
  },
  offset: 20,
  spacing: 10,
  z_index: 3000,
  delay: 10000,
  timer: 1000,
  url_target: '_blank',
  mouse_over: null,
  animate: {
      enter: 'animated fadeInDown',
      exit: 'animated fadeOutUp'
  },
  onShow: null,
  onShown: null,
  onClose: null,
  onClosed: null,
  icon_type: 'class',
  template: '<div data-notify="container" class="col-xs-11 col-sm-3 alert alert-{0}" role="alert">' +
      '<button type="button" aria-hidden="true" class="close" data-notify="dismiss">×</button>' +
      '<span data-notify="icon"></span> ' +
      '<span data-notify="title" style="word-break:break-all;">{1}</span> ' +
      '<span data-notify="message" style="word-break:break-all;">{2}</span>' +
      '<div class="progress" data-notify="progressbar">' +
          '<div class="progress-bar progress-bar-{0}" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>' +
      '</div>' +
      '<a href="{3}" target="{4}" data-notify="url"></a>' +
  '</div>' 
});


function notify(msg, type) {
  $.notify('<strong>' + msg + '</strong>', {type: type, z_index: 3000});
}

// 메뉴 제거
function hideMenu() {
  $("#menu_div").html('');
  hideMenuModule();
  hideMenuPage();
  hideSettingMenuPage();
}

function hideMenuModule() {
  $("#menu_module_div").html('');
}

function hideMenuPage() {
  $("#menu_page_div").html('');
}

function hideSettingMenuPage() {
  $("#setting_menu_page_div").html('');
}

// 넓은 화면
function setWide() {
  $('#main_container').attr('class', 'container-fluid');
}


function showModal(data='EMPTY', title='JSON', json=true) {
  document.getElementById("modal_title").innerHTML = title;
  if (json) {
    data = JSON.stringify(data, null, 2);
  } 
  document.getElementById("modal_body").innerHTML = '<pre style="white-space: pre-wrap;">' +data + '</pre>';
  $("#large_modal").modal();
}


function getFormdata(form_id) {
  // on, off 일수도 있으니 모두 True, False로 통일하고
  // 밑에서는 False인 경우 값이 추가되지 않으니.. 수동으로 넣어줌
  var checkboxs = $(form_id + ' input[type=checkbox]');
  //for (var i in checkboxs) {
  for (var i =0 ; i < checkboxs.length; i++) {
    if ( $(checkboxs[i]).is(':checked') ) {
      $(checkboxs[i]).val('True');
    } else {
      $(checkboxs[i]).val('False');
    }
  }
  var formData = $(form_id).serialize();
  $.each($(form_id + ' input[type=checkbox]')
    .filter(function(idx) {
      return $(this).prop('checked') === false 
    }), 
    function(idx, el) { 
      var emptyVal = "False"; 
      formData += '&' + $(el).attr('name') + '=' + emptyVal; 
    }
  );
  formData = formData.replace("&global_scheduler=True", "")
  formData = formData.replace("&global_scheduler=False", "")
  formData = formData.replace("global_scheduler=True&", "")
  formData = formData.replace("global_scheduler=False&", "")
  return formData;
}

///////////////////////////////////////
// camel


function use_collapse(div, reverse=false) {
  var ret = $('#' + div).prop('checked'); 
  if (reverse) {
    if (ret) {
      $('#' + div + '_div').collapse('hide');
    } else {
      $('#' + div + '_div').collapse('show');
    }
  } else {
    if (ret) {
      $('#' + div + '_div').collapse('show');
    } else {
      $('#' + div + '_div').collapse('hide');
    }
  }
}

// jquery extend function
// post로 요청하면서 리다이렉트
$.extend(
  {
    redirectPost: function(location, args)
    {
        var form = '';
        $.each( args, function( key, value ) {
            value = value.split('"').join('\"')
            form += '<input type="hidden" name="'+key+'" value="'+value+'">';
        });
        $('<form action="' + location + '" method="POST">' + form + '</form>').appendTo($(document.body)).submit();
    }
  });





















///////////////////////////////////////
// 유틸리티 - 프로젝트 관련성 없음
///////////////////////////////////////

function humanFileSize(bytes) {
  var thresh = 1024;
  if(Math.abs(bytes) < thresh) {
      return bytes + ' B';
  }
  var units = ['KB','MB','GB','TB','PB','EB','ZB','YB']
  var u = -1;
  do {
      bytes /= thresh;
      ++u;
  } while(Math.abs(bytes) >= thresh && u < units.length - 1);
  return bytes.toFixed(1)+' '+units[u];
}

function FormatNumberLength(num, length) {
  var r = "" + num;
  while (r.length < length) {
      r = "0" + r;
  }
  return r;
}

function msToHMS( ms ) {
  // 1- Convert to seconds:
  var seconds = ms / 1000;
  // 2- Extract hours:
  var hours = parseInt( seconds / 3600 ); // 3,600 seconds in 1 hour
  seconds = seconds % 3600; // seconds remaining after extracting hours
  // 3- Extract minutes:
  var minutes = parseInt( seconds / 60 ); // 60 seconds in 1 minute
  // 4- Keep only seconds not extracted to minutes:
  seconds = seconds % 60;
  return (''+hours).padStart(2, "0")+":"+(''+minutes).padStart(2, "0")+":"+parseInt(seconds);
}

































///////////////////////////////////////
// 사용 미확인
///////////////////////////////////////



function duration_str(duration) {
  duration = duration / 100;
  var minutes = parseInt(duration / 60);
  var hour = parseInt(minutes / 60);
  var min = parseInt(minutes % 60);
  var sec = parseInt((duration/60 - parseInt(duration/60)) * 60);
  return pad(hour, 2) + ':' + pad(min, 2) + ':' + pad(sec,2);

}
// 자리맞춤
function pad(n, width) {
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join('0') + n;
}

