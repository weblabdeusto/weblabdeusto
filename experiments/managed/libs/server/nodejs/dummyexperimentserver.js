//
// Copyright (C) 2013 University of Deusto
// All rights reserved.
//
// This software is licensed as described in the file COPYING, which
// you should have received as part of this distribution.
//
// This software consists of contributions made by many individuals,
// listed below:
//
// Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
//

experimentserver = require("./node.weblab.experimentserver");



DummyExperimentServer = new function() {
	
	this.test_me = function(message) {
		console.log("On test_me");
		return message;
	}

    // Is the experiment up and running?
    // The scheduling system will ensure that the experiment will not be
    // assigned to other student while this method is called. The result
    // is an array of integer + String, where the first argument is:
    //   - result >= 0: "the experiment is OK; please check again
    //                 within $result seconds"
    //   - result == 0: the experiment is OK and I can't perform a proper
    //                 estimation
    //   - result == -1: "the experiment is broken"
    // And the second (String) argument is the message detailing while
    // it failed.
	this.is_up_and_running = function() {
		console.log("On is_up_and_running");
		return [600, ""];
	}
	
	this.start_experiment = function(client_initial_data, server_initial_data) {
		// Start experiment can return a JSON string specifying the initial configuration.
		// The "config" object can contain anything. It will be delivered as-is to the client.
		var config = {};
		var initial_config = { "initial_configuration" : config, "batch" : false };
		return JSON.stringify(initial_config);
	}
	
	this.send_file = function (content, file_info) {
		console.log("On send_file");
		return "ok";
	}
	
	this.send_command = function (command_string) {
		console.log("On send_command");
		return "ok";
	}
	
	// Returns a numeric result, defined as follows:
    // result > 0: it hasn't finished but ask within result seconds.
    // result == 0: completely interactive, don't ask again
    // result < 0: it has finished.
	this.should_finish = function() {
		return 0;
	}
	
	// May optionally return data as a string, which will often be json-encoded.
	this.dispose = function () {
		console.log("On dispose");
		return "ok";
	}	
}


experimentserver.launch(12345, DummyExperimentServer);

        