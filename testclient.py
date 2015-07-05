import socket
import sys
import datetime
import time
import multiprocessing
import logging
import os

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
    
    def run(self):
        data = "0" + str(diskinfo('/'))
        hello = "1" + str(datetime.datetime.now()) + " Connected to Server." + "\n"
        bye = "1" + str(datetime.datetime.now()) + " Disconnected from Server." + "\n"

        dur = 0.1

        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((self.host, self.port))
            sock.sendall(hello)
            time.sleep(0.1)
            sock.sendall(data + "\n")
            elapsed = 0
            while elapsed < 60*dur:
                time.sleep(30)
                elapsed = elapsed + 30
                heart = "1" + str(datetime.datetime.now()) + " Still here" + "\n"
                sock.sendall(heart)
            time.sleep(0.1)
            sock.sendall(bye)
            print "Sent data."
        except:
            print "Socket Error"

        finally:
            sock.close()


        print "Sent:    {}".format(data)
