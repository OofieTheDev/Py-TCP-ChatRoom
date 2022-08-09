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
admins = []
bans = []

def starter():
    server.listen()
    print(f"Server has started on Port {PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=client_handler, args=(conn, addr))
        thread.start()

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

def send_msg_to_client(msg, user_conn):
    msg = msg.encode(FORMAT) # encodes the message to bytes
    msg_len = len(msg) # gets the length of that encoded msg
    msg_len_encoded = str(msg_len).encode(FORMAT) # encodes the length of that encoded message
    msg_len_encoded += b' ' * (INITIAL_HEADER - len(msg_len_encoded)) # adds padding to that encoding to make it 64 bytes long
    user_conn.send(msg_len_encoded) # sends the final encoding length with padding
    user_conn.send(msg) # sends the actual message

def kick_user(user_name, user_conn):
    nicknames.remove(user_name)
    clients.remove(user_conn)
    send_msg_to_client("You have been kicked by an admin.", user_conn)
    user_conn.close()
    broadcast(f"{user_name} has been kicked from the server.")

def ban_user(user_name, user_conn, addr):
    nicknames.remove(user_name)
    clients.remove(user_conn)
    bans.append(f"{addr[0]:{addr[1]}}")
    send_msg_to_client("You have been banned by an admin.", user_conn)
    user_conn.close()
    broadcast(f"{user_name} has been banned from the server.")

def client_handler(conn, addr):
    if f"{addr[0]}:{addr[1]}" in bans:
        send_msg_to_client("You are banned from this server.", conn)
        conn.close()
        return
    print(f"[NEW CONNECTION][{addr[0]}][{addr[1]}] has joined the chat!")
    clients.append(conn)
    connected = True
    while connected:
        msg_len = conn.recv(INITIAL_HEADER).decode(FORMAT) # gets length of preceding message from client

        if msg_len:
            # print(f"Msg LEN: {msg_len}")

            msg_len = int(msg_len)
            msg = conn.recv(msg_len).decode(FORMAT)
            
            if msg.startswith("admin:"):
                pw = msg.replace("admin:")
                if pw == "admin":
                    nicknames.append("admin")
                    admins.append(addr[0] + ":" + addr[1])
                    conn.send("Connected to the server.".encode(FORMAT))
                    broadcast(f"An admin has joined the chat!")
                    continue
                else:
                    clients.remove(conn)
                    conn.send("Incorrect password.".encode(FORMAT))
                    conn.close()
                    connected = False
                    break

            if msg.startswith("NICK:"):
                nick = msg.replace("NICK:","")
                if nick != "admin":
                    nicknames.append(nick)
                    print(f'[{addr[0]}][{addr[1]}] set their nickname as "{nick}"')
                    conn.send("Connected to the server.".encode(FORMAT))
                    broadcast(f"{nick} has joined the chat!")
                    continue
                        
            if msg.startswith("/"):
                if f"{addr[0]}:{addr[1]}" in admins:
                    if msg.startswith("/kick"):
                        target_name = msg.replace("/kick ")
                        if target_name in nicknames:
                            target_index = nicknames.index(target_name)
                            target_conn = clients[target_index]
                            kick_user(target_name, target_conn)
                            

                    if msg.startswith("/ban"):
                        target_name = msg.replace("/ban ")
                        if target_name in nicknames:
                            target_index = nicknames.index(target_name)
                            target_conn = clients[target_index]
                            ban_user(target_name, target_conn, addr)

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




starter()
