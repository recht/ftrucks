var truckApp = angular.module('truckApp', []);
truckApp.controller('TruckAppController', function($scope) {

    // the list of known vehicles for a specific route
    var busses = {};

    var socket = io.connect('http://localhost:5000');
    socket.on('init', function(msg) {
        $scope.busses = msg.busses;
        $scope.$apply();
        console.log('init', msg);
    });

    $scope.$watch('bus', function(bus) {
        if (bus) {
            socket.emit('bus-selected', bus);
        }
        busses = {};
    });


    var map = new ol.Map({
            target: 'map',
            layers: [
              new ol.layer.Tile({
                source: new ol.source.OSM({layer: 'sat'})
              })
            ],
            view: new ol.View({
              center: ol.proj.transform([-122.406615761073, 37.7854697464899], 'EPSG:4326', 'EPSG:3857'),
              zoom: 16
            })
          });
    var popup = new ol.Overlay({
        element: document.getElementById('popup'),
        positioning: 'bottom-center',
        stopEvent: false,
    });
    map.addOverlay(popup);
    map.on('click', function(evt) {
        var feature = map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
            return feature;
        });
        if (feature) {
            var geom = feature.getGeometry();
            var coord = geom.getCoordinates();
            popup.setPosition(coord);
            $('#popup').html('<div class="truck-name">' + feature.get('name') + '</div><div class="truck-items">' + feature.get('items') + '</div>');
            $scope.popupName = feature.get('name');
            $scope.$apply();
            $('#popup').show();
        } else {
            $('#popup').hide();

            if (!$scope.bus) {
                var p = new ol.geom.Point(evt.coordinate);
                var coords = p.transform("EPSG:900913", "EPSG:4326").getCoordinates();
                socket.emit('new-location', [{lon: coords[0], lat: coords[1]}]);
            }
        }
    });
    $(map.getViewport()).on('mousemove', function(evt) {
        var pixel = map.getEventPixel(evt.originalEvent);
        var hit = map.forEachFeatureAtPixel(pixel, function(feature, layer) {
            return true;
        });
        if (hit) {
            document.getElementById('map').style.cursor = 'pointer';
        } else {
            document.getElementById('map').style.cursor = '';
        }
    });


    var iconStyle = new ol.style.Style({
        image: new ol.style.Icon({
            src: 'truck.png',
        })
    });
    var busIconStyle = new ol.style.Style({
        image: new ol.style.Icon({
            src: 'bus.png'
        })
    });

    var layer;
    socket.on('new-trucks', function(msg) {
        if (layer) {
            map.removeLayer(layer);
        }
        var vector = new ol.source.Vector({});
        msg.forEach(function(truck) {
            console.log(truck);
            var f = new ol.Feature({
                geometry: getPoint(truck.location.lon, truck.location.lat),
                name: truck.applicant,
                items: truck.items
            });
            vector.addFeature(f);
        });

        layer = new ol.layer.Vector({
            source: vector,
            style: iconStyle
        });
        map.addLayer(layer);

    });

    var busLayer;
    socket.on('bus-located', function(msg) {
        msg.forEach(function(bus) {
            busses[bus.id] = bus;
        });

        var vector = new ol.source.Vector({});
        var locations = [];
        console.log('busses', busses);
        _.values(busses).forEach(function(bus) {
            locations.push({lon: bus.lon, lat: bus.lat});
            var f = new ol.Feature({
                geometry: getPoint(bus.lon, bus.lat),
                name: 'Bus route ' + bus.route,
                items: ''
            });
            vector.addFeature(f);
        });

        if (busLayer) {
            map.removeLayer(busLayer);
        }
        busLayer = new ol.layer.Vector({
            source: vector,
            style: busIconStyle
        });
        map.addLayer(busLayer);

        socket.emit('new-location', locations);
        console.log('located', msg);
    });

    // for some reason this is not triggered automatically when connecting so we emulate here to start the app
    socket.emit('connect', {});


    function getPoint(lon, lat) {
        return new ol.geom.Point(ol.proj.transform([parseFloat(lon), parseFloat(lat)], 'EPSG:4326', 'EPSG:3857'));
    }
});
