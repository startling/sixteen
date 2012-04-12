// globals, so we can keep track of them.
var canvas = null;
var context = null;
var socket = null;


function init() {
    // on the window's load, get canvas and its 2D context
    canvas = document.getElementsByTagName("canvas")[0];
    context = canvas.getContext("2d");
}


// run init when the window loads
window.addEventListener('load', init, false);


// initialize a websocket
socket = new WebSocket("ws://localhost:8080");


socket.onopen = function(msg) {
    // when the socket opens, let us debuggers know
    console.log("[Socket opened]");
    // and then send some blank text back, so the cpu cycles.
    socket.send("");
}

socket.onmessage = function(msg) {
    // get the json data from the message
    data = JSON.parse(msg.data);
    // just log it for now.
    console.log(data);
};


socket.onerror = function() {
    // I'm not sure when this gets called
    console.log("[socket error]");
};
