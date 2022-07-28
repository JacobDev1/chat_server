from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from datetime import datetime

HOST = "127.0.0.1"  # Enter your server's IP
PORT = 32500
MAX_USERS = 100

BUFFER_SIZE = 1024

clients = {}
addresses = {}
SOCK = socket(AF_INET, SOCK_STREAM)
SOCK.bind((HOST, PORT))

# Security
def isSpam(msg, IP):
    is_spam = True
    msg_str = ""
    try:
        msg_str = msg.decode("utf8")
    except:
        print(f"[Security] Couldn't decode the message ({IP})")
        return is_spam
        
    if msg_str.strip() == "": # is Empty
        print(f"[Security] Empty message ({IP})")
    elif len(msg_str) >= BUFFER_SIZE:
        print(f"[Security] Overly long message ({IP})")
    else:
        is_spam = False
    return is_spam

def verifyClient(msg_b, IP):
    try:
        msg_str = msg_b.decode("utf8")
    except:
        print(f"[Security] Couldn't decode the message ({IP})")
        return False

    if msg_str == "CHAT":
        return True 
    else:
        print(f"[Security] Client verification failed ({IP})")
        return False

# Connectivity
def closeConnection(conn):
    if conn in clients:
        del clients[conn]
    try:
        conn.send("/quit".encode("utf8"))
        conn.close()
    except:
        pass

def broadcast(msg_str):
    print(f"[Broadcast] {msg_str}")
    msg = bytes(msg_str+'\n',"utf8")
    try:    # Fixes server crashes
        for sock in clients:
            sock.send(msg)
    except:
        pass

def log(msg, type="Info"):
    now = datetime.now().strftime("[%H:%M:%S]")
    print(f"[{type}][{now}] {msg}")
    
# Submain server function
def handleClient(conn, address):
    # Receive and check
    while True:
        conn.send("Enter your nickname:\n".encode("utf8"))
        try:
            name = conn.recv(BUFFER_SIZE)
        except:
            print(f"[Security] Couldn't receive the message ({address[0]})")
            closeConnection(conn)
            return

        if isSpam(name, address[0]):
            closeConnection(conn)
            return

        # Process the first request
        name = name.decode("utf8")

        if name == "/quit":
            closeConnection(conn)
            print(f"[Info] {address[0]}:{address[1]} has left the chat")
            return

        # Check for a similar name
        if name in clients.values():
            print(f"[Info] Duplicate name found ({name})")
            conn.send("Nickname taken\n".encode("utf8"))
            continue
        else:
            clients[conn] = name
            break

    print(f"[Info] {address[0]}:{address[1]} chose username \"{name}\"")
    msg = f"{name} has joined the chat"
    broadcast(msg)

    # Keep processing requests
    while True:
        # Receive and check
        try:
            msg = conn.recv(BUFFER_SIZE)
        except:
            print(f"[Security] Couldn't receive the message ({address[0]})")
            closeConnection(conn)
            return

        if isSpam(msg, address[0]):
            closeConnection(conn)
            return

        # Handle the message
        msg = msg.decode("utf8")

        if msg == "/quit":
            closeConnection(conn)
            broadcast(f"{name} has left the chat")
            break

        now = datetime.now().strftime("[%H:%M:%S]")
        broadcast(f"{name} {now}: "+ msg)

# Main server function
def acceptIncomingConnections():
    while True:
        conn, address = SOCK.accept()

        # Verify
        try:
            header = conn.recv(BUFFER_SIZE)
        except:
            print(f"[Security] Couldn't receive the message ({address[0]})")
            closeConnection(conn)
            continue
        
        if not verifyClient(header, address[0]):
            closeConnection(conn)
            continue

        # Start the loop
        print(f"[Info] {address[0]}:{address[1]} has connected")
        addresses[conn] = address
        Thread(target=handleClient, args=(conn, address)).start()

SOCK.listen(MAX_USERS)
print(f"Chat Server is running at {HOST}:{PORT}")
accept_connections = Thread(target=acceptIncomingConnections)
accept_connections.start()
accept_connections.join()
SOCK.close()