LIBS=-lxmlrpc -lxmlrpc_util -lxmlrpc_xmlparse -lxmlrpc_xmltok -lxmlrpc_server_abyss -lpthread
OUTPUT=dummy_experiment_server
PORT=12345

all: 
	g++ -Wall -o ${OUTPUT} ${LIBS} weblabdeusto_experiment_server.cpp dummy_experiment_server.cpp

run: all
	./${OUTPUT}
