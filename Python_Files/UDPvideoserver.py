import socket, threading, errno
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
    
    def findClient(self, address):
        for client in clients:
            if client.getAddress() == address:
                return client
        
        print("Client does not exist")

    # Send video to all clients
    def handleVideo(self):
        while True:
            packet, address = self.video_socket.recvfrom(buffer_size)
            try:
                if packet.decode('ascii') == "END":
                    # LET CLIENT KNOW TO CLOSE VIDEO WINDOW
                    print("Received END STREAM")
                    self.sendVideo("STOP".encode('ascii'), address)
                    break
                elif packet.decode('ascii') == "BYE":
                        # REMOVE CLIENT FROM LIST
                        client = self.findClient(address)
                        clients.remove(client)
                        print(f"Removed client at {address}")
            except:
                self.sendVideo(packet, address)

    # Forwarding received data to the other clients
    def sendVideo(self, packet, sent_addr):
        if len(clients) >= 2:
            for client in clients:
                if client.getAddress() != sent_addr:
                    try:
                        self.video_socket.sendto(packet, client.getAddress())
                    except socket.error as err:
                        print(f"Removed client because {err}")
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
                        
                    elif msg.decode('ascii') == "START":
                        print("NEW THREAD")
                        sendVideoThread = threading.Thread(target=self.handleVideo)
                        sendVideoThread.start()

                        sendVideoThread2 = threading.Thread(target=self.handleVideo)
                        sendVideoThread2.start()
                    
                    elif msg.decode('ascii') == "END":
                        # LET CLIENT KNOW TO CLOSE VIDEO WINDOW
                        self.sendVideo("STOP".encode('ascii'), address)
                    elif msg.decode('ascii') == "BYE":
                        # REMOVE CLIENT FROM LIST
                        client = self.findClient(address)
                        clients.remove(client)
                        print(f"Removed client at {address}")
                except:
                    self.sendVideo(msg, address)
                    
            except OSError as err:
                print(err)

if __name__ == '__main__':
    video_server = VideoServer()
    video_server.start()
