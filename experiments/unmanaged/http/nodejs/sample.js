
var http = require('http');
var express = require('express');


var server = express();

require("./routes")(server);


server.get("/", function(req, res) {
    res.send("Hello");
});


server.post("/sample/weblab/sessions/", function(req, res) {

});



















server.listen(5000, '127.0.0.1');
console.log('Server running at http://127.0.0.1:5000/');