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
              $('#sidenav').append("<a class='" + "{% if '/visualize' in request.path %} current {% endif %}'" + 'href="/visualize">Plot Results</a>');
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
    $.ajax({
      url: 'plots/get',
      type: 'get',
      data: {"type": linkId},
      success: function(response){
        $("#plotbar").html(response);
      }
    });
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
});
