CFLAGS=-lxmlrpc -lxmlrpc_util -lxmlrpc_xmlparse -lxmlrpc_xmltok -lxmlrpc_server_abyss -lpthread
OUTPUT=dummy_experiment_server
PORT=12345

all: dummy_experiment_server.c
	gcc -Wall -o ${OUTPUT} ${CFLAGS} dummy_experiment_server.c weblabdeusto_experiment_server.c

run: all
	./${OUTPUT} 12345
