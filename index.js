const $ = require('jquery');
const knn = require('leaflet-knn');
const nodes = require('./nodes');
const oldnodes = require('./oldnodes');
const datetime = require('eonasdan-bootstrap-datetimepicker');
let convoys = {};
let convoyID = 1;
const map = L.map('map', {
    minZoom: 8,
    maxZoom: 11,
    maxBounds: [[57.5155, 21.6918], [58.9975, 27.1535], [59.7975, 28.355]],
    maxBoundsViscosity: 1.0
    }).setView([58.7764, 25.1305], 8);


$(function () {
    L.tileLayer('tiles/{z}/{x}/{y}.png').addTo(map);

    var pathNodes1 = [489, 1231, 211, 568, 184, 2600, 3303, 786, 2274, 2935, 1960, 2576, 3763, 2925, 3644, 1972, 169, 3423, 3292, 374, 3266, 2662, 1535, 1756, 3332, 437, 3158, 3402, 2308, 254, 2659, 3378, 1848, 1775, 470, 274, 2961, 3375, 2594, 2967, 1059, 1031, 961, 2544, 2052, 736, 1289, 113, 875, 29, 2020, 2354, 510]
    var pathNodes2 =[3564, 1892, 2940, 366, 2721, 1510, 562, 2832, 1296, 685, 341, 2890, 3804, 968, 3691, 2755, 355, 1850, 3679, 2586, 730, 715, 1592, 2972, 1731, 2234, 1180, 3141, 1764, 710, 2831, 2700, 1471, 1798, 838, 3138, 720, 1841, 783, 533, 3839, 1639, 3180, 3169, 1391, 1970, 1257, 273, 2664, 1058, 1670, 677, 1387, 113, 1289, 761, 2763, 567, 1037, 23, 1484, 3225, 2541, 2026, 2294, 3042, 97, 448, 2634, 1905, 291, 514, 727, 829, 1543, 255, 1888, 2781, 1832, 1377, 2141, 1130, 2422, 3700, 2800, 3770, 327, 2580, 1256, 323, 1904];
    var pathNodes3 = [1, 690, 3610, 2243, 1207, 1194, 242, 3017, 2587, 3228, 2059, 1607, 3614, 2620, 248, 2629, 3391, 1947, 38, 3088, 1919, 1587, 3628, 2796, 1395, 2387, 1651, 2837, 876, 267, 476, 513, 2367, 706, 741, 335, 69, 3493, 830, 1920, 2443, 2778, 3860, 2497, 375, 82, 3048, 1329, 2874, 3229, 1067, 3021, 597, 997, 1691, 1098, 2105, 3561, 1459, 3087, 3719, 2981, 3854, 1793, 1421, 516, 2565, 1060, 2385, 1889, 1728, 339, 2228, 1989, 1349, 1531, 3531, 3524, 721, 1020, 1490, 3, 11];
    var pathNodes4 = [296, 2238, 1859, 1288, 329, 2452, 3280, 3122, 2521, 81, 1923, 986, 2548, 2971, 3070, 872, 3422, 2819, 3643, 2919, 2857, 2871, 2519, 571, 2158, 94, 1920, 2443, 316, 2754, 16, 2556, 1437, 3214, 3662, 3410, 1081, 1723, 903, 2550, 650, 3167, 1928, 2499, 2758, 1968, 947, 3652, 3318, 2343, 1756, 3332, 241, 1355, 1315, 2423, 426, 1973, 1436, 3263, 1616, 1829, 2106, 1640, 2814, 3835, 3773, 957, 3508, 1147, 2734, 3344, 347, 644, 2646, 1812, 1008, 2681, 3799, 364, 1072, 3064, 3700, 2422, 1130, 2057, 1509, 932];
    var pathNodes5 =[515, 3732, 3165, 922, 1936, 950, 3049, 3830, 2731, 3450, 3143, 2691, 2240, 1747, 2858, 2989, 3074, 2379, 1154, 606, 3398, 2756, 370, 1508, 2080, 978, 3169, 1391, 1970, 1257, 273, 2664, 1058, 1999, 2060, 2738, 3725, 2544, 2171, 1390, 844, 2229, 3656, 3254, 3163, 3550, 144, 118, 1150, 466, 966, 3598, 1111, 2974, 3186, 1160, 2938, 438, 1205, 203, 2401, 905, 1742, 2106, 1829, 1804, 3047, 1821, 141, 475, 697, 2077, 135, 859, 2523, 3091, 2330, 1065, 2728, 3059, 3601, 1601, 3113, 881, 407, 3231, 100];

    drawPath(L.polyline(getCoordinates(pathNodes1)), 'red', 8000, 2000);
    drawPath(L.polyline(getCoordinates(pathNodes2)), 'Navy ', 5000, 2300);
    drawPath(L.polyline(getCoordinates(pathNodes3)), 'lime', 6800, 2700);
    drawPath(L.polyline(getCoordinates(pathNodes4)), 'OrangeRed', 7000, 2500);
    drawPath(L.polyline(getCoordinates(pathNodes5)), 'purple', 8000, 2000);

    console.log($('#map').parent());


    $(function(){
        $('#datetimepicker').datetimepicker({
            locale: 'en',
            format: 'DD-MM-YYYY HH:mm',
            sideBySide: true,
            // todayHighlight: true,
            // dateFormat: 'yy-mm-dd',
            useCurrent:true
            // viewDate: '2015-01-01 23:59:59',
            // showTodayButton: true,
            // showClose:true
        }).show();
    });



    $('#add-btn').click(function () {
        let row = '<tr><td><button type="button" class="btn btn-lg btn-default id" id="ID_' + convoyID +'" title="Convoy ID"></td>' +
            '<td><button type="button" class="btn btn-lg btn-warning" id = "origin_' + convoyID+'" title="Add origin"><span class="glyphicon glyphicon-play"></span></button></td>' +
            '<td><button type="button" class="btn btn-lg btn-warning" id = "destination_' + convoyID+'" title="Add destination"><span class="glyphicon glyphicon-stop"></button></td>' +
            '<td><div class="input center merge-bottom-input pluss-minus" id = "length_' + convoyID+'">5000</div><div class="btn-group btn-block" role="group" aria-label="plus-minus">' +
            '<button type="button" class="btn btn-xs btn-default minus-button merge-top-left-button"><span class="glyphicon glyphicon-minus"></span></button>' +
            '<button type="button" class="btn btn-xs btn-basic plus-button merge-top-right-button"><span class="glyphicon glyphicon-plus"></span></button></div></td>' +
            '<td><div class="input center merge-bottom-input pluss-minus" id = "speed_' + convoyID+'">50</div><div class="btn-group btn-block" role="group" aria-label="plus-minus">' +
            '<button type="button" class="btn btn-xs btn-default minus-button merge-top-left-button"><span class="glyphicon glyphicon-minus"></span></button>' +
            '<button type="button" class="btn btn-xs btn-basic plus-button merge-top-right-button"><span class="glyphicon glyphicon-plus"></span></button></div></td>' +
            '<td><div class="input center merge-bottom-input pluss-minus" id = "ready_' + convoyID+'">0</div><div class="btn-group btn-block" role="group" aria-label="plus-minus">' +
            '<button type="button" class="btn btn-xs btn-default minus-button merge-top-left-button"><span class="glyphicon glyphicon-minus"></span></button>' +
            '<button type="button" class="btn btn-xs btn-basic plus-button merge-top-right-button"><span class="glyphicon glyphicon-plus"></span></button></div></td>' +
            '<td><div class="input center merge-bottom-input pluss-minus" id = "due_' + convoyID+'">24</div><div class="btn-group btn-block" role="group" aria-label="plus-minus">' +
            '<button type="button" class="btn btn-xs btn-default minus-button merge-top-left-button"><span class="glyphicon glyphicon-minus"></span></button>' +
            '<button type="button" class="btn btn-xs btn-basic plus-button merge-top-right-button"><span class="glyphicon glyphicon-plus"></span></button></div></td>' +
            '<td><button type="button" class="btn btn-lg btn-danger delete" title="Delete row"><span class="glyphicon glyphicon-minus"></span></td></tr>';
        $('#convoy-list').find('thead').removeClass("hidden");
        $('#convoy-list').append(row);
        $('#ID_' + convoyID).text(convoyID+'.');
        convoys[convoyID]= {};
        convoys[convoyID]['length']= $('#length_' + convoyID).text();
        convoys[convoyID]['speed']= $('#speed_' + convoyID).text();
        convoys[convoyID]['ready']= $('#ready_' + convoyID).text();
        convoys[convoyID]['due']= $('#due_' + convoyID).text();
        console.log(convoys);


        $("#origin_" + convoyID +",#destination_" + convoyID).each(function() {
            $(this).click(function () {
                let id = this.id;
                map.on('click', (function(e) {
                    addMarker(e, id);
                    map.off('click');
                }));
                $(this).off('click');
            });
        });
        convoyID++;
    });


    $('.addBtnRemove').click(function () {
        $('#convoy-list').closest('tr').remove();
    });
});



