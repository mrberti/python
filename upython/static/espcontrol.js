var edHost = document.getElementById('edHost');
var spanLedState = document.getElementById('spanLedState');
var spinnerLed = document.getElementById('spinnerLed');
var btnLedOn = document.getElementById('btnLedOn');
var btnLedOff = document.getElementById('btnLedOff');
var btnLedToggle = document.getElementById('btnLedToggle');

function getHost() {
    return edHost.value;
}

function apiLedResponseHandler() {
    console.log(this.responseText);
    var data = JSON.parse(this.responseText);
    console.log(data);
    var state = data.led.state;
    spanLedState.innerHTML = state;
    if (state == "off") {
        btnLedOff.classList.remove("btn-outline-danger");
        btnLedOff.classList.add("btn-danger");
        btnLedOn.classList.remove("btn-success");
        btnLedOn.classList.add("btn-outline-success");
    }
    else if (state == "on") {
        btnLedOn.classList.remove("btn-outline-success");
        btnLedOn.classList.add("btn-success");
        btnLedOff.classList.remove("btn-danger");
        btnLedOff.classList.add("btn-outline-danger");
    }
    spinnerLed.style.display = "None";
}

function apiLedStartHandler() {
    spinnerLed.style.display = "";
}

var apiLed = new XMLHttpRequest();
apiLed.addEventListener("load", apiLedResponseHandler);
apiLed.addEventListener("loadstart", apiLedStartHandler);

function getLedState() {
    apiLed.open("GET", `http://${getHost()}/api/led`);
    apiLed.send();
}

btnLedOn.addEventListener("click", function () {
    apiLed.open("POST", `http://${getHost()}/api/led?state=on`);
    apiLed.send();
});

btnLedOff.addEventListener("click", function () {
    apiLed.open("POST", `http://${getHost()}/api/led?state=off`);
    apiLed.send();
});

btnLedToggle.addEventListener("click", function () {
    apiLed.open("POST", `http://${getHost()}/api/led?state=toggle`);
    apiLed.send();
});

getLedState();
setInterval(getLedState, 1000);