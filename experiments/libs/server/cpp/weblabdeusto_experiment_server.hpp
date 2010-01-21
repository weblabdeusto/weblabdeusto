
//
// Copyright (C) 2005-2009 University of Deusto
// All rights reserved.
//
// This software is licensed as described in the file COPYING, which
// you should have received as part of this distribution.
//
// This software consists of contributions made by many individuals, 
// listed below:
//
// Author: Luis Rodríguez <4lurodri@rigel.deusto.es>
// 

#ifndef __WEBLABSERVER_HPP
#define __WEBLABSERVER_HPP

#include <string>

#include <xmlrpc-c/base.h>
#include <xmlrpc-c/server.h>
#include <xmlrpc-c/server_abyss.h>



class ExperimentServer
{

public:

	virtual std::string onStartExperiment() = 0;
	virtual std::string onSendFile(std::string const & encoded_file, std::string const & fileinfo) = 0;
	virtual std::string onSendCommand(std::string const & command) = 0;
	virtual std::string onDispose() = 0;

	void launch(unsigned short port, std::string const & log_file = "");
	
	ExperimentServer();
	
	virtual ~ExperimentServer() {}

private:

	static xmlrpc_value * c_xmlrpc_test_me(xmlrpc_env *   const env, xmlrpc_value * const param_array, void * const user_data);
	static xmlrpc_value * c_xmlrpc_send_file_to_device(xmlrpc_env *   const env, xmlrpc_value * const param_array, void * const user_data);
	static xmlrpc_value * c_xmlrpc_send_command_to_device(xmlrpc_env *   const env, xmlrpc_value * const param_array, void * const user_data);
	static xmlrpc_value * c_xmlrpc_start_experiment(xmlrpc_env *   const env, xmlrpc_value * const param_array, void * const user_data);
	static xmlrpc_value * c_xmlrpc_dispose(xmlrpc_env *   const env, xmlrpc_value * const param_array, void * const user_data);	
	
};


#endif
