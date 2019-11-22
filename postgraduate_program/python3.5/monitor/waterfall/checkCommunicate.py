import zmq
import sys

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.0.1:6666")

	if data == 'Imok':
		socket.send(data)
	else:
		print('Wrong Input. Please input Imok')
		sys.exit()

	message = socket.recv()

	print message
