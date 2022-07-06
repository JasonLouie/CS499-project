import socket, threading
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
    
    def shutdown(self):
        self.video_socket.close()

    # Send video to all clients

    # Forwarding received data to the other clients
    def sendVideo(self, packet, sent_addr):
        if len(clients) >= 2:
            for client in clients:
                if client.getAddress() != sent_addr:
                    try:
                        self.video_socket.sendto(packet, client.getAddress())
                    except:
                        print("Removed client")
                        clients.remove(client)
    
    # Receive data from clients
    def receive(self):
        print(f"Listening for a connection...")
        while True:
            try:
                msg, address = self.video_socket.recvfrom(buffer_size)
                # Cannot decode the jpg frames of video from client
                try:
                    if msg.decode('ascii') == "First Time":
                        print(f"Connected to UDP video with {address}")
                        clients.append(User(address))
                except:
                    self.sendVideo(msg, address)
                    
            except OSError as err:
                print(err)

if __name__ == '__main__':
    video_server = VideoServer()
    video_server.start()
