truckApp.factory('mapService', function() {

    var layers = {};

    function getPoint(lon, lat) {
        return new ol.geom.Point(ol.proj.transform([parseFloat(lon), parseFloat(lat)], 'EPSG:4326', 'EPSG:3857'));
    }

    return {
        /**
         * Create a new map.
         * @param id ID of the DOM element to attach the map to,
         * @param onclick Handler to invoke when the user clicks on the map. It receives one argument, the coordinate of the click.
         */
        createMap: function(id, $scope, onclick) {
            var map = new ol.Map({
                    target: id,
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
                    $('#popup').show();
                } else {
                    $('#popup').hide();

                    if (!$scope.bus) {
                        var p = new ol.geom.Point(evt.coordinate);
                        var coords = p.transform("EPSG:900913", "EPSG:4326").getCoordinates();
                        onclick({lon: coords[0], lat: coords[1]});
                    }
                }
            });
            $(map.getViewport()).on('mousemove', function(evt) {
                var pixel = map.getEventPixel(evt.originalEvent);
                var hit = map.forEachFeatureAtPixel(pixel, function(feature, layer) {
                    return true;
                });
                if (hit) {
                    document.getElementById(id).style.cursor = 'pointer';
                } else {
                    document.getElementById(id).style.cursor = '';
                }
            });
            return map;
        },

        /**
         * Create an icon instance.
         * @param icon URL for the icon.
         */
        createIcon: function(icon) {
            var iconStyle = new ol.style.Style({
                image: new ol.style.Icon({
                    src: icon,
                })
            });
            return iconStyle;
        },

        /**
         * Attach a list of features (markers) to the map.
         * @param type A type identifier for the feature - features are grouped by this, so if setFeatures is called
         *             again with the same type then the existing features will be replaced.
         * @param icon The icon to use, created using createIcon.
         * @param features An array of feature objects containing lon, lat, name, items.
         */
        setFeatures: function(map, type, icon, features) {
            var layer = layers[type];

            if (layer) {
                map.removeLayer(layer);
            }

            var vector = new ol.source.Vector({});
            features.forEach(function(feature) {
                var f = new ol.Feature({
                    geometry: getPoint(feature.lon, feature.lat),
                    name: feature.name,
                    items: feature.items,
                });
                vector.addFeature(f);
            });
            layer = new ol.layer.Vector({
                source: vector,
                style: icon,
            });
            layers[type] = layer;
            map.addLayer(layer);
        }
    };
});