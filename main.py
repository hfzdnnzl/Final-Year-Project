# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 15:57:38 2022

@author: hafiz
"""

from ipaddress import ip_address
import sys
import demo
import conference
import numpy as np
import pyperclip as pc
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MainWindow(QDialog):

    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi("user_interfaces/home.ui",self)
        self.demoButton.clicked.connect(self.goToDemoScreen)
        self.joinButton.clicked.connect(self.clientConference)
        self.createButton.clicked.connect(self.serverConference)

    def clientConference(self):
        widget.setCurrentIndex(1)
        local_ip = self.local_ip_address_lineEdit.text().strip()
        client_ip = self.client_ip_address_lineEdit.text().strip()
        widget.currentWidget().local_ip_address_label.setText("Local IP Address: "+local_ip)
        widget.currentWidget().client_ip_address_label.setText("Client IP Address: "+client_ip)
        widget.currentWidget().startListening()

        
    def serverConference(self):
        widget.setCurrentIndex(1)
        # add ip address label
        local_ip = self.local_ip_address_lineEdit.text().strip()
        widget.currentWidget().local_ip_address_label.setText("Local IP Address: " + local_ip)
        widget.currentWidget().startListening()
        widget.currentWidget().audio_receiver.voiceReceive.connect(widget.currentWidget().serverRespond)

    def goToDemoScreen(self):
        widget.setCurrentIndex(2)

### CODING BELOW
class ConferenceWindow(QDialog):
    def __init__(self):
        super(ConferenceWindow,self).__init__()
        loadUi("user_interfaces/conference.ui",self)
        # assign button value
        self.copyIPButton.clicked.connect(self.copyIP)
        self.mainPageButton.clicked.connect(self.goToMainScreen)
        # ip address
        self.local_ip = self.local_ip_address_label.text().replace("Local IP Address: ","")
        self.client_ip = self.client_ip_address_label.text().replace("Client IP Address: ","")

    def startListening(self):
        self.audio_receiver = conference.audioReceiver(self.local_ip,9010)
        self.audio_receiver.start()

    def startSending(self):
        self.audio_sender = conference.audioSender(self.client_ip,9010)
        self.audio_sender.start()

    def serverRespond(self,ip_address):
        self.client_ip = ip_address
        self.client_ip_address_label.setText("Client IP Address: "+ip_address)
        self.startSending()

    def goToMainScreen(self):
        try:
            self.audio_receiver.stop()
            self.audio_sender.stop()
        except:
            print("Audio sender was never started")
        widget.setCurrentIndex(0)

    def copyIP(self):
        pc.copy(self.local_ip)
### CODING ABOVE

class DemoWindow(QDialog):
    def __init__(self):
        super(DemoWindow,self).__init__()
        loadUi("user_interfaces/demo.ui",self)
        # connect buttons
        self.startCameraButton.clicked.connect(self.startCamera)
        self.facialLandmarksButton.clicked.connect(self.FacialLandmarks)
        self.facialReenactmentButton.clicked.connect(self.FacialReenactment)
        self.mainPageButton.clicked.connect(self.goToMainScreen)
        # demo function
        self.demoFx = demo.demoFx()
        # camera class
        self.onCamera = demo.onCamera()
        # gan iter
        self.gan_iter = 0
        self.gan_iter_max = 5

    def goToMainScreen(self):
        self.stopCamera()
        widget.setCurrentIndex(0)
        
    def localImageUpdateSlot(self, Image):
        Image = self.demoFx.webcamFrame(Image)
        self.localCameraLabel.setPixmap(Image)
        
    def demoImageUpdateSlotv1(self, Image):
        blank = self.demoFx.facialLandmarksFrame(Image)
        self.clientCameraLabel.setPixmap(blank)
        
    def demoImageUpdateSlotv2(self, Image):
        if self.gan_iter%self.gan_iter_max==0:
            image = self.demoFx.facialReenactmentFrame(Image)
            self.clientCameraLabel.setPixmap(image)
        # iterate
        self.gan_iter += 1
        if self.gan_iter==self.gan_iter_max:
            self.gan_iter = 0
        
    def startCamera(self):
        if self.startCameraButton.text() == 'Start camera':
            self.onCamera.start()
            self.onCamera.ImageUpdate.connect(self.localImageUpdateSlot)
            # change button enable status
            self.facialLandmarksButton.setEnabled(True)
            self.facialReenactmentButton.setEnabled(True)
            # start button status
            self.startCameraButton.setStyleSheet('background-color:rgb(208, 52, 44);')
            self.startCameraButton.setText('Stop camera')
            
        elif self.startCameraButton.text() == 'Stop camera':
            self.stopCamera()
        
    def stopCamera(self):
        if self.onCamera.isRunning():
            self.onCamera.stop()
        # reset frame
        self.localCameraLabel.setText("Local Camera")
        self.clientCameraLabel.setText("Demo Frames")
        # button enable status
        self.facialLandmarksButton.setEnabled(False)
        self.facialReenactmentButton.setEnabled(False)
        # start button status
        self.startCameraButton.setStyleSheet('background-color: rgb(236, 219, 186);')
        self.startCameraButton.setText('Start camera')
        
    def FacialLandmarks(self):
        # close other button
        try:
            self.onCamera.ImageUpdate.disconnect(self.demoImageUpdateSlotv2)
            self.clientCameraLabel.setText("Demo Frames")
            self.facialReenactmentButton.setStyleSheet('background-color:rgb(236, 219, 186);')
            self.facialReenactmentButton.setText('Show facial reenactment')
        except:
            print('function detached')
        # start process
        if self.clientCameraLabel.text() == 'Demo Frames':
            self.onCamera.ImageUpdate.connect(self.demoImageUpdateSlotv1)
            self.facialLandmarksButton.setStyleSheet('background-color:rgb(208, 52, 44);')
            self.facialLandmarksButton.setText('Hide facial landmarks')
        else:
            self.onCamera.ImageUpdate.disconnect(self.demoImageUpdateSlotv1)
            self.clientCameraLabel.setText("Demo Frames")
            self.facialLandmarksButton.setStyleSheet('background-color:rgb(236, 219, 186);')
            self.facialLandmarksButton.setText('Show facial landmarks')
            
    def FacialReenactment(self):
        # close other button
        try:
            self.onCamera.ImageUpdate.disconnect(self.demoImageUpdateSlotv1)
            self.clientCameraLabel.setText("Demo Frames")
            self.facialLandmarksButton.setStyleSheet('background-color:rgb(236, 219, 186);')
            self.facialLandmarksButton.setText('Show facial landmarks')
        except:
            print('function detached')
        # start process
        if self.clientCameraLabel.text() == 'Demo Frames':
            self.onCamera.ImageUpdate.connect(self.demoImageUpdateSlotv2)
            self.facialReenactmentButton.setStyleSheet('background-color:rgb(208, 52, 44);')
            self.facialReenactmentButton.setText('Hide facial reenactment')
        else:
            self.onCamera.ImageUpdate.disconnect(self.demoImageUpdateSlotv2)
            self.clientCameraLabel.setText("Demo Frames")
            self.facialReenactmentButton.setStyleSheet('background-color:rgb(236, 219, 186);')
            self.facialReenactmentButton.setText('Show facial reenactment')
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()

    mainWindow = MainWindow()
    conferenceWindow = ConferenceWindow()
    demoWindow = DemoWindow()

    local_ip = ''

    widget.addWidget(mainWindow)
    widget.addWidget(conferenceWindow)
    widget.addWidget(demoWindow)

    widget.setFixedHeight(660)
    widget.setFixedWidth(1320)


    widget.show()
    sys.exit(app.exec_())