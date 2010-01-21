#ifndef WEBLAB_LIB
#define WEBLAB_LIB

struct ExperimentServer{
    char * (* start_experiment)();
    char * (* send_file)(char * encoded_file, char * fileinfo);
    char * (* send_command)(char * command);
    char * (* dispose)();
};

void launch(int port, struct ExperimentServer handlers);

#endif
