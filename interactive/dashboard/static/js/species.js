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

  // return html for a property input box
  function property_input_html(property_name, property_value) {
    return `
      <div class="input-group mb-3" property="`+property_name+`">
        <div class="input-group-prepend">
          <span class="input-group-text">`+property_name+`</span>
        </div>
        <input type="text" class="form-control" placeholder="Property value" value="`+property_value+`">
        <div class="input-group-append">
          <button class="btn btn-primary remove-property" property="`+property_name+`">
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
    $('.species-detail .properties').append(property_input_html(property_name, $(this).attr('default-value')));
    $('.new-property .dropdown-item[property="'+property_name+'"]').hide();
  });

  // show editable chemical species detail
  $(".species-detail-link").on('click', function(){
    $.ajax({
      url: 'species-detail',
      type: 'get',
      dataType: 'json',
      data: { 'name': $(this).attr('species') },
      success: function(response){
        $('.species-detail').html(`
          <div class="card mb-4 shadow-sm">
            <div class="card-header">
              <h4 class="my-0 fw-normal">`+response.name+`</h4>
            </div>
            <form class="body card-body">
              <div class="form-group properties">
              </div>
              <div class="dropdown show">
                <a href="#" class="btn btn-primary dropdown-toggle" role="button" id="new-property-dropdown" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                  Add property
                </a>
                <div class="dropdown-menu new-property" aria-labelledby="new-property-dropdown">
                  <a class="dropdown-item" href="#" property="descrition" default-value="">description</a>
                  <a class="dropdown-item" href="#" property="absolute tolerance" default-value="1e-12">absolute tolerance</a>
                  <a class="dropdown-item" href="#" property="molecular weight [kg mol-1]" default-value="0">molecular weight</a>
                </div>
              </div>
              <div class="container text-center mt-3">
                <button class="btn btn-primary btn-save">Save</button>
                <button class="btn btn-secondary btn-cancel">Cancel</button>
              </div>
            </form>
          </div>
        `);
        for (var key of Object.keys(response)) {
          if (key == "name" || key == "type") continue;
          $('.new-property .dropdown-item[property="'+key+'"]').hide();
          $('.species-detail .properties').append(property_input_html(key, response[key]));
        }
      }
    });
  });

});
