// globals, so we can keep track of them.
var canvas = null;
var context = null;
var socket = null;

// characters is an empty object that we'll use to keep track of 
var characters = {};

// constants for the height and width of pixels and characters
var pixel_width = 4;
var pixel_height = 4;

var char_width = pixel_width * 4
var char_height = pixel_height * 8


function init() {
    // on the window's load, get canvas and its 2D context
    canvas = document.getElementsByTagName("canvas")[0];
    canvas.width = char_width * 32;
    canvas.height = char_height * 12;
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
    // if we get a background color, change the canvas' border.
    if (data["background"] != null) {
        canvas.style.borderColor = data["background"];
    };

    // iterate through the given new characters and change our map of
    // characters.
    Object.keys(data["characters"]).forEach(function (key) {
        characters[key] = data["characters"][key];
    });

    // and then change all the cells
    data.cells.forEach(draw_cell);
    
    // register a callback to send a reply in
    setTimeout(function () {
        socket.send("");
    }, 10);
};


function draw_pixel(x, y) {
    var x_a = pixel_width * x;
    var y_a = pixel_height * y;
    context.fillRect(x_a, y_a, pixel_width, pixel_height);
};


function draw_cell(n) {
    // adjust the coordinates
    var x = char_width * n.x;
    var y = char_height * n.y;
    // draw the background
    context.fillStyle = n.background;
    context.fillRect(x, y, char_width, char_height);
    // draw the character
    character = characters[n["char"]];
    context.fillStyle = n.foreground;
    var r = 0;
    character.forEach(function (row) {
        var column = 0;
        row.forEach(function (cell) {
            if (cell == 1) {
                draw_pixel((n.x * pixel_width) + column, (n.y * pixel_height) + r);
            };
            column++;
        });
        r++;
    });
};


socket.onerror = function() {
    // I'm not sure when this gets called
    console.log("[socket error]");
};
