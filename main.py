# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 15:57:38 2022

@author: hafiz
"""

import sys,demo,conference,time,torch,math
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
        # ip address save code
        local_ip = open('saved_ip/local_ip.txt','r')
        client_ip = open('saved_ip/client_ip.txt','r')
        self.local_ip_address_lineEdit.setText(local_ip.read())
        self.client_ip_address_lineEdit.setText(client_ip.read())
        local_ip.close()
        client_ip.close()
        self.saveAddressCB.setChecked(True)
        if self.local_ip_address_lineEdit.text()=="" and self.client_ip_address_lineEdit.text()=="":
            self.saveAddressCB.setChecked(False)
        self.saveAddressCB.stateChanged.connect(self.saveAddress)
        # check for cuda
        if torch.version.cuda is None:
            self.enableCudaCB.setEnabled(False)
            self.enableCudaCB.setChecked(False)
            self.popupWindow('Note','Cuda is not installed. Cuda will be disabled.',QMessageBox.Warning)

    def saveAddress(self):
        local_ip = open('saved_ip/local_ip.txt','w')
        client_ip = open('saved_ip/client_ip.txt','w')
        if self.saveAddressCB.isChecked():
            local_ip.write(self.local_ip_address_lineEdit.text())
            client_ip.write(self.client_ip_address_lineEdit.text())
        else:
            local_ip.write("")
            client_ip.write("")
        local_ip.close()
        client_ip.close()

    def clientConference(self):
        widget.setCurrentIndex(1)
        # add cuda mod
        widget.currentWidget().enableCuda = self.enableCudaCB.isChecked()
        # add ip address label
        local_ip = self.local_ip_address_lineEdit.text().strip()
        client_ip = self.client_ip_address_lineEdit.text().strip()
        widget.currentWidget().local_ip_address_label.setText("Local IP Address: "+local_ip)
        widget.currentWidget().client_ip_address_label.setText("Client IP Address: "+client_ip)
        widget.currentWidget().local_ip = local_ip
        widget.currentWidget().client_ip = client_ip
        # try connecting
        try:widget.currentWidget().startListening()
        except:
            widget.setCurrentIndex(0)
            self.popupWindow("Error Found","Unable to connect to the local IP address")
            return
        try:widget.currentWidget().startSending()
        except:
            widget.setCurrentIndex(0)
            self.popupWindow("Error Found","Unable to connect to the client IP address")

    def serverConference(self):
        widget.setCurrentIndex(1)
        # add cuda mod
        widget.currentWidget().enableCuda = self.enableCudaCB.isChecked()
        # add ip address label
        local_ip = self.local_ip_address_lineEdit.text().strip()
        widget.currentWidget().local_ip_address_label.setText("Local IP Address: " + local_ip)
        widget.currentWidget().local_ip = local_ip
        widget.currentWidget().client_ip_address_label.setText("Client IP Address: waiting...")
        # try connecting
        try:widget.currentWidget().startListening(True)
        except:
            widget.setCurrentIndex(0)
            self.popupWindow("Error Found","Unable to connect to the local IP address")

    def popupWindow(self,title,errorMessage,Icon=QMessageBox.Critical,frameless=False,buttonless=False):
        self.msg = QMessageBox()
        if frameless:self.msg.setWindowFlags(Qt.FramelessWindowHint)
        if buttonless:self.msg.setStandardButtons(QMessageBox.NoButton)
        self.msg.setWindowTitle(title)
        self.msg.setWindowIcon(QIcon("user_interfaces/sharingan_icon.png"))
        self.msg.setText(errorMessage)
        self.msg.setStyleSheet(
            "QMessageBox{"
            "background-color: QLinearGradient(x1:0, y1:0, x2:1, y2:1, stop: 0 #2193b0, stop: 1 #6dd5ed);"
            "border-radius:15px;border-width :1px;} QLabel{color: white}"
            "QPushButton{"
            "background-color: white;color:#2193b0;border-radius: 10px;width:100px;height:30px;}"
            "QPushButton:hover{"
            "background-color: #2193b0;color: white;border: 1px solid white;}")
        self.msg.setIcon(Icon)
        self.msg.exec_()

    def goToDemoScreen(self):
        widget.setCurrentIndex(2)
        widget.currentWidget().demoFx = demo.demoFx(enable_cuda=self.enableCudaCB.isChecked())


### CODING BELOW
class ConferenceWindow(QDialog):
    def __init__(self):
        super(ConferenceWindow,self).__init__()
        loadUi("user_interfaces/conference.ui",self)
        self.demoFx = demo.demoFx()
        self.enableCuda = False
        # assign button value
        self.copyIPButton.clicked.connect(self.copyIP)
        self.cameraButton.clicked.connect(self.camState)
        self.voiceButton.clicked.connect(self.micState)
        self.facialLandmarksButton.clicked.connect(self.facState)
        self.facialReenactmentButton.clicked.connect(self.ganState)
        self.mainPageButton.clicked.connect(self.goToMainScreen)
        # disable reenactment if cuda is not installed
        if torch.version.cuda is None:
            self.facialReenactmentButtn.setEnabled(False)
        # button styling
        self.selectedButtonStyling = "QPushButton{background-color:red;color:white;}"
        self.selectedButtonStyling += "QPushButton:hover{background-color:rgba(255,0,0,0.5);}"

    def localImageUpdateSlot(self,Image):
        if len(Image)==1:
            self.localCameraLabel.setText("Local Camera")
            self.localFrameLabel.setText("0 fps")
        elif len(Image)>1:
            self.localFrameLabel.setText(str(Image[1]) + " fps")
            self.uploadSizeLabel.setText(self.convert_size(Image[2]))
            Image = Image[0]
            Image = QImage(
                Image.data,
                Image.shape[1],
                Image.shape[0],
                QImage.Format_RGB888)
            Image = QPixmap.fromImage(Image)
            self.localCameraLabel.setPixmap(Image)

    def clientImageUpdateSlot(self,Image):
        if len(Image)==1:
            self.clientCameraLabel.setText("Client Camera")
            self.clientFrameLabel.setText("0 fps")
        elif len(Image)>1:
            self.clientFrameLabel.setText(str(Image[1]) + " fps")
            self.downloadSizeLabel.setText(self.convert_size(Image[2]))
            Image = Image[0]
            Image = QImage(
                Image.data,
                Image.shape[1],
                Image.shape[0],
                QImage.Format_RGB888)
            Image = QPixmap.fromImage(Image)
            self.clientCameraLabel.setPixmap(Image)

    def startListening(self,serverSide=False):
        # audio
        self.audio_receiver = conference.audioReceiver(self.local_ip,9999)
        if serverSide:
            self.audio_receiver.voiceReceive.connect(self.serverRespond)
        self.audio_receiver.start()
        # video
        self.video_receiver = conference.videoReceiver(self.local_ip,7777)
        self.video_receiver.videoReceive.connect(self.clientImageUpdateSlot)
        self.video_receiver.start()
        # landmark
        self.landmarks_receiver = conference.landmarkReceiver(self.local_ip,8888,enable_cuda=self.enableCuda,skipMax=3)
        self.landmarks_receiver.landmarkReceive.connect(self.clientImageUpdateSlot)
        self.landmarks_receiver.start()

    def startSending(self):
        self.audio_receiver.voiceReceive.connect(self.serverClose)
        # audio
        self.audio_sender = conference.audioSender(self.client_ip,9999)
        self.audio_sender.start()
        # video
        self.video_sender = conference.videoSender(self.client_ip,7777)
        self.video_sender.videoSend.connect(self.localImageUpdateSlot)
        self.video_sender.start()
        # landmark
        self.landmarks_sender = conference.landmarkSender(self.client_ip,8888)
        self.landmarks_sender.landmarkSend.connect(self.localImageUpdateSlot)
        self.landmarks_sender.start()

    def serverRespond(self,ip_address):
        self.client_ip = ip_address
        self.client_ip_address_label.setText("Client IP Address: "+ip_address)
        self.audio_receiver.voiceReceive.disconnect(self.serverRespond)
        self.startSending()

    def serverClose(self,message):
        if message!='Closing':return
        print("Closing app")
        self.audio_receiver.stop()
        self.video_receiver.stop()
        self.landmarks_receiver.stop()
        self.audio_sender.stop()
        self.video_sender.stop()
        self.landmarks_sender.stop()
        self.popupWindow("Close","Connection Lost",QMessageBox.Information)
        widget.close()

    def popupWindow(self,title,errorMessage,Icon=QMessageBox.Critical):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setWindowIcon(QIcon("user_interfaces/sharingan_icon.png"))
        msg.setText(errorMessage)
        msg.setStyleSheet(
            "QMessageBox{"
            "background-color: QLinearGradient(x1:0, y1:0, x2:1, y2:1, stop: 0 #2193b0, stop: 1 #6dd5ed);"
            "border-radius:15px;border-width :1px;} QLabel{color: white}"
            "QPushButton{"
            "background-color: white;color:#2193b0;border-radius: 10px;width:100px;height:30px;}"
            "QPushButton:hover{"
            "background-color: #2193b0;color: white;border: 1px solid white;}")
        msg.setIcon(Icon)
        msg.exec_()

    def goToMainScreen(self):
        try:
            self.audio_receiver.stop()
            self.video_receiver.stop()
            self.landmarks_receiver.stop()
            self.audio_sender.stop()
            self.video_sender.stop()
            self.landmarks_sender.stop()
        except:
            print("Some threads were never run")
        self.popupWindow("Close","Connection closed",QMessageBox.Information)
        widget.close()

    def copyIP(self):
        pc.copy(self.local_ip)

    def camState(self):
        if self.cameraButton.text() == "Open Camera":
            # stop sending facial data
            self.facialLandmarksButton.setText("Show Facial Landmarks")
            self.facialLandmarksButton.setStyleSheet("")
            self.landmarks_sender.detectorOff = True
            self.landmarks_sender.cameraOff = False
            time.sleep(1)
            # change state
            self.cameraButton.setText("Off Camera")
            self.cameraButton.setStyleSheet(self.selectedButtonStyling)
            self.video_sender.cameraOff = False
        elif self.cameraButton.text() == "Off Camera":
            self.cameraButton.setText("Open Camera")
            self.cameraButton.setStyleSheet("")
            self.video_sender.cameraOff = True
            self.landmarks_sender.cameraOff = True

    def micState(self):
        if self.voiceButton.text() == "Open Microphone":
            self.voiceButton.setText("Off Microphone")
            self.voiceButton.setStyleSheet(self.selectedButtonStyling)
            self.audio_sender.mute = False
        elif self.voiceButton.text() == "Off Microphone":
            self.voiceButton.setText("Open Microphone")
            self.voiceButton.setStyleSheet('')
            self.audio_sender.mute = True

    def facState(self):
        if self.facialLandmarksButton.text()=="Show Facial Landmarks":
            # stop sending webcam data
            self.cameraButton.setText("Open Camera")
            self.cameraButton.setStyleSheet('')
            self.video_sender.cameraOff = True
            time.sleep(1)
            # change state
            self.facialLandmarksButton.setText("Hide Facial Landmarks")
            self.facialLandmarksButton.setStyleSheet(self.selectedButtonStyling)
            self.landmarks_sender.detectorOff = False
            self.landmarks_sender.cameraOff = False
            
        elif self.facialLandmarksButton.text()=="Hide Facial Landmarks":
            self.facialLandmarksButton.setText("Show Facial Landmarks")
            self.facialLandmarksButton.setStyleSheet("")
            self.landmarks_sender.detectorOff = True
            self.landmarks_sender.cameraOff = True

    def ganState(self):
        if self.facialReenactmentButton.text() =="Show Facial Reenactment":
            self.facialReenactmentButton.setText("Hide Facial Reenactment")
            self.facialReenactmentButton.setStyleSheet(self.selectedButtonStyling)
            self.landmarks_receiver.ganOff = False
        elif self.facialReenactmentButton.text() =="Hide Facial Reenactment":
            self.facialReenactmentButton.setText("Show Facial Reenactment")
            self.facialReenactmentButton.setStyleSheet("")
            self.landmarks_receiver.ganOff = True

    def convert_size(self,size_bytes):
        if size_bytes == 0:return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %sps" % (s, size_name[i])
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
        # camera class
        self.onCamera = demo.onCamera()
        # gan iter
        self.gan_iter = 0
        self.gan_iter_max = 10
        # button stylesheet
        self.NormalButtonCSS = 'QPushButton{background-color:white;color:#2193b0;}'
        self.NormalButtonCSS +='QPushButton:hover{background-color:rgb(245, 247, 249);}'

        self.DisabledButtonCSS = 'QPushButon{background-color:white;color:grey;}'

        self.CancelButtonCSS = 'QPushButton{background-color:red;color:white;}'
        self.CancelButtonCSS += 'QPushButton:hover{background-color:rgba(255,0,0,0.5)}'

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
            try:image = self.demoFx.facialReenactmentFrame(Image)
            except: return
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
            self.startCameraButton.setStyleSheet(self.CancelButtonCSS)
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
        self.startCameraButton.setStyleSheet(self.NormalButtonCSS)
        self.startCameraButton.setText('Start camera')
        # close facial reenactment
        try:
            self.onCamera.ImageUpdate.disconnect(self.demoImageUpdateSlotv2)
            self.clientCameraLabel.setText("Demo Frames")
            self.facialReenactmentButton.setStyleSheet(self.DisabledButtonCSS)
            self.facialReenactmentButton.setText('Show facial reenactment')
        except: print('Facial Reenactment Unused')
        # close facial landmarks
        try:
            self.onCamera.ImageUpdate.disconnect(self.demoImageUpdateSlotv1)
            self.clientCameraLabel.setText("Demo Frames")
            self.facialLandmarksButton.setStyleSheet(self.DisabledButtonCSS)
            self.facialLandmarksButton.setText('Show facial landmarks')
        except: print('Facial Landmarks Unused')

        
    def FacialLandmarks(self):
        # close other button
        try:
            self.onCamera.ImageUpdate.disconnect(self.demoImageUpdateSlotv2)
            self.clientCameraLabel.setText("Demo Frames")
            self.facialReenactmentButton.setStyleSheet(self.NormalButtonCSS)
            self.facialReenactmentButton.setText('Show facial reenactment')
        except:
            print('function detached')
        # start process
        if self.clientCameraLabel.text() == 'Demo Frames':
            self.onCamera.ImageUpdate.connect(self.demoImageUpdateSlotv1)
            self.facialLandmarksButton.setStyleSheet(self.CancelButtonCSS)
            self.facialLandmarksButton.setText('Hide facial landmarks')
        else:
            self.onCamera.ImageUpdate.disconnect(self.demoImageUpdateSlotv1)
            self.clientCameraLabel.setText("Demo Frames")
            self.facialLandmarksButton.setStyleSheet(self.NormalButtonCSS)
            self.facialLandmarksButton.setText('Show facial landmarks')
            
    def FacialReenactment(self):
        # close other button
        try:
            self.onCamera.ImageUpdate.disconnect(self.demoImageUpdateSlotv1)
            self.clientCameraLabel.setText("Demo Frames")
            self.facialLandmarksButton.setStyleSheet(self.NormalButtonCSS)
            self.facialLandmarksButton.setText('Show facial landmarks')
        except:
            print('function detached')
        # start process
        if self.clientCameraLabel.text() == 'Demo Frames':
            self.onCamera.ImageUpdate.connect(self.demoImageUpdateSlotv2)
            self.facialReenactmentButton.setStyleSheet(self.CancelButtonCSS)
            self.facialReenactmentButton.setText('Hide facial reenactment')
        else:
            self.onCamera.ImageUpdate.disconnect(self.demoImageUpdateSlotv2)
            self.clientCameraLabel.setText("Demo Frames")
            self.facialReenactmentButton.setStyleSheet(self.NormalButtonCSS)
            self.facialReenactmentButton.setText('Show facial reenactment')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    widget.setWindowTitle("GAN Meet!")
    widget.setWindowIcon(QIcon("user_interfaces/sharingan_icon.png"))

    mainWindow = MainWindow()
    conferenceWindow = ConferenceWindow()
    demoWindow = DemoWindow()

    widget.addWidget(mainWindow)
    widget.addWidget(conferenceWindow)
    widget.addWidget(demoWindow)

    widget.setFixedHeight(660)
    widget.setFixedWidth(1320)

    widget.show()
    sys.exit(app.exec_())