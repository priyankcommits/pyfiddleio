/* globals */
var height = $(window).height();
var width = $(window).width();
var loader = $('#loader-div');
var spinner = $('#spinner-div');
var canRun = true;
var canReset = true;
var canSave = true;
var editor;

/* pre ajax call setup */
var csrftoken = $.cookie('csrftoken');

function csrfSafeMethod(method) {
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
    }
  }
})

/* ajax form submit */
function submit_ajax_form(action, data_to_send) {
  spinner.show();
  editor.save();
  var options = {
    statusCode: {
      500: function() {
        canSave = true;
        canReset = true;
        canRun = true;
        toaster("Uknown Error Occured", 4000);
      },
      504: function() {
        canSave = true;
        canReset = true;
        canRun = true;
        toaster("Uknown Error Occured", 4000);
      },
    },
    dataType: 'json',
    data: data_to_send,
    url: "/"+action+"/",
    success: function(data, textStatus, jqXHR) {
      /* Execute callbacks */
      if (action == "run") {
        exec_run(data);
      }
      if (action == "save") {
        exec_save(data);
      }
      if (action == "star") {
        exec_star(data);
      }
      if (action == "share") {
        exec_share(data);
      }
      if (action == "delete") {
        exec_delete(data);
      }
      if (action == "upload") {
        exec_upload(data);
      }
      if (action == "file_delete") {
        exec_file_delete(data, data_to_send.file_id);
      }
      spinner.hide();
    },
    error: function(jqXHR, textStatus, errorThrown){
      if(textStatus == "timeout") {
        toaster("Exceeded computation limit", 4000);
      } else {
        toaster(errorThrown, 4000);
      }
      spinner.hide();
    },
    timeout: 300000
  }
  $('#fiddle_form').ajaxSubmit(options);
}
function exec_run(data) {
  canRun = true;
  if (data.error != undefined) {
    toaster(data.error, 4000);
  } else {
    if (data.statusCode != 200) {
      toaster("Uknown Error Occured", 4000);
    }
    if (data.statusCode == 200) {
      $(".shell-result").animate({ scrollTop: $('.shell-result').prop("scrollHeight")}, 1000);
      $("#shell_output").html($("#shell_output").html()+"<span class='bash-name'>read-only@bash: </span><span class='bash-output'></span>");
      $('.bash-output').last().text(atob(data.output));
      toaster("Successfully ran Fiddle", 4000);
    }
  }
};
function exec_save(data) {
  canSave = true;
  if (data.errors != undefined) {
    $.each(JSON.parse(data.errors), function(err, val) {
      toaster(err+" : "+val[0].message, 4000);
    });
  }
  if (data.fiddle_id != undefined) {
    window.location = '/fiddle/'+data.fiddle_id+'/?m='+data.message;
  } else {
    toaster(data.message, 4000);
  }
};
function exec_star(data) {
  toaster(data.message, 4000);
};
function exec_share(data) {
  if (data.errors != undefined) {
    $.each(JSON.parse(data.errors), function(err, val) {
      toaster(err+" : "+val[0].message, 4000);
    });
  } else {
    if (data.fiddle_id != undefined) {
      share_modal_open(data.fiddle_id);
    }
    toaster(data.message, 4000);
  }
};
function exec_delete(data) {
  if (data.status == 0) {
    toaster(data.message, 4000);
  }
  if (data.status == 1) {
    window.location = '/?m="'+data.message+'"';
  }
};
$("#email_form_button").on('click', function(e) {
  e.preventDefault();
  submit_email_ajax_form(this.id);
});
function exec_upload(data) {
  if (data.fiddle_id != undefined) {
    window.location = '/fiddle/'+data.fiddle_id+'/?m=Uploaded file(s)';
  }
  if (data.status == true) {
    files = $("#file-list").empty();
      files.append(
        '<div class="item">' +
        '<i class="file icon"></i>' +
        '<div class="content">' +
        '<div class="header">main.py ( now editing .. )</div></div>'
      )
    $.each(data.files, function(key, value) {
      files.append(
        '<div class="item">' +
        '<i class="file icon"></i>' +
        '<div class="content">' +
        '<div class="header">'+value.name+
        '<span id="'+value.id+'" name="file_to_delete" class="file_to_delete pointer fa fa-minus-circle fa-1x" value="'+value.name+'">' +
        '</span></div></div>'
      )
    });
    toaster("Uploaded files", 4000);
  } else {
    toaster("One or more files could not be uploaded", 4000);
  }
}
function exec_file_delete(data, file_id) {
  if (data.status == 1) {
    toaster("File Deleted", 4000);
    $("#"+file_id).remove();
  }
  if (data.status == 2) {
    toaster("Not your fiddle to delete", 4000);
  }
  if (data.status == 0) {
    toaster("Could not delete file", 4000);
  }
}
function submit_email_ajax_form(form_name) {
  spinner.show();
  var options = {
    dataType: 'json',
    url: '/prod/email/',
    success: function(data, textStatus, jqXHR) {
      toaster(data.message, 4000)
      $(".ui.feedback-form.modal").modal('hide');
      spinner.hide();
    },
    error: function(jqXHR, textStatus, errorThrown){
      if(textStatus == "timeout") {
        toaster("Exceeded computation limit", 4000);
      } else {
        toaster(errorThrown, 4000);
      }
      $(".ui.feedback-form.modal").modal('hide');
      spinner.hide();
    },
    timeout: 300000
  }
  $('#'+form_name).ajaxSubmit(options);
}
function share_modal_open(fiddle_id) {
  var url_to_display = $.url(document.URL).attr().base;
  $(".ui.share-content.modal").modal({"inverted": true}).modal('show');
  $("#url_to_display_text").val(url_to_display+"/fiddle/"+fiddle_id+"/?i=true");
  $("#url_to_display_text").select();
  $("#button_copy_url").on("click", function () {
    $("#url_to_display_text").select();
    document.execCommand("copy");
    toaster("Copied Link", 4000);
  });
  $("#button_copy_url").trigger("click");
}
function upload_file() {
  var action = "upload"
  var data = {}
  var fiddle_id = document.URL.split("/")[4]
  data.fiddle_id = fiddle_id;
  submit_ajax_form(action, data);
}

