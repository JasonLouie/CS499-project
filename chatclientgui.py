import socket, threading
from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"

user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user.connect(('68.237.86.46', 55555))

class ChatClient:
    def __init__(self):
        self.runThread = True
        self.clientWindow = Tk()
        self.setupWindow()
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)
        self.nickname = ""
        self.msg_to_send = ""
        self.prev_msg = ""
        
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

        self.write_thread = threading.Thread(target=self.write)
        self.write_thread.start()
    
    def setupWindow(self):
        self.clientWindow.title("Chat Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=470, height=550, bg=bg_color)

        # Header with user info

        self.head_label = Label(self.clientWindow, bg=bg_color, fg=text_color, text="Username:", pady=10)
        self.head_label.place(relwidth=1)

        # Chat window
        self.chat_window = Text(self.clientWindow, width=20, height=2, bg=bg_color, fg=text_color, padx=4,pady=4)
        self.chat_window.place(relheight=0.675, relwidth=1, rely=0.1)
        self.chat_window.configure(state=DISABLED)

        # Scrollbar
        scrollbar = Scrollbar(self.chat_window)
        scrollbar.place(relheight=1, relx=0.967)
        scrollbar.configure(command=self.chat_window.yview)

        # Bottom label
        bottom_label = Label(self.clientWindow, bg=bg_bottom, height=80)
        bottom_label.place(relwidth=1, rely=0.8)
        
        # User input area
        self.user_input = Entry(bottom_label, bg=bg_entry, fg=text_color)
        self.user_input.place(relwidth=0.75, relheight=0.05, rely=0.01, relx=0.01)
        self.user_input.focus()
        self.user_input.bind("<Return>", self.pressedEnter)

        # Button for sending
        send_button = Button(bottom_label, text="Send", width=20, bg=bg_bottom, command=lambda: self.pressedEnter(None))
        send_button.place(relx=0.7, rely=0.01, relheight=0.05, relwidth=0.2)
    
    def run(self):
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
            self.head_label
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
            self.prev_msg = new_msg
            msg1 = f"{sender}: {msg}\n"

        # Must allow chat window to be configured temporarily when a new message is added
        self.chat_window.configure(state=NORMAL)
        self.chat_window.insert(END, msg1)
        self.chat_window.configure(state=DISABLED)

        # Scroll to the bottom of the chat window everytime a new message is sent
        self.chat_window.see(END)

    def receive(self):
        while self.runThread:
            try:
                message = user.recv(1024).decode('ascii')
                if message == 'NAME':
                    self.sendMessage("Enter a username: ", "")
                elif self.prev_msg != message:
                    self.sendMessage(message, "")
            except:
                user.close()
                break

    def write(self):
        while self.runThread:
            if self.msg_to_send != "":
                user.send(self.msg_to_send.encode('ascii'))
                self.msg_to_send = ""
    
    def quit(self):
        user.close()
        self.runThread = False
        self.clientWindow.destroy()

if __name__ == '__main__':
    chat_client = ChatClient()
    chat_client.run()