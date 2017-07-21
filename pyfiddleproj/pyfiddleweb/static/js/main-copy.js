var canRun = true;
var canReset = true;
var canSave = true;
var editor;
$(document).ready(function () {
  /* semantic js */
  $('.ui.dropdown').dropdown();
  $('.ui.accordion').accordion();
  $(".help.button").click(function(){
    $('.longer.modal').modal('show');
  });

  loader = $(".preloader-parent-div");
  loader.show();
  height = $(window).height();
  width = $(window).width();
  width_body = (width*0.6)+15;
  window.onload = function() {
    editor = CodeMirror.fromTextArea(id_code, {
      mode: "python",
      lineNumbers: true,
      lineWrapping: true,
      theme : 'monokai',
      tabSize: 4,
      indentUnit: 4,
      autofocus: true,
    });
    editor.setSize(null,height*0.72);
    var change_count = 0
    editor.on("change", function(editor) {
      change_count += 1;
      if (change_count == 50) {
        change_count = 0;
        Materialize.toast("Considerable amount of code change detected, consider saving by clicking save button", 4000);
      }
    });  };
  $('.main-body').attr("style", 'margin-left:'+width*0.2+'px !important;');
  $('.main-body').width(width_body);
  if (height*0.1 < 80) {
    $(".action-row").height(80);
  } else {
    $(".action-row").height(height*0.1);
  }
  //$('#shell_div').height(height*0.25);
  $('#shell_div').width(width_body);
  //$('#shell_output').width(width_body-15);
  $('#shell_output').height(height*0.72);
  $('.footer-custom').attr("style", 'margin-left:'+width*0.2+'px !important; bottom: 0 !important');
  $('.footer-custom').width(width_body);
  $("input[value='General']").parent().find("span").each(function () {
    $(this).addClass("run");
  }
  )
  // pre ajax call setup
  var csrftoken = $.cookie('csrftoken');

  function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  var delay = ( function() {
    var timer = 0;
    return function(callback, ms) {
      clearTimeout (timer);
      timer = setTimeout(callback, ms);
    };
  })();

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
      }
    }
  })
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
  function share_modal_open(fiddle_id) {
    var url_to_display = $.url(document.URL).attr().base;
    $("#share-modal").modal('open');
    $("#url_to_display_text").val(url_to_display+"/fiddle/"+fiddle_id+"/?i=true");
    $("#url_to_display_text").select();
    $("#button_copy_url").on("click", function () {
      $("#url_to_display_text").select();
      document.execCommand("copy");
      Materialize.toast("Copied Link", 4000);
    })
  }

  $("#id_upload").on('change', function(e) {
    e.preventDefault();
    var action = "upload"
    var data = {}
    var fiddle_id = document.URL.split("/")[4]
    data.fiddle_id = fiddle_id;
    submit_ajax_form(action, data);
  })
  $(document).on('click', '.file_to_delete', function(){
    var action = "file_delete"
    var data = {}
    var fiddle_id = document.URL.split("/")[4];
    var file_name = $(this).attr("value");
    data.fiddle_id = fiddle_id;
    data.file_name = file_name;
    data.file_id = $(this).attr("id")
    submit_ajax_form(action, data)
  });
  function submit_ajax_form(action, data_to_send) {
    loader.show();
    editor.save();
    var options = {
      statusCode: {
        500: function() {
          canSave = true;
          canReset = true;
          canRun = true;
          Materialize.toast("Uknown Error Occured", 4000);
        },
        504: function() {
          canSave = true;
          canReset = true;
          canRun = true;
          Materialize.toast("Uknown Error Occured", 4000);
        },
      },
      dataType: 'json',
      data: data_to_send,
      url: "/prod/"+action+"/",
      success: function(data, textStatus, jqXHR) {
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
        loader.hide();
      },
      error: function(jqXHR, textStatus, errorThrown){
        if(textStatus == "timeout") {
          Materialize.toast("Exceeded computation limit", 4000);
        } else {
          Materialize.toast(errorThrown, 4000);
        }
        loader.hide();
      },
      timeout: 300000
    }
    $('#fiddle_form').ajaxSubmit(options);
  }
  function exec_run(data) {
    canRun = true;
    if (data.error != undefined) {
      Materialize.toast(data.error, 4000);
    } else {
      if (data.statusCode != 200) {
        Materialize.toast("Uknown Error Occured", 4000);
      }
      if (data.statusCode == 200) {
        $("#shell_output").text("read-only@bash: "+atob(data.output));
        Materialize.toast("Successfully ran Fiddle", 4000);
      }
    }
  };
  function exec_save(data) {
    canSave = true;
    if (data.errors != undefined) {
      $.each(JSON.parse(data.errors), function(err, val) {
        Materialize.toast(err+" : "+val[0].message, 4000);
      });
    }
    if (data.fiddle_id != undefined) {
      window.location = '/fiddle/'+data.fiddle_id+'/?m='+data.message;
    } else {
      Materialize.toast(data.message, 4000);
    }
  };
  function exec_star(data) {
    Materialize.toast(data.message, 4000);
  };
  function exec_share(data) {
    if (data.errors != undefined) {
      $.each(JSON.parse(data.errors), function(err, val) {
        Materialize.toast(err+" : "+val[0].message, 4000);
      });
    } else {
      if (data.fiddle_id != undefined) {
        share_modal_open(data.fiddle_id);
      }
      Materialize.toast(data.message, 4000);
    }
  };
  function exec_delete(data) {
    if (data.status == 0) {
      Materialize.toast(data.message, 4000);
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
      window.location = '/fiddle/'+data.fiddle_id+'/?m=Uploaded files';
    }
    if (data.status == true) {
      files = $("#file-list").empty();
      $.each(data.files, function(key, value) {
        files.append(
          '<div>'+
          '<div class="file-chip chip"><span class="fa fa-file fa-1x">&nbsp;</span>'+value.name+'</div>'+
          '<span id="'+value.id+'" name="file_to_delete" class="file_to_delete pointer fa fa-minus-circle fa-1x" value="'+value.name+'">' +
          '</span>'+
          '</div>'
        )
      });
      Materialize.toast("Uploaded files", 4000);
    } else {
      Materialize.toast("One or more files could not be uploaded", 4000);
    }
  }
  function exec_file_delete(data, file_id) {
    if (data.status == 1) {
      Materialize.toast("File Deleted", 4000);
      $("#"+file_id).parent().remove();
    }
    if (data.status == 2) {
      Materialize.toast("Not your fiddle to delete", 4000);
    }
    if (data.status == 0) {
      Materialize.toast("Could not delete file", 4000);
    }
  }
  function submit_email_ajax_form(form_name) {
    loader.show();
    var options = {
      dataType: 'json',
      url: '/prod/email/',
      success: function(data, textStatus, jqXHR) {
        Materialize.toast(data.message, 4000)
        loader.hide();
      },
      error: function(jqXHR, textStatus, errorThrown){
        if(textStatus == "timeout") {
          Materialize.toast("Exceeded computation limit", 4000);
        } else {
          Materialize.toast(errorThrown, 4000);
        }
        loader.hide();
      },
      timeout: 300000
    }
    $('#email_form').ajaxSubmit(options);
  }
});
$(window).load(function() {
  var date = new Date();
  date.setTime(date.getTime() + (1440 * 60 * 1000));
  $.cookie("i", "true", { expires: date });
  width = $(window).width();
  loader = $(".preloader-parent-div");
  loader_small = $(".preloader-small-parent-div");
  if (width < 1000) {
    $("input[value='General']").parent().find("span").each(function () {
      $(this).addClass("run");
    });
    $("#small_devices").show();
    $("#main-container").hide();
    $("#features, #info").hide();
    loader_small.hide();
    $("#email_form_button_2").on('click', function(e) {
      e.preventDefault();
      submit_email_ajax_form_2(this.id);
    });
    function submit_email_ajax_form_2(form_name) {
      loader_small.show();
      var options = {
        dataType: 'json',
        url: '/prod/email/',
        success: function(data, textStatus, jqXHR) {
          Materialize.toast(data.message, 4000)
          loader_small.hide();
        },
        error: function(jqXHR, textStatus, errorThrown){
          if(textStatus == "timeout") {
            Materialize.toast("Exceeded computation limit", 4000);
          } else {
            Materialize.toast(errorThrown, 4000);
          }
          loader_small.hide();
        },
        timeout: 300000
      }
      $('#email_form_2').ajaxSubmit(options);
    }
  } else {
    $('.input-field label').addClass('active');
    $("#main-container").show();
    $("#features, #info").show();
    $(".preloader-parent-div").hide();
    if ($.url(document.URL).param().i == "true") {
      $('#features').trigger("click");
    }
  }
  $(window).resize(function() {
    width = $(window).width();
    if (width < 1000) {
      $("input[value='General']").parent().find("span").each(function () {
        $(this).addClass("run");
      });
      $("#small_devices").show();
      loader_small.hide();
      $("#main-container").hide();
      $("#features, #info").hide();
    } else {
      $(".preloader-parent-div").hide();
      $("#main-container").show();
      $("#features, #info").show();
      $("#small_devices").hide();
    }
  });
  document.addEventListener("keydown", function (zEvent) {
    if (((zEvent.ctrlKey == true || zEvent.metaKey == true) && zEvent.key == "Enter") && canRun == true ){
      canRun = false;
      $("#run").trigger("click");
    }
    if (((zEvent.ctrlKey == true || zEvent.metaKey == true) && zEvent.key == "s") && canSave == true ){
      zEvent.preventDefault()
      canSave = false;
      $("#save").trigger("click");
    }
    if (((zEvent.ctrlKey == true || zEvent.metaKey == true) && zEvent.key == "Backspace") && canReset == true ){
      zEvent.preventDefault()
      editor.setValue("");
      editor.clearHistory();
      editor.clearGutter("gutterId");
    }
  });
});
