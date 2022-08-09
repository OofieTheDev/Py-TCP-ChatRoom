import socket
import threading
import string

req_chars = [x for x in string.ascii_letters + string.digits]

SERVER = '192.168.1.88' # put same IP and port as the server.py
PORT = 57000
FORMAT = 'utf-8'
INITIAL_HEADER = 64
DC_MSG = "!DC"

ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send(msg):
    msg = msg.encode(FORMAT) # encodes the message to bytes
    msg_len = len(msg) # gets the length of that encoded msg
    msg_len_encoded = str(msg_len).encode(FORMAT) # encodes the length of that encoded message
    msg_len_encoded += b' ' * (INITIAL_HEADER - len(msg_len_encoded)) # adds padding to that encoding to make it 64 bytes long
    client.send(msg_len_encoded) # sends the final encoding length with padding
    client.send(msg) # sends the actual message

def recv_msg(): # for receiving messages
    while True:
        try:
            msg_len = client.recv(INITIAL_HEADER).decode(FORMAT) # gets length of preceding message from client
            if msg_len: # if msg_len is received
                msg_len = int(msg_len) # assume it is int and convert it as such
                msg = client.recv(msg_len).decode(FORMAT) # receive the actual message using the given int length
                print(msg) # print the msg received
        except:
            print("An error occured, closing connection.")
            client.close()
            break

def send_msgs():
    while True:
        try:
            msg = input('')
            send(msg)
        except:
            send(DC_MSG)

def starter():
    msg_recv = threading.Thread(target=recv_msg)
    msg_recv.start()
    msg_sender = threading.Thread(target=send_msgs)
    msg_sender.start()

NICKNAME = input("Nickname: ")

if any(l in NICKNAME for l in req_chars) and NICKNAME != "admin":
    client.connect(ADDR)
    send(f"NICK:{NICKNAME}")
    starter()
elif NICKNAME == "admin":
    pw = input("Password:")
    client.connect(ADDR)
    send(f"admin:{pw}")
    starter()
else:
    print("Illegal nickname.")
