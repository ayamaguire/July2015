import socket
import sys
import datetime
import time
import multiprocessing
import logging
import os

dur = 0.2 
 
def diskinfo(path):
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    system_info = [total, used, free]
    return system_info

class TestClient():
    def __init__(self, host, port):    
        self.host = host
        self.port = port
        self.queue = multiprocessing.Queue()
    
    def dataqueue(self):
        elapsed = 0
        while elapsed < 60*dur:
            time.sleep(10)
            data = "0" + str(datetime.datetime.now()) + " " + str(diskinfo('/'))
            self.queue.put(data)
            elapsed = elapsed + 10

    def heartbeats(self):
        hello = "1" + str(datetime.datetime.now()) + " Connected to Server." + "\n"
        bye = "1" + str(datetime.datetime.now()) + " Disconnected from Server." + "\n"
        self.queue.put(hello)
        elapsed = 0
        while elapsed < 60*dur:
            time.sleep(30)
            elapsed = elapsed + 30
            heart = "1" + str(datetime.datetime.now()) + " Still here" + "\n"
            self.queue.put(heart)
        self.queue.put(bye)

    def datasend(self):
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print "Sending Data to the Server."
            sock.connect((self.host, self.port))
            i = 1
            while i < 2:
                tosend = self.queue.get()
                sock.sendall(tosend + "\n")
                i = i + 1
            print "Sent data."
        except:
            print "Could not send data."
        finally:
            sock.close()

    def run(self):
        qdata = multiprocessing.Process(target = self.dataqueue)
        sdata = multiprocessing.Process(target = self.datasend)
        qheart = multiprocessing.Process(target = self.heartbeats)
        qdata.start()
        qheart.start()
        print "Check"
        sdata.start()
