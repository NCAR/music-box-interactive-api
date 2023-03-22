function beautifyReaction(reaction) {
  reaction.replace('->', '→');
  reaction.replace('_', ' + ');
  
  return reaction
}
function refreshTableNames() {
  var children = document.getElementById('plotbar').children;
  for (var i = 0; i < children.length; i++) {
    var tableChild = children[i];
    tableChild.innerHTML = beautifyReaction(tableChild.innerHTML);
  }
}
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
        refreshTableNames();
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
          refreshTableNames();
        }
      });
    }
  });
  refreshTableNames();
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
        refreshTableNames();
      }
    });
  });

  // subproperty plot buttons
  $("body").on('click', "a.sub_p", function(){
    $("#plotmessage").html('')
    var linkId = $(this).attr('id')
    if ($(this).attr('clickStatus') == 'true'){
      $(this).attr('class', 'sub_p list-group-item list-group-item-action')
      $(this).attr('clickStatus', 'false')
      $(this).text($(this).text().replace("☑", "☐")); // change to empty checkbox


      $("#" + linkId.replace(">", "") +'plot').remove(); // '>' is not valid for an id in html5
    } else {
      $(this).attr('class', 'sub_p list-group-item list-group-item-action active')
      $(this).attr('clickStatus','true');
      $(this).text($(this).text().replace("☐", "☑"));  // change to ticked checkbox
    if ($('#species').hasClass('btn-ncar-active')){
      var propType = 'CONC.'
    } else if ($('#rates').hasClass('btn-ncar-active')){
      var propType = 'CONC.myrate__'
    } else if ($('#env').hasClass('btn-ncar-active')){
      var propType = 'ENV.'
    }
    var prop = propType + linkId;
    if ($("#plotsUnitSelect").length) {
      var plotUnit = $("#plotsUnitSelect").val();
    } else {
      var plotUnit = 'n/a'
    }

    $('#plot').prepend('<img id="'+linkId.replace(">", "")+ 'plot"src="plots/get?type=' + prop + '&unit=' + plotUnit + '">'); // replace '>' with '' to get rid of invalid id
    refreshTableNames();
    }
  });
 
  //update plot units from select
  $(document).on('change', "#plotsUnitSelect", function() {
    var unitName = $(this).val();
    var plotsList = $('#plot').children();
    var plotsNameList = []
    $.each(plotsList, function(i, plot){
      var name = plot.id;
      var speciesName = name.replace("plot", "");
      plotsNameList.push(speciesName);
    });
    $('#plot').empty();
    $.each(plotsNameList, function(i, name){
      $('#plot').append('<img id="'+ name + 'plot"src="plots/get?type=CONC.' + name + '&unit=' + unitName + '">');
    });
  });

});
