
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
_id = -1
start = False
start_time = 0
game_time = 'Starting Soon'
kbyte = 1024

# CLASSES ==============================================================

class Config:
	
	def __init__(self):
		
		# Configs: -----------------------------------------------------
		
		self.WEAPON = {
			'Laser': {
				'path': 'img/weapons/laser.png',
				'dmg': 100,			# Base damage
				'inc': 1,			# Damage increment per level 
				'dist': 400,		# Minimum distance to attack enemies
				'pct_sp': .7,		# Damage percentage to SP
				'mult': 1			# Damage multiplier
			}
		}
		
		self.speedmul = 100								# Speed multiplier
		self.SHIP = {
			'Prometheus': {
				'path': 'img/Prometheus.png',
				'weapon': 'Laser',
				'speed': int(.5 * self.speedmul),
				'spd_lvl': 0,
				'hp':    350,
				'sp':    250
			}
		}
		
		self.STRANGERS = {
			'Iken': {
				'path':     'img/Prometheus.png',
				'creds':    100,
				'exp':      100,
				'wpn_name': 'Laser',
				'wpn_lvl':  100,
				'speed':    int(.5 * self.speedmul),
				'spd_lvl':  0,
				'lhp':      3,
				'lsp':      6,
				'hp':       350,
				'sp':       250
			}
		}
		
		self.MAP = {
			'Zwem':   { 'x': 200, 'y': 200 },
			'Karont': { 'x': 300, 'y': 300 },
			'Arkont': { 'x': 400, 'y': 400 }
		}
		
		# Data settings
		self.BASE_SPEED = 1 * self.speedmul				# Base Speed of Ships
		self.MAX_SPEED  = 2 * self.speedmul				# Max Speed of Ships
		self.dtdiv = 10 * self.speedmul					# Detla Time Divide
		self.posdiv = 20								# Divide the actual position of pixels X and Y to generate coordinates for the map
		self.rad_dmg = 500								# Radioactive Damage 
		self.min_select_dist = 32						# Minimum target selection distance (on pixels)
		
		# Counters
		self.curr_frame = 0								# Current Frame
		
		# Screen settings
		self.RESOLUTION = (600, 450)					# Resolution
		self.MFPS = 120									# Max Frames per Second
		self.fps = 60									# Number of Frames per Second
		
		# Map settings
		self.map_name = 'Zwem'
	
	@property
	def CENTER(self):
		return {'x': self.RESOLUTION[0]//2, 'y': self.RESOLUTION[1]//2}
	
	@property
	def map_limits(self, map_name=None):	# Actual map coordinates in number of pixels
		
		limits = self.MAP['Zwem']
		
		if not map_name: map_name = self.map_name
		
		if self.MAP.get(map_name):
			
			limits = {
				'x': self.MAP[map_name]['x'] * self.posdiv,
				'y': self.MAP[map_name]['y'] * self.posdiv
			}
		
		return limits

config = Config()

class Weapon:
	
	def __init__(self, name):
		self.name = name
		self.path = config.WEAPON[name]
		self.dmg  = config.WEAPON[name]['dmg']
		self.inc  = config.WEAPON[name]['inc']
		self.dist = config.WEAPON[name]['dist']
		self.pct_sp = config.WEAPON[name]['pct_sp']
		self.mult = config.WEAPON[name]['mult']
		self.lvl  = 0
		self.init_time = 0
	
	def levelUpDmg(self, lvl=1):
		self.lvl += lvl
		self.dmg += lvl*self.inc
	
	def perSecond(self, t=1):
		if time.perf_counter() - self.init_time >= t:
			self.init_time = time.perf_counter()
			return True
		return False


class Ship:
	
	def __init__(self, name):
		
		self.name = name
		self.base = config.SHIP[name]
		self.weapon = Weapon(self.base['weapon'])
		self.destroyed = False
		self.spd_lvl = self.base['spd_lvl']
		
		# Health
		self.hp  = 0					# Health points
		self.chp = 0					# Current Health Points
		self.lhp = 1					# Level Health Points
		self.pct_hp = .3				# Health Damage Percentage
		self.heal_hp = False
		self.time_hp_init = 0			# Time Counter to heal HP
		
		# Shield
		self.shield_unlocked = False
		self.sp  = 0					# Shield points
		self.csp = 0					# Current Shield Points
		self.lsp = 0					# Level Shield Points
		self.pct_sp = .7				# Shield Damage Percentage
		self.heal_sp = False
		self.time_sp_init = 0			# Time Counter to heal SP
		
		self.timeOnBorder = 0
		
		self.damageRecv = []
		self.healthRecv = []
	
	@property
	def speed(self):
		speed  = config.BASE_SPEED
		speed += self.base['speed']
		speed += self.spd_lvl
		return speed
	
	def speedLevelUP(self, lvl=1):
		self.spd_lvl += lvl
	
	def levelUpHP(self, lvl=1):					# Incrementa de nivel el HP
		inc = self.base['hp'] * lvl
		self.hp += inc
		self.chp += inc
		self.lhp += lvl
	
	def levelUpSP(self, lvl=1):					# Incrementa de nivel el SP
		if self.shield_unlocked:
			inc = self.base['sp'] * lvl
			self.sp += inc
			self.csp += inc
			self.lsp += lvl
	
	def recvDamage(self, damage, pct_sp=None, mult=1):			# Registra el daño recibido para mostrarlo
		
		if self.destroyed: return
		
		self.heal_hp = False
		self.heal_sp = False
		self.time_hp_init = 0
		self.time_sp_init = 0
		
		if pct_sp == None:
			dhp = int(damage * self.pct_hp * mult)
			dsp = int(damage * self.pct_sp * mult)
		else:
			dhp = int(damage * (1-pct_sp) * mult)
			dsp = int(damage *    pct_sp  * mult)
		
		while dhp+dsp < int(damage*mult): dsp += 1
		
		if self.csp > 0:
			self.csp = int(self.csp - dsp)
			if self.csp < 0:
				self.chp = int(self.chp + self.csp)
				self.csp = 0
		else: self.chp = int(self.chp - dsp)
		if self.chp > 0: self.chp = int(self.chp - dhp)
		if self.chp < 0: self.chp = 0
		
		if self.chp == 0: self.destroyed = True
	
	def healHP(self, pct=10, sec_init=6, sec=3):
		if not self.chp >= self.hp:
			if self.heal_hp:
				if self.time_hp_init == 0:
					self.time_hp_init = time.perf_counter()
				if time.perf_counter()-self.time_hp_init >= sec:
					hp_add = self.hp * (pct/100)
					if self.chp < self.hp: self.chp += int(hp_add)
					if self.chp > self.hp: self.chp = self.hp
					self.time_hp_init = 0
			else:
				if self.time_hp_init == 0:
					self.time_hp_init = time.perf_counter()
				if time.perf_counter()-self.time_hp_init >= sec_init:
					self.heal_hp = True
	
	def healSP(self, pct=5, sec_init=10, sec=1):
		if not self.csp >= self.sp:
			if self.heal_sp:
				if self.time_sp_init == 0:
					self.time_sp_init = time.perf_counter()
				if time.perf_counter()-self.time_sp_init >= sec:
					sp_add = self.sp * (pct/100)
					if self.csp < self.sp: self.csp += int(sp_add)
					if self.csp > self.sp: self.csp = self.sp
					self.time_sp_init = 0
			else:
				if self.time_sp_init == 0:
					self.time_sp_init = time.perf_counter()
				if time.perf_counter()-self.time_sp_init >= sec_init:
					self.heal_sp = True


class Stranger:
	
	def __init__(self, name, id_):
		
		self.name = name
		self.ship = None
		self.ship_name = None
		
		self.creds = 0
		self.exp = 0
		self.id = id_
		self.x = 0
		self.y = 0
		
		self.angle = 0
		self.attacking = False
		self.under_attack = False
		
		self.selected = {
			'id':   -1,
			'name': '',
			'dist': '',
			'dmginfo': {
				'dmg':     0,		# Damage caused by the player.
				'pct_sp': .7,		# Damage distributed in percentage of SP and HP.
				'mult':    1,		# Damage multiplier.
				'time':    0
			}
		}
		
		self.curr_pos = (
			int(self.x/config.posdiv),
			int(self.y/config.posdiv)
		)
	
	def setData(self):
		
		data_f  = '{{'
		data_f +=   '"x":{},'
		data_f +=   '"y":{},'
		# ~ data_f +=   '"creds":{},'
		# ~ data_f +=   '"exp":{},'
		data_f +=   '"ang":{},'
		data_f +=   '"atk":"{}",'
		data_f +=   '"shipdata":{{'
		# ~ data_f +=     '"name":"{}",'
		# ~ data_f +=     '"lhp":{},'
		# ~ data_f +=     '"lsp":{},'
		data_f +=     '"chp":{},'
		data_f +=     '"csp":{},'
		# ~ data_f +=     '"s_unlkd":"{}",'
		data_f +=     '"dtry":"{}"'
		# ~ data_f +=     '"spd_lvl":{},'
		# ~ data_f +=     '"weapon":{{'
		# ~ data_f +=       '"name":"{}",'
		# ~ data_f +=       '"lvl":{}'
		# ~ data_f +=     '}}'
		data_f +=   '}},'
		data_f +=   '"dmginfo":{{'
		data_f +=     '"id":{},'
		data_f +=     '"dmg":{},'
		data_f +=     '"pct_sp":{},'
		data_f +=     '"mult":{},'
		data_f +=     '"time":{}'
		data_f +=   '}}'
		data_f += '}}'
		
		data = data_f.format(
			round(self.x, 2),
			round(self.y, 2),
			# ~ self.creds,
			# ~ self.exp,
			self.angle,
			self.attacking,
			# ~ self.ship.name,
			# ~ self.ship.lhp,
			# ~ self.ship.lsp,
			self.ship.chp,
			self.ship.csp,
			# ~ self.ship.shield_unlocked,
			self.ship.destroyed,
			# ~ self.ship.spd_lvl,
			# ~ self.ship.weapon.name,
			# ~ self.ship.weapon.lvl,
			self.selected['id'],
			self.selected['dmginfo']['dmg'],
			self.selected['dmginfo']['pct_sp'],
			self.selected['dmginfo']['mult'],
			self.selected['dmginfo']['time']
		)
		
		self.selected['dmginfo']['dmg']    = 0
		self.selected['dmginfo']['pct_sp'] = 0
		self.selected['dmginfo']['mult']   = 0
		self.selected['dmginfo']['time']   = 0
		
		# ~ print(data)
		
		data = json.loads(data)
		
		player = players[self.id]
		player_s = player['ship']
		
		data_s = data['shipdata']
		# ~ data_sw = data_s['weapon']
		
		if not player['x']         == data['x']:                     player['x']         = data['x']
		if not player['y']         == data['y']:                     player['y']         = data['y']
		# ~ if not player['creds']     == data['creds']:                 player['creds']     = data['creds']
		# ~ if not player['exp']       == data['exp']:                   player['exp']       = data['exp']
		if not player['ang']       == data['ang']:                   player['ang']       = data['ang']
		if not player['atk']       == (data['atk'] == 'True'):       player['atk']       = data['atk'] == 'True'
		# ~ if not player_s['name']    == data_s['name']:                player_s['name']    = data_s['name']
		# ~ if not player_s['lhp']     == data_s['lhp']:                 player_s['lhp']     = data_s['lhp']
		# ~ if not player_s['lsp']     == data_s['lsp']:                 player_s['lsp']     = data_s['lsp']
		if not player_s['chp']     == data_s['chp']:                 player_s['chp']     = data_s['chp']
		if not player_s['csp']     == data_s['csp']:                 player_s['csp']     = data_s['csp']
		# ~ if not player_s['s_unlkd'] == (data_s['s_unlkd'] == 'True'): player_s['s_unlkd'] = data_s['s_unlkd'] == 'True'
		if not player_s['dtry']    == (data_s['dtry'] == 'True'):    player_s['dtry']    = data_s['dtry'] == 'True'
		# ~ if not player_s['spd_lvl'] == data_s['spd_lvl']:             player_s['spd_lvl'] = data_s['spd_lvl']
		# ~ if not player_sw['name']   == data_sw['name']:               player_sw['name']   = data_sw['name']
		# ~ if not player_sw['lvl']    == data_sw['lvl']:                player_sw['lvl']    = data_sw['lvl']
		
		if data['dmginfo']['dmg'] > 0 and data['dmginfo']['id'] >= 0:
			
			dmginfo = players[data['dmginfo']['id']]['dmginfo']
			
			if not dmginfo.get(current_id):
				dmginfo[current_id] = []
			
			dmginfo[current_id].append([
				data['dmginfo']['dmg'],
				data['dmginfo']['pct_sp'],
				data['dmginfo']['mult'],
				data['dmginfo']['time']
			])
		
		players[self.id]['dmginfo'] = {}
		
		return data
	
	def loadData(self, players):
		
		stranger = players[self.id]
		
		self.x = stranger['x']
		self.y = stranger['y']
		
		self.selected['name'] = stranger['selected']['name']
		self.selected['id']   = stranger['selected']['id']
		
		self.creds = stranger['creds']
		self.exp = stranger['exp']
		
		self.angle = stranger['ang']
		self.attacking = stranger['atk']
			
		self.ship_name = stranger['ship']['name']
		self.ship = Ship(self.ship_name)
		
		self.ship.hp = 0
		self.ship.sp = 0
		self.ship.lhp = 0
		self.ship.lsp = 0
		self.ship.levelUpHP(stranger['ship']['lhp'])
		self.ship.shield_unlocked = stranger['ship']['s_unlkd']
		self.ship.levelUpSP(stranger['ship']['lsp'])
		
		if not stranger['ship']['chp'] == 0 \
		and stranger['ship']['chp'] <= self.ship.lhp:
			self.ship.chp = stranger['ship']['chp']
		else:
			self.ship.chp = self.ship.hp
		
		if stranger['ship']['csp'] <= self.ship.lsp:
			self.ship.csp = stranger['ship']['csp']
		else:
			self.ship.csp = self.ship.sp
		
		self.ship.destroyed = stranger['ship']['dtry']
		self.ship.spd_lvl = stranger['ship']['spd_lvl']
		
		self.ship.weapon = Weapon(stranger['ship']['weapon']['name'])
		self.ship.weapon.levelUpDmg(stranger['ship']['weapon']['lvl'])

	def chkDmgRecv(self, primary_atk):
		
		for enemy_id, values in players[self.id]['dmginfo'].items():
			for dmg, pct_sp, mult, t in values:
				self.ship.recvDamage(dmg, pct_sp, mult)
			
			if (primary_atk == None and enemy_id in players) \
			or (not primary_atk == None and not primary_atk in players):
				primary_atk = enemy_id
		
		return primary_atk
		

# STRANGERS ============================================================

def threaded_bot(stranger_id, stranger_name):
	
	global connections, players, game_time, _id
	
	FPS = 1/240
	
	while True:
		
		stranger_info = config.STRANGERS[stranger_name]
		
		players[stranger_id] = {
			'x':     random.randrange(0,2000),
			'y':     random.randrange(0,2000),
			'name':  stranger_name,								# Stranger name
			'type':  'Stranger',								# Type of ship
			'creds': stranger_info['creds'],					# Number of credits
			'exp':   stranger_info['exp'],						# Score
			'ang':   0,											# Angle
			'atk':   False,										# Attacking
			'ship': {
				'name':    'Prometheus',						# Ship Name
				'lhp':     stranger_info['lhp'],				# Health Points
				'lsp':     stranger_info['lsp'],				# Shield Points
				'chp':     stranger_info['lhp']*stranger_info['hp'],		# Current Health Points
				'csp':     stranger_info['lsp']*stranger_info['sp'],		# Current Shield Points
				's_unlkd': True,								# Shield Unlocked
				'dtry':    False,								# Destroyed
				'spd_lvl': stranger_info['spd_lvl'],			# Speed level
				'weapon': {
					'name': stranger_info['wpn_name'],			# Weapon name
					'lvl':  stranger_info['wpn_lvl']			# Weapon level
				}
			},
			'selected': {
				'name': '',					# Selected Username
				'id':   -1,					# Selected ID user
			},
			'dmginfo': {}
		}
		
		stranger = Stranger(players[stranger_id], stranger_id)
		stranger.loadData(players)
		
		print(f"[LOG] {stranger_name} Generated. ID: {stranger_id} ({int(stranger.x/config.posdiv)},{int(stranger.y/config.posdiv)})")
		
		primary_atk = None				# Primary attacker
		
		while stranger.ship.chp > 0:
			
			# ~ try:
				
				game_time = int(time.perf_counter()-start_time)
				
				primary_atk = stranger.chkDmgRecv(primary_atk)
				stranger.setData()
				stranger.ship.healHP()
				stranger.ship.healSP()
				
			# ~ except Exception as e:
				# ~ if not str(e).startswith('[WinError 10054]'):
					# ~ print(e, 'Error')
				# ~ break
			
				time.sleep(FPS)
		
		print(f'[LOG] Destroyed: {stranger_name}, ID: {stranger_id}')
		
		players[primary_atk]['creds'] += players[stranger_id]['creds']
		players[primary_atk]['exp']   += players[stranger_id]['exp']
		
		time.sleep(1)
		
		del players[stranger_id]
		
		_id += 1
		stranger_id = _id


for i in range(10):
	_id += 1
	thread.start_new_thread(threaded_bot, (_id, 'Iken'))
	time.sleep(.01)
time.sleep(1)

# FUNCTIONS ============================================================

def threaded_client(conn, _id):
	
	global connections, players, game_time, start
	
	FPS = 1/240
	current_id = _id
	
	data = conn.recv(24)
	name = data.decode('utf-8')
	print(f"[LOG] '{name}' connected to the server. Client Id: {_id}")
	
	players[current_id] = {
		'x':     random.randrange(1200,1600),
		'y':     random.randrange(1200,1600),
		'name':  name,					# Username
		'type':  'Human',				# Type of ship
		'creds': 0,						# Number of credits
		'exp':   0,						# Score
		'ang':   0,						# Angle
		'atk':   False,					# Attacking
		'ship': {
			'name':    'Prometheus',	# Ship Name
			'lhp':     10,				# Health Points
			'lsp':     0,				# Shield Points
			'chp':     0,				# Current Health Points
			'csp':     0,				# Current Shield Points
			's_unlkd': False,			# Shield Unlocked
			'dtry':    False,			# Destroyed
			'spd_lvl': 0,				# Speed
			'weapon': {
				'name': 'Laser',		# Weapon name
				'lvl': 0				# Weapon level
			}
		},
		'selected': {
			'name': '',					# Selected Username
			'id':   -1,					# Selected ID user
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
				
				player = players[current_id]
				player_s = player['ship']
				player_sw = player_s['weapon']
				
				data_s = data['shipdata']
				data_sw = data_s['weapon']
				
				if not player['x']         == data['x']:                     player['x']         = data['x']
				if not player['y']         == data['y']:                     player['y']         = data['y']
				if not player['creds']     == data['creds']:                 player['creds']     = data['creds']
				if not player['exp']       == data['exp']:                   player['exp']       = data['exp']
				if not player['ang']       == data['ang']:                   player['ang']       = data['ang']
				if not player['atk']       == (data['atk'] == 'True'):       player['atk']       = data['atk'] == 'True'
				if not player_s['name']    == data_s['name']:                player_s['name']    = data_s['name']
				if not player_s['lhp']     == data_s['lhp']:                 player_s['lhp']     = data_s['lhp']
				if not player_s['lsp']     == data_s['lsp']:                 player_s['lsp']     = data_s['lsp']
				if not player_s['chp']     == data_s['chp']:                 player_s['chp']     = data_s['chp']
				if not player_s['csp']     == data_s['csp']:                 player_s['csp']     = data_s['csp']
				if not player_s['s_unlkd'] == (data_s['s_unlkd'] == 'True'): player_s['s_unlkd'] = data_s['s_unlkd'] == 'True'
				if not player_s['dtry']    == (data_s['dtry'] == 'True'):    player_s['dtry']    = data_s['dtry'] == 'True'
				if not player_s['spd_lvl'] == data_s['spd_lvl']:             player_s['spd_lvl'] = data_s['spd_lvl']
				if not player_sw['name']   == data_sw['name']:               player_sw['name']   = data_sw['name']
				if not player_sw['lvl']    == data_sw['lvl']:                player_sw['lvl']    = data_sw['lvl']
				
				if data['dmginfo']['dmg'] > 0 and data['dmginfo']['id'] >= 0:
					
					dmginfo = players[data['dmginfo']['id']]['dmginfo']
					
					if not dmginfo.get(current_id):
						dmginfo[current_id] = []
					
					dmginfo[current_id].append([
						data['dmginfo']['dmg'],
						data['dmginfo']['pct_sp'],
						data['dmginfo']['mult'],
						data['dmginfo']['time']
					])
				
				send_data = pickle.dumps((players, game_time))
				
				# ~ for id_, dmginfo in players[current_id]['dmginfo'].items():
					# ~ for di in dmginfo:
						# ~ print(di[3])
				
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
	
	_id += 1
	connections += 1
	thread.start_new_thread(threaded_client,(host,_id))

print('[SERVER] Server offline')



