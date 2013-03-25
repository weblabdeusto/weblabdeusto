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

var xmlrpc = require('xmlrpc')


exports.module_version = "1.0";
exports.api_version = "2";
exports.api_concurrent_version = "2_concurrent";


function launch( port, exp_server ) {

	// Creates an XML-RPC server to listen to XML-RPC method calls
	var server = xmlrpc.createServer({ host: 'localhost', port: port });
	
	// Lists the supported methods
	var methods = {'Util.test_me' : exp_server.test_me, 'Util.is_up_and_running' : exp_server.is_up_and_running, 'Util.start_experiment' : exp_server.start_experiment, 
		'Util.send_file_to_device' : exp_server.send_file, 'Util.send_command_to_device' : exp_server.send_command, 'Util.dispose' : exp_server.dispose};
	
	// Handle methods not found
	server.on('NotFound', 
		function (method, params) {
			console.log('[SYSTEM] Method ' + method + ' does not exist');
	});
	
	// We now need to register the methods that we wish to support. This is not done
	// in a particularly intuitive way. 
	for( var method in methods ) {
		
		// With server.on we register each method. Because we are dynamically creating different callbacks
		// for each method, we actually have to wrap it within an object. Otherwise, if we called 
		// methods[method]() within the callback itself, because the callback execution is deferred,
		// it wouldn't resolve to the right one.
		server.on(method, 
			new function() {
				var m = methods[method];
				var func = function (err, params, callback) {
							//console.log('Method call params for "' + method + '": ' + params)
							var resp = m.apply(this, params);
			
							// Send a method response with a value
							callback(null, resp)
						};
				return func;
			}
		);
		
		// We will also register the get_api method. This is an special method which specifies
		// which version of the Weblab API experiments are made for. The response of this method
		// is hard-coded because it is precissely this library which implements a specific
		// version of the Weblab-API.
		server.on("Util.get_api", function(err, params, callback) {
						callback(null, exports.api_version);
						});
	}
	
	console.log('[SYSTEM] XML-RPC server listening on port ' + port)	
}


DefaultExperimentServer = new function() {
	
	this.test_me = function(message) {
		return message;
	}
	
	this.is_up_and_running = function() {
		return True;
	}
	
	this.start_experiment = function(client_initial_data, server_initial_data) {
		// Start experiment can return a JSON string specifying the initial configuration.
		// The "config" object can contain anything. It will be delivered as-is to the client.
		var config = {};
		var initial_config = { "initial_configuration" : config, "batch" : false };
		return JSON.stringify(initial_config);
	}
	
	this.send_file = function (content, file_info) {
		return "ok";
	}
	
	this.send_command = function (command_string) {
		return "ok";
	}
	
	this.dispose = function () {
		return "ok";
	}
}



// We define the visible interface of the module here. Exports is an special object
// in the node environment.
exports.launch = launch;
exports.DefaultExperimentServer = DefaultExperimentServer;




