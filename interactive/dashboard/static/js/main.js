var currentlyLoadingGraph = false
var currentMinValOfGraph = 0
var currentMaxValOfGraph = 1
var shouldShowArrowWidth = true // if true, show arrow width slider (mostly used for debug)

function reloadSlider(firstVal, secondVal, minVal, maxVal) {
  var stepVal = (parseFloat(maxVal) - parseFloat(minVal)) / 60;
  console.log("step value: " + stepVal);
  console.log("received values: "+firstVal+" "+parseFloat(secondVal).toExponential(3));
  console.log("received min max (* 10^100): "+(parseFloat(minVal) * Math.pow(10,100))+" "+(parseFloat(maxVal) * Math.pow(10,100)));
  $( "#range-slider2", window.parent.document ).slider("destroy");
  currentMinValOfGraph = parseFloat(minVal);
  currentMaxValOfGraph = parseFloat(maxVal);
  $( function() {
    $( "#range-slider2",window.parent.document ).slider({
      range: true,
      min: parseFloat(minVal).toExponential(3) * Math.pow(10,100),
      max: parseFloat(maxVal).toExponential(3) * Math.pow(10,100),
      step: stepVal * Math.pow(10,100),
      values: [ parseFloat(firstVal).toExponential(3) *Math.pow(10,100), parseFloat(secondVal).toExponential(3) * Math.pow(10,100) ],
      // values: [ parseFloat(document.getElementById("flow-start-range2").value), parseFloat(document.getElementById("flow-end-range2").value) ],
      slide: function( event, ui ) {
          // update values when slider changed
        // $( "#filterRange" ).val( "" + parseFloat(ui.values[ 0 ]).toExponential(3) + " to " + parseFloat(ui.values[ 1 ]).toExponential(3) + "" );
        document.getElementById("flow-start-range2").value = (ui.values[ 0 ] / Math.pow(10,100)).toExponential(3);
        document.getElementById("flow-end-range2").value = (ui.values[ 1 ] / Math.pow(10,100)).toExponential(3);
      },
      stop: function(event, ui) {
          // reload graph when slider is released (a lot less stress on the server by waiting for the user to release the slider)
          reloadGraph();
          }
    });
  } );
}
// helper function to reload graph (called when something other than elements changed)
function reloadGraph() {
  currentlyLoadingGraph = true
  var includedSpecies = []
  var blockedSpecies = []
    $.each($("#flow-species-menu-list").children(), function(i, value){
      if ($(value).hasClass('active')) {
        includedSpecies.push($(value).html().replace("☐ ", "").replace("☑ ", ""))
      }
    });

    $.each($("#blocked-elements-list").children(), function(i, value){
      if ($(value).hasClass('active')) {
        blockedSpecies.push($(value).html().replace("☐ ", "").replace("☑ ", ""))
      }
    });


    let stringed = includedSpecies.toString();
    console.log("stringed: " + stringed);
    console.log("asking for new plot graph")
    $.ajax({
      url:'get_flow',
      type: 'get',
      data: {
        "includedSpecies": stringed,
        "blockedSpecies": blockedSpecies.toString(),
        "startStep": $("#flow-start-range").val(),
        "endStep": $("#flow-end-range").val(),
        "maxArrowWidth": $("#flow-arrow-width-range").val(),
        "arrowScalingType": $("#flow-scale-select").val(),
        "minMolval": parseFloat(parseFloat($("#flow-start-range2").val())).toExponential(3),
        "maxMolval": parseFloat(parseFloat($("#flow-end-range2").val())).toExponential(3),
        "currentMinValOfGraph": currentMinValOfGraph,
        "currentMaxValOfGraph": currentMaxValOfGraph,
        "isPhysicsEnabled": $("#physics").is(":checked"),
      },
      success: function(response){
        $("#flow-diagram-container").html('<img src="../static/img/plot_diagram_legend.png" style="margin-left:40px;margin-top:40px;width:200px; position: absolute;border: 2px solid rgb(189,189,189);"> <iframe style="width: 100%;height: 100%;" id="graph-frame" title="Network plot" src="show_flow"></iframe>');
        
      }
    });
}

