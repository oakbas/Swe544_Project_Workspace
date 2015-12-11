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

        #The case, message has less than three-character length
        if len(data) < 3:
            response = "ERR"
            self.csock.send(response)
            return

        #The case, command root is more than three characters
        if len(data) > 3 and not data[3] == " ":
            response  = "ERR"
            self.csock.send(response)
            return

        rest = data[4:] #get the rest of the message, no problem even if data < 4

    def run(self):
        while True:
            data = self.csoc.recv(1024)
