#FileName: client.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Client Side of Internet Relay Chat Protocol

import sys
import socket
import threading
import Queue
import time


# Class Name: ReadThread
# Description : This class for processing the incoming messages to the socket and
#               deriving user friendly information from the incoming messages
class ReadThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue, screenQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.nickname = ""
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue

    def incoming_parser(self, data):
        #ToDo: Implement Client Incoming Parser
        if len(data) == 0:
            return
    def run(self):
        while True:
            data = self.csoc.recv(1024)