function delete_file(file_element) {
  var action = "file_delete"
  var data = {}
  var fiddle_id = document.URL.split("/")[4];
  var file_name = file_element.attr("value");
  data.fiddle_id = fiddle_id;
  data.file_name = file_name;
  data.file_id = file_element.attr("id");
  submit_ajax_form(action, data);
}
function resize() {
  height = $(window).height();
  width = $(window).width();
  $("#code-div").height(height-$("#code-div").offset().top);
  editor.setSize(null, height-$("#code-div").offset().top-20);
}
function toaster(message, time) {
  $(".toast-message").append(
    "<div class='ui visible message'>" +
    "<p>"+message+"</p>" +
    "</div>"
  );
  var delay = ( function() {
    var timer = 0;
    return function(callback, ms) {
      clearTimeout (timer);
      timer = setTimeout(callback, ms);
    };
  })();
  delay(function(){
    $('.message').remove();
  }, time );
}
function create_help_cookie() {
  var date = new Date();
  date.setTime(date.getTime() + (1440 * 60 * 1000));
  $.cookie("i", "true", { expires: date });
}

function trigger_help() {
  if ($.url(document.URL).param().i == "true") {
    $('#help').trigger("click");
  }
}

function check_for_mobile_view() {
  if ( height <= 500 || width <=1000 ) {
    $("#desktop-view").hide();
    $("#desktop-header").hide();
    $("#mobile-view").show();
  }
  else {
    $("#desktop-view").show();
    $("#desktop-header").show();
    $("#mobile-view").hide();
  }
}

