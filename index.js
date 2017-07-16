// const $ = require('jquery');
require('drmonty-leaflet-awesome-markers');
// const boot = require('bootstrap');
require('bootstrap-timepicker');
require('./src/Clock');
require('./src/MoveableMarker');
require('./src/Playback');
require('./src/Tick');
require('./src/TickPoint');
require('./src/Util');
const fs = require('fs');
const knn = require('leaflet-knn');
const nodes = require('./nodes');
const endpoints = require('./endpoints');
const roads = require('./roads');
const tracks = require('./tracks');
require('eonasdan-bootstrap-datetimepicker');
let defaultValues = {'length':5000,'speed':50, 'ready': 0, 'due':24, 'headway':5, 'time': 'current','algorithm':'naive', 'playback':1000};
let convoys = {};
let mapObjects = {};
let paths = {};
let times = {};
let startOrder = [];
let convoyID = 0;
let colorIdx = 0;
let colors = ['darkpurple', 'orange', 'darkblue', 'green', 'red',  'black',  'purple',  'blue',  'darkred', 'lightgreen', 'cadetblue',  'pink', 'darkgreen', 'lightred', 'gray', 'beige',  'lightblue', 'lightgray'];
let hex = {'red': '#D33D2A','darkred':'#A03336', 'lightred':'#FF8D7E', 'orange':'#F49630', 'beige':'#FFCA91', 'green':'#71AF26', 'darkgreen':'#718224', 'lightgreen':'#BBF770', 'blue':'#38A9DB', 'darkblue':'#0065A0', 'lightblue':'#89DBFF', 'purple':'#D051B8', 'darkpurple':'#593869', 'pink':'#FF90E9', 'cadetblue':'#426877', 'gray':'#575757', 'lightgray':'#A3A3A3', 'black':'#303030'};
let algorithms = ['naive', "k-shortest"];
let playbackValues = [1, 100, 500, 1000, 2000];
let dateTimeCounter;
let dateTime;
let result;

const map = L.map('map', {
    minZoom: 8,
    maxZoom: 11,
    maxBounds: [[57.5155, 21.6918], [58.9975, 27.1535], [59.7975, 28.355]],
    maxBoundsViscosity: 1.0,
    zoomControl: false
    }).setView([58.7764, 25.1305], 8);

function writePaths(data){
    fs.writeFile('tracks.js', data, function(err){
        if(err){
            console.log(err);
        }
    });
}



function assignColor(convoyID) {
    let color = colors[colorIdx++%18];
    mapObjects[convoyID]['color'] = color;
    return color;
}


function updateClock(dateTime = (new Date()).getTime()) {
    // Update the time display
    $('#cursor-date').html("&nbsp;&nbsp;"+L.Playback.Util.DateStr(dateTime));
    $('#cursor-time').html("&nbsp;"+L.Playback.Util.TimeStr(dateTime));
}



function init_video(tracks) {
    // Colors for AwesomeMarkers




    // =====================================================
    // =============== Playback ============================
    // =====================================================

    // Playback options
    var playbackOptions = {
        playControl: true,
        dateControl: true,
        sliderControl: true
    };


    // Initialize playback
    var playback = new L.Playback(map, null, null, playbackOptions);

    // Initialize custom control
    var control = new L.Playback.Control(playback);
    control.addTo(map);

    // Add data
    console.log(tracks);
    playback.addData(tracks);

}

function start(startTime, path, color, duration, passingTime){
    console.log(startTime, duration, passingTime);
    console.log(path, color);
    if (startTime == 0) {
        drawPath(L.polyline(path), color, duration, passingTime);
        return false
    }
    let start = +new Date;
    let interval = setInterval(function () {
        let time = (new Date - start);
        if (time >= startTime) {
            drawPath(L.polyline(path), color, duration, passingTime);
            clearInterval(interval);
        }
    }, 0);
    return false
}

function msToTime(duration) {
    let milliseconds = parseInt((duration % 1000) / 100), seconds = parseInt((duration / 1000) % 60), minutes = parseInt((duration / (1000 * 60)) % 60), hours = parseInt((duration / (1000 * 60 * 60)) % 24);
    hours = (hours < 10) ? "0" + hours : hours;
    minutes = (minutes < 10) ? "0" + minutes : minutes;
    seconds = (seconds < 10) ? "0" + seconds : seconds;

    return hours + ":" + minutes + ":" + seconds;
}


