function geoYandex() {
    ymaps.ready(init);
    var myMap;
}

function init() {
    var geolocation = ymaps.geolocation,
        myMap = new ymaps.Map('map', {
            center: [43.2566700, 76.9286100],
            zoom: 10
        });

    geolocation.get({
        provider: 'browser',
        mapStateAutoApply: false,
    }).then(function (result) {
        result.geoObjects.options.set('preset', 'islands#redCircleIcon');
        result.geoObjects.get(0).properties.set({
            balloonContentBody: 'Мое местоположение'
        });
        myMap.geoObjects.add(result.geoObjects);
        sendRequest(result.geoObjects.get(0).geometry.getCoordinates());
        myMap.setCenter([result.geoObjects.get(0).geometry.getCoordinates()[0], result.geoObjects.get(0).geometry.getCoordinates()[1]], 14, {checkZoomRange: true});

    });


    myMap.controls.remove('geolocationControl');
}


function sendRequest(state) {
    const Http = new XMLHttpRequest();
    const url = 'https://geocode-maps.yandex.ru/1.x?geocode=' + state[1] + ',' + state[0] + '&apikey=7af4d9cc-1a22-44c4-82cf-dbd6503a6696&kind=house';
    Http.open("GET", url);
    Http.send();


    $.get(url, function (data, status) {
        const text = data;
        const parser = new DOMParser();
        const xmlDOM = parser.parseFromString(text, "text/xml");
        var value = text.getElementsByTagName("GeocoderMetaData")[0].getElementsByTagName("Address")[0];
        var city = value.getElementsByTagName('Component')[2].getElementsByTagName("name")[0].childNodes[0].nodeValue;
        var address = value.getElementsByTagName('Component')[3].getElementsByTagName("name")[0].childNodes[0].nodeValue + ',' + value.getElementsByTagName('Component')[4].getElementsByTagName("name")[0].childNodes[0].nodeValue;
        document.querySelector('#id_cities').style.display = 'block'
        var cities = []
        for (var i = 0; i < document.querySelector('#id_city').options.length; i++) {
            c = document.querySelector('#id_city').options[i]
            if (c != undefined) {
                cities.push(c.innerHTML)
            }
        }
        if (cities.includes(city)) {
            document.querySelector('#id_city').value = city
            document.querySelector('#id_from_address').value = address
        } else {
            document.querySelector('#error-geolocation').innerHTML = 'Город "' + city + '" не обслуживается'
        }

    });


}