/* Window ready */
$(document).ready(function () {
  loader.show();
  spinner.hide();
  /* semantic js */
  $('.ui.dropdown').dropdown();
  $('.ui.accordion').accordion();
  $(".help.button").click(function(){
    $('.ui.help-content.modal').modal('show');
  });
  $('.menu .item').tab();
  $('.feedback .button').click(function(){
    $('.ui.feedback-form.modal').modal('show');
  });
  $('.message .close').on('click', function() {
    $(this).closest('.message').transition('fade');
  });

  editor = CodeMirror.fromTextArea(id_code, {
    mode: 'python',
    lineNumbers: true,
    lineWrapping: true,
    theme : 'solarized',
    tabSize: 4,
    indentUnit: 4,
    autofocus: true,
  });
  editor.setSize(null, height-$("#code-div").offset().top-20);
  var change_count = 0
  editor.on('change', function(editor) {
    change_count += 1;
    if (change_count == 50) {
      change_count = 0;
      toaster("Considerable amount of code change detected, consider saving by clicking save button", 4000);
    }
  });
  var fiddle_id = document.URL.split("/")[4];
  if (fiddle_id == undefined || fiddle_id == "" || fiddle_id == null) {
    editor.setValue("print('Your Code Here')")
  }
  resize();
  /* Call Editor, Shell resizer */
  $("input[value='General']").parent().find("span").each(function () {
    $(this).addClass("run");
  }
  )
  /* Button Actions */
  $(".btn-action").on('click', function(e) {
    e.preventDefault();
    var action = $(this).val();
    var data = {}
    var fiddle_id = document.URL.split("/")[4]
    if (fiddle_id != undefined) {
      data.fiddle_id = fiddle_id;
    }
    if (action == "run") {
      submit_ajax_form(action, data);
    }
    if (action == "save") {
      submit_ajax_form(action, data);
    }
    if (action == "star") {
      submit_ajax_form(action, data);
    }
    if (action == "delete") {
      submit_ajax_form(action, data);
    }
    if (action == "share") {
      if (fiddle_id != undefined) {
        share_modal_open(fiddle_id);
      } else {
        submit_ajax_form(action, data);
      }
    }
  });
  /* Upload File */
  $("#file").on('change', function(e) {
    e.preventDefault();
    upload_file();
  })
  /* Delete File */
  $(document).on('click', '.file_to_delete', function(){
    delete_file($(this));
  });
  /* Toasting any url encoded messages */
  var message_url = $.url(document.URL).param().m;
  if (message_url != undefined && message_url != "") {
    toaster(message_url, 4000);
  }
  /* Send Feedback */
  $("#email_form").submit(function(e) {
    e.preventDefault();
    submit_email_ajax_form('email_form');
  });
    $("#email_form_mobile").submit(function(e) {
    e.preventDefault();
    submit_email_ajax_form('email_form_mobile');
  });
  /* Expanding popular fiddles */
  $("#popular").trigger("click");
  check_for_mobile_view();
});
/* Window on load */
$(window).load(function() {
  trigger_help();
  create_help_cookie();
  loader.hide();
  /* Window Resize */
  $(window).resize(function() {
    editor.setSize(null, height-$("#code-div").offset().top-20);
    height = $(window).height();
    width = $(window).width();
    resize();
    check_for_mobile_view();
  });
  document.addEventListener("keydown", function (zEvent) {
    /* Run */
    if (((zEvent.ctrlKey == true || zEvent.metaKey == true) && zEvent.key == "Enter") && canRun == true ){
      canRun = false;
      $("#run").trigger("click");
    }
    /* Save */
    if (((zEvent.ctrlKey == true || zEvent.metaKey == true) && zEvent.key == "s") && canSave == true ){
      zEvent.preventDefault()
      canSave = false;
      $("#save").trigger("click");
    }
    /* Reset */
    if (((zEvent.ctrlKey == true || zEvent.metaKey == true) && zEvent.key == "Backspace") && canReset == true ){
      zEvent.preventDefault()
      editor.setValue("");
      editor.clearHistory();
      editor.clearGutter("gutterId");
      $("#shell_output").text("");
    }
  });
});
