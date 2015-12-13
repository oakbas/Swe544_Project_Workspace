#FileName: client.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Client Side of Internet Relay Chat Protocol

import sys
import socket
import threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
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
        #TODO screen queue

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

        rest = data[4:]     #get the rest of the message, no problem even if data < 4

        #The case, communication ends
        if data[0:3] == "BYE":
            if len(rest) == 0:
                response = "ERR"
                screenMsg = "Wrong message format from the server"
                return
            #ToDo: Check the registered user name in rest data
            screenMsg = "Good Bye " + rest

        #The case, registration
        if data[0:3] == "HEL":
            if len(rest) == 0:
                response = "ERR"
                screenMsg = "Wrong message format from the server"
                return
            #ToDo: Check the registered user name is true
            screenMsg = "Registered as" + rest

        #The case, user registration is rejected
        if data[0:3] == "REJ":
            if len(rest) == 0:
                response = "ERR"
                screenMsg = "Wrong message format from the server"
                return
            screenMsg = "Invalid or existing nickname " + rest

        #The case, user is not authenticated
        if data[0:3] == "ERL":
            if len(rest) > 0:
                response = "ERR"
                screenMsg = "Wrong message format from server"
                return
            screenMsg = 'User is not authenticated, please type /nick <user>'

        #The case, receiver is invalid
        if data[0:3] == "MNO":
            if len(rest) == 0:
                response = "ERR"
                screenMsg = "Wrong message format from server"
                return
            screenMsg = "Invalid user " + rest

        #The case, there is incoming message
        if data[0:3] == "MSG":
            if len(rest) == 0:
                response = "ERR"
                screenMsg = "Wrong message format from server"
                return
            splitted = rest.split(":")
            if len(splitted) != 2:
                response = "ERR"
                screenMsg = "Wrong message format from server"
                return
            user = splitted[0]
            msg = splitted[1]
            screenMsg = "*" + user + "*: " + msg
            response = "MOK"

        #The case, general message is received
        if data[0:3] == "SAY":
            if len(rest) == 0:
                response = "ERR"
                screenMsg = "Wrong message format from server"
                return
            screenMsg = "General message: " + rest
            response = "SOK"

        #The case, message is received from server
        if data[0:3] == "SYS":
            if len(rest) == 0:
                response = "ERR"
                screenMsg = "Wrong message format from server"
                return
            screenMsg = "-Server: " + rest
            response = "YOK"

        #The case, registered nicks are listed
        if data[0:3] == "LSA":
            if len(rest) == 0:
                response = "ERR"
                screenMsg = "Wrong message format from server"
                return
            splitted = rest.split(":")
            msg = "-Server- Registered nicks: "

            for i in splitted:
                msg += i + ","
            msg = msg[:-1]

    def run(self):
        while True:
            data = self.csoc.recv(1024)
            #ToDo it is just sceletal code

# Class Name: WriteThread
# Description : This class for writing messages comes from GUI, to the socket
class WriteThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.threadQueue = threadQueue
    def run(self):
        if self.threadQueue.qsize() > 0:
            queue_message = self.threadQueue.get()
            #ToDo it is just sceletal code
            try:
                self.csoc.send(queue_message)
            except socket.error:
                self.csoc.close()
                #break

class ClientDialog(QDialog):

    def __init__(self, threadQueue, screenQueue):
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue

        # create a Qt application --- every PyQt app needs one
        self.qt_app = QApplication(sys.argv)

        # Call the parent constructor on the current object
        QDialog.__init__(self, None)

        # Set up the window
        self.setWindowTitle('IRC Client')
        self.setMinimumSize(500, 200)
        self.resize(640, 480)

        # Add a vertical layout
        self.vbox = QVBoxLayout()
        self.vbox.setGeometry(QRect(10, 10, 621, 461))

        # Add a horizontal layout
        self.hbox = QHBoxLayout()

        # The sender textbox
        self.sender = QLineEdit("", self)

        # The channel region
        self.channel = QTextBrowser()
        self.channel.setMinimumSize(QSize(480, 0))

        # The send button
        self.send_button = QPushButton('&Send')

        # The users' section
        self.userList = QListView()

        # Connect the Go button to its callback
        self.send_button.clicked.connect(self.outgoing_parser)

        # Add the controls to the vertical layout
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)
        self.hbox.addWidget(self.channel)
        self.hbox.addWidget(self.userList)

        # start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateChannelWindow)

        # update every 10 ms
        self.timer.start(10)

        # Use the vertical layout for the current window
        self.setLayout(self.vbox)

    def cprint(self, data):
        self.channel.append(data)


    def updateChannelWindow(self):
        if self.screenQueue.qsize() > 0:
            queue_message = self.screenQueue.get()
            # self.channel.append(...)

    #ToDO: GUI part will be implemented after Qt installation
    def outgoing_parser(self):
        #ToDo: Implement GUI data to outgoing parser
        data = self.sender.text()
        if len(data) == 0:
            return
        if data[0] == "/":
            command = data[1:]

            #The case, request for registered users
            if command == "list":
                self.threadQueue.put = "LSQ"

            #The case, request for exit
            elif command == "quit":
                self.threadQueue.put = "QUI"

            #The case, request for private message
            elif command == "msg":
                rest = data[5:]
                splitted = rest.split(" ")

                #Check username and msg is written by space separated
                if len(splitted) != 2:
                    self.cprint("Local: Command Error.")
                    return
                user = splitted[0]
                msg = splitted[1]

                self.threadQueue.put = "MSG " + user + ":" + msg
            #The case, there is not meaningful comment after / parameter
            else:
                self.cprint("Local: Command Error.")
                return

        #The case, request for general message
        else:
            self.threadQueue.put("SAY " + data)
        self.sender.clear()

    #Run the app and show the main form
    def run(self):
        self.show()
        self.qt_app.exec_()

# Connect to the server
s = socket.socket()
host = "178.233.19.205"
port = 12345
s.connect((host,port))
print s.recv(1024)      #To check server connection will be deleted

sendQueue = Queue.Queue()
screenQueue = Queue.Queue()
app = ClientDialog(sendQueue, screenQueue)
app.run()