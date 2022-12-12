/*
<div class="d-inline-block"></div>

*/
function j_button_group(h) {
  var str = '<div class="btn-group btn-group-sm flex-wrap mr-2" role="group">';
  str += h
  str += '</div>';
  return str;
}

// primary, secondary, success, danger, warning, info, light, dark, white
function j_button(id, text, data={}, color='primary', outline=true, small=false, _class='') {
  var str = '<button id="'+id+'" name="'+id+'" class="btn btn-sm btn';
  if (outline) {
    str += '-outline';
  }
  str += '-' + color+'';
  str += ' ' + _class;
  if (small) {
    str += ' py-0" style="font-size: 0.8em;"';
  } else {
    str += '" ';
  }
  for ( var key in data) {
    str += ' data-' + key + '="' + data[key]+ '" '
  }
  str += '>' + text + '</button>';
  return str;
}

function j_button_small(id, text, data={}, color='primary', outline=true) {
  return j_button(id, text, data, color, outline, true);
}



function j_row_start(padding='10', align='center') {
  var str = '<div class="row chover" style="padding-top: '+padding+'px; padding-bottom:'+padding+'px; align-items:'+align+';">';
  return str;
}
function j_row_start_hover(padding='10', align='center') {
  var str = '<div class="row my_hover" style="padding-top: '+padding+'px; padding-bottom:'+padding+'px; align-items:'+align+';">';
  return str;
}

function j_col(w, h, align='left') {
  var str = '<div class="col-sm-' + w + ' " style="text-align: '+align+'; word-break:break-all;">';
  str += h;
  str += '</div>';
  return str;
}

function j_col_with_class(w, h, align='left', _class='context_menu') {
  var str = '<div class="col-sm-' + w + ' '+_class+'" style="text-align: '+align+'; word-break:break-all;">';
  str += h;
  str += '</div>';
  return str;
}

function j_col_wide(w, h, align='left') {
  var str = '<div class="col-sm-' + w + ' " style="padding:0px; margin:0px; text-align: '+align+'; word-break:break-all;">';
  str += h;
  str += '</div>';
  return str;
}

function j_row_end() {
  var str = '</div>';
  return str;
}

function j_hr(margin='5') {
  var str = '<hr style="width: 100%; margin:'+margin+'px;" />';
  return str;
}

function j_hr_black() {
  var str = '<hr style="width: 100%; color: black; height: 2px; background-color:black;" />';
  return str;
}



// 한줄 왼쪽
function j_row_info(left, right, l=2, r=8) {
  var str =' \
  <div class="row"> \
    <div class="col-sm-'+1+'" style="text-align:right;"></div> \
    <div class="col-sm-'+l+'" style="text-align:right;"> \
      <strong>'+ left +'</strong> \
    </div> \
    <div class="col-sm-'+r+'" style="word-break:break-all;"> \
      <span class="text-left" style="padding-left:10px; padding-top:3px;">'+right +'</span> \
    </div> \
  </div>';
  return str;
}

function j_progress(id, width, label) {
  var str = '';
  str += '<div class="progress" style="height: 25px;">'
  str += '<div id="'+id+'" class="progress-bar bg-success" style="width:'+width+'%"></div>';
  str += '<div id="'+id+'_label" class="justify-content-center d-flex w-100 position-absolute" style="margin-top:2px">'+label+'</div>';
  str += '</div>'
  return str;
}


function j_td(text, width='10', align='center', colspan='1') {
  str = '<td scope="col" colspan="'+colspan+'" style="width:'+width+'%; text-align:'+align+';">'+ text + '</td>';  
  return str;
}

function j_th(text, width='10', align='center', colspan='1') {
  str = '<th scope="col" colspan="'+colspan+'" style="width:'+width+'%; text-align:'+align+';">'+ text + '</td>';  
  return str;
}



function j_info_text(key, value, left=2, right=10) {
  row = j_row_start(0);
  row += j_col(left, '<strong>' + key + '</strong>', aligh='right');
  row += j_col(right, value, aligh='left');
  row += j_row_end();
  return row;
}

