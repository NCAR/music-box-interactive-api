$(document).ready(function() {

  //collapse panels on getting started page
  $("#exampleToggle").on('click', function(){
    $(".load-panel").collapse('hide')
    $(".example-panel").collapse('show')
  });

  // collapses load-configuration panel
  $("#loadToggle").on('click', function(){
    $(".example-panel").collapse('hide')
    $(".load-panel").collapse('show')
  });

});
