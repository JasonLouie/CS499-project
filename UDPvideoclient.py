import cv2, imutils, socket, numpy as np, time, base64, threading
from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"
buffer_size = 65536
host_ip = '68.237.86.46'
port = 55666

message = "First Time"

class VideoClient:
    def __init__ (self):
        self.video = cv2.VideoCapture(0)
        self.runThread = True
        self.showVideo = False
        self.showPreview = True
        self.clientWindow = Tk()
        self.setupWindow()
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)

    def setupWindow(self):
        self.clientWindow.title("Video Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=400, height=400, bg=bg_color)

        self.send_button = Button(self.clientWindow, text="Share Video", width=80, bg=bg_bottom, command=self.shareVideo)
        self.send_button.place(relx=0.5, rely=0.03, relheight=0.07, relwidth=0.35)
    
    def shareVideo(self):
        self.showVideo = not self.showVideo
        if not self.showVideo:
            self.send_button['text'] = 'Share Video'
        else:
            self.send_button['text'] = 'Stop Sharing Video'

    def run(self):
        self.receive_thread = threading.Thread(target=self.receiveVideo)
        self.receive_thread.start()

        self.send_thread = threading.Thread(target=self.sendVideo)
        self.send_thread.start()

        self.clientWindow.mainloop()

    def quit(self):
        video_socket.close()
        self.video.release()
        self.runThread = False
        self.clientWindow.destroy()

    def sendVideo(self):
        fps, st, frame_count, cnt = (0, 0, 20, 0)

        while self.runThread:
            WIDTH = 400
            while self.showVideo:
                _,frame = self.video.read()
                frame = imutils.resize(frame,width=WIDTH)
                encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
                message = base64.b64encode(buffer)
                video_socket.sendto(message, (host_ip, port))

                if self.showPreview:
                    frame = cv2.putText(frame,"FPS: "+str(fps), (10,40), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
                    cv2.imshow("Preview of Video",frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or self.showVideo == False:
                        print("Preview closed")
                        cv2.destroyAllWindows()
                        break
                    if cnt == frame_count:
                        try:
                            fps = round(frame_count/(time.time()-st))
                            st=time.time()
                            cnt=0
                        except:
                            pass
                    cnt+=1

    def receiveVideo(self):
        fps, st, frame_count, cnt = (0, 0, 20, 0)
        while self.runThread:
            packet,_ = video_socket.recvfrom(buffer_size)
            data = base64.b64decode(packet, ' /')
            npdata = np.frombuffer(data,dtype=np.uint8)
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

if __name__ == '__main__':
    try:
        video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        video_socket.sendto(message.encode('ascii'), (host_ip, port))
        video_client = VideoClient()
        video_client.run()
    except:
        print("UDP Video Server is offline. Please try again later.")