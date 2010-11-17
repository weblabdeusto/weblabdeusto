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
// Author: Luis Rodr�guez <4lurodri@rigel.deusto.es>
//         Jaime Irurzun <jaime.irurzun@gmail.com>
//

#include "weblabdeusto_experiment_server.h"

char * start_experiment(){
    return "ok";
}

char * send_file(char * encoded_file, char * fileinfo){
    return "ok";
}

char * send_command(char * command){
    return "ok";
}

char * dispose(){
    return "ok";
}

int main(int const argc, const char ** const argv) {

    struct ExperimentServer handlers;
    handlers.start_experiment  = start_experiment;
    handlers.send_command      = send_command;
    handlers.send_file         = send_file;
    handlers.dispose           = dispose;

    /* For optional methods, you can use the default
       implementation by pointing to default_<handler-name> */
    handlers.is_up_and_running = default_is_up_and_running;

    launch(12345, handlers);

    return 0;
}
