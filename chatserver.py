import threading,socket

buffer_size = 65536
host = socket.gethostbyname(socket.gethostname())
chatPort = 55555
videoPort = 55666
audioPort = 55777

clients = []

class User:
    def __init__(self, name, chat_connection):
        self.username = name
        self.chat_socket = chat_connection
        self.address = ""
    
    def setAddress(self, addr):
        self.address = addr

    def getUsername(self):
        return self.username
    
    def getAddress(self):
        return self.address
    
    def getChatConnection(self):
        return self.chat_socket
    
    def endConnection(self):
        self.chat_socket.close()

class Server:
    def __init__(self):
        self.chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def start(self):
        print("Listening for connections...")
        self.chat_server.bind((host,chatPort))
        self.chat_server.listen()

        self.video_server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        self.video_server.bind((host, videoPort))
        self.receive()
        self.videoReceiveServer()
    
    def shutdown(self):
        print("Shutting Down...")
        self.chat_server.close()
        # self.video_server.close()

    def broadcast(self, message):
        for client in clients:
            client.getChatConnection().send(message)
    
    def sendMessage(self, message, user):
        for client in clients:
            if client.getChatConnection() != user:
                client.getChatConnection().send(message)
    
    def findClient(self, username):
        for client in clients:
            if username == client.getUsername():
                return client
        
        print("No client found")

    def sendVideo(self, addr, packet):
        if len(clients) >= 2:
            for client in clients:
                if client.getAddress() != addr:
                    self.video_server.sendto(packet, client.getAddress())
    
    def streamVideo(self):
        while True:
            packet,addr = self.video_server.recvfrom(buffer_size)
            try:
                # End thread when user disconnects
                msg = packet.decode('ascii')
                if msg[0:6] == "FIRST:":
                    client = self.findClient(msg[6:])
                    client.setAddress(addr)
                elif msg == "BYE":
                    print("Thread ended")
                    break
            except:
                self.sendVideo(addr, packet)

    def handle(self, user, address):
        try:
            user.send('NAME'.encode('ascii'))
            username = user.recv(1024).decode('ascii')
            newUser = User(username, user)
            clients.append(newUser)
            print(f"Username of the client is {username}!")
            self.broadcast(f'{username} joined the chat!'.encode('ascii'))
            user.send("Connected to the server!".encode('ascii'))
        except:
            print("User disconnected before entering a username")
            user.close()
            return

        # Create thread to handle video, then func
        handleVideo_thread = threading.Thread(target=self.streamVideo)
        handleVideo_thread.start()

        while True:
            try:
                message = user.recv(1024)
                self.sendMessage(message, user)
            except:
                # remove the client that sends a failed message
                clients.remove(newUser)
                newUser.endConnection()
                self.broadcast(f'{newUser.getUsername()} left the chat!'.encode('ascii'))
                print(f'{newUser.getUsername()} left the chat!')
                break

    def receive(self):
        try:
            while True:
                user, address = self.chat_server.accept()
                print(f"Connected with {str(address)}")
                handleUser_thread = threading.Thread(target=self.handle, args=(user, address,))
                handleUser_thread.start()
        except KeyboardInterrupt:
            print("Shutting down...")
            self.shutdown()

    def videoReceiveServer(self):
        while True:
            packet,addr = self.video_server.recvfrom(buffer_size)
            try:
                msg = packet.decode('ascii')
                if msg[0:6] == "FIRST:":
                    client = self.findClient(msg[6:])
                    client.setAddress(addr)
            except:
                self.sendVideo(addr, packet)
        
if __name__ == '__main__':
    chat_server = Server()
    chat_server.start()