# Aya Maguire
# July 2015
# Coding project for SolidFire employment candidacy

import socket
import threading
import SocketServer
import sys
import datetime
import time
import multiprocessing
import os

    ###############################
    # diskinfo and fileinfo
    #
    # These functions are just helpers so they don't need to be in the class.
    # diskinfo measures the total, used, and freespace on a directory.
    # fileinfo just measures the size of a file.
    ###############################

def diskinfo(path):
    dire = os.statvfs(path)
    free = dire.f_bavail * dire.f_frsize
    total = dire.f_blocks * dire.f_frsize
    used = (dire.f_blocks - dire.f_bfree) * dire.f_frsize
    system_info = total, used, free
    return system_info

def fileinfo(path):
    filesize = os.stat(path)
    return filesize.st_size

class Client(object):

    ###############################
    # __init__
    #
    # This method sets all the parameters that were passed in by 
    # main.py. It also initializes the queue I use to pass info 
    # between the methods.
    ###############################

    def __init__(self, host, port, direc, cid, chunksize, msize, dur):    
        self.host = host
        self.port = port
        self.direc = direc
        self.cid = cid
        self.chunksize = chunksize
        self.dur = dur
        self.msize = msize
        self.queue = multiprocessing.Queue()
        self.freestart = 0
        self.freeend = 0
   
    ###############################
    # dataqueue
    #
    # This method reads local system information, writes it as a string,
    # and puts that string onto the queues. It does so every 10 seconds
    # until the time limit has been reached.
    ###############################

    def dataqueue(self):
        print str(datetime.datetime.now()) + " Client #" + str(self.cid) + " Measuring on directory " + str(self.direc)
        data = "0" + str(datetime.datetime.now()) + " " + str(self.direc) + " Total Disk Space is: " + str(diskinfo(self.direc)[0]) + " bytes."
        self.queue.put(data)
        elapsed = 0
        while elapsed < self.dur:
            time.sleep(10)
            data = "0" + str(datetime.datetime.now()) + " " + str(self.direc) + " Used, Free: "+ str(diskinfo(self.direc)[1]) + ", " + str(diskinfo(self.direc)[2]) + " bytes."
            self.queue.put(data)
            elapsed = elapsed + 10
        self.queue.put("9")

    ###############################
    # randomdata
    #
    # This method writes random data to a a file so that the memory usage can be
    # monitored by the dataqueue method. It writes in "chunksize" amounts every 
    # ten seconds (an arbitrary choice I made). It stops when the program has been
    # running for its set length of time (minus 11 seconds so that data isn't 
    # written after the last status message is sent).
    ###############################


    def randomdata(self):
        if self.direc == "/":
            rdatapath = str(self.cid) + "rdata0.txt"
        else:
            rdatapath = str(self.direc) + str(self.cid) + "rdata0.txt"
        rdatafile = open(rdatapath, 'a')
        size = fileinfo(rdatapath)
        self.freestart = str(diskinfo(self.direc)[2])
        i = 0
        elapsed = 0
        while elapsed < self.dur-11:
            rdatafile.write(os.urandom(self.chunksize))
            rdatafile.flush()
            size = fileinfo(rdatapath)
            time.sleep(10)
            elapsed = elapsed + 10
            if size + self.chunksize > self.msize:
                ro = "1" + str(datetime.datetime.now()) + " Client #" + str(self.cid) + " Rolling over random data file." 
                print ro[1:]
                self.queue.put(ro)
                i = i + 1
                rdatafile.flush()
                rdatafile.close()
                if self.direc == "/":
                    rdatapath = str(self.cid) + "rdata" + str(i) + ".txt"
                else:
                    rdatapath = str(self.direc) + str(self.cid) + "rdata" + str(i) + ".txt"
                rdatafile = open(rdatapath, 'a')
        rdatafile.flush()
        rdatafile.close()
        self.freeend = str(diskinfo(self.direc)[2])

    ###############################
    # heartbeats
    #
    # This method writes out status information and puts those statuses on the
    # Server queue (self.queue).
    ###############################

    def heartbeats(self):
        hello = "1" + str(datetime.datetime.now()) + " Client #" + str(self.cid) + " Connected to Server."
        self.queue.put(hello)
        elapsed = 0
        while elapsed < self.dur:
            time.sleep(5)
            elapsed = elapsed + 5 
            heart = "1" + str(datetime.datetime.now()) + " Client #" + str(self.cid) + " Still here" 
            self.queue.put(heart)

    ###############################
    # datasend
    #
    # This method reads strings off of the queue and sends them to the Server.
    # If something goes wrong it prints a message saying so. When it's done,
    # it closes the socket.
    ###############################


    def datasend(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        while True:
            try:
                tosend = self.queue.get()
                time.sleep(0.1)
                if tosend == "9":
                    bye = "1" + str(datetime.datetime.now()) + " Client #" + str(self.cid) + " Disconnected from Server. \n"
                    self.sock.sendall(bye)
                    time.sleep(0.1)
                    self.sock.sendall("4" + str(self.freestart))
                    time.sleep(0.1)
                    self.sock.sendall("5" + str(self.freeend))
                    time.sleep(0.1)
                    self.sock.sendall("6" + str(self.direc))
                    time.sleep(0.1)
                    self.sock.sendall("3")
                    break
                self.sock.sendall(tosend + "\n")
            except:
                print "Could not send data."
            finally:
                pass
        self.sock.close()

                

    ###############################
    # run
    #
    # This method takes the previous four methods and runs them as separate
    # threads.
    ###############################

    def run(self):
        qdata = threading.Thread(target = self.dataqueue)
        sdata = threading.Thread(target = self.datasend)
        qheart = threading.Thread(target = self.heartbeats)
        rdata = threading.Thread(target = self.randomdata)
        qdata.start()
        qheart.start()
        rdata.start()
        sdata.start()



    ###############################
    # ThreadedTCPRequestHandler and ThreadedTCPServer
    #
    # These classes inherit from the built-in SocketServer library. Essentially,
    # because a threaded socket server already existed, I just wrote over the
    # handle method to organize the messages as they came in.
    #
    # Example code which helped choose this class was found at:
    # https://docs.python.org/2/library/socketserver.html
    ###############################

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    ###############################
    # handle
    # 
    # This method got a little long, so I'll break it down.
    # First we set the data file, where we store system information, and the logfile,
    # where hearbeats and other connection information is written.
    #
    # The next part decides what to do with a message based on its flag. The flags
    # (first symbol in the string) are:
    # 0 - System information, write to datafile.
    # 1 - Connection information, write to logfile.
    # 3 - This is the last message! Exit the while loop.
    # 4 - The amount of free space on the client's directory at the start
    # 5 - The amounf of free space on the client's directory at the end
    # 6 - The client's directory
    #
    # When all messages have been received, the files are closed and some system
    # information is printed.
    ###############################

    def handle(self):
        while True:
            self.datafile = open("sysdata.txt", 'a')
            self.logfile = open("log.txt", 'a')
            direc = ""
            info = "init"
            while info != "":
                info = str(self.request.recv(1024))
                if info == "":
                    self.logfile.write(str(datetime.datetime.now()) + " All communications received on directory" + str(direc) + " \n")
                else:
                    if info[0] == "0":
                        self.datafile.write(info[1:])
                        self.datafile.flush()
                    elif info[0] == "1":
                        self.logfile.write(info[1:])
                        self.logfile.flush()
                    elif info[0] == "4":
                        freestart = info[1:]
                    elif info[0] == "5":
                        freeend = info[1:]
                    elif info[0] == "6":
                        direc = info[1:]
                    else:
                        if info == "3":
                            break
                        else:
                            self.logfile.write(str(datetime.datetime.now()) + " Received unexpected string. Status messages must begin with a 1; information sent must begin with a 0.\n")
                            self.logfile.flush()
            sys.stdout.flush()
            self.datafile.flush()
            self.logfile.flush()
            self.datafile.close()
            self.logfile.close()
            break
        print str(int(freestart) - int(freeend)) + " bytes changed on directory " + str(direc) + " during monitoring."
        print "Closing socket..."


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass



if __name__ == "__main__":

    ###############################
    # Input Parameters
    #
    # The following parameters are taken from the user at the command line:
    # cnum - How many clients to run at once
    # filepath - Which directory to monitor system usage on. You will be reprompted if
    #           the filepath is not in the right form (/Users/name/ or / for current directory)
    # msize - The maximum file size for the random data files
    # dur - How long to run the clients
    # chunksize - What size chunks to write random data to. The user will be reprompted if
    # a number less than 10 is chosen, or if the chunk size is too small to allow the random
    # data file to roll over to a new file twice.
    ###############################

    cnum = int(raw_input("How many directories should be monitored (how many clients should we run)?"))
    filepath = ["1" for i in range(cnum)]
    for i in range(cnum):
        while filepath[i][0] != '/' or filepath[i][-1] != '/':
            filepath[i] = raw_input("For client number " + str(i) + ", What directory should be monitored?")

    msize = float(raw_input("Enter the maximum random data file size in MB. Between 30 and 100 is OK."))
    dur = float(raw_input("Enter how long to run in minutes."))

    chunksize = [1 for i in range(cnum)]
    for i in range(cnum):
        chunksize[i] = int(raw_input("Enter the chunksize in MB for directory number " +  str(i) + "."))
        while chunksize[i] < 10:
            chunksize[i] = int(raw_input("Chunksize must be larger than 10. \n" + "Enter the chunksize in MB for directory number " +  str(i) + "."))
        while 6*(dur-1) + 4 < 2 * (msize/chunksize[i]):
            chunksize[i] = int(raw_input("Chunksize must be large enough to allow the random data logs to rollover twice. \n" + "Enter the chunksize in MB for directory number " +  str(i) + "."))

    # This next part sets up the server.
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server started."


    # For each directory given in the above parameters, start a client with the given
    # input parameters:

    for i in range(len(filepath)):
        a_client = Client(ip, port, filepath[i], i, chunksize[i]*1000000, msize*1000000, 60*dur)
        a_client.run()

    server.shutdown()
