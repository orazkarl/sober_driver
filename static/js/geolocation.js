ymaps.ready(function () {
    var map;
    ymaps.geolocation.get().then(function (res) {
        var mapContainer = $('#map'),
            bounds = res.geoObjects.get(0).properties.get('boundedBy'),
            // Рассчитываем видимую область для текущей положения пользователя.
            mapState = ymaps.util.bounds.getCenterAndZoom(
                bounds,
                [mapContainer.width(), mapContainer.height()]
            );
        createMap(mapState);
        sendRequest(mapState['center']);

    }, function (e) {
        // Если местоположение невозможно получить, то просто создаем карту.
        createMap({
            center: [55.751574, 37.573856],
            zoom: 2
        });
    });

    function createMap (state) {
        map = new ymaps.Map('map', state);
    }
});

function sendRequest(state){
    const Http = new XMLHttpRequest();
    const url = 'https://geocode-maps.yandex.ru/1.x?geocode=' + state[1] +',' + state[0] +  '&apikey=7af4d9cc-1a22-44c4-82cf-dbd6503a6696&kind=house';
    Http.open("GET", url);
    Http.send();



    $.get(url, function(data, status){
        const text = data;
        const parser = new DOMParser();
        const xmlDOM = parser.parseFromString(text,"text/xml");
        var value = text.getElementsByTagName("GeocoderMetaData")[0].getElementsByTagName("Address")[0];
        var city = value.getElementsByTagName('Component')[2].getElementsByTagName("name")[0].childNodes[0].nodeValue;
        var address = value.getElementsByTagName('Component')[3].getElementsByTagName("name")[0].childNodes[0].nodeValue +',' +  value.getElementsByTagName('Component')[4].getElementsByTagName("name")[0].childNodes[0].nodeValue;
        insertData(city, address)
    });


}

function insertData(city, address){
console.log(city);
document.getElementsById('id_city').value = String(city);
        document.getElementsById('id_from_address').value = String(address);

}