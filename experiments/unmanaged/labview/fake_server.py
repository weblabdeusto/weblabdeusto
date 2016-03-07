import time
import SocketServer

class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        splitted = self.data.split('@@@')
        print "Splitted: ", splitted
        if splitted[0] == 'start':
            self.request.sendall('{ "url" : "http://localhost/this.is.working" }')
        elif splitted[0] == 'end':
            time.sleep(2)
            self.request.sendall("Ended!")
        elif splitted[0] == 'status':
            self.request.sendall("20")
        else:
            self.request.sendall("Could not understand you")

if __name__ == "__main__":
    HOST, PORT = "localhost", 20000

    class MyTCPServer(SocketServer.TCPServer):
        allow_reuse_address = True

    server = MyTCPServer((HOST, PORT), MyTCPHandler)
    print "Listening on {}:{}".format(HOST,PORT)
    server.serve_forever()