function j_info_text_left(key, value, left=3, right=9) {
  row = j_row_start(0);
  row += j_col(left, '<strong>' + key + '</strong>', aligh='left');
  row += j_col(right, value, aligh='left');
  row += j_row_end();
  return row;
}


function j_tab_make(data) {
  str = '<nav><div class="nav nav-tabs" id="nav-tab" role="tablist">';
  for (i in data) {
    if (data[i][2]) {
      str += '<a class="nav-item nav-link active" id="tab_head_'+data[i][0]+'" data-toggle="tab" href="#tab_content_'+data[i][0]+'" role="tab">'+data[i][1]+'</a>';
    } else {
      str += '<a class="nav-item nav-link" id="tab_head_'+data[i][0]+'" data-toggle="tab" href="#tab_content_'+data[i][0]+'" role="tab">'+data[i][1]+'</a>';
    }
  }
  str += '</div></nav>';
  str += '<div class="tab-content" id="nav-tabContent">';
  for (i in data) {
    if (data[i][2]) {
      str += '<div class="tab-pane fade show active" id="tab_content_'+data[i][0]+'" role="tabpanel" ></div>';
    } else {
      str += '<div class="tab-pane fade show" id="tab_content_'+data[i][0]+'" role="tabpanel" ></div>';
    }
  }
  str += '</div>';
  return str;
}


// javascript에서 화면 생성
function text_color(text, color='red') {
  return '<span style="color:'+color+'; font-weight:bold">' + text + '</span>';
}


function j_pre(text) {
  return '<pre style="word-wrap: break-word;white-space: pre-wrap;white-space: -moz-pre-wrap;white-space: -pre-wrap;white-space: -o-pre-wrap;word-break:break-all;">'+text+'</pre>';
}































///////////////////////////////////////
// UI - 확장설정 - dropdown
///////////////////////////////////////

document.addEventListener("DOMContentLoaded", function(){
  /////// Prevent closing from click inside dropdown
  document.querySelectorAll('.dropdown-menu').forEach(function(element){
    element.addEventListener('click', function (e) {
      e.stopPropagation();
    });
  })

    // make it as accordion for smaller screens
  if (window.innerWidth < 992) {
    // close all inner dropdowns when parent is closed
    document.querySelectorAll('.navbar .dropdown').forEach(function(everydropdown){
      everydropdown.addEventListener('hidden.bs.dropdown', function () {
        // after dropdown is hidden, then find all submenus
          this.querySelectorAll('.submenu').forEach(function(everysubmenu){
            // hide every submenu as well
            everysubmenu.style.display = 'none';
          });
      })
    });
  
    document.querySelectorAll('.dropdown-menu a').forEach(function(element){
      element.addEventListener('click', function (e) {

          let nextEl = this.nextElementSibling;
          if(nextEl && nextEl.classList.contains('submenu')) {	
            // prevent opening link if link needs to open dropdown
            e.preventDefault();
            if(nextEl.style.display == 'block'){
              nextEl.style.display = 'none';
            } else {
              nextEl.style.display = 'block';
            }

          }
      });
    })
  }
// end if innerWidth
}); 
// DOMContentLoaded  end
///////////////////////////////////////

























































































function m_row_start_top(padding='10') {
  return m_row_start(padding, 'top');
}
function m_row_start_color(padding='10', align='center', color='') {
  var str = '<div class="row" style="padding-top: '+padding+'px; padding-bottom:'+padding+'px; align-items:'+align+'; background-color:'+color+'">';
  return str;
}
function m_row_start_color2(padding='10', align='center') {
  var str = '<div class="row bg-dark text-white" style="padding-top: '+padding+'px; padding-bottom:'+padding+'px; align-items:'+align+';">';
  return str;
}



//border








// 체크박스는 자바로 하면 on/off 스크립트가 안먹힘.