$(document).on("click", ".feature-row", function(e) {
    $(document).off("mouseout", ".feature-row", clearHighlight);
    sidebarClick(parseInt($(this).attr("id"), 10));
});

if ( !("ontouchstart" in window) ) {
    $(document).on("mouseover", ".feature-row", function(e) {
        highlight.clearLayers().addLayer(L.circleMarker([$(this).attr("lat"), $(this).attr("lng")], highlightStyle));
    });
}

$(document).on("mouseout", ".feature-row", clearHighlight);

$("#about-btn").click(function() {
    $("#aboutModal").modal("show");
    $(".navbar-collapse.in").collapse("hide");
    return false;
});

$("#full-extent-btn").click(function() {
    map.fitBounds(boroughs.getBounds());
    $(".navbar-collapse.in").collapse("hide");
    return false;
});

$("#legend-btn").click(function() {
    $("#legendModal").modal("show");
    $(".navbar-collapse.in").collapse("hide");
    return false;
});

$("#login-btn").click(function() {
    $("#loginModal").modal("show");
    $(".navbar-collapse.in").collapse("hide");
    return false;
});

$("#list-btn").click(function() {
    animateSidebar();
    return false;
});

$("#nav-btn").click(function() {
    $(".navbar-collapse").collapse("toggle");
    return false;
});

