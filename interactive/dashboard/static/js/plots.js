$(document).ready(function(){

  // default plot sub-page
  var linkId = $('.propfam:first-child').attr('id');
  $('.propfam:first-child').attr('class','propfam btn btn-primary btn-ncar-active');
  if (typeof linkId !== typeof undefined && linkId !== '') {
    $.ajax({
      url: 'plots/get_contents',
      type: 'get',
      data: {"type": linkId},
      success: function(response){
        $("#plotbar").html(response);
      }
    });
  }

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
    $('#plot').prepend('<img id="'+linkId+ 'plot"src="plots/get?type=' + prop + '">');
    }
  });

  //update plot units from select
  $(document).on('change', "#plotsUnitSelect", function() {
    var unitName = $(this).val();
    $.ajax({
      url: 'plots/select-units',
      type: 'get',
      data: {"unit": unitName},
      success: function(response){
      }
    });
  });
});