$(function () {
    // add map tiles
    L.tileLayer('tiles/{z}/{x}/{y}.png').addTo(map);
    // add zoom control
    L.control.zoom({position:'topright'}).addTo(map);


    updateClock();
    dateTimeCounter = setInterval(updateClock, 1000);



    //
    // //fences
    //
    //
    let demoTracks = [tracks];

    let samples = new L.GeoJSON(demoTracks, {
        pointToLayer: function(geojson, latlng) {
            var circle = new L.CircleMarker(latlng, {radius:5});
            // circle.bindPopup(i);
            return circle;
        }
    });



    let playback = new L.Playback(map, demoTracks, clockCallback);

    // map.on('click', function(e) {
    //     console.log(e.latlng.toString());
    // });


    let isPlaying = false;
    $('#play-pause').click(function() {
        if (isPlaying === false && result) {
            playback.start();
            // geoTriggers.startPolling();
            $('#play-pause-icon').removeClass('icon-play');
            $('#play-pause-icon').addClass('icon-pause');
            isPlaying = true;

            // let currentTime = 0;
            for (let i = 0; i < startOrder.length; i++) {
                let convoyID = startOrder[i];
                let travelTime = times[convoyID]['travel']/defaultValues['playback'];
                let startTime = times[convoyID]['start']/defaultValues['playback'];
                let passingTime = times[convoyID]['pass']/defaultValues['playback'];
                // let runningStartTime = startTime - currentTime;
                // currentTime = startTime;
                let color = hex[mapObjects[convoyID]['color']];
                start(startTime, paths[convoyID], color, travelTime, passingTime);
            }
        } else {
            playback.stop();
            // geoTriggers.stopPolling();
            $('#play-pause-icon').removeClass('icon-pause');
            $('#play-pause-icon').addClass('icon-play');
            isPlaying = false;
        }
    });

    $('#set-cursor').click(function(){
        var val = $('#cursor-time').val();
        playback.setCursor(val);
        $('#time-slider').slider('value', val);
    });

    // $('#start-time-txt').html(new Date(playback.getStartTime()).toString());
    // startTime = playback.getStartTime();
    // startTime = (new Date()).getTime();
    // $('#cursor-date').html("&nbsp;&nbsp;"+L.Playback.Util.DateStr(startTime));
    // $('#cursor-time').html("&nbsp;&nbsp;"+L.Playback.Util.TimeStr(startTime));

    $('#time-slider').slider({
        min: playback.getStartTime(),
        max: playback.getEndTime(),
        step: playback.getTickLen(),
        value: playback.getTime(),
        slide: function( event, ui ) {
            playback.setCursor(ui.value);
            $('#cursor-time').val(ui.value.toString());
            $('#cursor-time-txt').html(new Date(ui.value).toString());
        }
    });

    // $('#cursor-time').val(playback.getTime().toString());
    $('#speed').val(playback.getSpeed().toString());

    $('#speed-slider').slider({
        // min: -9,
        min: 0,
        // max: 9,
        max: 4,
        // step: .1,
        step: 1,
        value: 3,
        // value: speedToSliderVal(playback.getSpeed()),
        orientation: 'vertical',
        slide: function( event, ui ) {
            $("#speed-input").val( playbackValues[ui.value] );
            // $("#label").text(playbackValues[ui.value]);
            $('#speed-icon-val').html(playbackValues[ui.value]);
            defaultValues['playback']= playbackValues[ui.value]
            // var speed = sliderValToSpeed(parseFloat(ui.value));
            // playback.setSpeed(speed);
            // $('.speed').html(speed).val(speed);
        }
    });
    //
    // $('#speed-input').on('keyup', function(e) {
    //     console.log("haaa")
    //     var speed = parseFloat($('#speed-input').val());
    //     if (!speed) return;
    //     playback.setSpeed(speed);
    //     $('#speed-slider').slider('value', speedToSliderVal(speed));
    //     $('#speed-icon-val').html(speed);
    //     if (e.keyCode === 13) {
    //         $('.speed-menu').dropdown('toggle');
    //     }
    // });

    $('#calendar').datepicker({
        changeMonth: true,
        changeYear: true,
        altField: '#date-input',
        altFormat: 'mm/dd/yy',
        defaultDate: dateTime,
        onSelect: function(date) {
            var date = new Date(date);
            var time =  $('#timepicker-input').val();
            var ts = combineDateAndTime(date, time);
            playback.setCursor(ts);
            updateClock(ts);
            $('#time-slider').slider('value', ts);
        }
    });

    $('#date-input').on('keyup', function(e) {
        $('#calendar').datepicker('setDate', $('#date-input').val());
    });


    $('.dropdown-menu').on('click', function(e) {
        e.stopPropagation();
    });

    $('#timepicker').datetimepicker({
        format: 'HH:mm:ss'
    });


    $('#timepicker-input').val($('#cursor-time').text());
    //
    // $('#timepicker').timepicker({
    //     showSeconds: true
    // });
    // $('#timepicker').datetimepicker('setTime',
    //     new Date(dateTime).toTimeString());
    //
    // $('#timepicker').datetimepicker().on('changeTime.timepicker', function(e) {
    //     var date = $('#calendar').datepicker('getDate');
    //     var ts = combineDateAndTime(date, e.time);
    //     playback.setCursor(ts);
    //     $('#time-slider').slider('value', ts);
    // });





    // insert default values to settings
    $("input[name=default_headway]").val(defaultValues['headway']);
    $("input[name=default_length]").val(defaultValues['length']);
    $("input[name=default_speed]").val(defaultValues['speed']);
    $("input[name=default_ready]").val(defaultValues['ready']);
    $("input[name=default_due]").val(defaultValues['due']);
    $("input[name=default_time]").val(defaultValues['time']);
    for (let i = 0; i < algorithms.length; i++) {
        let opt = document.createElement('option');
        opt.value = algorithms[i];
        opt.id = 'option_'+i;
        opt.className = 'option';
        opt.innerHTML = algorithms[i];
        $('.selectpicker').append(opt);
    }
    $("#option_"+algorithms.indexOf(defaultValues['algorithm'])).attr("selected", "selected");

    $('.selectpicker').change(function () {
        defaultValues['algorithm']=this.value;
    });

    $('#add-btn').click(function () {
        convoyID++;
        addConvoy(convoyID);

        convoys[convoyID]= {};
        convoys[convoyID]['length']= defaultValues['length'];
        convoys[convoyID]['speed']= defaultValues['speed'];
        convoys[convoyID]['ready']= defaultValues['ready'];
        convoys[convoyID]['due']= defaultValues['due'];
        mapObjects[convoyID]= [];

        $('.modify').click(function(){
            modifyNumbers(this, convoyID);
        });

        $('.input-number').focusin(function(){
            $(this).data('oldValue', $(this).val());
        });
        $('.input-number').change(function() {
            modifyInput(this, convoyID);
        });

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

        // remove row/convoy and all deleted convoy's references
        $('#delete_' + convoyID).click(function () {
            this.parentNode.parentNode.remove();
            let id = this.id.split('_')[1];
            delete convoys[id];
            // remove convoy's mapObjects
            if(mapObjects[id]['origin']){
                map.removeLayer(mapObjects[id]['origin']);
            }
            if(mapObjects[id]['destination']){
                map.removeLayer(mapObjects[id]['destination']);
            }
            delete mapObjects[id];

            // reorder convoy numbering
            let old_key = parseInt(id);
            let new_key = old_key + 1;
            while(convoys[new_key]){
                Object.defineProperty(convoys, old_key,
                    Object.getOwnPropertyDescriptor(convoys, new_key));
                delete convoys[new_key];
                Object.defineProperty(mapObjects, old_key,
                    Object.getOwnPropertyDescriptor(mapObjects, new_key));
                delete mapObjects[new_key];
                $('#ID_' + new_key).text(old_key+'.');
                $('#row_' + new_key)[0].id = "row_"+old_key;
                $('#row_' + old_key).find('.btn, .input').each(function () {
                    let old_id = $(this)[0].id;
                    let parts = old_id.split('_');
                    $(this)[0].id = parts[0]+'_' + (parseInt(parts[1])-1).toString();
                });
                old_key = new_key;
                new_key++;
            }

            // remove calculate button, if necessary
            if(!$('#calc-btn').hasClass("hidden")){
                let removeCalculate = true;
                for (let convoyID in convoys) {
                    if(Object.keys(convoys[convoyID]).length == 6){
                        removeCalculate = false;
                        break;
                    }
                }
                if (removeCalculate){
                    $('#calc-btn').addClass("hidden");
                    let top = parseInt($('.sidebar-table').css('top').slice(0, -2))-40;
                    $('.sidebar-table').css('top',top);
                }
            }
            // remove run button, if present
            if(!$('#run-btn').hasClass("hidden")){
                paths = {}
                $('#run-btn').addClass("hidden");
                let top = parseInt($('.sidebar-table').css('top').slice(0, -2))-40;
                $('.sidebar-table').css('top',top);
            }
            convoyID--;
        });
    });



    $('#calc-btn').click(function () {
        //stop clock
        clearInterval(dateTimeCounter);
        let date = new Date(moment($('#cursor-date').text()).format('YYYY, MM, DD'));
        dateTime= combineDateAndTime(date, $('#cursor-time').text());

        // let data = JSON.stringify(convoys);
        // let data = "ddd"
        let inputConvoys={};
        for (let convoyID in convoys) {
            if (Object.keys(convoys[convoyID]).length == 6) {
                inputConvoys[convoyID] = convoys[convoyID];
            }
        }
        let input = [inputConvoys, defaultValues['headway'], defaultValues['algorithm']];
        // console.log(input);
        getPaths(input, function(output){
            if (output.startsWith('error')){
                console.log(output);
                delete result;
            }
            else {
                result = JSON.parse(output);
                console.log(result);
                startOrder = [];
                let featureGroup = [];
                for (let i = 0; i < result.length; i++) {
                    let path = result[i][0];
                    let travelTime = result[i][1]*3600000;
                    let startTime = result[i][2]*3600000;
                    let convoyID = result[i][3];
                    let passingTime = ((convoys[convoyID]['length']/1000)/convoys[convoyID]['speed'])*3600000;
                    let color = hex[mapObjects[convoyID]['color']];
                    paths[convoyID] = constructPath(path);
                    mapObjects[convoyID]['path']= L.polyline(paths[convoyID], {color: color, weight: 5});
                    featureGroup.push(mapObjects[convoyID]['path']);
                    times[convoyID] = {};
                    times[convoyID]['travel']= travelTime;
                    times[convoyID]['start']= startTime;
                    times[convoyID]['pass']= passingTime;
                    startOrder.push(convoyID);
                }
                mapObjects['group'] = L.featureGroup(featureGroup);
                $('#run-btn').removeClass("hidden");
                $('.play').removeClass("hidden");
                $('.sidebar-table').css('top','180px');
                $('.nav > li.dropdown').css('left','10px');
            }
        });
    });

});

