import os
import socket
import threading
import signal
import math
from source import *

debug = True

def log(message):
    if debug:
        print(message)
    else:
        f = fopen("client.log", "w+")
        f.write(message+"\n")
        f.close()

def error(message):
    log(message)
    if not debug:
        print(message)

class Client():

    def __init__(self):
        self.buffer = 512
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        port = 6677
        try:
            self.s.connect((host, port))
        except:
            print("Connection error")
            os._exit(0)
        threading.Thread(target=self.listenMessages).start()
        self.inputUser()

    def sendMessage(self, Type, Message):
        print(len(Message))
        Message = Type+"!"+Message+chr(0)
        length = len(Message)
        packets = int(math.ceil(length / self.buffer))
        cur = 0
        for i in range(packets): 
            self.s.send(Message[cur:cur+self.buffer].encode())
            cur += self.buffer

    def closeSocket(self):
        try:
            self.s.send((Type.Exit.value).encode())
        except:
            print("server unreachable")
        self.s.close()
        os._exit(0)

    def inputUser(self):
        while True:
            try:
                inp = str(input("'Quit' to leave\n'???' to send message\n:"))
            except:
                print("EOF read, input cant work")
                break
            if inp == "quit" or inp == "Quit":
                break
            else:
                self.sendMessage(Type.Message.value, inp)

    def messageHandler(self, typ, message):
        if typ == "":
            error("Unknow packet recieved : " + message)
        elif typ == Type.Exit.value:
            error("Server closed :" + message)
            self.closeSocket()
        elif typ == Type.Close.value:
            print("Kicked by server : ", message)
            self.closeSocket()
        elif typ == Type.Status.value:
            self.sendMessage(Type.Status.value, str(True))
        elif typ == Type.Message.value:
            error(message)
        elif typ == Type.Exec.value:
            message = self.ExecHandler(message)
            self.sendMessage(Type.Exec.value, message)
        else:
            try:
                typ = Type(typ)
            except:
                error("unknow type")
                typ = ""
            error("Server sent" + str(typ) + message)

    """
    for each client listen if message is sent
    """
    def listenMessages(self):
        message = ""
        while True:
            try:
                data, addr = self.s.recvfrom(self.buffer)
                data = data.decode()
                if data == "":
                    raise Exception("server off")
            except:
                error("Connection lost")
                self.closeSocket()
            # read message
            length = len(data)
            done = data[length-1] == chr(0) 
            message = message + data
            if not done:
                continue
            # analyse message
            typ , length = "", len(message)
            for i in range(length):
                if message[i] == "!":
                    typ = message[:i]
                    message = message[i+1:length-1]
                    break
            self.messageHandler(typ, message)
            message = ""

    def ExecHandler(self, message):
        arr = []
        for line in message.split("!"):
            arr.append(StrToMat(line))
        ma, mb = arr[0], arr[1]
        result = MultMatr(ma, mb)
        return MatToStr(result)

toClose = None
def signal_handler(sig, frame):
        if toClose:
            toClose.closeSocket()
        os._exit(0)
signal.signal(signal.SIGINT, signal_handler)


client = Client()
toClose = client
