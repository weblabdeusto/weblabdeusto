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


int 
main(int           const argc, 
     const char ** const argv) {

    struct ExperimentServer handlers;
    handlers.start_experiment = start_experiment;
    handlers.send_command     = send_command;
    handlers.send_file        = send_file;
    handlers.dispose          = dispose;

    launch(12345, handlers);

    return 0;
}
