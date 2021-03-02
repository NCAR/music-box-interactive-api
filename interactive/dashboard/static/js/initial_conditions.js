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

  // loads the initial species concentrations
  load_initial_concentrations();
  function load_initial_concentrations() {
    $.ajax({
      url: 'initial-species-concentrations',
      type: 'get',
      dataType: 'json',
      data: {},
      success: function(initial_concentrations) {
        $.ajax({
          url: '/mechanism/conditions-species-list',
          type: 'get',
          dataType: 'json',
          data: {},
          success: function(result) {
            $("#initial-concentration-container").empty();
            $("#initial-concentration-container").append(`
              <div class="row">
                <div class="col-4">Species name</div>
                <div class="col-3">Intial value</div>
                <div class="col-3">Units</div>
              </div>`);
            for (key in initial_concentrations) {
              $('#initial-concentration-container').append(initial_concentration_row_html(result["species"]));
              $('#initial-concentration-container div:last-child .species-dropdown').val(key);
              $('#initial-concentration-container div:last-child .initial-value').val(initial_concentrations[key]["value"]);
              $('#initial-concentration-container div:last-child .units-dropdown').val(initial_concentrations[key]["units"]);
            }
          }
        });
      }
    });
  }

  // adds a row to the initial concentration list
  $(".initial-concentration-add").on('click', function(){
    $.ajax({
      url: '/mechanism/conditions-species-list',
      type: 'get',
      dataType: 'json',
      data: {},
      success: function(result) {
        $("#initial-concentration-container").append(initial_concentration_row_html(result["species"]));
      }
    });
  });

  // removes a row from the initial concentration list
  $('#initial-concentration-container').on('click', '.btn-remove-row', function() {
    $(this).closest('.row').remove();
  });

  // returns the html for a initial concentration row
  function initial_concentration_row_html(species_list) {
    var html = `
          <div class="row my-1 row-data">
            <div class="col-4">
              <select class="form-control species-dropdown">
                <option value="Select species" selected>Select species</option>`;
    for (id in species_list) {
      html += `
                <option value="`+species_list[id]+`">`+species_list[id]+`</option>`;
    }
    html += `
              </select>
            </div>
            <div class="col-3">
              <input type="text" class="form-control initial-value">
              </input>
            </div>
            <div class="col-3">
              <select class="form-control units-dropdown">
                <option value="mol m-3" selected>mol m-3</option>
                <option value="molecule m-3">molecule m-3</option>
                <option value="mol cm-3">mol cm-3</option>
                <option value="molecule cm-3">molecule cm-3</option>
              </select>
            <div class="col-2">
              <button class="btn btn-secondary btn-remove-row">
                Remove
              </button>
            </div>
          </div>`;
    return html;
  }

  // removes a row from the initial concentration list
  $("#initial-concentration-container").on('click', '.btn-remove', function() {
    $(this).closest('.row').remove();
  });

  // saves the initial species concentrations
  $(".btn-save-initial-concentrations").click(function() {
    const csrftoken = $('[name=csrfmiddlewaretoken]').val();
    initial_concentrations = {};
    $("#initial-concentration-container .row-data").each(function() {
      initial_concentrations[$(this).find(".species-dropdown").val()] =
        {
          "value" : $(this).find(".initial-value").val(),
          "units" : $(this).find(".units-dropdown").val()
        };
    });
    $.ajax({
      url:'initial-species-concentrations-save',
      type: 'post',
      headers: {'X-CSRFToken': csrftoken},
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      data: JSON.stringify(initial_concentrations),
      success: function(response) {
        location.reload();
      },
      error: function(response) {
        alert(response['error']);
      }
    });
  });

  // cancels changes to the initial species concentrations
  $(".btn-cancel-initial-concentrations").click(function() {
    load_initial_concentrations();
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
