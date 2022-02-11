# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 23:45:01 2022

@author: hafiz
"""

import socket
import pyaudio

# socket codes
# host = socket.gethostbyname(socket.gethostname())
host = '10.210.32.254'
port = 9099
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((host,port))

# sound
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024)


try:
    while True:
        # send voice
        data = stream.read(1024)
        # data = "hi".encode('utf-8')
        try:
            client.send(data)
        except:
            print("Connection lost")
            break
except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
audio.terminate()