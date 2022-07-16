import pyaudio, socket, threading
from tkinter import *

audioPort = 55777
host = socket.gethostbyname(socket.gethostname())
# audio will be in chunks of 1024 sample
chunk = 1024
# 16 bits per sample
audio_format = pyaudio.paInt16
channels = 2
# Record at 44100 samples per second
fs = 44100
# Number of seconds to record
seconds = 0.25
filename = "audio_output.wav"

clients = []

class User:
    def __init__(self, audioSock):
        self.audioSocket = audioSock
    
    def getAudioSocket(self):
        return self.audioSocket
    
    def endAudio(self):
        self.audioSocket.close()

class AudioServer:
    def __init__(self):
        self.audio_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    def start(self):
        print("Listening for connections...")
        self.audio_server.bind((host,audioPort))
        self.audio_server.listen()
        self.receiveAudio()
    
    def sendAudio(self, audio, user):
        for client in clients:
            if client.getAudioSocket() != user:
                try:
                    client.getAudioSocket().send(audio)
                except:
                    print("Error has occurred")
    
    def handleAudio(self, user, address):
        try:
            user.send("Hello".encode('ascii'))
            if user.recv(1024).decode('ascii') == "Joining":
                newUser = User(user)
                clients.append(newUser)
        except:
            print("Connection error")
            user.close()
            return

        while True:
            try:
                audio = user.recv(1024*8)
                self.sendAudio(audio, user)
            except:
                # remove the client that sends a failed message
                clients.remove(newUser)
                newUser.endAudio()
                print(f"{address} disconnected.")
                break


    def receiveAudio(self):
        while True:
            user, address = self.audio_server.accept()
            print(f"Connected with {str(address)}")
            handleAudio_thread = threading.Thread(target=self.handleAudio, args=(user, address,))
            handleAudio_thread.start()

if __name__ == '__main__':
    audio = AudioServer()
    audio.start()