$('#run-btn').click(function () {
    // animateSidebar();
    if (result){
        // let currentTime = 0;
        for (let i = 0; i < startOrder.length; i++) {
            let convoyID = startOrder[i];
            let travelTime = times[convoyID]['travel']/defaultValues['playback'];
            let startTime = times[convoyID]['start']/defaultValues['playback'];
            let passingTime = times[convoyID]['pass']/defaultValues['playback'];
            // let runningStartTime = startTime - currentTime;
            // currentTime = startTime;
            let color = hex[mapObjects[convoyID]['color']];
            start(startTime, paths[convoyID], color, travelTime, passingTime);
        }
    }



    // for (let convoyID in result) {
    //     let data = result[convoyID];

        // console.log(pathNodes)
        // let path = constructPath(pathNodes);
        // mapPaths[convoyID] = {
        //     "type": "LineString",
        //     "coordinates": path
        // };
        // let color = mapObjects[convoyID]['color'];
        // drawPath(L.polyline(path), color, 5000, 5000);
    // }
    // let myjson = JSON.stringify(mapPaths);
    // writePaths(myjson);
    // init_video(tracks);
});

$('#clock-btn').click(function (){
    clearInterval(dateTimeCounter);
    // $('#timepicker').html(+L.Playback.Util.TimeStr(dateTime));
    // $('#date-input').html(L.Playback.Util.DateStr(dateTime));
});

