import socket,struct,cv2,pyaudio,pickle
import imutils,dlib,time,torch,GANnotation,sys
import numpy as np
from PyQt5.QtCore import *

class audioReceiver(QThread):
    voiceReceive = pyqtSignal(str)

    def __init__(self,host,port,format=pyaudio.paInt16,channels=1,
    rate=44100,frames_per_buffer=4096):
        super(QThread,self).__init__()
        # initiate port
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.bind((self.host,self.port))
        self.server.listen()
        # initiate audio
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=format,
            channels=channels,
            rate = rate,
            output=True,
            frames_per_buffer=frames_per_buffer)
        self.frames_per_buffer = frames_per_buffer

    def run(self):
        # connecting to socket
        self.threadActive = True
        com_socket, address = self.server.accept()
        print(f"Audio receiver connected to {address}")
        self.voiceReceive.emit(address[0])
        
        while self.threadActive:
            try:
                message = com_socket.recv(self.frames_per_buffer)
                if message!=b'':self.stream.write(message)
            except:
                print("Error getting audio")
                self.voiceReceive.emit("Closing")
                break

    def stop(self):
        self.threadActive = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.terminate()

class audioSender(QThread):
    voiceSend = pyqtSignal(str)

    def __init__(self,host,port,format=pyaudio.paInt16,channels=1,
    rate=44100, frames_per_buffer=4096,mute = True):
        super(QThread,self).__init__()
        # initiate port
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect((self.host,self.port))
        # initiate audio
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=format,
            channels=channels,
            rate = rate,
            input=True,
            frames_per_buffer=frames_per_buffer)
        self.frames_per_buffer = frames_per_buffer
        self.mute = mute
        
    def run(self):
        # connecting to socket
        self.Thread = True
        while self.Thread:
            try:
                if self.mute:
                    self.client.send("".encode('utf-8'))
                    time.sleep(1)
                else:
                    message = self.stream.read(self.frames_per_buffer)
                    self.client.send(message)
            except:
                print("Error sending audio")
                break
    
    def stop(self):
        self.Thread = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.terminate()


class videoReceiver(QThread):
    videoReceive = pyqtSignal(np.ndarray)

    def __init__(self,host,port):
        super(QThread,self).__init__()
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.bind((self.host,self.port))
        self.server.listen()

    def run(self):
        np.warnings.filterwarnings('error', category=np.VisibleDeprecationWarning)
        com_socket, address = self.server.accept()
        print(f"Video receiver connected to {address}")
        self.ThreadActive = True
        # frame rate init
        pTime, currentFPS, currentBPS = 0,0,0
        fps, bps = [],[]

        while self.ThreadActive:
            payload_size = struct.calcsize('>L')
            data = b''
            while self.ThreadActive:
                while len(data)<payload_size:
                    try:message = com_socket.recv(4096)
                    except:
                        print("Error getting video")
                        time.sleep(1)
                        break
                    if message == b'':break
                    data += message

                if data ==b'':break
                if message ==b'':break

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(">L",packed_msg_size)[0]

                while len(data)<msg_size:
                    message = com_socket.recv(4096)
                    data += message

                frame_data = data[:msg_size]
                data = data[msg_size:]
                frame = pickle.loads(frame_data,fix_imports=True,encoding='bytes')
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                # count frame rate
                cTime = time.time()
                dTime = cTime-pTime
                if dTime!=0: fps.append(1/dTime)
                pTime = cTime
                # update frame rate
                bps.append(sys.getsizeof(frame_data)*currentFPS)
                if len(fps)>=10:
                    currentFPS = int(np.mean(fps))
                    currentBPS = int(np.mean(bps))
                    fps,bps = [],[]
                # object
                frame_list = np.array([frame,currentFPS,currentBPS],dtype=object)
                self.videoReceive.emit(frame_list)

    def stop(self):
        self.ThreadActive = False
        self.terminate()

