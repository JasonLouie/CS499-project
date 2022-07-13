import cv2, imutils, socket, numpy as np, time, threading
from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"
host_ip = '68.237.86.46'
chatPort = 55555
videoPort = 55666
audioPort = 55777
buffer_size = 65536

class ChatClient:
    def __init__(self):
        # Chat socket (TCP)
        self.user_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Video socket (UDP)
        self.user_vid = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.shareAudio = False
        self.showVideo = False
        self.showPreview = False
        self.runThread = True
        self.canDisplay = False
        self.clientWindow = Tk()
        self.setupWindow()
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)
        self.video = cv2.VideoCapture(0)
        self.nickname = ""
        self.msg_to_send = ""
    
    def setupWindow(self):
        self.clientWindow.title("Chat Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=600, height=550, bg=bg_color)

        # Header with user info
        self.head_label = Label(self.clientWindow, bg=bg_color, fg=text_color, text="Username:", pady=10)
        self.head_label.place(relwidth=(470/600))

        # Chat window
        self.chat_window = Text(self.clientWindow, width=20, height=2, bg=bg_color, fg=text_color, padx=4,pady=4)
        self.chat_window.place(relheight=0.675, relwidth=(470/600), rely=0.1)
        self.chat_window.configure(state=DISABLED)

        # Stream video
        self.send_video = Button(self.clientWindow, text="Share Video", width=40, bg=bg_bottom, command=self.shareVideo)
        self.send_video.place(relx=0.79, rely=0.27, relheight=0.07, relwidth=0.18)
        self.send_video.configure(state=DISABLED)

        # Display preview
        self.show_preview = Button(self.clientWindow, text="Show Preview", width=40, bg=bg_bottom, command=self.allowPreview)
        self.show_preview.place(relx=0.79, rely=0.38, relheight=0.07, relwidth=0.18)

        # Stream audio
        # self.send_audio = Button(self.clientWindow, text="Mic Off", width=40, bg=bg_bottom, command=self.allowAudio)
        # self.send_audio.place(relx=0.79, rely=0.49, relheight=0.07, relwidth=0.18)

        # Scrollbar
        scrollbar = Scrollbar(self.chat_window)
        scrollbar.place(relheight=1, relx=0.967)
        scrollbar.configure(command=self.chat_window.yview)

        # Bottom label
        bottom_label = Label(self.clientWindow, bg=bg_bottom, height=80)
        bottom_label.place(relwidth=(470/600), rely=0.8)
        
        # User input area
        self.user_input = Entry(bottom_label, bg=bg_entry, fg=text_color)
        self.user_input.place(relwidth=0.75, relheight=0.05, rely=0.01, relx=0.01)
        self.user_input.bind("<Return>", self.pressedEnter)
        self.user_input.configure(state=DISABLED)

        # Button for sending
        send_button = Button(bottom_label, text="Send", width=20, bg=bg_bottom, command=lambda: self.pressedEnter(None))
        send_button.place(relx=0.7, rely=0.01, relheight=0.05, relwidth=0.2)
    
    def connect(self):
        self.user_chat.connect((host_ip, chatPort))
        self.user_vid.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)

    def run(self):
        try:
            self.connect()
        except:
            print("Servers are down. Try again later.")

        self.receive_thread = threading.Thread(target=self.receiveChat)
        self.receive_thread.start()

        self.write_thread = threading.Thread(target=self.write)
        self.write_thread.start()

        self.receive_thread = threading.Thread(target=self.receiveVideo)
        self.receive_thread.start()

        self.send_thread = threading.Thread(target=self.sendVideo)
        self.send_thread.start()

        self.preview_thread = threading.Thread(target=self.displayPreview)
        self.preview_thread.start()

        self.clientWindow.mainloop()
    
    def pressedEnter(self, event):
        msg = self.user_input.get()
        self.sendMessage(msg, "You")

    def sendMessage(self, msg, sender):
        if not msg:
            return
        
        # Clear user input
        self.user_input.delete(0, END)

        # If chat client does not have a nickname, assign one
        if not self.nickname and sender == "You":
            self.nickname = msg
            self.msg_to_send = msg
            self.sendMessage(f"Your username is: {self.nickname}", "")
            self.head_label.configure(text=f"Username: {self.nickname}")
            return

        # Use f string to format messages
        msg1 = f"{msg}\n"

        # Format message
        if sender == "You":
            new_msg = f"{self.nickname}: {msg}"
            # Send message to server
            self.msg_to_send = new_msg
            msg1 = f"{sender}: {msg}\n"

        # Must allow chat window to be configured temporarily when a new message is added
        self.chat_window.configure(state=NORMAL)
        self.chat_window.insert(END, msg1)
        self.chat_window.configure(state=DISABLED)

        # Scroll to the bottom of the chat window everytime a new message is sent
        self.chat_window.see(END)

    def receiveChat(self):
        while self.runThread:
            try:
                message = self.user_chat.recv(1024).decode('ascii')
                if message == 'NAME':
                    self.user_input.configure(state=NORMAL)
                    self.sendMessage("Enter a username", "")
                elif message == 'STARTVID':
                    self.canDisplay = True
                elif message == 'ENDVID':
                    self.canDisplay = False
                elif message == "Connected to the server!":
                    self.send_video.configure(state=NORMAL)
                    self.user_vid.sendto(f"FIRST:{self.nickname}".encode('ascii'), (host_ip, videoPort))
                else:
                    self.sendMessage(message, "")
            except:
                break
    
    # Send a message if it isn't empty
    def write(self):
        while self.runThread:
            if self.msg_to_send != "":
                self.user_chat.send(self.msg_to_send.encode('ascii'))
                self.msg_to_send = ""
    
    # FUNCTIONS FOR VIDEO CHAT
    # Toggle share video
    def shareVideo(self):
        self.showVideo = not self.showVideo
        if not self.showVideo:
            self.send_video['text'] = 'Share Video'
        else:
            self.send_video['text'] = 'End Video'
            # SEND START
            self.user_chat.send("STARTVID".encode('ascii'))
    
    # Toggle audio
    # def allowAudio(self):
        # self.shareAudio = not self.shareAudio
        # if not self.shareAudio:
            # self.send_audio['text'] = 'Mic On'
        # else:
            # self.send_audio['text'] = 'Mic Off'
    
    # Toggle viewing preview
    def allowPreview(self):
        self.showPreview = not self.showPreview
        if not self.showPreview:
            self.show_preview['text'] = 'Show Preview'
        else:
            self.show_preview['text'] = 'End Preview'
    
    # Show preview of video
    def displayPreview(self):
        while self.runThread:
            WIDTH = 400
            fps, st, frame_count, cnt = (0, 0, 20, 0)
            while self.showPreview:
                _,frame = self.video.read()
                frame = imutils.resize(frame,width=WIDTH)

                frame = cv2.putText(frame,"FPS: "+str(fps), (10,40), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
                cv2.imshow("Preview of Video",frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or self.showPreview == False:
                    cv2.destroyWindow("Preview of Video")
                    break
                if cnt == frame_count:
                    try:
                        fps = round(frame_count/(time.time()-st))
                        st=time.time()
                        cnt=0
                    except:
                        pass
                cnt+=1
            try:
                cv2.destroyWindow("Preview of Video")
            except:
                pass
    
    # Send video to UDP server
    def sendVideo(self):
        while self.runThread:
            WIDTH = 400
            doneStreaming = False
            while self.showVideo:
                if not doneStreaming:
                    self.user_chat.send("STARTVID".encode('ascii'))
                    doneStreaming = True
                _,frame = self.video.read()
                frame = imutils.resize(frame,width=WIDTH)
                encoded,buffer = cv2.imencode('.jpg',frame)
                self.user_vid.sendto(buffer, (host_ip, videoPort))

            if doneStreaming and not self.showVideo:
                self.user_chat.send("ENDVID".encode('ascii'))
                doneStreaming = False

    # Receive video content from clients via UDP server
    def receiveVideo(self):
        fps, st, frame_count, cnt = (0, 0, 20, 0)
        while self.runThread:
            while self.canDisplay:
                packet,_ = self.user_vid.recvfrom(buffer_size)
                npdata = np.frombuffer(packet,dtype=np.uint8)
                frame = cv2.imdecode(npdata, 1)

                # Display framerate
                frame = cv2.putText(frame,"FPS: "+str(fps), (10,40), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
                cv2.imshow("Receiving Video",frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                if cnt == frame_count:
                    try:
                        fps = round(frame_count/(time.time()-st))
                        st=time.time()
                        cnt=0
                    except:
                        pass

                cnt+=1
            try:
                cv2.destroyWindow("Receiving Video")
            except:
                pass
    
    # Handles closing client (closes all threads and sockets)
    def quit(self):
        self.user_chat.close()
        self.user_vid.sendto("BYE".encode('ascii'), (host_ip, videoPort))
        self.user_vid.close()
        self.showPreview = False
        self.showVideo = False
        cv2.destroyAllWindows()
        self.runThread = False
        self.clientWindow.destroy()

if __name__ == '__main__':
    chat_client = ChatClient()
    chat_client.run()
    