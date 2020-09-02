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

    $("#plotnav").children().attr('class', 'none');
    $('#'+linkId).attr('class','selection');
    $.ajax({
      url: 'plots/get_contents',
      type: 'get',
      data: {"type": linkId},
      success: function(response){
        $("#plotbar").html(response);
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
    var linkId = $(this).attr('id');

    if ($('#species').attr('class') == 'selection'){
      var propType = 'CONC.'
    } else if ($('#rates').attr('class') == 'selection'){
      var propType = 'RATE.'
    }
    var prop = propType + linkId;
    $('#plot').html('<img src="plots/get?type=' + prop + '">');
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
    $.ajax({
      url: "/mechanism/load",
      type: 'get',
      data: {'name': itemName},
      success: function(response){
        $('#molec_detail').html(response);
      }
    });
  });
});