$("#sidebar-toggle-btn").click(function() {
    animateSidebar();
    return false;
});

$("#sidebar-hide-btn").click(function() {
    animateSidebar();
    return false;
});

function animateSidebar() {
    $("#sidebar").animate({
        width: "toggle"
    }, 350, function() {
        map.invalidateSize();
    });
}

function sizeLayerControl() {
    $(".leaflet-control-layers").css("max-height", $("#map").height() - 50);
}

function clearHighlight() {
    highlight.clearLayers();
}

function sidebarClick(id) {
    var layer = markerClusters.getLayer(id);
    map.setView([layer.getLatLng().lat, layer.getLatLng().lng], 17);
    layer.fire("click");
    /* Hide sidebar and go to the map on small screens */
    if (document.body.clientWidth <= 767) {
        $("#sidebar").hide();
        map.invalidateSize();
    }
}

function syncSidebar() {
    /* Empty sidebar features */
    $("#feature-list tbody").empty();
    /* Loop through theaters layer and add only features which are in the map bounds */
    theaters.eachLayer(function (layer) {
        if (map.hasLayer(theaterLayer)) {
            if (map.getBounds().contains(layer.getLatLng())) {
                $("#feature-list tbody").append('<tr class="feature-row" id="' + L.stamp(layer) + '" lat="' + layer.getLatLng().lat + '" lng="' + layer.getLatLng().lng + '"><td style="vertical-align: middle;"><img width="16" height="18" src="assets/img/theater.png"></td><td class="feature-name">' + layer.feature.properties.NAME + '</td><td style="vertical-align: middle;"><i class="fa fa-chevron-right pull-right"></i></td></tr>');
            }
        }
    });
    /* Loop through museums layer and add only features which are in the map bounds */
    museums.eachLayer(function (layer) {
        if (map.hasLayer(museumLayer)) {
            if (map.getBounds().contains(layer.getLatLng())) {
                $("#feature-list tbody").append('<tr class="feature-row" id="' + L.stamp(layer) + '" lat="' + layer.getLatLng().lat + '" lng="' + layer.getLatLng().lng + '"><td style="vertical-align: middle;"><img width="16" height="18" src="assets/img/museum.png"></td><td class="feature-name">' + layer.feature.properties.NAME + '</td><td style="vertical-align: middle;"><i class="fa fa-chevron-right pull-right"></i></td></tr>');
            }
        }
    });
    /* Update list.js featureList */
    featureList = new List("features", {
        valueNames: ["feature-name"]
    });
    featureList.sort("feature-name", {
        order: "asc"
    });
}












