$(document).ready(function(){

  // remove a reaction from the mechanism
  $(".reaction-remove").on('click', function(){
    $.ajax({
      url: 'reaction-remove',
      type: 'get',
      data: { 'index': $(this).attr('reaction-id') },
      success: function(response){
        location.reload();
      }
    });
  });

  // add a new reaction to the mechanism
  $(".reaction-new").on('click', function(){
    var reaction_data = { };
    $('.reaction-detail').html(reaction_detail_html(reaction_data));
  });

  // return html for a property input box
  function property_input_html(property_name, data_type, property_value) {
    return `
      <div class="input-group mb-3" property="`+property_name+`" data-type="`+data_type+`">
        <div class="input-group-prepend">
          <span class="input-group-text">`+property_name+`</span>
        </div>
        <input type="text" class="form-control" placeholder="Property value" value="`+property_value+`">
      </div>
    `
  }

  // cancel any changes and exit reaction detail
  $('.reaction-detail').on('click', '.btn-cancel', function() {
    $('.reaction-detail').empty();
  });

  // set a property value
  function set_property_value(reaction, key, value) {
    key = key.split('.');
    var obj = reaction;
    while(key.length) {
      obj = reaction[key.shift()];
    }
    obj = value;
  }

  // save changes and exit reaction detail
  $('.reaction-detail').on('click', '.btn-save', function() {
    const csrftoken = $('[name=csrfmiddlewaretoken]').val();
    var reaction_data = { };
    reaction_data['type'] = $('.reaction-detail .reaction-card').attr('reaction-type');
    $('.reaction-detail .properties .input-group').each(function(index) {
      if ($(this).attr('data-type') == "object") {
        set_property_value(reaction_data, $(this).attr('property'), { });
      } else if ($(this).attr('data-type') == "string") {
        set_property_value(reaction_data, $(this).attr('property'), $(this).children('input:first').val());
      } else {
        set_property_value(reaction_data, $(this).attr('property'), +$(this).children('input:first').val());
      }
    });
    $.ajax({
      url: 'reaction-save',
      type: 'post',
      headers: {'X-CSRFToken': csrftoken},
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      data: JSON.stringify(reaction_data),
      success: function(response) {
        location.reload();
      },
      error: function(response) {
        alert(response['error']);
      }
    });
  });

  // returns a label for a reaction type
  function reaction_type_label(reaction_type) {
    if (reaction_type == "ARRHENIUS") {
      return "Arrhenius";
    } else if (reaction_type == "EMISSION") {
      return "Emission";
    } else if (reaction_type == "FIRST_ORDER_LOSS") {
      return "First-order loss";
    } else if (reaction_type == "PHOTOLYSIS") {
      return "Photolysis";
    } else if (reaction_type == "TROE") {
      return "Troe";
    } else {
      return "Unknown reaction type";
    }
  }

  // returns html for reaction detail window
  function reaction_detail_html(reaction_data) {
    return `
          <div class="card mb-4 reaction-card shadow-sm" reaction-id="`+reaction_data['index']+`">
            <div class="card-header">
              <div class="dropdown show">
                <a href="#" class="btn btn-primary dropdown-toggle" id="reaction-type-dropdown" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                  `+reaction_type_label(reaction_data['type'])+`
                </a>
                <div class="dropdown-menu reaction-type" aria-labelledby="reaction-type-dropdown">
                  <a class="dropdown-item" href="#" reaction_type="ARRHENIUS">`+reaction_type_label("ARRHENIUS")+`</a>
                  <a class="dropdown-item" href="#" reaction_type="EMISSION">`+reaction_type_label("EMISSION")+`</a>
                  <a class="dropdown-item" href="#" reaction_type="FIRST_ORDER_LOSS">`+reaction_type_label("FIRST_ORDER_LOSS")+`</a>
                  <a class="dropdown-item" href="#" reaction_type="PHOTOLYSIS">`+reaction_type_label("PHOTOLYSIS")+`</a>
                  <a class="dropdown-item" href="#" reaction_type="TROE">`+reaction_type_label("TROE")+`</a>
                </div>
              </div>
            </div>
            <form class="body card-body">
              <div class="form-group properties">
              </div>
              <div class="container text-center mt-3">
                <button class="btn btn-primary btn-save">Save</button>
                <button class="btn btn-secondary btn-cancel">Cancel</button>
              </div>
            </form>
          </div>`
  }

  // show editable reaction detail
  $(".reaction-detail-link").on('click', function(){
    $.ajax({
      url: 'reaction-detail',
      type: 'get',
      dataType: 'json',
      data: { 'index': $(this).attr('reaction-id') },
      success: function(response){
        $('.reaction-detail').html(reaction_detail_html(response));
        for (var key of Object.keys(response).sort()) {
          if (key == "type") continue;
          if (response[key] instanceof String) {
            $('.reaction-detail .properties').append(property_input_html(key, "string", response[key]));
          } else {
            $('.reaction-detail .properties').append(property_input_html(key, "number", response[key]));
          }
        }
      }
    });
  });

});
