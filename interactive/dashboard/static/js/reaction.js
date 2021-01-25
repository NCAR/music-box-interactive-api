$(document).ready(function(){

  // replace spaces with dashes in a json key
  function format_json_key(key) {
    return key.replace('-', '--').replace(' ', '-');
  }

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
    `;
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

  // gets the html for a dropdown list
  function get_dropdown_html(label, list_elements) {
    var html = `
      <div class="col-3 dropdown show">
        <a href="#" class="btn btn-light dropdown-toggle" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
          `+((label=='') ? '&lt;select&gt;': label)+`
        </a>
        <div class="dropdown-menu" aria-labelledby="reaction-type-dropdown">
        <a class="dropdown-item" href="#" element-key="">&lt;select&gt;</a>`;
    for (element of list_elements) {
      html += `
        <a class="dropdown-item" href="#" element-key="`+element.key+`">`+element.label+`</a>`
    }
    html += `
        </div>
      </div>`;
    return html;
  }

  // gets the html for an input box with optional units
  function get_input_html(key, label, units, default_value, description) {
    var html = `
      <div class="input-group" property-key="` + key + `">
        <div class="input-group-prepend">
          <span class="input-group-text">` + label + `</span>
        </div>
        <input type="text" class="form-control" placeholder="` + default_value + `">`;
    if (units.length) {
      html += `
        <div class="input-group-append">
          <span class="input-group-text">` + units + `</span>
        </div>`;
    }
    html += `
      </div>`;
    if (description != '') {
      html += `<p><small>`+description+`</small></p>`;
    }
    return html;
  }

  // listener for change of reaction type
  $('.reaction-detail').on('click', '.reaction-type-selector .dropdown-item', function() {
    load_reaction_type_schema($(this).attr('element-key'));
  });

  // returns html for reaction detail window
  function get_reaction_detail_html(reaction_type) {
    var list_elements = [
      { key: "ARRHENIUS", label: reaction_type_label("ARRHENIUS") },
      { key: "EMISSION", label: reaction_type_label("EMISSION") },
      { key: "FIRST_ORDER_LOSS", label: reaction_type_label("FIRST_ORDER_LOSS") },
      { key: "PHOTOLYSIS", label: reaction_type_label("PHOTOLYSIS") },
      { key: "TROE", label: reaction_type_label("TROE") }
    ];
    return `
          <div class="card mb-4 reaction-card shadow-sm">
            <div class="card-header">
              <div class="reaction-type-selector">` +
                get_dropdown_html(reaction_type_label(reaction_type), list_elements) + `
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
          </div>`;
  }

  // add a property or set of properties to a container
  function add_property_to_container(container, property) {
    for (var key of Object.keys(property)) {
      var html_key = format_json_key(key);
      $(container).append(`<div class="container-fluid property-`+html_key+` mb-3"></div>`);
      var property_container = container + " .property-" + html_key;
      switch (property[key]['type']) {
        case 'object':
          if ('children' in property[key]) {
            add_property_to_container(property_container, property[key]['children']);
          }
          break;
        case 'array':
          add_array_to_container(property_container, html_key, key, property[key]);
          break;
        case 'real':
          add_real_to_container(property_container, html_key, key, property[key]);
          break;
        case 'integer':
          add_integer_to_container(property_container, html_key, key, property[key]);
          break;
        case 'string':
          add_string_to_container(property_container, html_key, key, property[key]);
          break;
        case 'string-list':
          add_string_list_to_container(property_container, html_key, key, property[key])
          break;
        case 'math':
          add_math_to_container(property_container, property[key]);
          break;
      }
    }
  }

  // add an array of properties to a container
  function add_array_to_container(container, html_key, key, array) {
    $(container).append(`
      <div class="card shadow-sm">
        <div class="card-header d-flex justify-content-between">
          <h3 class="my-0 fw-normal">`+key+`</h3>
          <button class="btn btn-primary `+html_key+`-add-element">
            <span class="oi oi-plus" toggle="tooltop" aria-hidden="true" title="Add element"></span>
          </button>
        </div>
        <div class="body card-body">
          <div class="form-group array-elements container-fluid">
            <div class="row array-element">
            </div>
          </div>
        </div>
      </div>`);
    var element_container = container + " .array-element";
    switch (array['children']['type']) {
      case 'object':
        var list_elements = [];
        for (val of array['children']['key'].split(';')) {
          list_elements.push( { key: format_json_key(val), label: val } );
        }
        $(element_container).html(get_dropdown_html('', list_elements));
        $(element_container).append(`<div class="col-7 element-properties"></div>`);
        add_property_to_container(element_container + ' .element-properties', array['children']['children']);
        $(element_container).append(`
              <div class="col-2 d-flex justify-content-between">
                <div></div>
                <div>
                  <button class="btn btn-primary `+html_key+`-remove-element">
                    <span class="oi oi-x" toggle="tooltip" aria-hidden="true" title="Remove element"></span>
                  </button>
                </div>
              </div>`);
        break;
      case 'array':
        add_array_to_container(element_container, format_json_key(array['key']), array['key'], array['children']);
        break;
      case 'real':
        add_real_to_container(element_container, format_json_key(array['key']), array['key'], array['children']);
        break;
      case 'integer':
        add_integer_to_container(element_container, format_json_key(array['key']), array['key'], array['children']);
        break;
      case 'string':
        add_string_to_container(element_container, format_json_key(array['key']), array['key'], array['children']);
        break;
    }
  }

  // add a real number property to a container
  function add_real_to_container(container, key, label, real_schema) {
    var units = "";
    var default_value = "";
    var description = "";
    if ('units' in real_schema) units = real_schema['units'];
    if ('default' in real_schema) default_value = real_schema['default'].toString();
    if ('description' in real_schema) description = real_schema['description'].toString();
    $(container).append(get_input_html(key, label, units, default_value, description));
  }

  // add an integer property to a container
  function add_integer_to_container(container, key, label, integer_schema) {
    var units = "";
    var default_value = "";
    var description = "";
    if ('units' in integer_schema) units = integer_schema['units'];
    if ('default' in integer_schema) default_value = integer_schema['default'].toString();
    if ('description' in integer_schema) description = integer_schema['description'].toString();
    $(container).append(get_input_html(key, label, units, default_value, description));
  }

  // add a string property to a container
  function add_string_to_container(container, key, label, string_schema) {
    var default_value = "";
    var description = "";
    if ('default' in string_schema) default_value = string_schema['default'];
    if ('description' in string_schema) description = string_schema['description'].toString();
    $(container).append(get_input_html(key, label, "", default_value, description));
  }

  // add a drop-down string list to a container
  function add_string_list_to_container(container, key, label, string_list_schema) {
    var default_value = "";
    var description = "";
    if ('default' in string_list_schema) default_value = string_list_schema['default'];
    if ('description' in string_list_schema) description = string_list_schema['description'].toString();
    var list_elements = [];
    for (val of string_list_schema['values'].split(';')) {
      list_elements.push( { key: format_json_key(val), label: val } );
    }
    var html = `
      <div class="input-group" property-key="` + key + `">
        <div class="input-group-prepend">
          <span class="input-group-text">` + label + `</span>
        </div>
        ` + get_dropdown_html(default_value, list_elements) + `
      </div>`;
    if (description != '') {
      html += `<p><small>`+description+`</small></p>`;
    }
    $(container).append(html);
  }

  // add a math equation to a container
  function add_math_to_container(container, math) {
    $(container).append(`<div>$$` + math.value + `$$</div>`);
    MathJax.typeset();
  }

  // load the reaction detail window with properties for a specific reaction type
  function load_reaction_type_schema(reaction_type) {
    $('.reaction-detail').html(get_reaction_detail_html(reaction_type));
    $.ajax({
      url: 'reaction-type-schema',
      type: 'get',
      dataType: 'json',
      data: { 'type': reaction_type },
      success: function(response) {
        add_property_to_container('.reaction-detail .properties', response);
      }
    });
  }

  // show editable reaction detail
  $(".reaction-detail-link").on('click', function() {
    $(".reaction-detail").empty();
    $.ajax({
      url: 'reaction-detail',
      type: 'get',
      dataType: 'json',
      data: { 'index': $(this).attr('reaction-id') },
      success: function(response) {
        load_reaction_type_schema(response['type']);
      }
    });
  });

});
