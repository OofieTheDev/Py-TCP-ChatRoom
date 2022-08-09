import socket
import threading
import hashlib

SERVER = '192.168.1.88'
PORT = 12000
INITIAL_HEADER = 64
DC_MSG = "!DC"
PW_HASH = "33bea234666b81088064d58f8f046d72986b100dd56b849caeb1113e918baea6"

ADDR = (SERVER, PORT)

FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = []
nicknames = []
admins = []
bans = []

def validate(password):
    if hashlib.sha256(password.encode()).hexdigest() == PW_HASH:
        return True
    else:
        return False

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
    print(f"[MOD ACTION] {user_name} has been kicked from the server.")
    broadcast(f"{user_name} has been kicked from the server.")

def ban_user(user_name, user_conn, addr):
    nicknames.remove(user_name)
    clients.remove(user_conn)
    bans.append(str(addr[0]))
    send_msg_to_client("You have been banned by an admin.", user_conn)
    user_conn.close()
    print(f"[MOD ACTION] {user_name} has been banned from the server.")
    broadcast(f"{user_name} has been banned from the server.")

def client_handler(conn, addr):
    if str(addr[0]) in bans:
        conn.close()
        return
    print(f"[NEW CONNECTION][{addr[0]}][{addr[1]}] has joined the chat!")
    clients.append(conn)
    connected = True
    try:
        while connected:
            msg_len = conn.recv(INITIAL_HEADER).decode(FORMAT) # gets length of preceding message from client

            if msg_len:
            # print(f"Msg LEN: {msg_len}")

                msg_len = int(msg_len)
                msg = conn.recv(msg_len).decode(FORMAT)
            
                if msg.startswith("admin:"):
                    pw = msg.replace("admin:", "")
                    if validate(pw):
                        nicknames.append("admin")
                        admins.append(str(addr[0]) + ":" + str(addr[1]))
                        print(f"[{addr[0]}][{addr[1]}] is an admin")
                        send_msg_to_client("Connected to the server", conn)
                        broadcast(f"An admin has joined the chat!")
                        continue
                    else:
                        clients.remove(conn)
                        send_msg_to_client("Incorrect password.", conn)
                        conn.close()
                        print(f"[CLIENT DISCONNECT - {addr[0]}:{addr[1]}]")
                        connected = False
                        break

                if msg.startswith("NICK:"):
                    nick = msg.replace("NICK:","")
                    if nick != "admin":
                        nicknames.append(nick)
                        print(f'[{addr[0]}][{addr[1]}] set their nickname as "{nick}"')
                        send_msg_to_client("Connected to the server", conn)
                        broadcast(f"{nick} has joined the chat!")
                        continue
                        
                if msg.startswith("/"):
                    if f"{addr[0]}:{addr[1]}" in admins:
                        if msg.startswith("/kick"):
                            target_name = msg.replace("/kick ", "")
                            if target_name in nicknames:
                                target_index = nicknames.index(target_name)
                                target_conn = clients[target_index]
                                kick_user(target_name, target_conn)
                                continue
                            

                        if msg.startswith("/ban"):
                            target_name = msg.replace("/ban ", "")
                            if target_name in nicknames:
                                target_index = nicknames.index(target_name)
                                target_conn = clients[target_index]
                                ban_user(target_name, target_conn, addr)
                                continue

                target_client = clients.index(conn)
            # print(target_client)
            # print(nicknames)
            
                if msg == DC_MSG:
                    conn.close()
                    clients.remove(conn)
                    broadcast(f"[CLIENT DISCONNECT - {nicknames[target_client]}]")
                    print(f"[CLIENT DISCONNECT - {nicknames[target_client]}]")
                    connected = False
                    break

                print(f"{nicknames[target_client]}: {msg}")
            
                broadcast(msg, nicknames[target_client])
        conn.close()
    except ConnectionAbortedError:
        print("Connection abort detected.")
        pass




starter()
