# Aya Maguire
# July 2015
# This is the code that sets up the Server.

import socket
import sys
import datetime

class TCPHandler:
    def run(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.bind((self.host, self.port))
            print 'Socket bind complete.'
        except socket.error as msg:
            print 'Bind failed. Error Code : '+ str(msg[0]) + 'Message'+ msg[1]
            sys.exit()

        self.socket.listen(5)
        wc = 2

        while wc == 2:
            self.datafile = open("data.txt", 'a')
            self.logfile = open("log.txt", 'a')
            conn, addr = self.socket.accept()
            print 'Connected with '+ addr[0] + ':' + str(addr[1])
            info = "init"
            while info != "":
                info = conn.recv(1024)
                if info == "":
                    self.logfile.write(str(datetime.datetime.now()) + " All communications received. \n")
                else:
                    if info[0] == "0":
                        self.datafile.write(info[1:])
                        self.datafile.flush()
                    elif info[0] == "1":
                        self.logfile.write(info[1:])
                        self.logfile.flush()
                    else:
                        if info == "3":
                            wc = 3
                        else:
                            self.logfile.write(str(datetime.datetime.now()) + " Received unexpected string. Status messages must begin with a 1; information sent must begin with a 0.\n")
                            self.logfile.flush()
            sys.stdout.flush()
            self.datafile.flush()
            self.logfile.flush()
            self.datafile.close()
            self.logfile.close()

        print "Closing Socket."
        self.socket.close()
    

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    server = TCPHandler()

    print "Starting the server"
    server.run(HOST, PORT)
