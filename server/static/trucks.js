var truckApp = angular.module('truckApp', []);
truckApp.controller('TruckAppController', ['$scope', 'mapService', function($scope, mapService) {

    // the list of known vehicles for a specific route
    var busses = {};

    var socket = io.connect(window.location.href.substring(0, window.location.href.indexOf('/', 8)));
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

    var map = mapService.createMap('map', $scope, function(coords) {
         socket.emit('new-location', [coords]);
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

    var truckIcon = mapService.createIcon('truck.png');
    var busIcon = mapService.createIcon('bus.png');

    socket.on('new-trucks', function(msg) {
        var features = [];

        msg.forEach(function(truck) {
            features.push({
                lon: truck.location.lon,
                lat: truck.location.lat,
                name: truck.applicant,
                items: truck.items,
            });
        });
        mapService.setFeatures(map, 'trucks', truckIcon, features);
    });

    socket.on('bus-located', function(msg) {
        msg.forEach(function(bus) {
            busses[bus.id] = bus;
        });

        var features = [];
        var locations = [];
        console.log('busses', busses);
        _.values(busses).forEach(function(bus) {
            locations.push({lon: bus.lon, lat: bus.lat});
            features.push({
                lon: bus.lon,
                lat: bus.lat,
                name: bus.route,
                items: '',
            });
        });
        mapService.setFeatures(map, 'bus', busIcon, features);

        socket.emit('new-location', locations);
        console.log('located', msg);
    });

    // for some reason this is not triggered automatically when connecting so we emulate here to start the app
    socket.emit('connect', {});

}]);
