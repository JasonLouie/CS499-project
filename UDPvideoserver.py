from ctypes import sizeof
import cv2, imutils, socket, numpy as np, time, base64, threading
from tkinter import *

buffer_size = 65536
host_ip = socket.gethostbyname(socket.gethostname())
videoPort = 55666

class User:
    def __init__(self, address):
        self.address = address
    
    def getAddress(self):
        return self.address
    

clients = []

class VideoServer:
    def __init__(self):
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def start(self):
        self.video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        self.video_socket.bind((host_ip, videoPort))
        self.receive()
        
    # Send video to all clients

    # Old function for sending video was server generating the data to send to clients
    # New function must be server receiving the data and forwarding it to the other clients
    def sendVideo(self, packet, sent_addr):
        if len(clients) >= 2:
            for client in clients:
                if client.getAddress() != sent_addr:
                    try:
                        self.video_socket.sendto(packet, client.getAddress())
                    except:
                        print("Removed client")
                        clients.remove(client)
                    
    # Receive video from a client 
    def receive(self):
        print(f"Listening for a connection...")
        while True:
            msg, address = self.video_socket.recvfrom(buffer_size)
            if msg.decode('ascii') == "First Time":
                print(f"Connected to UDP video with {address}")
                clients.append(User(address))
            else:
                self.sendVideo(msg, address)

if __name__ == '__main__':
    video_server = VideoServer()
    video_server.start()