// var pathLine = L.polyline([[58.39421039618,25.346738536559], [58.373986404641,25.380837436299], [58.372354131915,25.379122779344], [58.35998756107,25.403713172457], [58.338684648151,25.477553567988], [58.347090846189,25.509503471336], [58.355605679082,25.558855407809], [58.362611936775,25.583471034501], [58.367128421424,25.597435491267], [58.364717930898,25.624140692221], [58.362631257256,25.634742580058], [58.363319631301,25.638885160058], [58.37472731811,25.65243206017], [58.383339306641,25.673042189307], [58.393969138899,25.703634101143], [58.391833734122,25.730873753242], [58.391969873555,25.759669786869], [58.391811823934,25.761683111419], [58.397021157548,25.866431277797], [58.396875927575,25.871576665584], [58.386629438162,25.937433902258], [58.403113945534,25.980453123026], [58.419524170393,26.034173816959], [58.409655902507,26.074864565103], [58.331462607013,26.187667838585], [58.331166156904,26.302684999366], [58.33838013312,26.312610457225], [58.338570712801,26.313176651448], [58.340357216591,26.316926963346], [58.340527121709,26.317796779669], [58.340835102125,26.320194685332], [58.343178047578,26.35127536408], [58.345196548425,26.393889507852], [58.34736529299,26.434117830853], [58.350184996364,26.522293284112], [58.350347113215,26.523475340718], [58.353915496853,26.551780988912], [58.355035343613,26.576129578416], [58.353800172292,26.599097365008], [58.354896905604,26.612467960536], [58.359112394292,26.641979976988], [58.365185996897,26.671641153982], [58.367148878561,26.678115394283], [58.357212310962,26.68226722705], [58.353697791566,26.687287278169], [58.344936182562,26.705454178229], [58.343568797666,26.710928772222], [58.343762666718,26.713962351359], [58.331742261077,26.718175821571], [58.325425842207,26.787668322775], [58.3229245862,26.815850573969], [58.311441821159,26.845845643975], [58.300025768218,26.866452480837]]);

function drawPath(path, color, speed, length){
  let pathLine = L.polyline([], {color: color}).addTo(map);
  let marker = L.Marker.movingMarker(path.getLatLngs(), speed, {opacity: 0}).addTo(map);
  marker.on('move', function() {
    pathLine.addLatLng(marker.getLatLng());
    pathLine.redraw();
  });
  marker.start();
  setTimeout(function(){
    let marker2 = L.Marker.movingMarker(path.getLatLngs(), speed, {opacity: 0}).addTo(map);
    marker2.on('move', function() {
      pathLine.getLatLngs().splice(0,1);
      pathLine.redraw();
    });
    marker2.start();
  }, length);
}

// function getNodeID(position){
//     let node =
// }

function getCoordinates(path){
  let coordinates = [];
  for (let i = 0; i < path.length; i++) {
      coordinates.push(oldnodes[path[i]])
  }
  return coordinates
}

// function enableAddMarker() {
//     map.on('click', addMarker)
// }
//
function addMarker(e, id) {
    console.log(id);
    let parts = id.split('_');
    let feature = parts[0];
    let conID = parts[1];
    console.log(parts);

    let marker = L.marker(e.latlng,{
        draggable: true
    });
    marker.addTo(map);

    let nearest = findNearestNode(marker);
    marker.setLatLng(nearest);
    $('#'+id).removeClass('btn-warning').addClass('btn-success');
    updateConvoys(conID, feature, nearest);

    marker.on('dragend', function(event) {
        let marker = event.target;
        nearest = findNearestNode(marker);
        marker.setLatLng(nearest, {draggable: 'true'}).bindPopup(nearest).update();
        updateConvoys(conID, feature, nearest);
    });
}

function findNearestNode(marker) {
    let position = marker.getLatLng();
    let geojson = L.geoJson(nodes);
    return knn(geojson).nearest(position, 1)[0];
}

function updateConvoys(ID, feature, nearest){
    convoys[ID][feature]= nearest['layer']['feature']['properties'];
    console.log(Object.keys(convoys[ID]).length);
    if(Object.keys(convoys[ID]).length == 6){
        $('#calc-btn').removeClass("hidden");
        $('.sidebar-table').css('top','130px');

    }
}


$('#calc-btn').click(function () {
    // let data = JSON.stringify(convoys);
    // let data = "ddd";
    getPaths(convoys);
});

//
// function addMarker(e){
// // Add marker to map at click location; add popup window
//     var newMarker = new L.marker(e.latlng).addTo(map);
// }

// var marker3 = new L.Marker(nodes[3816],{icon:  greenIcon }).addTo(map);
// var marker4 = new L.Marker([59.1015405890164,27.205910446717013]).addTo(map);
// var marker5 = new L.Marker([58.777626294311425,27.205910446717013]).addTo(map);

// var marker6 = new L.Marker([58.96035818220546,26.813663286303196]).addTo(map);
// var marker7 = new L.Marker([58.94983166771614,26.71734877335933]).addTo(map);

// var myMovingMarker = L.Marker.movingMarker([[58.7764,25.1305],[59.3975,27.355]],
// 						[20000]).addTo(map);
// //...
// myMovingMarker.start();

// L.rectangle(bounds, {color: "#ff7800", weight: 1}).addTo(map);
