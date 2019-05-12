import os
import socket 
import threading
import signal
import math
import time
from source import *

debug = True
A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
B = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


def log(message):
    if debug:
        print(message)
    else:
        f = fopen("server.log", "w+")
        f.write(message+"\n")
        f.close()

def error(message):
    if not debug:
        print(message)
    log(message)

class ClientServer:
    def __init__(self, socket, addr):
        self.s = socket
        self.addr = addr
        self.avai = True
        self.resp = []

class Server:
    """
    Constructor
    """
    def __init__(self, host = socket.gethostname(), port = 6677):
        self.buffer = 4096
        self.banList = []
        self.s = socket.socket() 
        self.clients = []

        # set up server socket
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        log('Server started!')
        try:
            self.s.bind((host, port))
        except:
            error("Server binding error")
            self.closeServer()

    """
    start server
    """
    def start(self):
        self.s.listen(5) 
        t = threading.Thread(target=self.listenConnections)
        t.start()
        self.userInput()
        self.closeServer()

    """
    wait for new connection and link listenmessage thread for each new connection
    """
    def listenConnections(self):
        while True:
            c, addr = self.s.accept()
            client = ClientServer(c, addr)
            if addr[0] in self.banList:
                self.sendMessage(client, Type.Close.value, "banned")
                client.s.close()
                log("banned " + str(addr) + " blocked")
                continue
            self.clients.append(client)
            log("got connection from " + str(addr))
            t = threading.Thread(target=self.listenMessages,args=[client])
            t.start()

    """
    handle recieved message
    """
    def messageHandler(self, client, typ, message):
        if typ == Type.Exit.value or typ == Type.Close.value:
            self.removeClient(client.addr)
            error("Client disconned:" + message)
        elif typ == Type.Status.value:
            print(client.addr, "replied to status command")
        elif typ == Type.Message.value:
            error(str(client.addr) + " sent : "+ message)
        elif typ == Type.Exec.value:
            client.resp.append(message)
            client.avai= True
        else:
            try:
                typ = Type(typ)
            except:
                error("unknow type")
                typ = ""
            error("Client " + str(client.addr) + " sent : " + str(typ) + message)

    """
    for each client listen if message is sent
    """
    def listenMessages(self, client):
        message = ""
        while True:
            try:
                data, addr = client.s.recvfrom(self.buffer)
                data = data.decode()
                if data == "":
                    raise Exception("")
            except:
                self.removeClient(client.addr)
                log(str(client.addr) + " connection lost")
                break
            # read message
            length = len(data)
            done = data[length-1] == chr(0)
            message = message + data
            if not done:
                continue 
            # analyse message
            typ, length = "", len(message)
            for i in range(length):
                if message[i] == "!":
                    typ = message[:i]
                    message = message[i+1:length-1]
                    break
            self.messageHandler(client, typ, message)
            message = ""

    """
    get client socket by address
    """
    def findClient(self, addr):
        for val in self.clients:
            if val.addr == addr:
                return val

    """
    remove client from client array
    """
    def removeClient(self, addr):
        for i in range(len(self.clients)):
            if self.clients[i].addr == addr:
                self.clients.pop(i)
                break

    """
    kick client and remove
    """
    def kickClientByAddr(self, addr):
        client = self.findClient(addr)
        self.kickCkient(client)

    """
    kick client and remove
    """
    def kickClient(self, client, mes = "kicked"):
        self.sendMessage(client, Type.Close.value, mes)
        client.s.close()
        self.removeClient(client.addr)

    def sendMessageByAddr(self, addr, Type, Message):
        client = self.findClient(addr)
        self.sendMessage(client, Type, Message)

    def sendMessage(self, client, Type, Message):
        Message = Type+"!"+Message+chr(0)
        length = len(Message)
        packets = int(math.ceil(length / self.buffer))
        cur = 0
        for i in range(packets):
            client.s.send(Message[cur:cur+self.buffer].encode())
            cur += self.buffer

    """
    close server and program
    """
    def closeServer(self):
        log("Closing server")
        for client in self.clients:
            self.sendMessage(client, Type.Exit.value, "Server closed")
        self.s.close()
        os._exit(0)

    """
    read input of user
    """
    def userInput(self):
        print("press help to see available commands")
        while True:
            inp = str(input(":"))
            inp = inp.lower()
            length = len(self.clients)
            if inp == "help":
                print("'Quit' to leave\n'Exec' to launch program\n'status' to see clients\n:")
            elif inp == "quit":
                self.closeServer()
            elif inp==  "status":
                self.clientActions() if length > 0 else error("No clients")
            elif inp == "exec" or inp == "Exec":
                self.execMatrix(A, B)
            else:
                error("No valid actions")

    def clientActions(self):
        client = -1
        while True:
            arr, i = [], 1
            print("Select client\n(0 to quit)")
            for val in self.clients:
                print(i, ":", val.addr)
                arr.append(val)
                i += 1
            try:
                client = int(input())
            except:
                client = -1
            if client == 0:
                return
            elif client > 0 and client < i:
                client = arr[client-1]
                break
            else:
                print("Invalid input")
        action = -1
        while True:
            i = 1
            print("Select an action\n(0 to quit)")
            print(i, ":", "Send Message")
            i += 1
            print(i, ":", "Kick User")
            i+= 1
            print(i, ":", "Ban User")
            i+=1
            print(i, ":", "check connection")
            i+=1
            try:
                action = int(input())
            except:
                action = -1
            if action == 0:
                return
            elif action > 0 and action < i:
                break
        else:
            print("Invalid choice")
        if action == 1:
            print("enter message:")
            mes = str(input())
            self.sendMessage(client, Type.Message.value, mes)
        elif action == 2:
            self.kickClient(client)
        elif action == 3:
            self.banList.append(client.addr[0])
            toKick = []
            for client in self.clients:
                if client.addr[0] in self.banList:
                    toKick.append(client)
            for client in toKick:
                self.kickClient(client, "banned")
        elif action == 4:
            self.sendMessage(client, Type.Status.value, "")

    def exec_send(self, typ, count = 3, messages = [], sleep = 1/5):
        arr = []
        try:
            i = 0
            while i < count:
                if self.clients[i].avai and self.clients[i].resp == []:
                    arr.append([self.clients[i], messages[i], i])
                    i += 1
        except:
            error("Not enough clients")
            return -1
        for val in arr:
            client, message = val[0], val[1]
            self.sendMessage(client, typ, message)
            client.avai = False
        result = [None] * count
        done = False
        while not done:
            i = 0
            length = len(arr)
            while i < length:
                val = arr[i]
                if val[0].avai:
                    result[val[2]] = val[0].resp[0]
                    arr.pop(i)
                    length -= 1
                else:
                    i += 1
            done = arr == []
            time.sleep(sleep)
        return result

    def execMatrix(self, ma, mb):
        mbWidth = len(mb[0])
        mbHeight = len(mb)
        maWidth = len(ma[0])
        if mbHeight != maWidth:
            error("uncompatible matrixes")
            return
        messages = []
        a = MatToStr(ma) + "!"
        for i in range(mbWidth):
            mbi = []
            for j in range(mbHeight):
                mbi.append([mb[j][i]])
            messages.append(a + MatToStr(mbi))
        result = self.exec_send(Type.Exec.value, mbWidth, messages)
        mat = StrToMat(result[0])
        for i in range(1, len(result)):
            AddMat(mat, StrToMat(result[i]))
        print(mat)

# if SIGINT sent, close server
toClose = None
def signal_handler(sig, frame):
    error("Closing badly the server")
    if toClose:
        toClose.closeServer()
    os._exit(0)
signal.signal(signal.SIGINT, signal_handler)


sock = Server()
toClose = sock
sock.start()


