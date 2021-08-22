
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
MapW, MapH = 1600, 1600
HOST_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(HOST_NAME)

# try to connect to server
try:
    S.bind((SERVER_IP, PORT))
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
colors = [(128,200,100),(128,200,200),(128,100,100),(128,100,200),(200,100,100),(200,200,200),(200,200,100),(200,100,200)]

# FUNCTIONS ============================================================

def threaded_client(conn, _id):
	
	global connections, players, game_time, start
	
	FPS = 1/240
	current_id = _id
	
	data = conn.recv(16)
	name = data.decode('utf-8')
	print('[LOG]', name, 'connected to the server.')
	
	players[current_id] = {
		'x': random.randrange(600,1200),
		'y': random.randrange(600,900),
		'score': 0,
		'name': name,
		'ship': 'Prometheus',
		'vel': 50,
		'hp': 350,
		'sp': 250,
		'selected': {
			'name': '',
			'id': -1,
			# ~ 'x': 0,
			# ~ 'y': 0,
			# ~ 'angle': 0,
			# ~ 'dist': 0
		},
		'angle': 0,
		'color': random.choice(colors)
	}
	
	conn.send(str.encode(str(current_id)))
	
	while True:
		
		try:
			game_time = int(time.perf_counter()-start_time)
			
			data = conn.recv(64)
			
			if not data: break
			
			data = data.decode('utf-8')
			# ~ print('[DATA] Recieved', data, 'from client id:', current_id)
			
			if data.startswith('move:'):
				
				data = data[len('move:'):]
				data = json.loads(data)
				players[current_id]['x'] = data['x']
				players[current_id]['y'] = data['y']
				
				send_data = pickle.dumps((players, game_time))
			
			elif data.startswith('id'):
				
				send_data = str.encode(str(current_id))
				
			elif data.startswith('selected:'):
				
				data = data[len('selected:'):]
				data = json.loads(data)
				selected_name = data['name']
				selected_id   = data['id']
				name = players[current_id]['name']
				
				if selected_name:
					print(f'[SELECT] {name} select to {selected_name}')
				else:
					unselected = players[current_id]['selected']['name']
					print(f'[UNSELECT] {name} unselect to {unselected}')
				
				players[current_id]['selected']['name'] = selected_name
				if selected_name:
					players[current_id]['selected']['id'] = int(selected_id)
					# ~ players[current_id]['selected']['x']  = int(data['x'])
					# ~ players[current_id]['selected']['y']  = int(data['y'])
				else:
					players[current_id]['selected']['id'] = -1
					# ~ players[current_id]['selected']['x']  = 0
					# ~ players[current_id]['selected']['y']  = 0
					players[current_id]['selected']['angle'] = 0
					players[current_id]['selected']['dist']  = 0
				
				send_data = pickle.dumps(players)
			
			elif data.startswith('angle_dist:'):
				
				data = data[len('angle_dist:'):]
				data = json.loads(data)
				# ~ players[current_id]['selected']['x'] = int(data['x'])
				# ~ players[current_id]['selected']['y'] = int(data['y'])
				players[current_id]['selected']['angle'] = int(data['angle'])
				players[current_id]['selected']['dist']  = int(data['dist'])
				
				send_data = pickle.dumps(players)
				
			else: send_data = pickle.dumps((players, game_time))
			
			conn.send(send_data)
		
		except Exception as e:
			print(e, 'Error')
			break
		
		time.sleep(FPS)
	
	print('[DISCONNECT] Name:', name, ', Client Id:', current_id, 'disconnected')
	
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
	print('[CONNECTION] Connected to:', addr)
	
	if addr[0] == SERVER_IP and not(start):
		start = True
		start_time = time.perf_counter()
		print('[STARTED] Game Started')
	
	connections += 1
	thread.start_new_thread(threaded_client,(host,_id))
	_id += 1

print('[SERVER] Server offline')



