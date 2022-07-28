from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import tkinter
from tkinter.scrolledtext import *

HOST = "127.0.0.1"  # Enter your server's IP
PORT = 32500

BUFFER_SIZE = 1024
sock = socket(AF_INET, SOCK_STREAM)

def connectToOfficial():
    root.title("Chat [Official]")
    connect(HOST, PORT)

def connectToLocalhost():
    root.title("Chat [Localhost]")
    connect("127.0.0.1", PORT)

def connect(address, port):
    try:
        sock.connect((address, port))
        sock.send(bytes("CHAT", "utf8"))
        thread = Thread(target=receive)
        thread.start()
        start_screen.withdraw()
        root.deiconify()
    except:
        server_con_info.config(text=f"Couldn't connect to the server")

def send(event = None):
    msg = msg_input.get()
    msg_input.set("")
    if msg.strip() and len(msg) < BUFFER_SIZE:
        sock.send(bytes(msg, "utf8"))
    if msg == "/quit":
        sock.close()
        root.destroy()

def receive():
    while True:
        try:
            msg = sock.recv(BUFFER_SIZE).decode("utf8")
            if msg == "/quit":
                close()
            msg_output.insert(tkinter.END, msg)
            msg_output.yview(tkinter.END)
        except:
            break

def close(event = None):
    msg_input.set("/quit")
    send()

# GUI
root = tkinter.Tk()
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", close)
root.title("Chat")
root.withdraw()

# Start Screen
start_screen = tkinter.Toplevel()
start_screen.geometry("300x150")
start_screen.resizable(False, False)

server_info = tkinter.Label(start_screen, text="Choose Server", font=("helvetica", 20))
server_con_info = tkinter.Label(start_screen)
server1_button = tkinter.Button(start_screen, text="Official", command=connectToOfficial)
server2_button = tkinter.Button(start_screen, text="Localhost", command=connectToLocalhost)

server1_button.config(width=20, height=1, font=("helvetica", 10))
server2_button.config(width=20, height=1, font=("helvetica", 10))
server_con_info.config(fg="#e06207")

server_info.pack(side=tkinter.TOP, pady=5)
server1_button.pack(side=tkinter.TOP, pady=5)
server2_button.pack(side=tkinter.TOP, pady=5)
server_con_info.pack(pady=5)

# Main Window
main_window = tkinter.Frame(root)

msg_input = tkinter.StringVar()
msg_output = ScrolledText(main_window, height=20, width=50, wrap=tkinter.WORD)
input_field = tkinter.Entry(main_window, textvariable=msg_input)
send_button = tkinter.Button(main_window, text="Send")

msg_output.config(font=("helvetica", 11), padx=10, pady=10)
input_field.config(width=45, font=("helvetica", 11))
send_button.config(width=7, height=1, font=("helvetica", 12))

main_window.pack()
msg_output.pack()
input_field.pack(side=tkinter.LEFT, pady=5)
send_button.pack(side=tkinter.RIGHT)

msg_input.set("")
msg_output.bind("<Key>", lambda e: "break")   # Disable editing
input_field.bind("<Return>", send)
send_button.bind("<Button-1>", send)

# Main
tkinter.mainloop()