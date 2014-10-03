
// Global to store sessions.
var GDATA = {};

// Method to create a new Session.
exports.start = function(req, res) {

//    console.log( JSON.stringify(req.body) );

    var client_initial_data = JSON.parse(req.body["client_initial_data"]);
    var server_initial_data = JSON.parse(req.body["server_initial_data"]);

    // Calculate when we should end the experiment for the user.
    var start_date_str = server_initial_data["priority.queue.slot.start"];
    var start_date = new Date(start_date_str);
    var slot_length = parseFloat(server_initial_data["priority.queue.slot.length"]);
    var max_date = new Date(start_date.getTime() + 1000*slot_length);


    // Create the new session.
    var sessionid = Math.round(Math.random() * 10000000000).toString(); // TODO: IMPROVE THIS.
    GDATA[sessionid] = {
        'username': server_initial_data["request.username"],
        'max_date': max_date,
        'last_poll': new Date(),
        'back': req.body["back"]
    };

    var link = "/lab/" + sessionid;

    console.log(GDATA[sessionid]);

    res.send({"url": link, "session_id": sessionid});
};


exports.index = function() {};


// Method to check the status of an existing session.
exports.status = function(req, res)
{
    var sessionid = req.query.sessionid;

    var session = GDATA["sessionid"];

    if(sessionn != undefined) {
        console.log("Still time left");
    } else {
        req.send({"should_finish": -1});
    }
};


exports.dispose = function(req, res) {
    // Not yet implemented.
};
