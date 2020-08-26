$(document).ready(function(){
  
  $('.r_button').on('click', function(){
    var buttonId = $(this).attr('id');

    $.ajax({
    url: 'species/remove',
    type: 'get',
    data: {"species": buttonId},
    success: function(response){

    }
   }); 
  });


  $("#plotnav").children().on('click', function(){
    var linkId = $(this).attr('id');

    $("#plotnav").children().attr('class', 'none');
    $('#'+linkId).attr('class','selection');
    $('#plotbar').empty();

    if (linkId == "species") {
      var model_data = JSON.parse(localStorage.getItem("model_data"));
      var species = model_data.mechanism.molecules;
      for (key in species) {
        $('#plotbar').append(`
          <a id="` + species[key].moleculename +
            `">` + species[key].moleculename + `</a>`);
      }

    } else if (linkId == "rates") {
      var model_data = JSON.parse(localStorage.getItem("model_data"));
      var photolysis = model_data.mechanism.photolysis;
      for (key in photolysis) {
        var rxn_id   = reactionId(photolysis[key], photolysis);
        var rxn_name = reactionName('photolysis', photolysis[key], photolysis);
        $('#plotbar').append(`
          <a id="rate_` + rxn_id +
            `">` + rxn_name + `</a>`);
      }
      var molecular_rxns= model_data.mechanism.reactions;
      for (key in molecular_rxns) {
        var rxn_id   = reactionId(molecular_rxns[key], molecular_rxns);
        var rxn_name = reactionName('molecular', molecular_rxns[key], molecular_rxns);
        $('#plotbar').append(`
          <a id="rate_` + rxn_id +
            `">` + rxn_name + `</a>`);
      }
    } 
     


  });
});

