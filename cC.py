import tkinter as tk
from tkinter import messagebox
import time
import threading
import random
import queue
import socket
import select
import sys

que = queue.Queue()

class MyApp():
    def __init__(self, root, nick):
        self.root = root
        self.nick = nick
        self.createWidgets()

    def createWidgets(self):
        self.root = root
        self.root.title("User {}".format(self.nick))
        self.root.minsize(600,400)
        self.mainFrame = tk.Frame(self.root)
        self.mainFrame.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.frame = tk.Text(self.mainFrame, bg="white", width=1, height=1)
        self.frame.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.frame.config(state=tk.DISABLED)

        self.Lb = tk.Listbox(self.mainFrame, bg="white")
        self.Lb.insert(tk.END, "ALL")
        self.Lb.grid(column=1, row=0, rowspan=2, sticky=tk.N + tk.S + tk.W + tk.E)
        #self.Lb.exportselection = 0
        self.Lb.select_set(0)
        self.Lb.event_generate("<<ListboxSelect>>")

        self.frame10 = tk.Text(self.mainFrame, bg="white", width=1, height=1)
        self.frame10.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)

        self.Button1 = tk.Button(self.mainFrame, bg="gray", text="Send Message")
        self.Button1.grid(column=0, row=2, columnspan=1, sticky=tk.N + tk.S + tk.W + tk.E)

        self.Button2 = tk.Button(self.mainFrame, bg="gray", text="EXIT")
        self.Button2.grid(column=1, row=2, columnspan=1, sticky=tk.N + tk.S + tk.W + tk.E)

        self.mainFrame.rowconfigure(0,weight=4)
        self.mainFrame.rowconfigure(1,weight=2)
        self.mainFrame.rowconfigure(2,weight=1)

        self.mainFrame.columnconfigure(0,weight=3)
        self.mainFrame.columnconfigure(1,weight=1)

        self.root.bind("<Return>", lambda event: self.sendchat())
        self.Button1.focus_force()
        self.Button1.bind("<Button-1>", lambda event: self.sendchat())

        self.Button2.bind("<Button-1>", lambda event: self.close())

        self.list_clients = ['ALL']

    def close(self):
        s.close()
        self.root.destroy()

    def sendchat(self):
        sel = self.Lb.curselection()[0]
        name = self.list_clients[sel]
        txt = self.frame10.get('1.0', tk.END)
        st = txt.strip('\n')
        str1 = "MSG;{};{}".format(name, txt)
        str2 = self.nick + " => " + name + ":" + '\n'
        msg = bytes(str1, 'UTF-8')
        if st=='':
            messagebox.showinfo("ERROR", "Enter Message")
        else:
            s.send(msg)
            self.frame.config(state=tk.NORMAL)
            self.frame.insert(tk.END, str2)
            self.frame.insert(tk.END, txt)
            self.frame.config(state=tk.DISABLED)
            self.frame10.delete('1.0', tk.END)

    def processIncoming(self):
        while que.qsize():
            try:
                data = que.get(0)
                strdata = data.decode('UTF-8')
                if strdata.startswith('MSG'):
                    x = strdata.split(';')
                    if(x[1]=="ALL"):
                        msg = strdata[8:]
                        z = msg.find(';')
                        client = msg[0:z]
                        msg = msg[int(z+1):]
                        str1 = client + " => ALL:"
                        str2 = msg
                        str3 = str1 + '\n' + str2
                        self.frame.config(state=tk.NORMAL)
                        self.frame.insert(tk.END, str3) #frame10
                        self.frame.config(state=tk.DISABLED)
                    else:
                        msg = strdata[4:]
                        z = msg.find(';')
                        od = msg[0:z]
                        msg = msg[int(z+1):]
                        y = msg.find(';')
                        do = msg[0:y]
                        msg = msg[int(y+1):]
                        str0 = od + " => " + do + ":"
                        str1 = str0 + '\n' + msg
                        self.frame.config(state=tk.NORMAL)
                        self.frame.insert(tk.END, str1) #frame10
                        self.frame.config(state=tk.DISABLED)
                elif strdata.startswith('LOGIN;'):
                    name = strdata[6:]
                    self.Lb.insert(tk.END, name)
                    self.list_clients.append(name)
                elif strdata.startswith('LOGOUT;'):
                    name = strdata[7:]
                    for i in range(len(self.list_clients)):
                        if self.list_clients[i] == name:
                            self.Lb.delete(i)
                            break
                    self.list_clients.remove(name)
                elif strdata.startswith('LIST;'):
                    lusers = strdata.split(';')
                    i = 1
                    while i < len(lusers):
                        self.Lb.insert(tk.END, lusers[i])
                        self.list_clients.append(lusers[i])
                        i += 1
            except que.Empty:
                break #pass

class ThreadedClient(threading.Thread):
    def __init__(self, master, nick):
        self.master = master
        self.nick = nick
        self.gui = MyApp(master, self.nick)
        self.thr = work(self.nick)
        self.thr.daemon = True
        self.thr.start()
        self.periodicCall()

    def periodicCall(self):
        self.gui.processIncoming()
        self.master.after(200, self.periodicCall)

class work(threading.Thread):
    def __init__(self, nick):
        threading.Thread.__init__(self)
        s.connect(('localhost', 12345))
        self.nick = nick
        self.sen = "LOGIN;" + self.nick
        self.sendata = bytes(self.sen, 'UTF-8')
        s.send(self.sendata)

    def run(self):
        test = 0
        while True:
            if test==1:
                break
            else:
                try:
                    data = s.recv(4096)
                    if data:
                        que.put(data)
                    else:
                        s.close()
                        root.quit()
                        test = 1
                        break
                except:
                    s.close()
                    root.quit()
                    break

nick = input('Podaj nick:')

root = tk.Tk()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client = ThreadedClient(root, nick)
root.mainloop()
