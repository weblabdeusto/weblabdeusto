

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

#include "weblabdeusto_experiment_server.hpp"

#include <iostream>


ExperimentServer::ExperimentServer()
{
	
}

/* static */
xmlrpc_value * ExperimentServer::c_xmlrpc_start_experiment( xmlrpc_env * const env, xmlrpc_value * const param_array, void * user_data )
{
	if (env->fault_occurred)
		return NULL;
	
	ExperimentServer * _this = (ExperimentServer*)user_data;
		
	std::string const & ret = _this->onStartExperiment();
	return xmlrpc_build_value(env, "s", ret.c_str());
}

/* static */
xmlrpc_value * ExperimentServer::c_xmlrpc_test_me(xmlrpc_env *   const env, xmlrpc_value * const param_array, void * const user_data) {
    char * arg;
    xmlrpc_decompose_value(env, param_array, "(s)", &arg);
    if (env->fault_occurred)
        return NULL;
    return xmlrpc_build_value(env, "s", arg);
}

/* static */
xmlrpc_value * ExperimentServer::c_xmlrpc_send_file_to_device(xmlrpc_env *   const env, xmlrpc_value * const param_array, void * const user_data) {
    char * encoded_file;
    char * fileinfo;

    xmlrpc_decompose_value(env, param_array, "(ss)", &encoded_file, &fileinfo);
    if (env->fault_occurred)
        return NULL;

	ExperimentServer * _this = (ExperimentServer*)user_data;

	std::string const & ret = _this->onSendFile(encoded_file, fileinfo);
    return xmlrpc_build_value(env, "s", ret.c_str());
}

/* static */ 
xmlrpc_value * ExperimentServer::c_xmlrpc_send_command_to_device(xmlrpc_env *   const env, xmlrpc_value * const param_array, void * const user_data) {
    char * command;

    xmlrpc_decompose_value(env, param_array, "(s)", &command);
    if (env->fault_occurred)
        return NULL;

	ExperimentServer * _this = (ExperimentServer*)user_data;

	std::string const & ret = _this->onSendCommand(command);

    return xmlrpc_build_value(env, "s", ret.c_str());
}

/* static */ 
xmlrpc_value * ExperimentServer::c_xmlrpc_dispose(xmlrpc_env *   const env, xmlrpc_value * const param_array, void * const user_data) {

    if (env->fault_occurred)
        return NULL;

	ExperimentServer * _this = (ExperimentServer*)user_data;

	std::string const & ret = _this->onDispose();

    return xmlrpc_build_value(env, "s", ret.c_str());
}


void ExperimentServer::launch(unsigned short port, std::string const & log_file)
{
	xmlrpc_server_abyss_parms serverparm;
	xmlrpc_registry * registryP;
	xmlrpc_env env;

	xmlrpc_env_init(&env);

	registryP = xmlrpc_registry_new(&env);

	// We pass our this pointer when registering the callbacks.
	xmlrpc_registry_add_method( &env, registryP, NULL, "Util.test_me", &ExperimentServer::c_xmlrpc_test_me, this);
	xmlrpc_registry_add_method( &env, registryP, NULL, "Util.start_experiment", &ExperimentServer::c_xmlrpc_start_experiment, this);
	xmlrpc_registry_add_method( &env, registryP, NULL, "Util.dispose", &ExperimentServer::c_xmlrpc_dispose, this);
	xmlrpc_registry_add_method( &env, registryP, NULL, "Util.send_command_to_device", &ExperimentServer::c_xmlrpc_send_command_to_device, this);
	xmlrpc_registry_add_method( &env, registryP, NULL, "Util.send_file_to_device", &ExperimentServer::c_xmlrpc_send_file_to_device, this);

	serverparm.config_file_name = NULL;
	serverparm.registryP        = registryP;
	serverparm.port_number      = port;
	serverparm.log_file_name    = 
		( log_file.empty() ? 0 : log_file.c_str() );

	std::cout << "Running XML-RPC server on port " << port 
		<< "..." << std::endl;

	xmlrpc_server_abyss(&env, &serverparm, XMLRPC_APSIZE(log_file_name));
}
