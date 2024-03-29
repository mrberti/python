var edHost = document.getElementById('edHost');
var spanLedState = document.getElementById('spanLedState');
var spinnerLed = document.getElementById('spinnerLed');
var btnLedOn = document.getElementById('btnLedOn');
var btnLedOff = document.getElementById('btnLedOff');
var btnLedToggle = document.getElementById('btnLedToggle');
var btnCh1On = document.getElementById('btnCh1On');
var btnCh1Off = document.getElementById('btnCh1Off');
var btnGetRoom = document.getElementById('btnGetRoom');
var temperatureValue = document.getElementById('temperatureValue');
var humidityValue = document.getElementById('humidityValue');
var temperatureUnit = document.getElementById('temperatureUnit');
var humidityUnit = document.getElementById('humidityUnit');

function apiResponseHandler() {
    var data = JSON.parse(this.responseText);
    console.log(data);
    var state = data.led?.state ?? "...";
    if (state == "off") {
        spanLedState.innerHTML = state;
        btnLedOff.classList.remove("btn-outline-danger");
        btnLedOff.classList.add("btn-danger");
        btnLedOn.classList.remove("btn-success");
        btnLedOn.classList.add("btn-outline-success");
    }
    else if (state == "on") {
        spanLedState.innerHTML = state;
        btnLedOn.classList.remove("btn-outline-success");
        btnLedOn.classList.add("btn-success");
        btnLedOff.classList.remove("btn-danger");
        btnLedOff.classList.add("btn-outline-danger");
    }

    if (data.temperature) {
        temperatureValue.innerText = data.temperature.toFixed(1);
        temperatureUnit.innerText = data.temperature_unit;
    }
    if (data.humidity) {
        humidityValue.innerText = data.humidity.toFixed(1);
        humidityUnit.innerText = data.humidity_unit;
    }

    spinnerLed.style.display = "None";
}

function apiResponseStartHandler() {
    spinnerLed.style.display = "";
}

var api = new XMLHttpRequest();
api.addEventListener("load", apiResponseHandler);
api.addEventListener("loadstart", apiResponseStartHandler);

function sendRequest(method, path) {
    api.open(method, `http://${edHost.value}` + path);
    api.send();
}

function getLedState() {
    sendRequest("GET", "/api/led");
}

/* LED */
btnLedOn.addEventListener("click", function () {
    sendRequest("POST", "/api/led?state=on");
});

btnLedOff.addEventListener("click", function () {
    sendRequest("POST", "/api/led?state=off");
});

btnLedToggle.addEventListener("click", function () {
    sendRequest("POST", "/api/led?state=toggle");
});

/* RF */
btnCh1On.addEventListener("click", function () {
    sendRequest("POST", "/api/rf?ch1=on");
});

btnCh1Off.addEventListener("click", function () {
    sendRequest("POST", "/api/rf?ch1=off");
});

btnCh2On.addEventListener("click", function () {
    sendRequest("POST", "/api/rf?ch2=on");
});

btnCh2Off.addEventListener("click", function () {
    sendRequest("POST", "/api/rf?ch2=off");
});

btnCh3On.addEventListener("click", function () {
    sendRequest("POST", "/api/rf?ch3=on");
});

btnCh3Off.addEventListener("click", function () {
    sendRequest("POST", "/api/rf?ch3=off");
});

/* room */
var measureInterval;
btnGetRoom.addEventListener("click", function () {
    if (!measureInterval) {
        measureInterval = setInterval(() => {
            sendRequest("GET", "/api/room");
        }, 1000);
        btnGetRoom.innerHtml = "Stop Measurement";
    } else {
        measureInterval = clearInterval(measureInterval);
        btnGetRoom.innerHtml = "Start Measurement";
    }
});

/* MAIN */
getLedState();
// setInterval(getLedState, 1000);