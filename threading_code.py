# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 10:50:12 2022

@author: hafiz
"""

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
import cv2
import time

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.VBL = QVBoxLayout()
        
        self.blank = QImage(np.zeros((640, 480, 3)), 
                            640,480,QImage.Format_RGB888)
        self.FeedLabel = QLabel()
        self.FeedLabel.setPixmap(QPixmap.fromImage(self.blank))
        self.VBL.addWidget(self.FeedLabel)
        
        self.startBTN = QPushButton("Start")
        self.startBTN.clicked.connect(self.StartFeed)
        self.VBL.addWidget(self.startBTN)
        
        self.CancelBTN = QPushButton("Stop")
        self.CancelBTN.setEnabled(False)
        self.CancelBTN.clicked.connect(self.CancelFeed)
        self.VBL.addWidget(self.CancelBTN)
        
        self.setLayout(self.VBL)
        
    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))
        
    def StartFeed(self):
        self.Worker1 = Worker1()
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.startBTN.setEnabled(False)
        self.CancelBTN.setEnabled(True)
        
    def CancelFeed(self):
        self.Worker1.stop()
        self.FeedLabel.setPixmap(QPixmap.fromImage(self.blank))
        self.startBTN.setEnabled(True)
        self.CancelBTN.setEnabled(False)
        
        
class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    
    def run(self):
        self.ThreadActive = True
        self.Capture = cv2.VideoCapture(0)
        while self.ThreadActive:
            ret, frame = self.Capture.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                Pic = QImage(Image.data, 
                             Image.shape[1], 
                             Image.shape[0],
                             QImage.Format_RGB888)
                Pic = Pic.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
                
    def stop(self):
        self.ThreadActive = False
        self.Capture.release()
        self.quit()
        
if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())