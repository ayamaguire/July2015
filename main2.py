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