$('#now').click(function (){
    dateTimeCounter = setInterval(updateClock, 1000);
    $('#clock-btn').parent().removeClass('open');
    $("a[aria-expanded='true']").attr('aria-expanded','false');
    $('#timepicker-input').val($('#cursor-time').text())
});


function addConvoy(convoyID){
    let row = '<tr id="row_' + convoyID +'"><td><button type="button" class="nr btn btn-lg btn-default id" id="ID_' + convoyID +'" title="Convoy ID"></td>' +
        '<td><button type="button" class="btn btn-lg btn-default" id = "origin_' + convoyID+'" title="Add origin"><span class="glyphicon glyphicon-play"></span></button></td>' +
        '<td><button type="button" class="btn btn-lg btn-default" id = "destination_' + convoyID+'" title="Add destination"><span class="glyphicon glyphicon-stop"></button></td>' +
        '<td>' +
        '<input type="number"  name = "length" min="1" max="99999" value = "'+ defaultValues['length'] +'" data-field="length_' + convoyID +'" class="input center merge-bottom-input input-number convoy-input"><div class="btn-group btn-block">' +
        '<button type="button" class="btn btn-xs btn-default merge-top-left-button modify" data-type="minus" data-field="length_' + convoyID +'"><span class="glyphicon glyphicon-minus"></span></button>' +
        '<button type="button" class="btn btn-xs btn-basic merge-top-right-button modify" data-type="plus" data-field="length_' + convoyID +'"><span class="glyphicon glyphicon-plus"></span></button></div>' +
        '</td>' +
        '<td>' +
        '<input type="number" name = "speed" min="1"   max=  "999" value = "'+ defaultValues['speed'] +'" data-field="speed_' + convoyID +'" class="input center merge-bottom-input input-number convoy-input"><div class="btn-group btn-block">' +
        '<button type="button" class="btn btn-xs btn-default merge-top-left-button modify" data-type="minus" data-field="speed_' + convoyID +'"><span class="glyphicon glyphicon-minus"></span></button>' +
        '<button type="button" class="btn btn-xs btn-basic merge-top-right-button modify" data-type="plus" data-field="speed_' + convoyID +'"><span class="glyphicon glyphicon-plus"></span></button></div>' +
        '</td>' +
        '<td>' +
        '<input type="number" name = "ready" min="0"   max=  "99" value = "'+ defaultValues['ready'] +'" data-field="ready_' + convoyID +'" class="input center merge-bottom-input input-number convoy-input"><div class="btn-group btn-block">' +
        '<button type="button" class="btn btn-xs btn-default merge-top-left-button modify" data-type="minus" data-field="ready_' + convoyID +'"><span class="glyphicon glyphicon-minus"></span></button>' +
        '<button type="button" class="btn btn-xs btn-basic merge-top-right-button modify" data-type="plus" data-field="ready_' + convoyID +'"><span class="glyphicon glyphicon-plus"></span></button></div>' +
        '</td>' +
        '<td>' +
        '<input type="number" name = "due" min="1"   max=  "99" value = "'+ defaultValues['due'] +'"  data-field="due_' + convoyID +'" class="input center merge-bottom-input input-number convoy-input"><div class="btn-group btn-block">' +
        '<button type="button" class="btn btn-xs btn-default merge-top-left-button modify" data-type="minus" data-field="due_' + convoyID +'"><span class="glyphicon glyphicon-minus"></span></button>' +
        '<button type="button" class="btn btn-xs btn-basic merge-top-right-button modify" data-type="plus" data-field="due_' + convoyID +'"><span class="glyphicon glyphicon-plus"></span></button></div>' +
        '</td>' +
        '<td><button type="button" class="btn btn-lg btn-danger" id = "delete_' + convoyID+'" title="Delete row"><span class="glyphicon glyphicon-minus"></span></td></tr>';
    let table = $('#convoy-list');
    table.find('thead').removeClass("hidden");
    table.append(row);
    $('#ID_' + convoyID).text(convoyID+'.');
}



