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
            <div class="body card-body">
              <p>detail here</p>
            </div>
          </div>
        `);
      }
    });
  });

});
