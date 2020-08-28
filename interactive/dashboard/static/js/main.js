$(document).ready(function(){


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

  
});


$(document).ready(function(){
  
  $(".sub_p").on('click', function(){
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
});