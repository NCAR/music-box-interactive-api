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

  // loads the list of initial conditions files
  load_initial_conditions_files();
  function load_initial_conditions_files() {
    $.ajax({
      url: 'initial-conditions-files',
      type: 'get',
      dataType: 'json',
      data: {},
      success: function(files) {
        $("#initial-conditions-files-container").empty();
        if (Object.keys(files).length < 1) return;
        $("#initial-conditions-files-container").append(`
          <div class="row">
            <div class="col-8">File name</div>
          </div>`);
        for (key in files) {
          $("#initial-conditions-files-container").append(initial_conditions_file_row_html());
          $("#initial-conditions-files-container div:last-child .file-name").val(key);
        }
        $("#initial-conditions-files-container").append(`
          <div class="row">
            <div class="col-12">NOTE: Initial conditions set on this page will override those specified in input files</div>
          </div>`);
      }
    });
  }

  // returns html for a row in the initial conditions files list
  function initial_conditions_file_row_html() {
    html = `
      <div class="row my-1 row-data">
        <div class="col-8">
          <input type="text" class="form-control file-name" disabled>
        </div>
        <div class="col-2">
          <button class="btn btn-secondary btn-remove-row">
            Remove
          </button>
        </div>`;
    return html;
  }

  // removes an input file
  $('#initial-conditions-files-container').on('click', '.btn-remove-row', function() {
    const csrftoken = $('[name=csrfmiddlewaretoken]').val();
    request = { "file name" : $(this).parent().parent().find(".file-name").val() };
    $.ajax({
      url:'initial-conditions-file-remove',
      type: 'post',
      headers: {'X-CSRFToken': csrftoken},
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      data: JSON.stringify(request),
      success: function(response) {
        location.reload();
      },
      error: function(response) {
        alert(response['error']);
      }
    });

  });

  // returns the html for a initial concentration row
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

  // auto converts value after unit change
  $(document).on('change', ".condition-select-convert", function() {
    var selectId = this.id
    var newUnit = $(this).val();
    var initId = selectId.replace(".units", "\\.init");
    var initId = initId.replace('id_', '')
    var initValue = $("#" + initId).val();

    $.ajax({
      url: "/conditions/convert",
      type: 'get',
      data: {
        "value": initValue,
        "new unit": newUnit,
        "type": selectId
      },
      success: function(response){
        var newValue = response['new value'];
        $("#" + initId).val(newValue)
      }
    });
  });

  // collapsable unit conversion tool
  $('.view-calculator').click(function() {
    if ($('#unit-conversion-calculator').attr('isHidden') == 'true') {
    $('#unit-conversion-calculator').removeClass('col-hidden');
    $('#unit-conversion-calculator').addClass('col-5');
    $('.view-calculator').html('Hide calculator')
    $('#unit-conversion-calculator').attr('isHidden', 'false')
    } else {
    $('#unit-conversion-calculator').addClass('col-hidden');
    $('#unit-conversion-calculator').removeClass('col-5');
    $('.view-calculator').html('Unit conversion calculator')
    $('#unit-conversion-calculator').attr('isHidden', 'true')
    }
    
  });

  $("#hideConversionCalculator").click(function(){
    $('#unit-conversion-calculator').addClass('col-hidden');
    $('#unit-conversion-calculator').removeClass('col-5');
    $('.view-calculator').html('Unit conversion calculator')
    $('#unit-conversion-calculator').attr('isHidden', 'true')
  });
  

  //add additional argument if needed
  $(document).on('change', ".unit-select", function() {
    var initialUnit = $("#initialValueUnit").val();
    var finalUnit = $("#finalValueUnit").val();
    $.ajax({
      url: "/conditions/unit-conversion-arguments",
      type: 'get',
      data: {
        "initialUnit": initialUnit,
        'finalUnit': finalUnit
      },
      success: function(response){
        $("#additionalArgumentsHolder").html(response);
      }
    });
  });

  //get unit options
  $(document).on('change', "#selectUnitType", function() {
    var unitType = $(this).val();
    $.ajax({
      url: "/conditions/unit-options",
      type: 'get',
      data: {
        "unitType": unitType
      },
      success: function(response){
        $("#conversionForm").html(response)
      }
    });
  });

  //submit calculator
  $(document).on('click', "#convertSubmit", function() {
    initialValue = $("#initialValue").val();
    initialUnit = $("#initialValueUnit").val();
    finalUnit = $("#finalValueUnit").val();
    additionalInputs = $("#additionalArgumentsHolder").children();
    var argData = []
    $.each(additionalInputs, function(i, inputGroup){
      var title = $(inputGroup).find('span').html();
      var unit = $(inputGroup).find('select').val();
      var value = $(inputGroup).find('input').val();
      var argDict = {"title": title, "unit": unit, "value": value}
      argData.push(argDict);
    });


    $.ajax({
      url: "/conditions/conversion-calculator",
      type: 'get',
      data: {
        "initialUnit": initialUnit,
        "initialValue": initialValue,
        'finalUnit': finalUnit,
        'args': argData
      },
      success: function(response){
        $("#convertedValue").html(response)
      }
    });
  });
  

});
