$(document).ready(function(){

  // remove a chemical species from the mechanism
  $(".species-remove").on('click', function(){
    $.ajax({
      url: 'species-remove',
      type: 'get',
      data: { 'name': $(this).attr('species') },
      success: function(response){
        location.reload();
      }
    });
  });

  // look for changes to species name
  $('.species-detail').on('change', '.species-name', function(){
    if( $('.species-list .species-detail-link[species="'+$(this).val()+'"]').length ) {
      $(this).addClass('is-invalid');
      $(this).parents('.species-card').attr('species', '');
      return
    }
    $(this).removeClass('is-invalid');
    $(this).parents('.species-card').attr('species', $(this).val());
  });

  // add a new species to the mechanism
  $(".species-new").on('click', function(){
    $('.species-detail').html(species_detail_html(""));
    $('.species-detail .card-header').html(`
      <div class="input-group">
        <input type="text" class="form-control species-name" placeholder="Species name">
      </div>`);
  });

  // return html for a property input box
  function property_input_html(property_name, data_type, property_value) {
    return `
      <div class="input-group mb-3" property="`+property_name+`" data-type="`+data_type+`">
        <div class="input-group-prepend">
          <span class="input-group-text">`+property_name+`</span>
        </div>
        <input type="text" class="form-control" placeholder="Property value" value="`+property_value+`">
        <div class="input-group-append">
          <button type="button" class="btn btn-primary remove-property" property="`+property_name+`">
            <span class="oi oi-x" toggle="tooltip" aria-hidden="true" title="remove '+property+_name+'"></span>
          </button>
        </div>
      </div>
    `
  }

  // remove a property from the species
  $('.species-detail').on('click', '.btn.remove-property', function(){
    var property_name = $(this).parents('.input-group').attr('property');
    $('.species-detail .properties .input-group[property="'+property_name+'"]').remove();
    $('.new-property .dropdown-item[property="'+property_name+'"]').show();
  });

  // add property to species
  $('.species-detail').on('click', '.new-property .dropdown-item', function(){
    var property_name = $(this).attr('property');
    var added = false;
    var default_value = $(this).attr('default-value');
    var data_type = $(this).attr('data-type');
    $('.species-detail .properties .input-group').each(function(){
      if ($(this).attr('property') > property_name) {
        $(this).before(property_input_html(property_name, data_type, default_value));
        added = true;
        return false;
      }
    });
    if (!added) $('.species-detail .properties').append(property_input_html(property_name, data_type, default_value));
    $('.new-property .dropdown-item[property="'+property_name+'"]').hide();
  });

  // cancel any changes and exit species detail
  $('.species-detail').on('click', '.btn-cancel', function() {
    $('.species-detail').empty();
  });

  // save changes and exit species detail
  $('.species-detail').on('click', '.btn-save', function() {
    if( $('.species-detail .species-card').attr('species') == '' ) return;
    const csrftoken = $('[name=csrfmiddlewaretoken]').val();
    var species_data = { 'type': "CHEM_SPEC" };
    species_data['name'] = $('.species-detail .species-card').attr('species');
    $('.species-detail .properties .input-group').each(function(index) {
      if ($(this).attr('data-type') == "string") {
        species_data[$(this).attr('property')] = $(this).children('input:first').val();
      } else {
        species_data[$(this).attr('property')] = +$(this).children('input:first').val();
      }
    });
    $.ajax({
      url: 'species-save',
      type: 'post',
      headers: {'X-CSRFToken': csrftoken},
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      data: JSON.stringify(species_data),
      success: function(response) {
        location.reload();
      },
      error: function(response) {
        alert(response['error']);
      }
    });
  });

  // returns html for species detail window
  function species_detail_html(species_name) {
    return `
          <div class="card mb-4 species-card shadow-sm" species="`+species_name+`">
            <div class="card-header">
              <h4 class="my-0 fw-normal">`+species_name+`</h4>
            </div>
            <form class="body card-body">
              <div class="form-group properties">
              </div>
              <div class="dropdown show">
                <a href="#" class="btn btn-primary dropdown-toggle" role="button" id="new-property-dropdown" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                  Add property
                </a>
                <div class="dropdown-menu new-property" aria-labelledby="new-property-dropdown">
                  <a class="dropdown-item" href="#" property="descrition" data-type="string" default-value="">description</a>
                  <a class="dropdown-item" href="#" property="absolute tolerance [mol mol-1]" data-type="number" default-value="1e-12">absolute tolerance</a>
                  <a class="dropdown-item" href="#" property="molecular weight [kg mol-1]" data-type="number" default-value="0">molecular weight</a>
                </div>
              </div>
              <div class="container text-center mt-3">
                <button type="button" class="btn btn-primary btn-save">Save</button>
                <button type="button" class="btn btn-secondary btn-cancel">Cancel</button>
              </div>
            </form>
          </div>`
  }

  // show editable chemical species detail
  $(".species-detail-link").on('click', function(){
    $.ajax({
      url: 'species-detail',
      type: 'get',
      dataType: 'json',
      data: { 'name': $(this).attr('species') },
      success: function(response){
        $('.species-detail').html(species_detail_html(response.name));
        for (var key of Object.keys(response).sort()) {
          if (key == "name" || key == "type") continue;
          $('.new-property .dropdown-item[property="'+key+'"]').hide();
          if (typeof response[key] == "string") {
            $('.species-detail .properties').append(property_input_html(key, "string", response[key]));
          } else {
            $('.species-detail .properties').append(property_input_html(key, "number", response[key]));
          }
        }
      }
    });
  });

});
