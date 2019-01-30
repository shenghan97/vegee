import json
import shelve
import threading
import time
from queue import Queue

import serial
import coloring as c

from flask import Flask,request
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin

import serial
import time
import logging

import re
import glob

logging.basicConfig(level=logging.DEBUG,
					format='(%(threadName)-9s) %(message)s',)

app = Flask(__name__)
api = Api(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api.decorators=[cross_origin()]
q = Queue()

grbl_in = Queue()
grbl_out = Queue()




# Open grbl serial port
s = serial.Serial(glob.glob('/dev/tty.usb*')[0],115200)
# /dev/ttyUSB0





flag_stopSignal = threading.Event()
flag_serialIdle = threading.Event()
flag_serialIdle.set()
data = ('','')

with open('/Users/shawn/plant.json', 'r') as j:
	plantDB = json.load(j)

class command(Resource):
	def put(self):
		if(request.get_json()['type']!='cancel'):
			q.put(request.get_json())
		else:
			flag_stopSignal.set()

		logging.debug(plantDB[str(request.get_json()['plant_id'])]['position'])
		return {'position':plantDB[str(request.get_json()['plant_id'])]['position']}

api.add_resource(command, '/command')

class status(Resource):
	def get(self):
		return {'realtime':list(data)}
	def post(self):
		try:
			logging.debug(request.args)
			flag_serialIdle.wait()
			flag_serialIdle.clear()
			s.flushInput()
			if request.args.get('move')=='up':
				s.write('$J=G21G91Y1F10008\n'.encode())
				response = s.readline().strip().decode()
			if request.args.get('move')=='down':
				s.write('$J=G21G91Y-1F10008\n'.encode())
				response = s.readline().strip().decode()
			if request.args.get('move')=='left':
				s.write('$J=G21G91X-1F10008\n'.encode())
				response = s.readline().strip().decode()	
			if request.args.get('move')=='right':
				s.write('$J=G21G91X1F10008\n'.encode())	
				response = s.readline().strip().decode()
			if request.args.get('reset')== 'true':
				logging.debug(c.red('reseting'))
				s.write('G10 P0 L20 X0 Y0 Z0\n'.encode())			
				response = s.readline().strip().decode()
			logging.debug(c.red('response'))
			flag_serialIdle.set()
		except Exception as e:
			logging.debug(str(e))
		return response


api.add_resource(status, '/status')





# s = serial.Serial('/dev/ttyUSB0', 115200,timeout=2)


class dos:
	@staticmethod
	def water(flag_stopSignal):
		logging.debug(c.cyan('DOS: watering'))
		if flag_stopSignal.wait(2):  # wait for signal in 2s(regular water time). 
			logging.debug(c.cyan('DOS: !Canceled watering'))
			# GCODE return to origin
			return
		logging.debug(c.cyan('DOS: done watering'))
		
	@staticmethod
	def chemical(flag_stopSignal):
		logging.debug('chemicaling')
		if flag_stopSignal.wait(3):
			logging.debug(c.cyan('DOS: !Canceled chemicaling'))
			# GCODE return to origin
			return
		logging.debug('done chemecaling')

	@staticmethod
	def watch(flag_stopSignal):
		logging.debug(c.cyan('watching'))




def wait_until(condition, interval=0.1, timeout=1):
	start = time.time()
	while True:
		if condition:
			return True
		if time.time() - start < timeout:
			logging.debug('time out')
			return False
		time.sleep(interval)


def gcode_to(position):
	gcode = '$J=X%dY%dF1000\n' % (position[0], position[1])
	return gcode


def perform(operation,flag_stopSignal):
	flag_stopSignal.clear()
	# operation = json.load(operation_json)
	if operation['type'] == 'sequence':
		position = plantDB[str(operation['plant_id'])]['position']
		logging.debug(c.green(position))
		'''
		if not wait_until(condition=(s.in_waiting()==0 and s.out_waiting()==0)):
			logging.debug("Timeout due to uncleared buffer")
			return
'''

		flag_serialIdle.wait()
		flag_serialIdle.clear()
		s.write(gcode_to(position).encode())
		response = s.readline()
		flag_serialIdle.set()

		# logging.debug(gcode_to(position))
		# time.sleep(1)
		# response='ok'
		# grbl_in.put(gcode_to(position))
		# response = grbl_out.get()

		time.sleep(0.1)
		while data[0]!='Idle':
			time.sleep(0.1)
			logging.debug(data[0])
		logging.debug(c.green("jog over, start do"))
		eval('dos.' + operation['do'] +'(flag_stopSignal)')
	
	




def getRealtimeData():
	global data
	while True:
		logging.debug('data')
		s.flushInput()
		flag_serialIdle.wait()
		flag_serialIdle.clear()
		s.write('?\n'.encode())
		realTimeResponse = s.readline().strip().decode()

		data = re.search(r"<(.*?)\|.*?WPos:(.*?),(.*?),",realTimeResponse).groups()
		
		logging.debug(data)
		s.readline()
		flag_serialIdle.set()

		time.sleep(0.2)

""" 
def send_deamon():
	while True:
		#!		if ?serial.input_buffer == 0q
		s.write(command)


def get_loop():
	while True:
		# response=serial.read()
		if q.qsize() > 0:
			print(q.get())
			time.sleep(0.5) """


def  perform_deamon():
	# flag_idle = threading.Event()

	#flag_idle.set()
	logging.debug('deamon start')

	while True:
		operation = q.get()
		logging.debug('getting from q')
		if(operation['type']=='sequence'):
			# if not flag_idle.is_set():
			# 	flag_stopSignal.set()
			perform(operation,flag_stopSignal)
	
'''
def  serial_control():
	while(1):
		time.sleep(0.25)
		while(s.in_waiting>0):
			grbl_out.put(s.readline())  # Wait for grbl response with carriage return
			#print(grbl_out.strip().decode())
		
		l = grbl_in.get().strip() # Strip all EOL characters for consistency
		if(l=='q'):
			break
		elif(l=='x'):
			o='%c\n' % 0x18
		elif(l=='c'):
			o='%c\n' % 0x85
		else:
			o=l + '\n'

		s.write(o.encode()) # Send g-code block to grbl
		#print('\033[1A\033[92m>> ' + l+ '\033[0m' )
'''



if __name__ == '__main__':
	threading.Thread(target=app.run,kwargs={'host':'0.0.0.0'}).start()

	perform_thread = threading.Thread(target=perform_deamon)
	perform_thread.start()
	#app.run(host='0.0.0.0')
	# Wake up grbl
	s.write("\r\n\r\n".encode())
	time.sleep(2)   # Wait for grbl to initialize 
	#s.write('G10 P0 L20 X0 Y0 Z0\n'.encode())
	s.flushInput()  # Flush startup text in serial input

	threading.Thread(target=getRealtimeData).start()
