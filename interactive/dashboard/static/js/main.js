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
    $('#plot').html("<h3><div id='plotmessage'></div></h3>")
    $("#plotnav").children().attr('class', 'none');
    $('#'+linkId).attr('class','selection');
    $.ajax({
      url: 'plots/get_contents',
      type: 'get',
      data: {"type": linkId},
      success: function(response){
        $("#plotbar").html(response);
        $("#plotmessage").html('Select items from the left to plot');
      }
    });
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
  $("#runM").on('click', function(){
    $.ajax({
      url: "/model/run",
      type: 'get',
      success: function(response){
        $.ajax({
          url: "/model/check",
          type: 'get',
          success: function(response){
            if (response == 'true') {
              $('#download_results').remove();
              $('#plot_results').remove();
              $('#sidenav').append("<a id='plot_results' href='/visualize'>Plot Results</a>");
              $('#sidenav').append("<a href='/model/download' id='download_results' class='download_results'>Download Results</a>");
            } else {
              $('#download_results').remove();
            }
          }
        });
      }
    });
  });
  

  // subproperty plot buttons
  $("body").on('click', "button.sub_p", function(){
    $("#plotmessage").html('')
    var linkId = $(this).attr('id');
    if ($(this).attr('clickStatus') == 'true'){
      $(this).attr('clickStatus', 'false')
      $("#" + linkId +'plot').remove()
    } else {
      $(this).attr('clickStatus','true');
    if ($('#species').attr('class') == 'selection'){
      var propType = 'CONC.'
    } else if ($('#rates').attr('class') == 'selection'){
      var propType = 'RATE.'
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
        MathJax.typeset()
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
    $.ajax({
      url: "/mechanism/equation",
      type: 'get',
      data: {'name': itemName},
      success: function(response){
        $('#equation_box').html(response);
        MathJax.typeset()
      }
    });
  }


});
