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
	
	this.is_up_and_running = function() {
		console.log("On is_up_and_running");
		return true;
	}
	
	this.start_experiment = function() {
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
	
	this.dispose = function () {
		console.log("On dispose");
		return "ok";
	}	
}


experimentserver.launch(12345, DummyExperimentServer);

        