$(document).ready(function(){

  // disables enter button, unless a button or link has focus
  $('body').on('keypress', ':not(button, a)', function(event) {
    if (event.keyCode == '13') {
      event.preventDefault();
    }
  });

  // sets enter key or space bar to trigger click when button or link has focus
  $('body').on('keypress', 'button, a', function(event) {
    if (event.keyCode == '13' || event.keyCode == '32') {
      event.preventDefault();
      $(this).click();
    }
  });

  // add links for plotting and downloading configuration/results
  function display_post_run_menu_options() {
    $('#post-run-links').html(`
      <small class='nav-section'>ANALYSIS</small>
      <a class='nav-link' id='plot-results-link' href='/visualize'><span class='oi oi-graph oi-prefix'></span>Plot Results</a>
      <a class='nav-link' id='flow-diagram-link' href='/flow'><span class='oi oi-fork oi-prefix'></span>Flow Diagram</a>
      <a class='nav-link' id='download-link' href='/download'><span class='oi oi-data-transfer-download oi-prefix'></span>Download</a>
      `);
  }

  // runs the model
  $("#run-model").on('click', function(){
    $("#post-run-links").html('<div class="mx-2"><div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div></div>')
    $.ajax({
      url: "/model/run",
      type: 'get',
      success: function(response){
        if (response["model_running"]){
          $.ajax({
            url: "/model/check",
            type: 'get',
            success: function(response){
              if (response["status"] == 'done') {
                $("#post-run-links").html('')
                display_post_run_menu_options();
              } else if (response["status"] == 'error'){
                  alert("ERROR " + response["e_code"] + "   " + response["e_message"]);
                  if (response["e_type"] == 'species'){
                    $("#" + response['spec_ID']).css("border", "3px solid red")
                    $("#" + response['spec_ID']).css("border-radius", "4px")
                  }
              } else {
                alert('unknown error')
              }
            }
          });
        } else {
          alert(response["error_message"])
        }
      }
    });
  });

  // checks if model has been run or if config changed
  $.ajax({
    url: "/model/check-load",
    type: 'get',
    success: function(response){
      if (response["status"] == 'done') {
          display_post_run_menu_options();
        if (window.location.href.indexOf("visualize") > -1) {
          $('#plot-results-link').addClass('active');
          $('#plot-results-link').attr('aria-current', 'page');
        }
        if (window.location.href.indexOf("download") > -1) {
          $('#download-link').addClass('active');
          $('#download-link').attr('aria-current', 'page');
        }
      }
    }
  });

  // changes run button after click
  $("#runMB").on('click', function(){
    $('#runMB').attr('emphasis', 'false')
  });
  var sheet = window.document.styleSheets[0];
  $(".flow-species-item").on('click', function(){
    
    var id = $(this).attr('id');
    if ($("#" + id).hasClass('active')) {
      $("#" + id).removeClass('active')
      document.getElementById(id).innerHTML = document.getElementById(id).innerHTML.replace("☑ ", "☐ ");
    } else {
      $("#" + id).addClass('active')
      document.getElementById(id).innerHTML = document.getElementById(id).innerHTML.replace("☐ ", "☑ ");
    }

    reloadGraph();

  });

  // sync range sliders and inputs
  $("#flow-start-range").on('change', function(){
    var newValue = $("#flow-start-range").val()
    $("#flow-start-input").val(newValue)
    $("#range-slider").slider('values',0,newValue);
    reloadGraph()
  });
  // $("#range-slider").on('change', function(){
  //   reloadGraph();
  // });
  $("#flow-end-range").on('change', function(){
    var newValue = $("#flow-end-range").val()
    $("#flow-end-input").val(newValue)
    $("#range-slider").slider('values',1,newValue);
    reloadGraph()
  });
  $("#flow-start-range2").on('change', function(){
    var newValue = $("#flow-start-range2").val()
    $("#flow-start-input2").val(newValue)
    reloadGraph()
  });
  // $("#range-slider").on('change', function(){
  //   reloadGraph();
  // });
  $("#flow-end-range2").on('change', function(){
    var newValue = $("#flow-end-range2").val()
    $("#flow-end-input2").val(newValue)
    reloadGraph()
  });
  // physics checkbox
  $("#physics").on('change', function(){
    reloadGraph();
  });
  $("#flow-start-input").on('change', function(){
    var newValue = $("#flow-start-input").val()
    $("#flow-start-range").val(newValue)

  });
  $("#flow-end-input").on('change', function(){
    var newValue = $("#flow-end-input").val()
    $("#flow-end-range").val(newValue)
// slider value display for arrow slider
  });
  if (shouldShowArrowWidth == false) {
    console.log("removing arrow elements")
    document.getElementById("arrow-width-group-item").style.display = "none";
  }
  $("#flow-arrow-width-range").on('change', function(){
    var newValue = $("#flow-arrow-width-range").val()
    $("#arrow-range-val-display").html(newValue)
    document.getElementById("max-arrow-label").innerHTML = "Max arrow width: "+newValue;
    reloadGraph();
  });
  $("#flow-scale-select").on('change', function(){
    reloadGraph();
  });
});
function handleShowBlockElementChange() {
  if(document.getElementById('show-elements').classList.contains("selected-menu-it")) {
    //show blocked elements
    document.getElementById('block-elements').classList.add("selected-menu-it");
    document.getElementById('show-elements').classList.remove("selected-menu-it");
    
    document.getElementById("flow-species-menu-list").style.display = "none";
    document.getElementById("blocked-elements-list").style.display = "flex";
    
  } else {
    // show "show elements"
    document.getElementById('show-elements').classList.add("selected-menu-it");
    document.getElementById('block-elements').classList.remove("selected-menu-it");

    document.getElementById("blocked-elements-list").style.display = "none";
    document.getElementById("flow-species-menu-list").style.display = "flex";
  }
}