import threading,socket,cv2

host = socket.gethostbyname(socket.gethostname())
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen()

class User:
    def __init__(self, name, addr, connection):
        self.username = name
        self.address = addr
        self.user_socket = connection
    def getUsername(self):
        return self.username
    
    def getAddress(self):
        return self.address
    
    def getConnection(self):
        return self.user_socket
    
    def endConnection(self):
        self.user_socket.close()
    
clients = []

def broadcast(message):
    for client in clients:
        client.getConnection().send(message)

# user refers to the socket connection from a specific chat client
def handle(user):
    while True:
        try:
            message = user.recv(1024)
            broadcast(message)
        except:
            # remove the client that sends a failed message
            for client in clients:
                if client.getConnection() == user:
                    clients.remove(client)
                    client.endConnection()
                    broadcast(f'{client.getUsername()} left the chat!'.encode('ascii'))
                    print(f'{client.getUsername()} left the chat!')
                    break

def receive():
    while True:
        user, address = server.accept()
        print(f"Connected with {str(address)}")
        user.send('NAME'.encode('ascii'))
        try:
            username = user.recv(1024).decode('ascii')
            newUser = User(username, address, user)
            clients.append(newUser)
            print(f"Nickname of the client is {username}!")
            broadcast(f'{username} joined the chat!'.encode('ascii'))
            user.send('Connected to the server!'.encode('ascii'))
            thread = threading.Thread(target=handle, args=(user,))
            thread.start()

        except:
            print("User disconnected before entering a username")

        
if __name__ == '__main__':
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()