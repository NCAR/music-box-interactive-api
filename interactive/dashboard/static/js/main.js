$(document).ready(function(){

  $('#rates').on('click', function(){

    $.ajax({
    url: 'plots/get_contents',
    type: 'get',
    data: {"type": "rates"},
    success: function(response){
      $("#plotbar").html(response);
    }
   }); 
    

  });


});
