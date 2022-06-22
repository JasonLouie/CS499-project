import socket, threading
from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"

username = input("Enter a username: ")

user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user.connect(('192.168.1.171', 55555))



def receive():
    while True:
        try:
            message = user.recv(1024).decode('ascii')
            if message == 'NAME':
                user.send(username.encode('ascii'))
            else:
                print(message)
        except:
            print("An error occurred!")
            user.close()
            break

def write():
    while True:
        # Wait for a new message 
        message = f'{username}: {input("")}'
        user.send(message.encode('ascii'))

if __name__ == '__main__':
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()