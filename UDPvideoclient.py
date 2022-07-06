import cv2, imutils, socket, numpy as np, time, threading
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
        self.showPreview = False
        self.clientWindow = Tk()
        self.setupWindow()
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)

    def setupWindow(self):
        self.clientWindow.title("Video Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=400, height=400, bg=bg_color)

        self.send_video = Button(self.clientWindow, text="Share Video", width=80, bg=bg_bottom, command=self.shareVideo)
        self.send_video.place(relx=0.5, rely=0.03, relheight=0.07, relwidth=0.35)

        self.show_preview = Button(self.clientWindow, text="Show Preview", width=80, bg=bg_bottom, command=self.allowPreview)
        self.show_preview.place(relx=0.5, rely=0.14, relheight=0.07, relwidth=0.35)
    
    def allowPreview(self):
        self.showPreview = not self.showPreview
        if not self.showPreview:
            self.show_preview['text'] = 'Share Preview'
        else:
            self.show_preview['text'] = 'Stop Displaying Preview'

    def shareVideo(self):
        self.showVideo = not self.showVideo
        if not self.showVideo:
            self.send_video['text'] = 'Share Video'
            video_server.sendto("END".encode('ascii'), (host_ip,port))
        else:
            self.send_video['text'] = 'Stop Sharing Video'

    def run(self):
        self.receive_thread = threading.Thread(target=self.receiveVideo)
        self.receive_thread.start()

        self.send_thread = threading.Thread(target=self.sendVideo)
        self.send_thread.start()

        self.clientWindow.mainloop()

    def quit(self):
        video_server.close()
        self.video.release()
        self.runThread = False
        self.clientWindow.destroy()
        cv2.destroyAllWindows()

    def sendVideo(self):
        fps, st, frame_count, cnt = (0, 0, 20, 0)

        while self.runThread:
            WIDTH = 400
            while self.showVideo:
                _,frame = self.video.read()
                frame = imutils.resize(frame,width=WIDTH)
                encoded,buffer = cv2.imencode('.jpg',frame)
                video_server.sendto(buffer, (host_ip, port))

                if self.showPreview:
                    frame = cv2.putText(frame,"FPS: "+str(fps), (10,40), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
                    cv2.imshow("Preview of Video",frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or self.showVideo == False or self.showPreview == False:
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
                else:
                    cv2.destroyAllWindows()

    def receiveVideo(self):
        fps, st, frame_count, cnt = (0, 0, 20, 0)

        while self.runThread:
            packet,_ = video_server.recvfrom(buffer_size)
            try:
                if packet.decode('ascii') == "END":
                    print("No more video source")
                    cv2.destroyAllWindows()
            except:
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

if __name__ == '__main__':
    try:
        video_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        video_server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        video_server.sendto(message.encode('ascii'), (host_ip, port))
        video_client = VideoClient()
        video_client.run()
    except:
        print("UDP Video Server is offline. Please try again later.")