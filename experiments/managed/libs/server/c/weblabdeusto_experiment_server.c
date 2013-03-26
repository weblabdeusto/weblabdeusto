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
// Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
//         Jaime Irurzun <jaime.irurzun@gmail.com>
//

#include <stdlib.h>
#include <stdio.h>
#ifndef WIN32
#include <unistd.h>
#endif

#include <xmlrpc-c/base.h>
#include <xmlrpc-c/server.h>
#include <xmlrpc-c/server_abyss.h>

#include "weblabdeusto_experiment_server.h"


static struct ExperimentServer weblab_handlers;


/* XML-RPC wrappers */

static xmlrpc_value * weblab_xmlrpc_test_me(xmlrpc_env * const env, xmlrpc_value * const param_array, void * const user_data) {
    char * arg;
    xmlrpc_decompose_value(env, param_array, "(s)", &arg);
    if (env->fault_occurred)
        return NULL;
    return xmlrpc_build_value(env, "s", arg);
}

static xmlrpc_value * weblab_xmlrpc_send_file_to_device(xmlrpc_env * const env, xmlrpc_value * const param_array, void * const user_data) {
    char * encoded_file;
    char * fileinfo;
    char * response;
    xmlrpc_decompose_value(env, param_array, "(ss)", &encoded_file, &fileinfo);
    if (env->fault_occurred)
        return NULL;
    response = weblab_handlers.send_file(encoded_file, fileinfo);
    return xmlrpc_build_value(env, "s", response);
}

static xmlrpc_value * weblab_xmlrpc_send_command_to_device(xmlrpc_env * const env, xmlrpc_value * const param_array, void * const user_data) {
    char * command;
    char * response;
    xmlrpc_decompose_value(env, param_array, "(s)", &command);
    if (env->fault_occurred)
        return NULL;
    response = weblab_handlers.send_command(command);
    return xmlrpc_build_value(env, "s", response);
}

static xmlrpc_value * weblab_xmlrpc_start_experiment(xmlrpc_env * const env, xmlrpc_value * const param_array, void * const user_data) {
    char * response;
    if (env->fault_occurred)
        return NULL;
    response = weblab_handlers.start_experiment();
    return xmlrpc_build_value(env, "s", response);
}

static xmlrpc_value * weblab_xmlrpc_dispose(xmlrpc_env * const env, xmlrpc_value * const param_array, void * const user_data) {
    char * response;
    if (env->fault_occurred)
        return NULL;
    response = weblab_handlers.dispose();
    return xmlrpc_build_value(env, "s", response);
}

static xmlrpc_value * weblab_xmlrpc_is_up_and_running(xmlrpc_env * const env, xmlrpc_value * const param_array, void * const user_data) {
    int response;
    if (env->fault_occurred)
        return NULL;
    response = weblab_handlers.is_up_and_running();
    return xmlrpc_build_value(env, "b", response);
}

static xmlrpc_value * weblab_xmlrpc_get_api(xmlrpc_env * const env, xmlrpc_value * const param_array, void * const user_data) {
    char * response;
    if (env->fault_occurred)
        return NULL;
    response = API_VERSION;
    return xmlrpc_build_value(env, "s", response);
}


/* Default implementations */

int default_is_up_and_running(){
    return TRUE;
}


/* Exposed functions */

void launch(int port, struct ExperimentServer handlers){
    xmlrpc_server_abyss_parms serverparm;
    xmlrpc_registry * registryP;
    xmlrpc_env env;

    weblab_handlers.is_up_and_running = handlers.is_up_and_running;
    weblab_handlers.start_experiment  = handlers.start_experiment;
    weblab_handlers.send_command      = handlers.send_command;
    weblab_handlers.send_file         = handlers.send_file;
    weblab_handlers.dispose           = handlers.dispose;

    xmlrpc_env_init(&env);

    registryP = xmlrpc_registry_new(&env);

    xmlrpc_registry_add_method( &env, registryP, NULL, "Util.test_me", &weblab_xmlrpc_test_me, NULL);
    xmlrpc_registry_add_method( &env, registryP, NULL, "Util.is_up_and_running", &weblab_xmlrpc_is_up_and_running, NULL);
    xmlrpc_registry_add_method( &env, registryP, NULL, "Util.start_experiment", &weblab_xmlrpc_start_experiment, NULL);
    xmlrpc_registry_add_method( &env, registryP, NULL, "Util.send_command_to_device", &weblab_xmlrpc_send_command_to_device, NULL);
    xmlrpc_registry_add_method( &env, registryP, NULL, "Util.send_file_to_device", &weblab_xmlrpc_send_file_to_device, NULL);
    xmlrpc_registry_add_method( &env, registryP, NULL, "Util.dispose", &weblab_xmlrpc_dispose, NULL);
	xmlrpc_registry_add_method( &env, registryP, NULL, "Util.get_api", &weblab_xmlrpc_get_api, NULL);

    serverparm.config_file_name = NULL;
    serverparm.registryP        = registryP;
    serverparm.port_number      = port;
    serverparm.log_file_name    = "xmlrpc_log";

    printf("Running XML-RPC server on port %i...\n", port);

    xmlrpc_server_abyss(&env, &serverparm, XMLRPC_APSIZE(log_file_name));
}

