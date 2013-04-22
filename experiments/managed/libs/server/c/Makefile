CFLAGS=-lxmlrpc_server_abyss -lxmlrpc_server -lxmlrpc_abyss  -lpthread -lxmlrpc -lxmlrpc_xmlparse -lxmlrpc_xmltok -lxmlrpc_util   
OUTPUT=dummy_experiment_server
PORT=12345

all: dummy_experiment_server.c

	gcc -c dummy_experiment_server.c weblabdeusto_experiment_server.c
	
	gcc -o ${OUTPUT} dummy_experiment_server.o weblabdeusto_experiment_server.o ${CFLAGS} 

run: all
	./${OUTPUT} 12345
