
// Global to store sessions.
var GDATA = {};

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

    res.send({"url": link, "session_id": sessionid});
};





//
//    # Create a global session
//    session_id = str(random.randint(0, 10e8)) # Not especially secure 0:-)
//    DATA[session_id] = {
//        'username'  : server_initial_data['requ
// est.username'],
//        'max_date'  : max_date,
//        'last_poll' : datetime.datetime.now(),
//        'back'      : request_data['back']
//    }
//
//    link = url_for('index', session_id=session_id, _external = True)
//    print "Assigned session_id: %s" % session_id
//    print "See:",link
//    return json.dumps({ 'url' : link, 'session_id' : session_id })



exports.index = function() {};

exports.status = function() {};

exports.dispose = function() {};