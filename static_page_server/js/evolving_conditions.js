$(document).ready(function(){

  // shows linear combination button if evolving conditions have been read in
  if ( $("#evolvtable").length ){
    $("#evolvcontent").append('<button class="btn btn-secondary" id="linear_combo">Add Linear Combination</button>')
  }

  // saves linear combinations
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

  // clears evolving conditions files button
  $("#clearEvolvFiles").on('click', function(){
    $.ajax({
      url: "/conditions/clear-evolv-files",
      type: 'get',
      success: function(response){
        location.reload();
      }
    });
  });

  // enables save button when linear combinations have been changed
  $(".linear-combo-check").on('change input', function(){
    var name = $(this).attr('addButton');
    $("#" + name).removeClass('disabled')
    $("#" + name).addClass('btn-primary-active')
  });

  // shows scale factor form on click of conc. <li> form
  $('.linear-combo-conc').on('click', function(){
    $("#" + $(this).attr('fileName')).collapse();
  });

  // show/hide input file instructions
  $(".show-hide-input-file-instructions").on('click', function(){
    if ($(this).html() == "Show input file instructions") {
      $(".input-file-instructions").css("display", "block");
      $(this).html("Hide input file instructions");
    } else {
      $(".input-file-instructions").css("display", "none");
      $(this).html("Show input file instructions");
    }
  });


});
