LIBS=-lxmlrpc_server_abyss++ -lxmlrpc_server++ -lxmlrpc_server_abyss -lxmlrpc_server -lxmlrpc_abyss  -lpthread -lxmlrpc++ -lxmlrpc -lxmlrpc_xmlparse -lxmlrpc_xmltok -lxmlrpc_util
OUTPUT=dummy_experiment_server
PORT=12345

all: 
	g++ -c weblabdeusto_experiment_server.cpp dummy_experiment_server.cpp
	
	g++ -o ${OUTPUT} weblabdeusto_experiment_server.o dummy_experiment_server.o -lxmlrpc_server_abyss++ -lxmlrpc_server++ -lxmlrpc_server_abyss -lxmlrpc_server -lxmlrpc_abyss  -lpthread -lxmlrpc++ -lxmlrpc -lxmlrpc_xmlparse -lxmlrpc_xmltok -lxmlrpc_util   

run: all
	./${OUTPUT}