class videoSender(QThread):
    videoSend = pyqtSignal(np.ndarray)

    def __init__(self,host,port,cameraOff=True):
        super(QThread,self).__init__()
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect((self.host,self.port))
        self.cameraOff = cameraOff

    def run(self):
        np.warnings.filterwarnings('error', category=np.VisibleDeprecationWarning)
        self.ThreadActive = True
        while self.ThreadActive:
            try:
                if self.cameraOff:
                    self.client.sendall(''.encode('utf-8'))
                    time.sleep(1)
                    continue
                else:
                    # frame rate init
                    pTime, currentFPS, currentBPS = 0,0,0
                    fps, bps = [],[]

                    self.Capture = cv2.VideoCapture(0)
                    while not self.cameraOff:
                        ret, frame = self.Capture.read()
                        if not ret:
                            continue
                        # reformat data
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame = imutils.resize(frame,width=640)
                        # send data
                        _ , decoded = cv2.imencode('.jpg',frame,
                        [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                        data = pickle.dumps(decoded,0)
                        message = struct.pack(">L",len(data))+data
                        # calculate frame rate
                        cTime = time.time()
                        dTime = cTime-pTime
                        if dTime!=0: fps.append(1/dTime)
                        pTime = cTime
                        # update frame rate
                        bps.append(sys.getsizeof(data)*currentFPS)
                        if len(fps)>=10:
                            currentFPS = int(np.mean(fps))
                            currentBPS = int(np.mean(bps))
                            fps, bps = [],[]
                        # send data
                        frame_list = np.array([frame,currentFPS,currentBPS],
                        dtype=object)
                        self.videoSend.emit(frame_list)
                        self.client.sendall(message)
                    self.Capture.release()
            except:
                print("Error sending video")
                break

    def stop(self):
        self.ThreadActive = False
        try:self.Capture.release()
        except:print("Camera unused")
        self.terminate()


class landmarkReceiver(QThread):
    landmarkReceive = pyqtSignal(np.ndarray)

    def __init__(self,host,port,image_path='test_images/test_1.jpg',
    path_to_model='models/myGEN.pth',enable_cuda=True,ganOff=True,skipMax=10):
        super(QThread,self).__init__()
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.bind((self.host,self.port))
        self.server.listen()
        # gan model
        self.myGAN = GANnotation.GANnotation(path_to_model=path_to_model,enable_cuda=enable_cuda)
        # process base image
        self.test_image = cv2.cvtColor(cv2.imread(image_path),cv2.COLOR_BGR2RGB)
        self.test_image = self.test_image/255.0
        self.test_image = torch.from_numpy(self.test_image.swapaxes(2,1).swapaxes(1,0))
        self.test_image = self.test_image.type_as(torch.FloatTensor())
        # gan state
        self.ganOff = ganOff
        self.skipMax = skipMax

    def run(self):
        np.warnings.filterwarnings('error', category=np.VisibleDeprecationWarning)
        com_socket, address = self.server.accept()
        self.server.settimeout(5)
        print(f"Landmarks receiver connected to {address}")
        self.ThreadActive = True
        # frame rate init
        skipIter, pTime, currentFPS, currentBPS = 0,0,0,0
        fps,bps = [],[]

        while self.ThreadActive:
            try:
                message = com_socket.recv(4096)
                # count frame rate
                cTime = time.time()
                dTime = cTime-pTime
                if dTime!=0: fps.append(1/dTime)
                pTime = cTime
                # update frame rate
                bps.append(sys.getsizeof(message)*currentFPS)
                if len(fps)>=10:
                    currentFPS = int(np.mean(fps))
                    currentBPS = int(np.mean(bps))
                    fps,bps = [],[]
            except:
                print("Error getting facial landmarks")
                time.sleep(1)
                break
            try:message = pickle.loads(message)
            except: 
                print("Unable to load facial landmarks")
                continue

            if type(message) is str:
                if message == 'camera off':
                    self.landmarkReceive.emit(np.array(['']))
                    time.sleep(1)
            elif self.ganOff:
                blank = 255*np.ones((360,640,3),dtype=np.uint8)
                for point in message:
                    cv2.circle(blank, (int(point[0]), int(point[1])), 2, (33,147,176), -1)
                # send data
                blank_list = np.array([blank,currentFPS,currentBPS],dtype=object)
                self.landmarkReceive.emit(blank_list)
            elif not self.ganOff and skipIter%10==0:
                image, _ = self.myGAN.reenactment(self.test_image,message)
                image = cv2.resize(image[0],(400,400))
                # send data
                image_list = np.array([image,currentFPS,currentBPS],dtype=object)
                self.landmarkReceive.emit(image_list)
                skipIter = 0
            skipIter += 1

    def stop(self):
        self.ThreadActive = False
        self.terminate()

class landmarkSender(QThread):
    landmarkSend = pyqtSignal(np.ndarray)

    def __init__(self,host,port,detectorOff=True):
        super(QThread,self).__init__()
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect((self.host,self.port))
        self.detectorOff = detectorOff
        # detector functions
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')

    def run(self):
        np.warnings.filterwarnings('error', category=np.VisibleDeprecationWarning)
        self.ThreadActive = True
        self.cameraOff = True
        while self.ThreadActive:
            try:
                if self.detectorOff and self.cameraOff:
                    self.landmarkSend.emit(np.array(['']))
                    self.client.send(pickle.dumps('camera off'))
                    time.sleep(1)
                elif not self.detectorOff and not self.cameraOff:
                    # frame rate init
                    pTime, currentFPS, currentBPS = 0,0,0
                    fps, bps = [],[]

                    self.Capture = cv2.VideoCapture(0)
                    while not self.detectorOff:
                        # capture image
                        ret, frame = self.Capture.read()
                        if not ret:
                            continue
                        # reformat image
                        frame = imutils.resize(frame,width=640)
                        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                        # detect face
                        faces = self.detector(gray)
                        if len(faces) == 0: continue
                        face = faces[0]
                        landmarks = self.predictor(gray,face)
                        # get facial landmark points
                        blank = 255*np.ones((360,640,3),dtype=np.uint8)
                        points = []
                        for n in range(68):
                            if n==60 or n==64:
                                continue
                            points.append(landmarks.part(n).x)
                            points.append(landmarks.part(n).y)
                            # draw facial landmarks
                            cv2.circle(blank,(landmarks.part(n).x,landmarks.part(n).y),2,(33,147,176),-1)
                        # reshape image
                        points = np.array(points)
                        points = points.transpose().reshape(66,2,-1)
                        # send data
                        data = pickle.dumps(points)
                        self.client.send(data)
                        # count frame rate
                        cTime = time.time()
                        dTime = cTime-pTime
                        if dTime!=0: fps.append(1/dTime)
                        pTime = cTime
                        # update frame rate
                        bps.append(sys.getsizeof(data)*currentFPS)
                        if len(fps)>=10:
                            currentFPS = int(np.mean(fps))
                            currentBPS = int(np.mean(bps))
                            fps, bps = [],[]
                        # emit data
                        blank_list = np.array([blank,currentFPS,currentBPS],dtype=object)
                        self.landmarkSend.emit(blank_list)
                    # release camera
                    self.Capture.release()
            except:
                print("Error sending facial landmarks")
                break
    
    def stop(self):
        self.ThreadActive = False
        self.terminate()