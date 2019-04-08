from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

#import the base64 module
import base64
import sys
from twisted.python import log
from twisted.internet import reactor
import time
import threading
import os
from datetime import datetime

class MyServerProtocol(WebSocketServerProtocol):

	def onConnect(self, request):
		print("Client connecting: {0}".format(request.peer))

	def onOpen(self):
		print("WebSocket connection open.")

	def onMessage(self, payload, isBinary):
		payload = str(payload, 'utf-8')
		_id = payload.split('~')[0]
		cmno = payload.split('~')[1]

		try:
			content = payload.split(';')[1]
			image_encoded = content.split(',')[1]
			body = base64.decodebytes(image_encoded.encode('utf-8'))
			dir_name = "static/images/{0}/{1}/{2}.png".format(_id,cmno,datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
			os.makedirs(os.path.dirname(dir_name), exist_ok=True)
			with open(dir_name.format(_id,cmno), "wb") as image_file:
				image_file.write(body)

		except Exception as e:
			print(e)
			

	def onClose(self, wasClean, code, reason):
		print("WebSocket connection closed: {0}".format(reason))



class FrameTransfer():
	def __init__(self):
		t1 = threading.Thread(target=self.runloop) 
		t1.start()
	
	def runloop(self):
		while  True:
			t1 = threading.Thread(target=self.start) 
			t1.start()
			time.sleep(300)

		
	def start(self):
		try:	
			log.startLogging(sys.stdout)

			factory = WebSocketServerFactory("ws://localhost:8765")
			factory.protocol = MyServerProtocol

			reactor.listenTCP(8765, factory)
			reactor.run()
		except Exception as e:
			print(e)

			
				

FrameTransfer()