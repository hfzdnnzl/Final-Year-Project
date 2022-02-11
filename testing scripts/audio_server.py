# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 23:45:24 2022

@author: hafiz
"""

import socket
import pyaudio

# socket codes
host = socket.gethostbyname(socket.gethostname())
host = '10.210.33.250'
port = 9099
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen()

# sound
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    output=True,
                    frames_per_buffer=1024)

# connecting to socket
print("Waiting connection")
communication_socket, address = server.accept()
print(f"Connected to {address}")
try:
    while True:
        message = communication_socket.recv(1024)
        stream.write(message)

except KeyboardInterrupt:
    pass
communication_socket.close()    
print(f"Connection with {address} ended!")

stream.stop_stream()
stream.close()
audio.terminate()