function modifyNumbers(button, convoyID){
    let fieldID = $(button).attr('data-field');
    let fieldName = fieldID.split('_')[0];
    let type      = $(button).attr('data-type');
    let input = $("input[data-field='"+fieldID+"']");
    let currentVal = parseInt(input.val());
    if (!isNaN(currentVal)) {
        if(type == 'minus') {
            if(currentVal > input.attr('min')) {
                input.val(currentVal - 1).change();
                changeValue(fieldName, convoyID, parseInt(input.val()))
            }
            if(parseInt(input.val()) == parseInt(input.attr('min'))) {
                $(button).attr('disabled', true);
            }

        } else if(type == 'plus') {
            if(currentVal < input.attr('max')) {
                input.val(currentVal + 1).change();
                changeValue(fieldName, convoyID, parseInt(input.val()));
            }
            if(parseInt(input.val()) == input.attr('max')) {
                $(button).attr('disabled', true);
            }

        }
    } else {
        input.val(0);
    }
}

function modifyInput(input, convoyID){
    input = $(input);
    let minValue =  parseInt(input.attr('min'));
    let maxValue =  parseInt(input.attr('max'));
    let valueCurrent = parseInt(input.val());
    let fieldID = input.attr('data-field');
    let fieldName = fieldID.split('_')[0];
    if(valueCurrent >= minValue && valueCurrent <= maxValue) {
        $(".modify[data-type='minus'][data-field='"+fieldID+"']").removeAttr('disabled');
        $(".modify[data-type='plus'][data-field='"+fieldID+"']").removeAttr('disabled');
        changeValue(fieldName, convoyID, parseInt(input.val()));
    } else {
        input.val(input.data('oldValue'));
    }
}


