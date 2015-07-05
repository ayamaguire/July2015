# Aya Maguire
# July 2015
# This is the code that opens a local client to read data off the system.

import socket
import sys
import datetime
import time
import multiprocessing
import logging
import os

dur = float(raw_input("Enter how long to run in minutes.")) 
msize = float(raw_input("Enter the maximum local log file size in kb. (0.5 is a good place to start for now."))
 
def diskinfo(path):
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    system_info = ["total = " + str(total), "used = " + str(used), "free = " + str(free)]
    return system_info

def fileinfo(path):
    filesize = os.stat(path)
    return filesize.st_size

class Client():

    ###############################
    # __init__
    # This method sets the port and host number that are given in the main.py
    # program. It also initializes the two queues I use to pass information:
    # "self.queue" is used to collect all the information that is sent to the
    # Server, while "dataq" is used to transfer information between methods in
    # the client.
    ###############################

    def __init__(self, host, port):    
        self.host = host
        self.port = port
        self.queue = multiprocessing.Queue()
        self.dataq = multiprocessing.Queue()
   
    ###############################
    # dataqueue
    #
    # This method reads local system information, writes it as a string,
    # and puts that string onto the queues.
    ###############################

    def dataqueue(self):
        elapsed = 0
        while elapsed < 60*dur:
            time.sleep(10)
            data = "0" + str(datetime.datetime.now()) + " " + str(diskinfo('/'))
            self.queue.put(data)
            self.dataq.put(data)
            elapsed = elapsed + 10

    ###############################
    # loclog
    #
    # This method takes the data handed to it by the dataque method (off
    # self.dataq) and writes it to a local log file. It also writes a string
    # when the log rolls over and puts this string on the queue to send to the
    # Server (self.queue). 
    ###############################

    def loclog(self):
        elapsed = 0
        loclogfile = open("loclog0.txt", 'a')
        size = fileinfo('loclog0.txt')
        i = 0
        while elapsed < dur*60:
            time.sleep(10)
            data = "Logging information. \n The local filesystem information is \n" + str(datetime.datetime.now()) + " " + str(diskinfo('/'))
            loclogfile.write(data + "\n")
            loclogfile.flush()
            elapsed = elapsed + 10
            size = fileinfo('loclog' + str(i) + ".txt")
            print size
            if size > (msize * 1000):
                ro = "1" + str(datetime.datetime.now()) + " Rolling over local log file." 
                print ro[1:]
                self.queue.put(ro)
                i = i + 1
                loclogfile.flush()
                loclogfile.close()
                loclogfile = open("loclog" + str(i) + ".txt", 'a')
        loclogfile.flush()
        loclogfile.close()

    ###############################
    # heartbeats
    #
    # This method writes out status information and puts those statuses on the
    # Server queue (self.queue).
    ###############################

    def heartbeats(self):
        hello = "1" + str(datetime.datetime.now()) + " Connected to Server."
        bye = "1" + str(datetime.datetime.now()) + " Disconnected from Server."
        self.queue.put(hello)
        elapsed = 0
        while elapsed < 60*dur:
            time.sleep(5)
            elapsed = elapsed + 5 
            heart = "1" + str(datetime.datetime.now()) + " Still here" 
            self.queue.put(heart)
        self.queue.put(bye)

    ###############################
    # datasend
    #
    # This method reads strings off of the queue and sends them to the Server.
    ###############################

    def datasend(self):
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print "Sending Data to the Server."
            sock.connect((self.host, self.port))
            i = 1
            while i < 18*dur + 2:
                tosend = self.queue.get()
                sock.sendall(tosend + "\n")
                time.sleep(0.1)
                i = i + 1
            print "Sent data."
            sock.sendall("3")
        except:
            print "Could not send data."
        finally:
            sock.close()
    
    ###############################
    # run
    #
    # This method takes the previous four methods and runs them as separate
    # threads.
    ###############################

    def run(self):
        qdata = multiprocessing.Process(target = self.dataqueue)
        sdata = multiprocessing.Process(target = self.datasend)
        qheart = multiprocessing.Process(target = self.heartbeats)
        ldata = multiprocessing.Process(target = self.loclog)
        qdata.start()
        qheart.start()
        ldata.start()
        sdata.start()
