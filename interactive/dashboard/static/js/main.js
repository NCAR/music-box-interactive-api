$(document).ready(function(){

  // disables enter button, unless a button or link has focus
  $('body').on('keypress', ':not(button, a)', function(event) {
    if (event.keyCode == '13') {
      event.preventDefault();
    }
  });

  // sets enter key or space bar to trigger click when button or link has focus
  $('body').on('keypress', 'button, a', function(event) {
    if (event.keyCode == '13' || event.keyCode == '32') {
      event.preventDefault();
      $(this).click();
    }
  });

  // add links for plotting and downloading configuration/results
  function display_post_run_menu_options() {
    $('#post-run-links').html(`
      <small class='nav-section'>ANALYSIS</small>
      <a class='nav-link' id='plot-results-link' href='/visualize'><span class='oi oi-graph'></span>Plot Results</a>
      <a class='nav-link' id='download-link' href='/download'><span class='oi oi-data-transfer-download'></span>Download</a>
      `);
  }

  // runs the model
  $("#run-model").on('click', function(){
    $.ajax({
      url: "/model/run",
      type: 'get',
      success: function(response){
        if (response["model_running"]){
          $.ajax({
            url: "/model/check",
            type: 'get',
            success: function(response){
              if (response["status"] == 'done') {
                display_post_run_menu_options();
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
          alert(response["error_message"])
        }
      }
    });
  });

  // checks if model has been run or if config changed
  $.ajax({
    url: "/model/check-load",
    type: 'get',
    success: function(response){
      if (response["status"] == 'done') {
          display_post_run_menu_options();
        if (window.location.href.indexOf("visualize") > -1) {
          $('#plot-results-link').addClass('active');
          $('#plot-results-link').attr('aria-current', 'page');
        }
        if (window.location.href.indexOf("download") > -1) {
          $('#download-link').addClass('active');
          $('#download-link').attr('aria-current', 'page');
        }
      }
    }
  });

  // changes run button after click
  $("#runMB").on('click', function(){
    $('#runMB').attr('emphasis', 'false')
  });

});
