
var http = require('http');
var express = require('express');

var app = express();

// So that the JSON body is parsed automagically.
app.use(express.bodyParser());

app.use(function (req, res, next) {
  //console.log(req.body) // populated!
  next()
});

app.get("/", function(req, res) {
    res.send("Hello");
});



// This should be included *after* the app.use statements.
// Otherwise bodyParser doesn't apply etc.
var routes = require("./routes")(app);


// So that tests can see it.
exports.app = app;


app.listen(5000, '127.0.0.1');
console.log('Server running at http://127.0.0.1:5000/');