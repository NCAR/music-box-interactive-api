$(document).ready(function(){

  /*
   * File Upload
   */

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

  /*
   * Initial species concentrations
   */

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

  /*
   * Environmental conditions
   */

  /*
   * Reaction rates
   */

  // new initial reaction rate/rate constant
  $("#new-initial-reaction-rate").on('click', function(){
    $.ajax({
      url: "/conditions/new-initial-reaction-rate",
      type: 'get',
      success: function(response){
        window.location.href = "/conditions/initial#reaction-rates";
        location.reload();
      }
    });
  });

  // matches units to selected reaction type
  $('.musica-named-reaction-dropdown').filter(function() {
    var reaction = $(this).val();
    update_reaction_units($(this).parent().parent(), reaction);
  });
  $('.musica-named-reaction-dropdown').change(function() {
    var reaction = $(this).val();
    update_reaction_units($(this).parent().parent(), reaction);
  });

  // returns units for a given reaction
  function update_reaction_units(container, reaction_name) {
    units = '';
    if (typeof reaction_name !== typeof undefined) {
      switch(reaction_name.substring(0,4)) {
        case 'EMIS':
          units = 'mol m-3 s-1';
          break;
        case 'LOSS':
          units = 's-1';
          break;
        case 'PHOT':
          units = 's-1';
          break;
      }
    }
    container.children().children('.musica-named-reaction-units-dropdown').html(`
      <option value="`+units+`">`+units+`</option>`);
    container.children().children('.musica-named-reaction-units-dropdown').val(units);
  }

  // removes an initial reaction rate/rate constant
  $('.remove-reaction-rate-button').on('click', function(){
    var reaction_name = $(this).parent().parent().children().children('.musica-named-reaction-dropdown').attr('reaction');
    $.ajax({
      url: 'remove-initial-reaction-rate',
      type: 'get',
      data: {"reaction": reaction_name},
      success: function(response){
      }
    });
  });


});
