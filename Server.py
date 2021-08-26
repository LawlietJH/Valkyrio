
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
HOST_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(HOST_NAME)

# try to connect to server
try:
    S.bind((SERVER_IP, PORT))
    # ~ S.bind(('127.0.0.1', PORT))
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
kbyte = 1024

# FUNCTIONS ============================================================

def threaded_client(conn, _id):
	
	global connections, players, game_time, start
	
	FPS = 1/240
	current_id = _id
	
	data = conn.recv(24)
	name = data.decode('utf-8')
	print(f"[LOG] '{name}' connected to the server.")
	
	players[current_id] = {
		'x': random.randrange(1200,1600),
		'y': random.randrange(1200,1600),
		'name': name,				# Username
		'score': 0,					# Score
		'ang': 0,					# Angle
		'atk': False,				# Attacking
		'ship': {
			'name': 'Prometheus',	# Ship Name
			'hp': 350,				# Health Points
			'sp': 0,				# Shield Points
			'chp': 350,				# Current Health Points
			'csp': 0,				# Current Shield Points
			's_unlkd': False,		# Shield Unlocked
			'dtry': False,			# Destroyed
			'spd_lvl': 0			# Speed
		},
		'selected': {
			'name': '',		# Selected Username
			'id':   -1,		# Selected ID user
		},
		'dmginfo': {}
	}
	
	conn.send(str.encode(str(current_id)))
	
	while True:
		
		try:
			game_time = int(time.perf_counter()-start_time)
			
			data = conn.recv(kbyte)
			
			if not data: break
			
			data = data.decode('utf-8')
			# ~ print('[DATA] Recieved', data, 'from client id:', current_id)
			
			if data.startswith('data:'):
				
				data = data[len('data:'):]
				data = json.loads(data)
				players[current_id]['x']   = data['x']
				players[current_id]['y']   = data['y']
				players[current_id]['ang'] = data['ang']
				players[current_id]['atk'] = data['atk'] == 'True'
				players[current_id]['ship']['hp']      = data['shipdata']['hp']
				players[current_id]['ship']['sp']      = data['shipdata']['sp']
				players[current_id]['ship']['chp']     = data['shipdata']['chp']
				players[current_id]['ship']['csp']     = data['shipdata']['csp']
				players[current_id]['ship']['s_unlkd'] = data['shipdata']['s_unlkd'] == 'True'
				players[current_id]['ship']['dtry']    = data['shipdata']['dtry']
				players[current_id]['ship']['spd_lvl'] = data['shipdata']['spd_lvl']
				
				if data['dmginfo']['dmg'] > 0 and data['dmginfo']['id'] >= 0:
					
					dmginfo = players[data['dmginfo']['id']]['dmginfo']
					
					if not dmginfo.get(current_id):
						dmginfo[current_id] = []
					
					dmginfo[current_id].append([
						data['dmginfo']['dmg'],
						data['dmginfo']['pct_sp'],
						data['dmginfo']['mult']
					])
				
				send_data = pickle.dumps((players, game_time))
				
				players[current_id]['dmginfo'] = {}
				
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
				
			elif data == 'get':
				
				send_data = pickle.dumps(players)
				
			else: send_data = pickle.dumps((players, game_time))
			
			conn.send(send_data)
		
		except Exception as e:
			if not str(e).startswith('[WinError 10054]'):
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



