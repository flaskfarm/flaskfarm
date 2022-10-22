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
function j_button(id, text, data={}, color='success', outline=true, small=false) {
  var str = '<button id="'+id+'" name="'+id+'" class="btn btn-sm btn';
  if (outline) {
    str += '-outline';
  }
  str += '-' + color+'';
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

function j_button_small(id, text, data={}, color='success', outline=true) {
  return j_button(id, text, data, color, outline, true);
}



function j_row_start(padding='10', align='center') {
  var str = '<div class="row" style="padding-top: '+padding+'px; padding-bottom:'+padding+'px; align-items:'+align+';">';
  return str;
}
function j_col(w, h, align='left') {
  var str = '<div class="col-sm-' + w + ' " style="text-align: '+align+'; word-break:break-all;">';
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






























// javascript에서 화면 생성
function text_color(text, color='red') {
  return '<span style="color:'+color+'; font-weight:bold">' + text + '</span>';
}

function m_table(id, heads) {
  str += '<table id="result_table" class="table table-sm  tableRowHover "  ><thead class="thead-dark"><tr> \
  <th style="width:10%;text-align:center;">NO</th> \
  <th style="width:15%;text-align:center;">물어본 숫자</th> \
  <th style="width:10%;text-align:center;">스트라이크</th> \
  <th style="width:10%;text-align:center;">볼</th> \
  <th style="width:15%;text-align:center;">가능한 숫자 수</th> \
  <th style="width:40%;text-align:center;">Action</th> \
  </tr></thead><tbody id="list">';
}






































function m_row_start_hover(padding='10', align='center') {
  var str = '<div class="row my_hover" style="padding-top: '+padding+'px; padding-bottom:'+padding+'px; align-items:'+align+';">';
  return str;
}
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




function m_tab_head(name, active) {
  if (active) {
    var str = '<a class="nav-item nav-link active" id="id_'+name+'" data-toggle="tab" href="#'+name+'" role="tab">'+name+'</a>';
  } else {
    var str = '<a class="nav-item nav-link" id="id_'+name+'" data-toggle="tab" href="#'+name+'" role="tab">'+name+'</a>';
  }
  return str;
}

function m_tab_content(name, content, active) {
  if (active) {
    var str = '<div class="tab-pane fade show active" id="'+name+'" role="tabpanel" >';
  } else {
    var str = '<div class="tab-pane fade show" id="'+name+'" role="tabpanel" >';
  }
  str += content;
  str += '</div>'
  return str;
}

function m_progress(id, width, label) {
  var str = '';
  str += '<div class="progress" style="height: 25px;">'
  str += '<div id="'+id+'" class="progress-bar"  style="background-color:yellow;width:'+width+'%"></div>';
  str += '<div id="'+id+'_label" class="justify-content-center d-flex w-100 position-absolute" style="margin-top:2px">'+label+'</div>';
  str += '</div>'
  return str;
}


function m_progress2(id, width, label) {
  var str = '';
  str += '<div class="progress" style="height: 25px;">'
  str += '<div id="'+id+'" class="progress-bar"  style="background-color:yellow;width:'+width+'%"></div>';
  str += '<div id="'+id+'_label" class="justify-content-center d-flex w-100 position-absolute" style="margin:0px; margin-top:2px">'+label+'</div>';
  str += '</div>'
  return str;
}

  
  
function make_page_html(data) {
  str = ' \
    <div class="d-inline-block"></div> \
      <div class="row mb-3"> \
        <div class="col-sm-12"> \
          <div class="btn-toolbar" style="justify-content: center;" role="toolbar" aria-label="Toolbar with button groups" > \
            <div class="btn-group btn-group-sm mr-2" role="group" aria-label="First group">'
  if (data.prev_page) {
    str += '<button id="page" data-page="' + (data.start_page-1) + '" type="button" class="btn btn-secondary">&laquo;</button>'
  }

  for (var i = data.start_page ; i <= data.last_page ; i++) {
    str += '<button id="page" data-page="' + i +'" type="button" class="btn btn-secondary" ';
    if (i == data.current_page) {
      str += 'disabled';
    }
    str += '>'+i+'</button>';
  }
  if (data.next_page) {
    str += '<button id="page" data-page="' + (data.last_page+1) + '" type="button" class="btn btn-secondary">&raquo;</button>'
  }

  str += '</div> \
    </div> \
    </div> \
    </div> \
  '
  document.getElementById("page1").innerHTML = str;
  document.getElementById("page2").innerHTML = str;  
}



function make_log(key, value, left=2, right=10) {
  row = m_col(left, key, aligh='right');
  row += m_col(right, value, aligh='left');
  return row;
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
            console.log(nextEl);
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