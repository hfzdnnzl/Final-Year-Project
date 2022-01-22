
import socket
import select
import pyaudio
from PyQt5.QtCore import *


class audioReceiver(QThread):
    voiceReceive = pyqtSignal(str)

    def __init__(self,host,port,format=pyaudio.paInt16,rate=44100,frames_per_buffer=512):
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
            channels=1,
            rate = rate,
            output=True,
            frames_per_buffer=frames_per_buffer)

    def run(self):
        # connecting to socket
        self.threadActive = True
        while self.threadActive:
            com_socket, address = self.server.accept()
            self.voiceReceive.emit(address[0])
            print(f"Connected to {address}")
            try:
                while self.threadActive:
                    message = com_socket.recv(512)
                    self.stream.write(message)
            except:
                print("Error getting audio message")
                pass

    def stop(self):
        self.threadActive = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.terminate()

class audioSender(QThread):
    voiceSend = pyqtSignal(str)

    def run(self,host):
        # initiate port
        self.host = host
        self.port = 9010
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect((self.host,self.port))
        # initiate audio
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate = 44100,
            input=True,
            frames_per_buffer=512)
        # connecting to socket
        try:
            self.Thread = True
            while self.Thread:
                message = self.stream.read(512)
                try:
                    self.client.send(message)
                except:
                    print("Connection lost")
                    break
        except:
            print("Error getting audio message")
            pass

    def stop(self):
        self.Thread = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.terminate()