function changeValue(fieldName, convoyID, value){
    if(fieldName.startsWith('default')){
        defaultValues[fieldName] = value;
    }
    else{
        convoys[convoyID][fieldName] = value
    }
}





















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

$("#settings-btn").click(function() {
    $("#settingsModal").modal("show");
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

$('#list-menu, .sidebar-hide-btn').click(function() {
    let statbar = $('.statbar');
    if (!statbar.hasClass('closed')){
        for (let i = 0; i < startOrder.length; i++) {
            convoyID = startOrder[i];
            if ($('#checkbox_' + convoyID).is(':checked')){
                map.removeLayer(mapObjects[convoyID]['path']);
            }
            else{
                mapObjects[convoyID]['origin'].addTo(map);
                mapObjects[convoyID]['destination'].addTo(map)
            }
        }
        $(".stat-row").remove();
        statbar.toggleClass("closed");
        $('.navbar-toggle-btn').toggleClass('hidden');
        $('#zoom_group').toggleClass('hidden');
        animateStatbar(0);
    }
    animateSidebar();
    console.log($('#features').hasClass('hidden'));
    $('#features').toggleClass("hidden");
    return false;
});

$('#stat-menu, .navbar-toggle-btn').click(function() {

    if(startOrder.length > 0) {
        let statbar = $('.statbar');
        let  rows = 1;
        statbar.removeClass("hidden");
        let order = startOrder.sort(function(a, b){return a-b});
        if(statbar.hasClass("closed")){
            for (let i = 0; i < order.length; i++) {
                convoyID = order[i];
                mapObjects[convoyID]['path'].addTo(map);
                addStatRow(convoyID);
                rows = $("#stat-list").find("tr").length;
            }
            let sidebar = $('#features');
            $('.navbar-fixed-bottom').addClass("hidden");
            if(!sidebar.hasClass("hidden")){
                animateSidebar();
                sidebar.addClass("hidden");
            }
        }
        else{
            for (let i = 0; i < order.length; i++) {
                convoyID = order[i];
                map.removeLayer(mapObjects[convoyID]['path']);
            }
            $(".stat-row").remove();
        }
        statbar.toggleClass("closed");
        $('.navbar-toggle-btn').toggleClass('hidden');
        $('#zoom_group').toggleClass('hidden');
        animateStatbar(rows-1);
        return false;
    }

});


function animateSidebar() {
    let toggleWidth = $("#sidebar").width() == 460 ? "0px" : "460px";
    $("#sidebar").animate({
        width: toggleWidth
    }, function() {
        map.invalidateSize();
    });
}


function animateStatbar(nr) {
    let calcHeight;
    if (nr ==0){
        calcHeight = "0px";
    }
    else if (nr == 1){
        calcHeight = "80px";
    }
    else if (nr == 2){
        calcHeight = "130px";
    }
    else{
        calcHeight = "180px";
    }
    let statbar = $('.statbar');
    let toggleHeight = statbar.height() == "0px" ? "0px" : calcHeight;
    statbar.animate({
        height: toggleHeight
    }, function() {
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










function addStatRow(convoyID){
    let startTime  = dateTime +  times[convoyID]['start'];
    let travelTime = times[convoyID]['travel'];
    let passingTime = times[convoyID]['pass'];
    let finishTime = startTime + travelTime + passingTime;

    let row = '<tr class = "stat-row" id="stat-row_' + convoyID +'" align = "center">' +
        '<td>' +
        '<div class="checkbox">' +
        '<input type="checkbox" id="checkbox_' + convoyID +'"  checked>' +
        '<label for="checkbox_' + convoyID +'"  style="background-color:'+hex[mapObjects[convoyID]['color']]+'"></label>' +
        '</div>' +
        '</td>' +
        '<td>' +
        '<button type="button" class="btn btn-md btn-default zoom" id = "zoom_' + convoyID +'"><i class="glyphicon glyphicon-zoom-in"></i></button>'+
        '</td>' +
        '<td><label class = "stat-label" id = "stat_ID_' + convoyID +'"></label></td>' +
        '<td><label class = "stat-label" id ="stat_start_' + convoyID +'"></label></td>' +
        '<td><label class = "stat-label" id = "stat_finish_' + convoyID +'"></label></td>' +
        '<td><label class = "stat-label" id = "stat_travel_' + convoyID +'"></label></td>' +
        '<td><label class = "stat-label" id = "stat_pass_' + convoyID +'"></label></td>' +
        '<td><label ></label></td>' +
        '</td></tr>';
    let table = $('#stat-list');
    table.append(row);
    $('#stat_ID_' + convoyID).text(convoyID+'.');
    $('#stat_start_' + convoyID).html(L.Playback.Util.DateStr(startTime)+"<br />"+L.Playback.Util.TimeStr(startTime));
    $('#stat_finish_' + convoyID).html(L.Playback.Util.DateStr(finishTime)+"<br />"+L.Playback.Util.TimeStr(finishTime));
    $('#stat_travel_' + convoyID).html(msToTime(travelTime));
    $('#stat_pass_' + convoyID).html(msToTime(passingTime));


    $('#checkbox_' + convoyID).change(function(){
        let convoyID = this.id.split('_')[1];
        if (this.checked){
            mapObjects[convoyID]['path'].addTo(map);
            mapObjects[convoyID]['origin'].addTo(map);
            mapObjects[convoyID]['destination'].addTo(map);
            $('#stat-row_' + convoyID+' > td > label').css('color','black');
            }
        else{
            map.removeLayer(mapObjects[convoyID]['path']);
            map.removeLayer(mapObjects[convoyID]['origin']);
            map.removeLayer(mapObjects[convoyID]['destination']);
            $('#stat-row_' + convoyID+' > td > label').css('color','#ccc');
        }
    });

    $('#zoom_' + convoyID).click(function () {
        let convoyID = this.id.split('_')[1];
        map.fitBounds(mapObjects[convoyID]['path'].getBounds());
    });
}

$('#zoom_group').click(function () {
    console.log("shddsds")
    map.fitBounds(mapObjects['group'].getBounds());
});

// $('#stat-menu > li > a').click(function() {
//     console.log("sss")
//     $('.navmenu').offcanvas('toggle');
// });

function drawLine(path, color) {
    L.polyline(path, {color: color, weight: 5}).addTo(map);
}

function drawPath(path, color, duration, length){
  let pathLine = L.polyline([], {color: color, weight: 5}).addTo(map);
  let marker = L.Marker.movingMarker(path.getLatLngs(), duration, {opacity: 0}).addTo(map);
  marker.on('move', function() {
    pathLine.addLatLng(marker.getLatLng());
    pathLine.redraw();
  });
  marker.start();
  setTimeout(function(){
    let marker2 = L.Marker.movingMarker(path.getLatLngs(), duration, {opacity: 0}).addTo(map);
    marker2.on('move', function() {
      pathLine.getLatLngs().splice(0,1);
      pathLine.redraw();
    });
    marker2.start();
  }, length);
}


function addMarker(e, id) {
    let parts = id.split('_');
    let feature = parts[0];
    let convoyID = parts[1];
    let color = mapObjects[convoyID]['color'] || assignColor(convoyID);
    let marker_icon;

    if(feature === 'origin'){
        marker_icon = L.AwesomeMarkers.icon({
            icon: 'play',
            markerColor: color
        });
        $('#origin_' + convoyID).first().css('color', 'white');
    }
    else if(feature === 'destination') {
        marker_icon = L.AwesomeMarkers.icon({
            icon: 'stop',
            markerColor: color
        });

        $('#destination_' + convoyID).first().css('color', 'white');
    }

    let marker = L.marker(e.latlng,
        {'draggable': true, 'icon': marker_icon});

    map.addLayer(marker);
    mapObjects[convoyID][feature] = marker;

    let nearest = findNearestNode(marker);
    marker.setLatLng(nearest);
    $('#'+id).css('background-color',hex[mapObjects[convoyID]['color']]);
    $('#map').css('cursor', '-webkit-grab');
    updateConvoys(convoyID, feature, nearest);

    marker.on('dragend', function(event) {
        let marker = event.target;
        nearest = findNearestNode(marker);
        marker.setLatLng(nearest, {draggable: 'true'}).bindPopup(nearest).update();
        updateConvoys(convoyID, feature, nearest);
    });
}

function findNearestNode(marker) {
    let position = marker.getLatLng();
    let geojson = L.geoJson(nodes);
    return knn(geojson).nearest(position, 1)[0];
}

function updateConvoys(ID, feature, nearest){
    convoys[ID][feature]= nearest['layer']['feature']['properties'];
    console.log(convoys[ID]);
    if(Object.keys(convoys[ID]).length == 6){
        if(!$('#calc-btn').hasClass("hidden")) {
        }
        else{
            $('#calc-btn').removeClass("hidden");
            $('.sidebar-table').css('top', '140px');
        }
        $($('#row_' + ID)[0].firstChild.firstChild).css({'background-color': hex[mapObjects[ID]['color']], 'color':'white'});
    }
}


function constructPath(pathNodes){
    let pathList = [];
    for(let i=0;i<pathNodes.length-1;i++) {
        let section = pathNodes[i]+"-"+pathNodes[i+1];
        let road = endpoints[section]['node'];
        let direction = endpoints[section]['direction'];
        if (direction === 'original'){
            let coordinates = roads[road]['coordinates'];
            pathList.push(coordinates)
        }
        else{
            let coordinates = roads[road]['coordinates'];
            let reverse = coordinates.slice().reverse();
            pathList.push(reverse);
        }
    }
    return [].concat.apply([], pathList)
}






function clockCallback(ms) {
    $('#cursor-date').html(L.Playback.Util.DateStr(ms));
    $('#cursor-time').html(L.Playback.Util.TimeStr(ms));
    $('#time-slider').slider('value', ms);
    // $('#timepicker').timepicker('setTime', new Date(ms).toTimeString());
}

function speedToSliderVal(speed) {
    if (speed < 1) return -10+speed*10;
    return speed - 1;
}

function sliderValToSpeed(val) {
    if (val < 0) return parseFloat((1+val/10).toFixed(2));
    return val + 1;
}

function triggerFired(trigger) {
    var html =
        '<div class="accordion-inner">' +
        '  <strong>'+trigger.place.name+'</strong>' +
        '  <span class="broadcast-time">'+ trigger.display_date + '</span>' +
        '  <br/>' +
        trigger.trigger.text + '<br/>' +
        '  <button class="btn btn-info btn-small view-notification"><i class="icon-eye-open"></i> View</button>'+
        '</div>';

    $('#notifications').prepend(html);
    var count = $('#notifications').children().length;
    $('#notification-count').html('<span class="badge badge-important pull-right">'+count+'</span>');
    var $btn = $('#notifications').find('button').first();
    $btn.data('trigger',trigger);
    $btn.on('click', function(e) {
        var lat = trigger.place.latitude;
        var lng = trigger.place.longitude;
        var radius = trigger.place.radius * 1.5;
        var circle = new L.Circle([lat,lng],radius);
        var bounds = circle.getBounds();
        map.fitBounds(bounds);
    });
}

function combineDateAndTime(date, time) {
    console.log(date,time)
    let parts = time.split(':')
    let yr = date.getFullYear();
    let mo = date.getMonth();
    let dy = date.getDate();
    let hr = parseInt(parts[0]);
    let min = parseInt(parts[1]);
    let sec = parseInt(parts[2]);

    console.log(time, yr, hr, min, sec)
    // the calendar uses hour and the timepicker uses hours...
    // var hr = time.hours || time.hour;
    // if (time.meridian == 'PM' && hr != 12) hr += 12;
    // var min = time.minutes || time.minute;
    // var sec = time.seconds || time.second;
    return new Date(yr, mo, dy, hr, min, sec).getTime();
}



function save(data, name) {
    var json = JSON.stringify(data, null, 2);
    var blob = new Blob([json], {type:'text/plain'});
    var downloadLink = document.createElement("a");
    var url = (window.webkitURL != null ? window.webkitURL : window.URL);
    downloadLink.href = url.createObjectURL(blob);
    downloadLink.download = name || 'data.json';
    downloadLink.click();
}

function sliceData(data, start,end) {
    end = end || data.geometry.coordinates.length-1;
    data.geometry.coordinates = data.geometry.coordinates.slice(start,end);
    data.properties.time = data.properties.time.slice(start,end);
    data.properties.speed = data.properties.speed.slice(start,end);
    data.properties.altitude = data.properties.altitude.slice(start,end);
    data.properties.heading = data.properties.heading.slice(start,end);
    data.properties.horizontal_accuracy = data.properties.horizontal_accuracy.slice(start,end);
    data.properties.vertical_accuracy = data.properties.vertical_accuracy.slice(start,end);
    save(data,'sliced-data.json');
}

