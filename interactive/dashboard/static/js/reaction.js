$(document).ready(function(){

  /*********************
   * Utility functions *
   *********************/

  // replaces spaces with dashes in a json key
  function format_json_key(key) {
    return key.replace('-', '--').replace(' ', '-');
  }

  // sets a nested object property value
  function set_property_value(reaction, key, value) {
    key = key.split('.');
    var obj = reaction;
    while(key.length) {
      obj = reaction[key.shift()];
    }
    obj = value;
  }

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


  /**********************
   * Listener functions *
   **********************/

  // removes a reaction from the mechanism
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

  // adds a new reaction to the mechanism
  $(".reaction-new").on('click', function(){
    var reaction_data = { };
    $('.reaction-detail').html(reaction_detail_html(reaction_data));
  });

  // cancels any changes and exit reaction detail
  $('.reaction-detail').on('click', '.btn-cancel', function() {
    $('.reaction-detail').empty();
  });

  // saves changes and exit reaction detail
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

  // changes the reaction type
  $('.reaction-detail').on('click', '.reaction-type-selector .dropdown-item', function() {
    load_reaction_type( { 'type' : $(this).attr('element-key') } );
  });

  // shows an editable reaction detail window
  $(".reaction-detail-link").on('click', function() {
    $(".reaction-detail").empty();
    $.ajax({
      url: 'reaction-detail',
      type: 'get',
      dataType: 'json',
      data: { 'index': $(this).attr('reaction-id') },
      success: function(response) {
        load_reaction_type(response);
      }
    });
  });


  /*****************************
   * HTML generating functions *
   *****************************/

  // returns html for a property input box
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

  // returns html for a dropdown list
  function dropdown_html(label, list_elements) {
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

  // returns html for an input box with optional units
  function input_box_html(key, label, value, units, default_value, description) {
    var html = `
      <div class="input-group" property-key="` + key + `">
        <div class="input-group-prepend">
          <span class="input-group-text">` + label + `</span>
        </div>
        <input type="text" class="form-control" placeholder="` + default_value + `"`;
    if (value != null) html += ` value="`+value+`"`;
    html += `>`;
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
                dropdown_html(reaction_type_label(reaction_type), list_elements) + `
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


  /******************
   * Page modifiers *
   ******************/

  // adds a property or set of properties to a container
  function add_property_to_container(container, schema, property_data) {
    for (var key of Object.keys(schema)) {
      var html_key = format_json_key(key);
      var value = (property_data != null && key in property_data) ? property_data[key] : null;
      $(container).append(`<div class="container-fluid property-`+html_key+` mb-3"></div>`);
      var property_container = container + " .property-" + html_key;
      switch (schema[key]['type']) {
        case 'object':
          if ('children' in schema[key]) {
            add_property_to_container(property_container, schema[key]['children'], value);
          }
          break;
        case 'array':
          add_array_to_container(property_container, html_key, key, schema[key], value);
          break;
        case 'real':
          add_real_to_container(property_container, html_key, key, schema[key], value);
          break;
        case 'integer':
          add_integer_to_container(property_container, html_key, key, schema[key], value);
          break;
        case 'string':
          add_string_to_container(property_container, html_key, key, schema[key], value);
          break;
        case 'string-list':
          add_string_list_to_container(property_container, html_key, key, schema[key], value)
          break;
        case 'math':
          add_math_to_container(property_container, schema[key]);
          break;
      }
    }
  }

  // adds an array of properties to a container
  function add_array_to_container(container, html_key, key, schema, value) {
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
          </div>
        </div>
      </div>`);
    if ('description' in schema) {
      $(container).append(`<p><small>` + schema['description'] + `</small><p>`);
    }
    if (value != null) {
      if ("as-object" in schema && schema['as-object'] == true) {
        var index = 0;
        for (const [element_key, element] of Object.entries(value)) {
          add_array_element(container + " .array-elements", index, schema, { 'key' : element_key, 'value' : element });
          index += 1;
        }
      } else {
        for (const [index, element] of value.entries()) {
          add_array_element(container + " .array-elements", index, schema, element);
        }
      }
    }
  }

  // adds an array element to an array container
  function add_array_element(container, index, schema, value) {
    $(container).append(`
            <div class="row array-element-`+index+`">
            </div>
    `);
    var element_container = container + " .array-element-" + index;
    switch (schema['children']['type']) {
      case 'object':
        var list_elements = [];
        for (val of schema['children']['key'].split(';')) {
          list_elements.push( { key: format_json_key(val), label: val } );
        }
        $(element_container).html(dropdown_html((value != null && 'key' in value) ? value['key'] : '', list_elements));
        $(element_container).append(`<div class="col-7 element-properties"></div>`);
        add_property_to_container(element_container + ' .element-properties', schema['children']['children'], (value != null && 'value' in value) ? value['value'] : null);
        $(element_container).append(`
              <div class="col-2 d-flex justify-content-between">
                <div></div>
                <div>
                  <button class="btn btn-primary remove-element">
                    <span class="oi oi-x" toggle="tooltip" aria-hidden="true" title="Remove element"></span>
                  </button>
                </div>
              </div>`);
        break;
      case 'array':
        add_array_to_container(element_container, format_json_key(schema['key']), schema['key'], schema['children'], value);
        break;
      case 'real':
        add_real_to_container(element_container, format_json_key(schema['key']), schema['key'], schema['children'], value);
        break;
      case 'integer':
        add_integer_to_container(element_container, format_json_key(schema['key']), schema['key'], schema['children'], value);
        break;
      case 'string':
        add_string_to_container(element_container, format_json_key(schema['key']), schema['key'], schema['children'], value);
        break;
    }
  }

  // adds a real number property to a container
  function add_real_to_container(container, key, label, schema, value) {
    var units = "";
    var default_value = "";
    var description = "";
    if ('units' in schema) units = schema['units'];
    if ('default' in schema) default_value = schema['default'].toString();
    if ('description' in schema) description = schema['description'].toString();
    $(container).append(input_box_html(key, label, value, units, default_value, description));
  }

  // adds an integer property to a container
  function add_integer_to_container(container, key, label, schema, value) {
    var units = "";
    var default_value = "";
    var description = "";
    if ('units' in schema) units = schema['units'];
    if ('default' in schema) default_value = schema['default'].toString();
    if ('description' in schema) description = schema['description'].toString();
    $(container).append(input_box_html(key, label, value, units, default_value, description));
  }

  // adds a string property to a container
  function add_string_to_container(container, key, label, schema, value) {
    var default_value = "";
    var description = "";
    if ('default' in schema) default_value = schema['default'];
    if ('description' in schema) description = schema['description'].toString();
    $(container).append(input_box_html(key, label, value, "", default_value, description));
  }

  // adds a drop-down string list to a container
  function add_string_list_to_container(container, key, label, schema, value) {
    var default_value = "";
    var description = "";
    if ('default' in schema) default_value = schema['default'];
    if ('description' in schema) description = schema['description'].toString();
    var list_elements = [];
    for (val of schema['values'].split(';')) {
      list_elements.push( { key: format_json_key(val), label: val } );
    }
    var html = `
      <div class="input-group" property-key="` + key + `">
        <div class="input-group-prepend">
          <span class="input-group-text">` + label + `</span>
        </div>
        ` + dropdown_html((value === null) ? default_value : value, list_elements) + `
      </div>`;
    if (description != '') {
      html += `<p><small>`+description+`</small></p>`;
    }
    $(container).append(html);
  }

  // adds a math equation to a container
  function add_math_to_container(container, math) {
    $(container).append(`<div>$$` + math.value + `$$</div>`);
    MathJax.typeset();
  }

  // loads the reaction detail window with properties for a specific reaction type
  function load_reaction_type(reaction_data) {
    var reaction_type = reaction_data['type'];
    $('.reaction-detail').html(get_reaction_detail_html(reaction_type));
    delete reaction_data['type'];
    if ('index' in reaction_data) {
      $('.reaction-detail .reaction-card').attr('reaction-index', reaction_data['index']);
      delete reaction_data['index'];
    }
    $.ajax({
      url: 'reaction-type-schema',
      type: 'get',
      dataType: 'json',
      data: { 'type': reaction_type },
      success: function(response) {
        add_property_to_container('.reaction-detail .properties', response, reaction_data);
      }
    });
  }

});
