import socket
import sys
import threading
import select
from tkinter import messagebox

lock = threading.Lock()

class ChatServer:
    def __init__(self, host, port):
        self.clients = []
        self.nicks = ['ALL']
        self.open_socket(host,port)
        self.dict = {}
    def open_socket(self, host, port):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind( (host, port) )
            self.server.listen(5)
        except socket.error:
            messagebox.showerror("ERROR", "Busy host by other server")
            self.server.close()

    def run(self):
        while True:
            clientSocket, clientAddr = self.server.accept()
            print("Zgloszenie klienta, adres: {0}".format(clientAddr))
            lock.acquire()
            self.clients.append(clientSocket)
            sendList = "LIST;"
            for i in range(len(self.nicks)):
                if(self.nicks[i] != 'ALL'):
                    sendList += self.nicks[i] + ";"
            le = len(sendList)
            sendListtwo = sendList[0:le-1]
            sentList = bytes(sendListtwo, 'UTF-8')
            clientSocket.send(sentList)
            lock.release()
            Client(clientSocket, clientAddr, self).start()


    def send_all(self, msg, sendsock):
        for sock in self.clients:
            if sock != sendsock:
                try:
                    sock.send(msg)
                except:
                    self.clean_client(sock)

    def send(self, msg, clientsocket, sendsock):
        strdata = msg.decode('UTF-8')
        x = strdata.split(';')
        for key in self.dict.keys():
            if key == x[2]:
                self.dict[key].send(msg)

    def clean_client(self, client, name):
        if client in self.clients:
            self.clients.remove(client)
            for k,v in self.dict.copy().items():
                if v == client:
                   del self.dict[k]
            client.close()
        if name in self.nicks:
            self.nicks.remove(name)
    #def clean_clients(self, err):
        #for client in err:
            #self.clean_client(client)

class Client(threading.Thread):
    def __init__(self, clientSocket, clientAddr, server):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
        self.server = server
        self.name = ''

    def run(self):
    	while True:
            try:
                data = self.clientSocket.recv(4096)
                strdata = data.decode('UTF-8')
                if data:
                    lock.acquire()
                    if strdata.startswith('MSG;ALL;'):
                        msg = strdata[8:]
                        str3 = "MSG;ALL;" + self.name + ";" + msg
                        sendata = bytes(str3, 'UTF-8')
                        self.server.send_all(sendata, self.clientSocket)
                    elif strdata.startswith('MSG;'):
                        msg = strdata[4:]
                        z = msg.find(';')
                        client = msg[0:z]
                        msg = msg[int(z+1):]
                        sendd = "MSG;" + self.name + ";" + client + ";" + msg
                        sendata = bytes(sendd, 'UTF-8')
                        self.server.send(sendata, client, self.clientSocket)
                    elif strdata.startswith('LOGIN;'):
                        self.server.nicks.append(strdata[6:])
                        msg = strdata[6:]
                        self.name = msg
                        self.server.dict[strdata[6:]] = self.clientSocket
                        self.server.send_all(data, self.clientSocket)
                    lock.release()
                else:
                    lock.acquire()
                    msg = 'LOGOUT;' + self.name
                    sendata = bytes(msg, 'UTF-8')
                    self.server.send_all(sendata, self.clientSocket)
                    #print(self.name)
                    self.server.clean_client(self.clientSocket, self.name)
                    lock.release()
                    break
            except:
                lock.acquire()
                self.server.clean_client(self.clientSocket, self.name)
                lock.release()
                break

server = ChatServer('localhost', 12345)
server.run()
#192.168.0.11
