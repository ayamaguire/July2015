# Aya Maguire
# July 2015
# This is the main program. It just needs to be run.
# It just runs the "run" method from an instance of the class "Client".

import server
import socket
import sys
import SocketServer
import client
import os

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    
    a_client = client.Client(HOST, PORT)
    a_client.run()
