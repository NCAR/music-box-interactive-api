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
        $('#download_results').remove();
        $('#plot_results').remove();
        $('#main-nav').append("<a class='nav-link' id='plot_results' href='/visualize'>Plot Results</a>");
        $('#main-nav').append("<a class='nav-link' href='/model/download' id='download_results' class='download_results'>Download Results</a>");
        if (window.location.href.indexOf("visualize") > -1) {
          $('#plot_results').addClass('active');
          $('#plot_results').attr('aria-current', 'page');
        }
      }
    }
  });

  // changes run button after click
  $("#runMB").on('click', function(){
    $('#runMB').attr('emphasis', 'false')
  });

});
