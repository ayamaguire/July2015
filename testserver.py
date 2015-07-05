import SocketServer

class TCPHandler(SocketServer.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.setup()
        self.datafile = open("data.txt", 'a')
        self.logfile = open("log.txt", 'a')   
        try:
            self.handle()
        finally:
            self.finish()

    def handle(self):
        info = self.request.recv(1024).strip()
#        self.request.sendall(self.data.upper())
        
       
        if info == "":
            self.logfile.write("Empty string received.\n")
        else: 
            if info[0] == "0":
                self.datafile.write(info + "\n")
            elif info[0] == "1":
                self.logfile.write(info)
            else:
                self.logfile.write("Received unexpected string. Status messages must begin with a 1; information sent must begin with a 0.\n")
    

if __name__=="__main__":
    HOST, PORT = "localhost", 9999

    server=SocketServer.TCPServer((HOST, PORT), TCPHandler)

    print "Starting test server"
    server.serve_forever()  
    print "Ending test server" 
