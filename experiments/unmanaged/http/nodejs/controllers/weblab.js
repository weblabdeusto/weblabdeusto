
// Global to store sessions.
var GDATA = {};
var GEXPIRED = {};

exports.GDATA = GDATA;
exports.GEXPIRED = GEXPIRED;

// Create a new session, whose data will be internally stored.
// This is called by the Weblab Core when reserve.
exports.start = function(req, res) {

    // console.log( JSON.stringify(req.body) );

    if(req.body["client_initial_data"] == undefined) {
        res.status(400).send("client_initial_data not provided");
        return;
    }

    if(req.body["server_initial_data"] == undefined) {
        res.status(400).send("server_initial_data not provided");
        return;
    }

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

    //console.log(GDATA[sessionid]);

    res.send({"url": link, "session_id": sessionid});
};

//! Index for authorized users.
//! This should be the page that serves the laboratory itself.
//!
exports.index = function(req, res)
{
    var sessionid = req.params.sessionid;
    var session = GDATA[sessionid];

    if(session == undefined)
    {
        var back_url = GEXPIRED[sessionid];
        if(back_url == undefined)
        {
            res.status(404).send("Session identifier not found");
            return;
        }
        else
        {
            return res.redirect(back_url);
        }
    }

    session["last_poll"] = new Date();

    res.send("<html><body>Hello</body></html>")
    return;
};


//    data['last_poll'] = datetime.datetime.now()
//    return """<html>
//    <head>
//        <meta http-equiv="refresh" content="10">
//    </head>
//    <body>
//        Hi %(username)s. You still have %(seconds)s seconds
//    </body>
//    </head>
//    """ % dict(username=data['username'], seconds=(data['max_date'] - datetime.datetime.now()).seconds)
//};


//! Checks the status of an existing session.
//!
//! It will return the number of seconds before Weblab should query again,
//! (which is usually 10 seconds), or -1 if the session has expired.
exports.status = function(req, res)
{
    var sessionid = req.params.sessionid;
    var session = GDATA[sessionid];


    if(session != undefined) {
        console.log("Still time left");
        res.send({"should_finish": 10});
    } else {
        res.send({"should_finish": -1});
    }
};


//! Removes the session from the internal DB.
//!
//! @return: 'deleted', 'not found' or 'unknown op'
exports.dispose = function(req, res) {
    if(req.body["action"] == "delete")
    {
        var sessionid = req.params.sessionid;
        session = GDATA[sessionid];
        if(session != undefined) {
            GEXPIRED[sessionid] = session["back"];
            GDATA[sessionid] = undefined;
            res.send("deleted");
            return;
        }
        res.send("not found");
        return;
    }
    res.send("unknown op");
    return;
};

