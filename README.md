# Python TCP Chat Room

## :pushpin: Quick Start

`client.py` connects automatically to the server created by `server.py` upon execution, so `server.py` needs to be run first.

Hence, run 
```
py server.py
```

Next, run
```
py client.py
```
(preferably, multiple instances)

## :heavy_check_mark: Summary

Firstly, server.py is run, creating the chat room server on Port 12000. SOCK_STREAM is used when initialising the socket, so that the server uses TCP for communication. I guess UDP could be used but who wants to receive incomplete messages, right?

The user uses client.py to connect to the server, and gets to choose their nickname before joining the chat room. Of course, there are meant to be multiple instances of client.py, because what good is a chat room if you're the only one in it?

When a client connects to the server, it is handled on its own individual thread. This is to allow multiple clients to connect to the server, for very obvious reasons already stated.

From then on it functions just like a normal chatroom, where the user's messages are broadcasted to all the other users, with their nickname at the start so the other users know who's saying what. 

If the user in question is an admin, he/she can enter their nickname as admin, which results in a password prompt. When the password is entered, it is hashed with SHA-256 and compared to the actual password (already hashed with SHA-256). Frankly, I could've put it as a simple string, given the simplicity of this application and the fact that it's just a fun little project, not like I'm putting some API key or whatever. Still, I decided to take this small step just to make it a little more professional. Anyways, moving on, if the hashes match, the user is let into the chat room as an admin.

An admin has the the following privileges, which normal users don't have.
- Kicking a user
- Banning a user

A kicked user can rejoin the chatroom. A banned user however, is IP banned. This prevents the banned user from joining the chat room again, even under a different name, though obviously this can be circumvented by the use of a proxy. This README.md was sponsored by ExpressVP-

## :computer: Deeper Dive
Most of the crucial parts of the code are explained by comments, but I think there are just some parts I need to explain a little more.

You will repeatedly notice something like this:

```py
msg = msg.encode(FORMAT) # encodes the message to bytes
msg_len = len(msg) # gets the length of that encoded msg
msg_len_encoded = str(msg_len).encode(FORMAT) # encodes the length of that encoded message
msg_len_encoded += b' ' * (INITIAL_HEADER - len(msg_len_encoded)) # adds padding to that encoding to make it 64 bytes long
client.send(msg_len_encoded) # sends the final encoding length with padding
client.send(msg) # sends the actual message
```

Basically, client.recv() is for the client/server to receive messages from each other. However, an argument NEEDS to be specified in the .recv() method, for example client.recv(2048) means that it will only receive the first 2048 bytes of a message. Hence, if the message length exceeds that, the client/server will not receive the rest. This code that I use makes it such that the length of the message is first calculated and then sent, allowing the receiver to prepare their .recv() to receive the exact length of the actual message by passing the length as the argument. Then and only then is the actual message sent. The length of the message can be safely received because I pass the default value of 64 into the first .recv(), and that is theoretically more than enough to contain even a very large number.

## :question: Why did I make this?
I've always wanted to practice the Python socket library, but I put it off until very recently. After learning its basics through the socket YouTube tutorials of YouTubers like [@TechWithTim](https://github.com/techwithtim) and [@NeuralNine](https://github.com/neuralnine), in which they did chatrooms too, I decided to make one myself to practice my Python socket knowledge, though of course with my own twists and ways of doing stuff added on. Special thanks to them for inspiring me to make this, and being awesome YouTubers in general.

## :keyboard: Fin
I might add additional features in future as further practice, such as mutes with durations and slowmode. Any further suggestions are welcome.




