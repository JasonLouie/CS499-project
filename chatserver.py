import threading,socket,cv2

host = socket.gethostbyname(socket.gethostname())
chatPort = 55555
videoPort = 55666
audioPort = 55777

clients = []

class User:
    def __init__(self, name, addr, chat_connection):
        self.username = name
        self.address = addr
        self.chat_socket = chat_connection
    
    def getUsername(self):
        return self.username
    
    def getAddress(self):
        return self.address
    
    def getChatConnection(self):
        return self.chat_socket
    
    def endConnection(self):
        self.chat_socket.close()

class ChatServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def start(self):
        print("Listening for TCP connections...")
        self.server.bind((host,chatPort))
        self.server.listen()
        self.receive()

    def broadcast(self, message):
        for client in clients:
            client.getChatConnection().send(message)

    def handle(self, user, address):
        try:
            user.send('NAME'.encode('ascii'))
            username = user.recv(1024).decode('ascii')
            newUser = User(username, address, user)
            clients.append(newUser)
            print(f"Username of the client is {username}!")
            self.broadcast(f'{username} joined the chat!'.encode('ascii'))
            user.send('Connected to the server!'.encode('ascii'))
        except:
            print("User disconnected before entering a username")
            user.close()
            return

        while True:
            try:
                message = user.recv(1024)
                self.broadcast(message)
            except:
                # remove the client that sends a failed message
                clients.remove(newUser)
                newUser.endConnection()
                self.broadcast(f'{newUser.getUsername()} left the chat!'.encode('ascii'))
                print(f'{newUser.getUsername()} left the chat!')
                break

    def receive(self):
        while True:
            user, address = self.server.accept()
            print(f"Connected with {str(address)}")
            handleChat_thread = threading.Thread(target=self.handle, args=(user, address,))
            handleChat_thread.start()
        
if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.start()