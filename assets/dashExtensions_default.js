window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, layer, context) {
                if (feature.properties.lokasi) {
                    layer.bindTooltip(`${feature['properties']['Nama UPT']} 
Kode:${feature['properties']['lokasi']} 
 Koord : (${feature['properties']['LAT']},${feature['properties']['LON']})`)
                }
            }

            ,
        function1: function(feature, latlng, context) {
            //const {min, max, colorscale, circleOptions, colorProp} = context.hideout;
            //const csc = chroma.scale(colorscale).domain([min, max]);  // chroma lib to construct colorscale
            //circleOptions.fillColor = csc(feature.properties[colorProp]);  // set color based on color prop
            return L.circleMarker(latlng); // render a simple circle marker
        }

    }
});