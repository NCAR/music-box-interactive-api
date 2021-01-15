$(document).ready(function(){
//remove species button
  $('.r_button').on('click', function(){
    var buttonId = $(this).attr('id');

    $.ajax({
    url: 'species/remove',
    type: 'get',
    data: {"species": buttonId},
    success: function(response){

    }
   }); 
  });

  // plot species and plot rates buttons
  $(".propfam").on('click', function(){
    var linkId = $(this).attr('id');
    $('#plot').html("")
    $(".propfam").attr('class', 'propfam btn btn-secondary');
    $('#'+linkId).attr('class','propfam btn btn-primary btn-ncar-active');
    if (linkId == "custom"){
      $.ajax({
        url: 'plots/custom',
        type: 'get',
        success: function(response){
        
        }
      });
    } else {
      $.ajax({
        url: 'plots/get_contents',
        type: 'get',
        data: {"type": linkId},
        success: function(response){
          $("#plotbar").html(response);
        }
      });
    }
  });
  //plot property buttons
  $(".prop").on('click', function(){
    var linkId = $(this).attr('id');
    $("#plotnav").children().attr('class', 'none');
    $('#'+linkId).attr('class','selection');
    $("#plotbar").html("");
    $.ajax({
      url: 'plots/get',
      type: 'get',
      data: {"type": linkId},
      success: function(response){
      
      }
    });
  });



  //run model button
  $("#run-model").on('click', function(){
    $.ajax({
      url: "/model/run",
      type: 'get',
      success: function(response){
        if (response["model_connected"]){
          $.ajax({
            url: "/model/check",
            type: 'get',
            success: function(response){
              if (response["status"] == 'done') {
                $('#download_results').remove();
                $('#plot_results').remove();
                $('#main-nav').append("<a class='nav-link' id='plot_results' href='/visualize'>Plot Results</a>");
                $('#main-nav').append("<a class='nav-link' href='/model/download' id='download_results' class='download_results'>Download Results</a>");
              } else if (response["status"] == 'error'){
                  alert("ERROR " + response["e_code"] + "   " + response["e_message"]);
                  if (response["e_type"] == 'species'){
                    $("#" + response['spec_ID']).css("border", "3px solid red")
                    $("#" + response['spec_ID']).css("border-radius", "4px")
                  }
              } else {
                alert('unknown error')
              }
            }
          });
        } else {
          alert('model is not connected')
        }
      }
    });
  });
  // check if model has been run or if config changed
  $.ajax({
    url: "/model/check-load",
    type: 'get',
    success: function(response){
      if (response["status"] == 'done') {
        $('#download_results').remove();
        $('#plot_results').remove();
        $('#main-nav').append("<a class='nav-link' id='plot_results' href='/visualize'>Plot Results</a>");
        $('#main-nav').append("<a class='nav-link' href='/model/download' id='download_results' class='download_results'>Download Results</a>");
        if (window.location.href.indexOf("visualize") > -1) {
          $('#plot_results').addClass('active');
          $('#plot_results').attr('aria-current', 'page');
        }
      }
      if (response["buttonstatus"]){
        $('#run-model').addClass('enabled')
        $('#run-model').removeClass('disabled')
      } else {
        $('#run-model').removeClass('enabled')
        $('#run-model').addClass('disabled')
      }
    }
  });

  // change run button after click
  $("#runMB").on('click', function(){
    $('#runMB').attr('emphasis', 'false')
  });

  // subproperty plot buttons
  $("body").on('click', "a.sub_p", function(){
    $("#plotmessage").html('')
    var linkId = $(this).attr('id');
    if ($(this).attr('clickStatus') == 'true'){
      $(this).attr('class', 'sub_p list-group-item list-group-item-action')
      $(this).attr('clickStatus', 'false')
      $("#" + linkId +'plot').remove()
    } else {
      $(this).attr('class', 'sub_p list-group-item list-group-item-action active')
      $(this).attr('clickStatus','true');

    if ($('#species').hasClass('btn-ncar-active')){
      var propType = 'CONC.'
    } else if ($('#rates').hasClass('btn-ncar-active')){
      var propType = 'RATE.'
    } else if ($('#env').hasClass('btn-ncar-active')){
      var propType = 'ENV.'
    }
    var prop = propType + linkId;
    $('#plot').append('<img id="'+linkId+ 'plot"src="plots/get?type=' + prop + '">');
    }
  });
 

  //new photolysis reaction
  $("#newPhoto").on('click', function(){
    $.ajax({
      url: "/configure/new-photo",
      type: 'get',
      success: function(response){
        location.reload()
      }
    });
  });

  // load mechanism item data
  $(".mechanism_item").on('click', function(){
    var itemName = $(this).attr('id')
    $('#message_box').html('');
    $('#sidemenu').children().children().attr('status','null')
    $('#'+ itemName).attr('status', 'selected')
    $.ajax({
      url: "/mechanism/load",
      type: 'get',
      data: {'name': itemName},
      success: function(response){
        $('#molec_detail').html(response);
        MathJax.typeset()

      }
    });
    $.ajax({
      url: "/mechanism/equation",
      type: 'get',
      data: {'name': itemName},
      success: function(response){
        $('#equation_box').html(response);
        MathJax.typeset()
      }
    });
  });

  //edit mechanism item
  $("body").on('click', "button.mech_edit", function(){
    var itemId = $(this).attr('species');
    $.ajax({
      url: "/mechanism/edit",
      type: 'get',
      data: {'name': itemId},
      success: function(response){
        $('#molec_detail').html(response);
        MathJax.typeset()
      }
    });
  });

  if (typeof $("#molec_detail").attr('save') == 'string'){
    var itemName = $("#molec_detail").attr('save');
    $('#molec_detail').html('');
    $.ajax({
      url: "/mechanism/load",
      type: 'get',
      data: {'name': itemName},
      success: function(response){
        $('#molec_detail').html(response);
        MathJax.typeset()

      }
    });
    $.ajax({
      url: "/mechanism/equation",
      type: 'get',
      data: {'name': itemName},
      success: function(response){
        $('#equation_box').html(response);
        MathJax.typeset()
      }
    });
  } else if (typeof $("#molec_detail").attr('error') == 'string'){
      alert($("#molec_detail").attr('error'))
  }

  //new molecule in mechanism
  $("#newmolecule").on('click', function(){
    $('#sidemenu').children().children().attr('status','null');
    $.ajax({
      url: "/mechanism/newmolec",
      type: 'get',
      success: function(response){
        $('#equation_box').html('');
        $('#molec_detail').html(response);
        MathJax.typeset()
      }
    });
  });
  
  // load mechanism reaction data
  $(".mechanism_reaction").on('click', function(){
    var itemName = $(this).attr('reaction')
    $('#message_box').html('');
    $('#sidemenu').children().children().attr('status','null')
    $(this).attr('status', 'selected')
    $.ajax({
      url: "/mechanism/load_reaction",
      type: 'get',
      data: {'name': itemName},
      success: function(response){
        $('#react_detail').html(response);
        
      }
    });
  });

  //edit mechanism reaction
  $("body").on('click', "button.mech_edit_R", function(){
    var itemId = $(this).attr('reaction');
    $.ajax({
      url: "/mechanism/edit_reaction",
      type: 'get',
      data: {'name': itemId},
      success: function(response){
        $('#react_detail').html(response);
        MathJax.typeset()
      }
    });
  });

  // load correct reaction after save
  if (typeof $("#react_detail").attr('save') == 'string'){
    var itemName = $("#react_detail").attr('save');
    $('#message_box').html('');
    $.ajax({
      url: "/mechanism/load_reaction",
      type: 'get',
      data: {'name': itemName},
      success: function(response){
        $('#react_detail').html(response);

      }
    });
  }

  //link products and reactants to molecule pages
  $("body").on('click', "a.r_to_m", function(){
    var itemId = $(this).attr('id');
    $.ajax({
      url: "/mechanism/r_to_m",
      type: 'get',
      data: {'name': itemId},
      success: function(response){
      }
    });
  });

  //check if there were reaction search results
  if (typeof $("#react_detail").attr('error') == 'string'){
    alert($("#react_detail").attr('error'))
  }

 // if evolving conditions have been read in show linear combination button
  if ( $("#evolvtable").length ){
    $("#evolvcontent").append('<button class="btn btn-secondary" id="linear_combo">Add Linear Combination</button>')
  }


  $("#linear_combo").on('click', function(){
    $('#evolvcontent').html('');
    $.ajax({
      url: "/configure/linear_combination_form",
      type: 'get',
      success: function(response){
        $('#evolvcontent').html(response);
      }
    });
  });


  // if photolysis file is uploaded and no start date is selected
  if ( $('#isFileUploaded').length ){
    $('#photo_file_panel').append('<button id="simstart">Choose simulation start time</button>')
    
  }

  $("#simstart").on('click', function(){
    $('#photo_file_panel').html('');
    $.ajax({
      url: "/configure/photo_datetime_form",
      type: 'get',
      success: function(response){
        $('#photo_file_panel').html(response);
      }
    });
  });

  // logging update toggle switch
  $("#islogon").on('click', function(){
    if ($('#islogon').is(":checked")){
      var loggingOn = "True";
    } else {
      var loggingOn = "False";
    }
    $.ajax({
      url: "/conditions/logging-toggle",
      type: 'get',
      data: {
        "isOn": loggingOn
      },
      success: function(response){
      }
    });
  });

  // fill logging toggle switch correctly
  if ( $('#islogon').length ){
    $.ajax({
      url: "/conditions/logging-toggle-check",
      type: 'get',
      success: function(response){
        if (response["isOn"]){
          $('#islogon').prop("checked", true)
        } else {
          $('#islogon').prop("checked", false)
        }
      }
    });
  }
 // clear evolving conditions files button
  $("#clearEvolvFiles").on('click', function(){
    $.ajax({
      url: "/conditions/clear-evolv-files",
      type: 'get',
      success: function(response){
        location.reload();
      }
    });
  });


  // check if forms have been changed
  $('form :input').on('change input', function() {
      var name = $(this).attr('savebutton')
      $("#" + name).addClass('btn-ncar-active')
  });

  

  $("#exampleToggle").on('click', function(){
    $(".example-panel").collapse('show')
  });

  
});
