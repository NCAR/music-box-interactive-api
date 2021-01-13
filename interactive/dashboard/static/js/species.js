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
              <hl>
              <label for="new-property-key" class="font-weight-bold">New property</label>
              <div class="input-group">
                <input class="form-control" placeholder="Property name">
                <div class="input-group-append">
                  <button class="btn btn-primary btn-ncar-active btn-add">Add</button>
                </div>
              </span>
              <div class="container text-center mt-3">
                <button class="btn btn-primary btn-ncar-active btn-save">Save</button>
                <button class="btn btn-secondary btn-cancel">Cancel</button>
              </div>
            </form>
          </div>
        `);
        for (var key of Object.keys(response)) {
          if (key == "name" || key == "type") continue;
          $('.species-detail .properties').append(`
            <div class="input-group mb-3">
              <div class="input-group-prepend">
                <span class="input-group-text">`+key+`</span>
              </div>
              <input type="text" class="form-control" property="`+key+`" placeholder="Property value" value="`+response[key]+`">
              <div class="input-group-append">
                <button class="btn btn-primary btn-ncar-active" property="`+key+`">
                  <span class="oi oi-x" toggle="tooltip" aria-hidden="true" title="remove `+key+`"></span>
                </button>
              </div>
            </div>
          `);
        }
      }
    });
  });

});
