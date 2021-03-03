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
            </div>
            <div class="col-2">
              <button class="btn btn-secondary btn-remove-row">
                Remove
              </button>
            </div>
          </div>`;
    return html;
  }

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

  // loads the initial reaction rates and rate constants
  load_initial_rates();
  function load_initial_rates() {
    $.ajax({
      url: 'initial-reaction-rates',
      type: 'get',
      dataType: 'json',
      data: {},
      success: function(initial_rates) {
        $.ajax({
          url: '/mechanism/reaction-musica-names-list',
          type: 'get',
          dataType: 'json',
          data: {},
          success: function(result) {
            $('#initial-rates-container').empty();
            $('#initial-rates-container').append(`
              <div class="row">
                <div class="col-4">Reaction label</div>
                <div class="col-3">Intial value</div>
                <div class="col-3">Units</div>
              </div>`);
            for (key in initial_rates) {
              $('#initial-rates-container').append(initial_rates_row_html(result['reactions'],[initial_rates[key]["units"]]));
              $('#initial-rates-container div:last-child .reaction-dropdown').val(key);
              $('#initial-rates-container div:last-child .initial-value').val(initial_rates[key]["value"]);
              $('#initial-rates-container div:last-child .units-dropdown').val(initial_rates[key]["units"]);
            }
          }
        });
      }
    });
  }

  // adds a row to the initial reaction rates/rate constants list
  $('.initial-rate-add').on('click', function() {
    $.ajax({
      url: '/mechanism/reaction-musica-names-list',
      type: 'get',
      dataType: 'json',
      data: {},
      success: function(result) {
        $('#initial-rates-container').append(initial_rates_row_html(result['reactions'],[]));
      }
    });
  });

  // removes a row from the initial reaction rates/rate constants list
  $('#initial-rates-container').on('click', '.btn-remove-row', function() {
    $(this).closest('.row').remove();
  });

  // returns html for an initial reaction rate/rate constant row
  function initial_rates_row_html(reactions, units) {
    var html = `
          <div class="row my-1 row-data">
            <div class="col-4">
              <select class="form-control reaction-dropdown">
                <option value="Select reaction" selected>Select reaction</option>`;
    for (const [key, value] of Object.entries(reactions)) {
      html += `
                <option value="`+key+`">`+key+`</option>`;
    }
    html += `
              </select>
            </div>
            <div class="col-3">
              <input type="text" class="form-control initial-value">
              </input>
            </div>
            <div class="col-3">
              <select class="form-control units-dropdown">`;
    for (const key in units) {
      html += `
                <option value="`+units[key]+`">`+units[key]+`</option>`;
    }
    html += `
              </select>
            </div>
            <div class="col-2">
              <button class="btn btn-secondary btn-remove-row">
                Remove
              </button>
            </div>
          </div>`;
    return html;
  }

  // saves the initial reaction rates/rate constants
  $('.btn-save-initial-rates').click(function() {
    const csrftoken = $('[name=csrfmiddlewaretoken]').val();
    initial_rates = {};
    $('#initial-rates-container .row-data').each(function() {
      initial_rates[$(this).find('.reaction-dropdown').val()] =
        {
          'value': $(this).find('.initial-value').val(),
          'units': $(this).find('.units-dropdown').val()
        };
    });
    $.ajax({
      url: 'initial-reaction-rates-save',
      type: 'post',
      headers: {'X-CSRFToken': csrftoken},
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      data: JSON.stringify(initial_rates),
      success: function(response) {
        location.reload();
      },
      error: function(response) {
        alert(response['error']);
      }
    });
  });

  // cancels changes to the initial reaction rates/rate constants
  $('.btn-cancel-initial-rates').click(function() {
    load_initial_rates();
  });

  // matches units to selected reaction type
  $('#initial-rates-container').on('change', '.reaction-dropdown', function() {
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
    container.children().children('.units-dropdown').html(`
      <option value="`+units+`">`+units+`</option>`);
    container.children().children('.units-dropdown').val(units);
  }

});
