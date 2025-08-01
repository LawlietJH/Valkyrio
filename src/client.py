import _pickle as pickle
import socket

kb = 1024

class Network:
	
	def __init__(self) -> None:
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.host = '127.0.0.1'
		self.port = 57575
		self.addr = (self.host, self.port)
	
	def connect(self, name) -> int:
		self.client.connect(self.addr)
		self.client.send(str.encode(name))
		val = self.client.recv(8)
		return int(val.decode()) # can be int because will be an int id
	
	def disconnect(self) -> None:
		self.client.close()
	
	def send(self, data, pick=False) -> bytes:
		try:
			if pick:
				self.client.send(pickle.dumps(data))
			else:
				self.client.send(str.encode(data))
			reply = self.client.recv(kb*16)
			# print(len(reply))
			try:
				reply = pickle.loads(reply)
			except Exception as e:
				print(e)
			return reply
		except socket.error as e:
			print(e)
