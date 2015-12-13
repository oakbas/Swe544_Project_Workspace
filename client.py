#FileName: client.py
#Author : Ozlem Akbas
#Description : SWE544 Course Project for Client Side of Internet Relay Chat Protocol

import sys
import socket
import threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Queue
import datetime


# Class Name: ReadThread
# Description : This class for processing the incoming messages to the socket and
#               deriving user friendly information from the incoming messages
class ReadThread (threading.Thread):
    def __init__(self, name, condition, csoc, threadQueue, screenQueue, userQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.nickname = ""
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue
        self.isRegisteredFlag = 0
        self.condition = condition

    def incoming_parser(self, data):

        #The case, message has less than three-character length
        if len(data) < 3:
            response = "ERR"
            condition.acquire()
            self.csoc.send(response)
            condition.release()
            return

        #The case, command root is more than three characters
        if len(data) > 3 and not data[3] == " ":
            response = "ERR"
            condition.acquire()
            self.csoc.send(response)
            condition.release()
            return

        rest = data[4:]     #get the rest of the message, no problem even if data < 4

        #The case, communication ends
        if data[0:3] == "BYE":
            if len(rest) == 0:
                response = "ERR"
                condition.acquire()
                self.csoc.send(response)
                condition.release()
                screenMsg = "Wrong message format from the server"
                self.screenQueue.put(screenMsg)
                return
            screenMsg = "Good Bye " + rest
            self.screenQueue.put(screenMsg)

        #The case, registration
        elif data[0:3] == "HEL":
            if len(rest) == 0:
                response = "ERR"
                condition.acquire()
                self.csoc.send(response)
                condition.release()
                screenMsg = "Wrong message format from the server"
                self.screenQueue.put(screenMsg)
                return
            self.isRegisteredFlag = 1
            self.nickname = rest
            screenMsg = "Registered as " + rest
            self.screenQueue.put(screenMsg)

        #The case, user registration is rejected
        elif data[0:3] == "REJ":
            if len(rest) == 0:
                response = "ERR"
                condition.acquire()
                self.csoc.send(response)
                condition.release()
                screenMsg = "Wrong message format from the server"
                self.screenQueue.put(screenMsg)
                return
            screenMsg = "Invalid or existing nickname " + rest
            self.screenQueue.put(screenMsg)

        #The case, user is not authenticated
        elif data[0:3] == "ERL":
            if len(rest) > 0:
                response = "ERR"
                condition.acquire()
                self.csoc.send(response)
                condition.release()
                screenMsg = "Wrong message format from server"
                self.screenQueue.put(screenMsg)
                return
            screenMsg = "User is not authenticated, please type /nick <user>"
            self.screenQueue.put(screenMsg)

        #The case, receiver is invalid
        elif data[0:3] == "MNO":
            if len(rest) == 0:
                response = "ERR"
                condition.acquire()
                self.csoc.send(response)
                condition.release()
                screenMsg = "Wrong message format from server"
                self.screenQueue.put(screenMsg)
                return
            screenMsg = "Invalid user " + rest
            self.screenQueue.put(screenMsg)

        #The case, there is incoming message
        elif data[0:3] == "MSG":
            if len(rest) == 0:
                response = "ERR"
                condition.acquire()
                self.csoc.send(response)
                condition.release()
                screenMsg = "Wrong message format from server"
                self.screenQueue.put(screenMsg)
                return
            splitted = rest.split(":")
            if len(splitted) != 2:
                response = "ERR"
                condition.acquire()
                self.csoc.send(response)
                condition.release()
                screenMsg = "Wrong message format from server"
                self.screenQueue.put(screenMsg)
                return
            user = splitted[0]
            usr_msg = splitted[1]
            msg = usr_msg.split(" ")
            msg = msg[1:]
            outmsg = " ".join(msg)
            response = "MOK"
            condition.acquire()
            self.csoc.send(response)
            condition.release()
            screenMsg = "*" + user + "*: " + str(outmsg)
            self.screenQueue.put(screenMsg)

        #The case, general message is received
        elif data[0:3] == "SAY":
            if len(rest) == 0:
                response = "ERR"
                condition.acquire()
                self.csoc.send(response)
                condition.release()
                screenMsg = "Wrong message format from server"
                self.screenQueue.put(screenMsg)
                return
            response = "SOK"
            condition.acquire()
            self.csoc.send(response)
            condition.release()
            splitted = rest.split(":")
            screenMsg = "<" + splitted[0] + "> " + splitted[1]
            self.screenQueue.put(screenMsg)

        #The case, message is received from server
        elif data[0:3] == "SYS":
            if len(rest) == 0:
                response = "ERR"
                condition.acquire()
                self.csoc.send(response)
                condition.release()
                screenMsg = "Wrong message format from server"
                self.screenQueue.put(screenMsg)
                return
            response = "YOK"
            condition.acquire()
            self.csoc.send(response)
            condition.release()
            screenMsg = "-Server: " + rest
            self.screenQueue.put(screenMsg)

        #The case, registered nicks are listed
        elif data[0:3] == "LSA":
            if len(rest) == 0:
                response = "ERR"
                condition.acquire()
                self.csoc.send(response)
                condition.release()
                screenMsg = "Wrong message format from server"
                self.screenQueue.put(screenMsg)
                return
            splitted = rest.split(":")
            userQueue.put(splitted)
            screenMsg = "-Server- Registered nicks: "


            for i in splitted:
                screenMsg += i + ","
            screenMsg = screenMsg[:-1]
            self.screenQueue.put(screenMsg)

        elif data[0:3] == "ERR":
            return

        elif data[0:3] == "TIC":
            if self.isRegisteredFlag:
                response = "TOC"
                condition.acquire()
                self.csoc.send(response)
                condition.release()

    def run(self):
        while True:
            data = self.csoc.recv(1024)
            self.incoming_parser(data)

# Class Name: WriteThread
# Description : This class for writing messages comes from GUI, to the socket
class WriteThread (threading.Thread):
    def __init__(self, name, condition, csoc, threadQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.threadQueue = threadQueue
        self.condition = condition

    def run(self):
        while True:
            condition.acquire()
            if self.threadQueue.qsize() > 0:
                queue_message = self.threadQueue.get()
                try:
                    temp = str(queue_message)
                    self.csoc.send(str(queue_message))
                except socket.error:
                    self.csoc.close()
                    break
            else:
                condition.wait()
            condition.release()

class ClientDialog(QDialog):

    def __init__(self, condition, threadQueue, screenQueue, userQueue):
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue
        self.userQueue = userQueue
        self.condition = condition

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
        self.userList.setWindowTitle("User List")


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
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.updateUserList)

        # update every 10 ms
        self.timer.start(10)
        self.timer2.start(10)

        # Use the vertical layout for the current window
        self.setLayout(self.vbox)

    # use this to append new message to channel with timestamp
    def cprint(self, data):
        now = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        channel_msg = now + " " + data
        self.channel.append(channel_msg)

    def updateChannelWindow(self):
        if self.screenQueue.qsize() > 0:
            queue_message = self.screenQueue.get()
            self.cprint(queue_message)

    def updateUserList(self):
        if self.userQueue.qsize() > 0:
            queue_message = self.userQueue.get()
            self.uprint(queue_message)

    def uprint(self, userlist):
        model = QStandardItemModel(self.userList)

        for user in userlist:
            item = QStandardItem(str(user))
            model.appendRow(item)

        self.userList.setModel(model)
        self.userList.show()

    def outgoing_parser(self):
        data = self.sender.text()

        if len(data) == 0:
            return

        if data[0] == "/":
            rest = data[1:].split(" ")
            command = rest[0]

            #The case, request for user registration
            if command == "nick":
                if rest[1]:
                    self.threadQueue.put("USR " + rest[1])
                else:
                    self.cprint("Local: Command Error.")

            #The case, request for registered users
            elif command == "list":
                self.threadQueue.put("LSQ")

            #The case, request for exit
            elif command == "quit":
                self.threadQueue.put("QUI")

            #The case, request for private message
            elif command == "msg":

                #Check username and msg is written by space separated
                if rest[1] and rest[2]:
                    user = rest[1]
                    msg = data[5:]
                    self.threadQueue.put("MSG " + user + ":" + msg)
                else:
                    self.cprint("Local: Command Error.")

            #The case, there is not meaningful comment after / parameter
            else:
                self.cprint("Local: Command Error.")

        #The case, request for general message
        else:
            self.threadQueue.put("SAY " + data)

        condition.acquire()
        condition.notify_all()
        condition.release()
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

threadLock = threading.Lock()
sendQueue = Queue.Queue()
screenQueue = Queue.Queue()
userQueue = Queue.Queue()

condition = threading.Condition()

app = ClientDialog(condition, sendQueue, screenQueue, userQueue)
# start threads
rt = ReadThread("ReadThread", condition, s, sendQueue, screenQueue, userQueue)
rt.start()
wt = WriteThread("WriteThread", condition, s, sendQueue)
wt.start()

app.run()

rt.join()
wt.join()

s.close()