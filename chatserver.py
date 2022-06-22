import threading,socket,cv2

host = socket.gethostbyname(socket.gethostname())
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen()

users = []
usernames = []

def broadcast(message):
    for user in users:
        user.send(message)

def handle(user):
    while True:
        try:
            message = user.recv(1024)
            broadcast(message)
        except:
            # remove the client that sends a failed message
            index = users.index(user)
            users.remove(user)
            user.close()
            username = usernames[index]
            broadcast(f'{username} left the chat!'.encode('ascii'))
            usernames.remove(username)
            break

def receive():
    while True:
        user, address = server.accept()
        print(f"Connected with {str(address)}")

        user.send('NAME'.encode('ascii'))
        username = user.recv(1024).decode('ascii')
        usernames.append(username)
        users.append(user)

        print(f"Nickname of the client is {username}!")
        broadcast(f'{username} joined the chat!'.encode('ascii'))
        user.send('Connected to the server!'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(user,))
        thread.start()

if __name__ == '__main__':
    receive()