
import _thread as thread
import _pickle as pickle
import atexit
import random
import socket
import json
import time

# ======================================================================
# setup sockets
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set constants
PORT = 57575
# ~ MapW, MapH = 1600, 1600
HOST_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(HOST_NAME)

# try to connect to server
try:
    S.bind((SERVER_IP, PORT))
    # ~ S.bind(('192.168.1.72', PORT))
except socket.error as e:
    print(str(e))
    print('[SERVER] Server could not start')
    quit()

# listen for connections
S.listen()

print(f'[SERVER] Server Started with local ip {SERVER_IP}')

# dynamic variables
players = {}
connections = 0
_id = 0
start = False
start_time = 0
game_time = 'Starting Soon'
# ~ colors = [(128,200,100),(128,200,200),(128,100,100),(128,100,200),(200,100,100),(200,200,200),(200,200,100),(200,100,200)]

# FUNCTIONS ============================================================

def threaded_client(conn, _id):
	
	global connections, players, game_time, start
	
	FPS = 1/240
	current_id = _id
	
	data = conn.recv(16)
	name = data.decode('utf-8')
	print(f"[LOG] '{name}' connected to the server.")
	
	players[current_id] = {
		'x': random.randrange(200,240),
		'y': random.randrange(200,240),
		'score': 0,		# Score
		'name': name,	# Username
		'vel': 50,		# Speed
		'ang': 0,		# Angle
		'atk': False,	# Attacking
		'ship': {
			'name': 'Prometheus',	# Ship Name
			'hp': 350,				# Health Points
			'sp': 250,				# Shield Points
			'chp': 350,				# Health Points
			'csp': 250,				# Current Shield Points
			'dtry': False,			# Destroyed
		},
		'selected': {
			'name': '',		# Selected Username
			'id': -1,		# Selected ID user
			# ~ 'x': 0,
			# ~ 'y': 0,
			# ~ 'angle': 0,
			# ~ 'dist': 0
		}
	}
	
	conn.send(str.encode(str(current_id)))
	
	while True:
		
		try:
			game_time = int(time.perf_counter()-start_time)
			
			data = conn.recv(1024)
			
			if not data: break
			
			data = data.decode('utf-8')
			# ~ print('[DATA] Recieved', data, 'from client id:', current_id)
			
			if data.startswith('data:'):
				
				data = data[len('data:'):]
				data = json.loads(data)
				players[current_id]['x'] = data['x']
				players[current_id]['y'] = data['y']
				players[current_id]['ship']['chp'] = data['chp']
				players[current_id]['ship']['csp'] = data['csp']
				players[current_id]['ship']['dtry'] = data['dtry']
				players[current_id]['ang'] = data['ang']
				players[current_id]['atk'] = data['atk']
				
				send_data = pickle.dumps((players, game_time))
			
			elif data.startswith('id'):
				
				send_data = str.encode(str(current_id))
				
			elif data.startswith('selected:'):
				
				data = data[len('selected:'):]
				data = json.loads(data)
				selected_name = data['name']
				selected_id   = data['id']
				name = players[current_id]['name']
				
				if not selected_name:
					unselected = players[current_id]['selected']['name']
					print(f"[UNSELECT] '{name}' unselect to '{unselected}'")
				else:
					print(f"[SELECT] '{name}' select to '{selected_name}'")
				
				players[current_id]['selected']['name'] = selected_name
				if selected_name:
					players[current_id]['selected']['id'] = int(selected_id)
				else:
					players[current_id]['selected']['id'] = -1
				
				send_data = pickle.dumps(players)
			
			else: send_data = pickle.dumps((players, game_time))
			
			conn.send(send_data)
		
		except Exception as e:
			print(e, 'Error')
			break
		
		time.sleep(FPS)
	
	print(f'[DISCONNECT] Name: {name}, Client Id: {current_id} disconnected')
	
	connections -= 1
	del players[current_id]
	conn.close()


@atexit.register
def close():
	time.sleep(1)


# MAINLOOP =============================================================

print('[GAME] Setting up level')
print('[SERVER] Waiting for connections')

while True:
	
	host, addr = S.accept()
	print(f'[CONNECTION] Connected to: {addr}')
	
	if addr[0] == SERVER_IP and not(start):
		start = True
		start_time = time.perf_counter()
		print('[STARTED] Game Started')
	
	connections += 1
	thread.start_new_thread(threaded_client,(host,_id))
	_id += 1

print('[SERVER] Server offline')



