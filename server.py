import socket
import threading
import logging

SERVER = '192.168.1.88'
PORT = 12000
INITIAL_HEADER = 64
DC_MSG = "!DC"

ADDR = (SERVER, PORT)

FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = []
nicknames = []

def starter():
    server.listen()
    print(f"Server has started on Port {PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=client_handler, args=(conn, addr))
        thread.start()

def client_handler(conn, addr):
    print(f"[NEW CONNECTION][{addr[0]}][{addr[1]}] has joined the chat!")
    clients.append(conn)
    connected = True
    while connected:
        msg_len = conn.recv(INITIAL_HEADER).decode(FORMAT) # gets length of preceding message from client

        if msg_len:
            # print(f"Msg LEN: {msg_len}")

            msg_len = int(msg_len)
            msg = conn.recv(msg_len).decode(FORMAT)
            
            if msg.startswith("NICK:"):
                nick = msg.replace("NICK:","")
                nicknames.append(nick)
                print(f'[{addr[0]}][{addr[1]}] set their nickname as "{nick}"')
                broadcast(f"{nick} has joined the chat!")
                continue

            target_client = clients.index(conn)
            # print(target_client)
            # print(nicknames)
            
            if msg == DC_MSG:
                conn.close()
                broadcast(f"[CLIENT DISCONNECT - {nicknames[target_client]}]")
                print(f"[CLIENT DISCONNECT - {nicknames[target_client]}]")
                connected = False
                break

            print(f"{nicknames[target_client]}: {msg}")
            
            broadcast(msg, nicknames[target_client])
    conn.close()

def broadcast(msg, author=None):
    if author:
        msg_len = len(f"{author}: {msg}".encode(FORMAT)) # get length of string when its encoded
        msg_len_encoded = str(msg_len).encode(FORMAT) # encode length of string
        msg_len_encoded += b' ' * (INITIAL_HEADER - len(msg_len_encoded)) # apply padding
        for client in clients:
            client.send(msg_len_encoded)
            client.send(f"{author}: {msg}".encode(FORMAT))
    else:
        msg_len = len(msg.encode(FORMAT)) # get length of string when its encoded
        msg_len_encoded = str(msg_len).encode(FORMAT) # encode length of string
        msg_len_encoded += b' ' * (INITIAL_HEADER - len(msg_len_encoded)) # apply padding
        for client in clients:
            client.send(msg_len_encoded)
            client.send(msg.encode(FORMAT))

starter()
