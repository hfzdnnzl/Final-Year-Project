
import cv2
import dlib
import torch
import GANnotation
import imutils
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class demoFx:
    def __init__(self,image_path = 'test_images/test_1.jpg'):
        # facial landmarks
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
        # process base image
        self.test_image = cv2.cvtColor(cv2.imread(image_path),cv2.COLOR_BGR2RGB)
        self.test_image = self.test_image/255.0
        self.test_image = torch.from_numpy(self.test_image.swapaxes(2,1).swapaxes(1,0))
        self.test_image = self.test_image.type_as(torch.FloatTensor())
        
    def webcamFrame(self,Image):
        Image = cv2.cvtColor(Image, cv2.COLOR_BGR2RGB)
        Image = QImage(Image.data,
                       Image.shape[1],
                       Image.shape[0],
                       QImage.Format_RGB888)
        Image = QPixmap.fromImage(Image)
        return Image
    
    def facialLandmarksFrame(self,Image):
        # blank canva
        blank = np.zeros((360,640,3),dtype=np.uint8)
        # detect face
        Gray = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(Gray)
        for face in faces:
            landmarks = self.predictor(Gray,face)
            for n in range(68):
                cv2.circle(blank,(landmarks.part(n).x,landmarks.part(n).y),2,(200,75,49),-1)
            break
        blank = QImage(blank.data,
                       blank.shape[1],
                       blank.shape[0],
                       QImage.Format_RGB888)
        blank = QPixmap.fromImage(blank)
        return blank
    
    def facialReenactmentFrame(self,Image,enable_cuda=False):
        # gan model
        self.myGAN = GANnotation.GANnotation(path_to_model='models/myGEN.pth',enable_cuda=enable_cuda)
        # detect face
        Gray = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(Gray)
        for face in faces:
            landmarks = self.predictor(Gray,face)
            # get points
            points = []
            for n in range(68):
                if n==60 or n==64:
                    continue
                points.append(landmarks.part(n).x)
                points.append(landmarks.part(n).y)
            points = np.array(points)
            points = points.transpose().reshape(66,2,-1)
            # get facial reenactment images
            image, _ = self.myGAN.reenactment(self.test_image,points)
            image = cv2.resize(image[0],(400,400))
            break
        image = QImage(image.data,
                        image.shape[1],
                        image.shape[0],
                        QImage.Format_RGB888)
        image = QPixmap.fromImage(image)
        return image

class onCamera(QThread):
    ImageUpdate = pyqtSignal(np.ndarray)
    
    def run(self):
        self.ThreadActive = True
        self.Capture = cv2.VideoCapture(0)
        
        while self.ThreadActive:
            ret, frame = self.Capture.read()
            if not ret:
                continue
            frame = imutils.resize(frame, width=640)
            self.ImageUpdate.emit(frame)
                
    def stop(self):
        self.ThreadActive = False
        try:
            self.Capture.release() 
        except:
            print('camera released')
        self.terminate()