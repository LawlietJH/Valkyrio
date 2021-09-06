
import _thread as thread
import _pickle as pickle
import atexit
import random
import socket
import json
import math
import time


# ======================================================================
# CLASSES ==============================================================
# ======================================================================

class Utils:
	
	def __init__(self):
		self.init_time = time.perf_counter()
	
	def perSecond(self, t=1):
		if time.perf_counter() - self.init_time >= t:
			self.init_time = time.perf_counter()
			return True
		return False
	
	def cos(self, deg=45, dec=None):
		rad = math.radians(deg)
		cos = math.cos(rad)
		if dec: return round(cos, dec)
		else: return cos
	
	def sin(self, deg=45, dec=None):
		rad = math.radians(deg)
		sin = math.sin(rad)
		if dec: return round(sin, dec)
		else: return sin
	
	def diagonal(self, h, deg=45, inv=False, dec=None):
		deg = deg%90
		ca = h * self.cos(deg, dec)
		co = h * self.sin(deg, dec)
		if inv:
			return {'x': co, 'y': ca}
		else:
			return {'x': ca, 'y': co}
	
	def euclideanDistance(self, A, B):
		''' Formula: d(A,B) = sqrt( (Xb-Xa)^2 + (Yb-Ya)^2 )
		Donde: A=(Xa,Ya), B=(Xb,Yb)
		'''
		Xa, Ya = A
		Xb, Yb = B
		X = (Xb-Xa)**2
		Y = (Yb-Ya)**2
		d = math.sqrt(X+Y)
		return d
	
	def getAngle(self, A, B):
		Xa, Ya = A
		Xb, Yb = B
		X = (Xb-Xa)
		Y = (Yb-Ya)
		atan2 = math.atan2(Y, X)
		angle = math.degrees(atan2)
		return angle
	
	def convertTime(self, t):
		if type(t) == str: return t
		if int(t) < 60: return str(t) + 's'
		else:
			minutes = str(t // 60)
			seconds = str(t % 60)
			if int(seconds) < 10:
				seconds = '0' + seconds
			return minutes + ':' + seconds
	
	def roundRect(self, surface, rect, color, rad=20, border=0, inside=(0,0,0,0)):
		rect = pygame.Rect(rect)
		zeroed_rect = rect.copy()
		zeroed_rect.topleft = 0,0
		image = pygame.Surface(rect.size).convert_alpha()
		image.fill((0,0,0,0))
		self._renderRegion(image, zeroed_rect, color, rad)
		if border:
			zeroed_rect.inflate_ip(-2*border, -2*border)
			self._renderRegion(image, zeroed_rect, inside, rad)
		surface.blit(image, rect)
	
	def _renderRegion(self, image, rect, color, rad):
		corners = rect.inflate(-2*rad, -2*rad)
		for attribute in ('topleft', 'topright', 'bottomleft', 'bottomright'):
			pygame.draw.circle(image, color, getattr(corners,attribute), rad)
		image.fill(color, rect.inflate(-2*rad,0))
		image.fill(color, rect.inflate(0,-2*rad))


class Config:
	
	def __init__(self):
		
		# Configs: -----------------------------------------------------
		
		self.WEAPON = {
			'Laser-mid': {
				'path': 'img/weapons/laser.png',
				'dmg': 50,			# Base damage
				'inc': 1,			# Damage increment per level
				'ammo': 1000,		# Ammunition
				'dist': 250,		# Minimum distance to attack enemies
				'pct_sp': .7,		# Damage percentage to SP
				'mult': 1			# Damage multiplier
			},
			'Laser': {
				'path': 'img/weapons/laser.png',
				'dmg': 100,			# Base damage
				'inc': 1,			# Damage increment per level
				'ammo': 1000,		# Ammunition
				'dist': 400,		# Minimum distance to attack enemies
				'pct_sp': .7,		# Damage percentage to SP
				'mult': 1			# Damage multiplier
			},
			'Plasma': {
				'path': 'img/weapons/plasma.png',
				'dmg': 1000,		# Base damage
				'inc': 10,			# Damage increment per level
				'ammo': 100,		# Ammunition
				'dist': 200,		# Minimum distance to attack enemies
				'pct_sp': .6,		# Damage percentage to SP
				'mult': 1			# Damage multiplier
			}
		}
		
		self.speedmul = 100								# Speed multiplier
		self.baseHP = 350
		self.baseSP = 250
		self.SHIP = {
			'Prometheus': {
				'path': 'img/Prometheus.png',
				'weapon': 'Laser',
				'min_dist_sel': 40,
				'speed':   100,
				'spd_lvl': 0,
				'hp':      self.baseHP,
				'sp':      self.baseSP
			}
		}
		
		self.STRANGERS = {
			'Iken': {
				'path':     'img/Iken (Epsilon).png',
				'lvl':      1,
				'creds':    2,
				'exp':      10,
				'min_dist': 350,
				'min_dist_sel': 40,
				'wpn_name': 'Laser-mid',
				'wpn_lvl':  0,
				'speed':    50,
				'spd_lvl':  0,
				'lhp':      1,
				'lsp':      1,
				'hp':       50,
				'sp':       100
			}
		}
		
		self.MAP = {
			'Zwem':   { 'x': 150, 'y': 150 },
			'Karont': { 'x': 200, 'y': 200 },
			'Arkont': { 'x': 250, 'y': 250 }
		}
		
		# Data settings
		self.BASE_SPEED = 50							# Base Speed of Ships
		self.MAX_SPEED  = 500							# Max Speed of Ships
		self.dtdiv = 10 * self.speedmul					# Detla Time Divide
		self.posdiv = 30								# Divide the actual position of pixels X and Y to generate coordinates for the map
		self.rad_dmg = 300								# Radioactive Damage 
		# ~ self.min_select_dist = 32						# Minimum target selection distance (on pixels)
		
		# Counters
		self.curr_frame = 0								# Current Frame
		
		# Screen settings
		self.RESOLUTION = (600, 450)					# Resolution
		self.MFPS = 120									# Max Frames per Second
		self.fps = 60									# Number of Frames per Second
		
		# Map settings
		self.map_name = 'Zwem'
	
	def getStranger(self, s_name, lvl):
		
		STRANGERS = {
			'Iken': {
				'path':     'img/{}.png',
				'lvl':      1,
				'creds':    1,
				'exp':      10,
				'min_dist': 350,
				'min_dist_sel': 40,
				'wpn_name': 'Laser-mid',
				'wpn_lvl':  0,
				'speed':    50,
				'spd_lvl':  0,
				'lhp':      1,
				'lsp':      1,
				'hp':       self.baseHP,
				'sp':       self.baseSP
			}
		}
		
		imgs = {
			'Iken': {
				1: 'Iken (Alfa)',
				2: 'Iken (Beta)',
				3: 'Iken (Gamma)',
				4: 'Iken (Delta)',
				5: 'Iken (Epsilon)'
			}
		}
		
		if s_name == 'Iken':
			if     0 <= lvl <=  28: s_type = 5
			elif  28 <  lvl <=  56: s_type = 4
			elif  56 <  lvl <=  84: s_type = 3
			elif  84 <  lvl <= 112: s_type = 2
			elif 112 <  lvl:        s_type = 1
		
		stranger = STRANGERS[s_name]
		stranger['lvl']      = lvl
		stranger['path']     = stranger['path'].format(imgs[s_name][s_type])
		stranger['creds']   *= lvl
		stranger['exp']     *= lvl
		stranger['wpn_lvl']  = lvl-1
		stranger['spd_lvl']  = lvl-1
		stranger['lhp']      = lvl
		stranger['lsp']      = lvl
		# ~ stranger['lhp']     *= lvl//2 + lvl%2
		# ~ stranger['lsp']     *= lvl//2
		
		return stranger
	
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
	
	def __init__(self, name, type_='Human'):
		
		self.name = name
		if type_ == 'Human':
			self.base = config.SHIP[name]
			self.weapon = Weapon(self.base['weapon'])
		else:
			self.base = config.STRANGERS[name]
			self.weapon = Weapon(self.base['wpn_name'])
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
		
		self.delta_t_init = time.perf_counter()
		self.t_init_move = 0
		self.t_wait_move = 0
		self.primary_atk = None				# Primary attacker
		self.wait = True
		self.dir = None
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
		data_f +=   '"ang":{},'
		data_f +=   '"atk":"{}",'
		data_f +=   '"shipdata":{{'
		data_f +=     '"chp":{},'
		data_f +=     '"csp":{},'
		data_f +=     '"dtry":"{}"'
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
			self.angle,
			self.attacking,
			self.ship.chp,
			self.ship.csp,
			self.ship.destroyed,
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
		
		if not player['x']         == data['x']:                     player['x']         = data['x']
		if not player['y']         == data['y']:                     player['y']         = data['y']
		if not player['ang']       == data['ang']:                   player['ang']       = data['ang']
		if not player['atk']       == (data['atk'] == 'True'):       player['atk']       = data['atk'] == 'True'
		if not player_s['chp']     == data_s['chp']:                 player_s['chp']     = data_s['chp']
		if not player_s['csp']     == data_s['csp']:                 player_s['csp']     = data_s['csp']
		if not player_s['dtry']    == (data_s['dtry'] == 'True'):    player_s['dtry']    = data_s['dtry'] == 'True'
		
		if data['dmginfo']['dmg'] > 0 and data['dmginfo']['id'] >= 0:
			
			dmginfo = players[data['dmginfo']['id']]['dmginfo']
			
			if not dmginfo.get(self.id):
				dmginfo[self.id] = []
			
			dmginfo[self.id].append([
				data['dmginfo']['dmg'],
				data['dmginfo']['pct_sp'],
				data['dmginfo']['mult'],
				data['dmginfo']['time']
			])
		
		# ~ time.sleep(.01)
		
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
		self.ship = Ship(self.ship_name, 'Stranger')
		
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
	
	def radioactiveZone(self):
		
		if (self.x < 0 or config.map_limits['x'] < self.x)\
		or (self.y < 0 or config.map_limits['y'] < self.y):
			if self.ship.timeOnBorder == 0:
				self.ship.timeOnBorder = time.perf_counter()
			if time.perf_counter() - self.ship.timeOnBorder > 2:
				self.ship.timeOnBorder = time.perf_counter()
				self.ship.recvDamage(config.rad_dmg, pct_sp=0)
		else:
			if self.ship.timeOnBorder > 0:
				self.ship.timeOnBorder = 0
	
	def chkDmgRecv(self):
		
		for enemy_id, values in players[self.id]['dmginfo'].items():
			for dmg, pct_sp, mult, t in values:
				self.ship.recvDamage(dmg, pct_sp, mult)
			
			if (self.primary_atk == None and enemy_id in players) \
			or (not self.primary_atk == None and not self.primary_atk in players):
				self.primary_atk = enemy_id
	
	def deltaTime(self, FPS, mili=True):
		
		delta = time.perf_counter() - self.delta_t_init
		self.delta_t_init = time.perf_counter()
		
		if mili: delta = int(delta * 1000)
		
		time.sleep(1/FPS)
		
		return delta
	
	def setAttack(self):
		
		# Draw Laser and damage on enemies:
		if self.selected['id'] >= 0 and self.attacking:
			# ~ print(self.selected['dist'], self.ship.weapon.dist)
			if self.selected['dist'] < self.ship.weapon.dist:
				
				id_ = self.selected['id']
				try:
					enemy = players[id_]
				except:
					self.selected['name'] = ''
					self.selected['id']   = -1
					self.selected['dist'] = -1
					self.attacking = False
					return
				
				if self.ship.weapon.perSecond():
					
					if enemy['ship']['chp'] > 0:
						
						if enemy['ship']['chp'] < self.ship.weapon.dmg:
							dmg = enemy['ship']['chp']
						else:
							dmg = self.ship.weapon.dmg
						
						pct_sp = self.ship.weapon.pct_sp
						mult = self.ship.weapon.mult
						
						self.selected['dmginfo']['dmg']    = dmg
						self.selected['dmginfo']['pct_sp'] = pct_sp
						self.selected['dmginfo']['mult']   = mult
						self.selected['dmginfo']['time']   = game_time
				
				if enemy['ship']['chp'] == 0:
					self.selected['name'] = ''
					self.selected['id']   = -1
					self.selected['dist'] = -1
					self.attacking = False
	
	def lookAtPlayer(self, p_id, data):
		
		# Gira hacia el enemigo
		if not p_id == self.selected['id']\
		and self.selected['id'] >= 0:
			return
		
		desX = (int(config.CENTER['x'])-int(self.x))	# Desplazamiento en X
		desY = (int(config.CENTER['y'])-int(self.y))	# Desplazamiento en Y
		
		selected_pos = data['x']+desX, data['y']+desY
		pposX, pposY = int(config.CENTER['x']), int(config.CENTER['y'])
		
		dist = round(utils.euclideanDistance((pposX,pposY), selected_pos), 2)
		
		# ~ print(dist, self.ship.base['min_dist'])
		
		if self.primary_atk:
			self.selected['name'] = data['name']
			self.selected['id']   = p_id
			self.selected['dist'] = dist
			self.attacking = True
		
		if dist < self.ship.base['min_dist']:
			self.angle = -round(utils.getAngle((pposX,pposY), selected_pos), 2)
			self.selected['name'] = data['name']
			self.selected['id']   = p_id
			self.selected['dist'] = dist
			self.attacking = True
		elif dist > self.ship.base['min_dist']*2:
			self.selected['name'] = ''
			self.selected['id']   = -1
			self.selected['dist'] = -1
			self.primary_atk = None
		else:
			self.attacking = False
	
	def moveOnMap(self, speed):
		
		limitX = config.MAP[config.map_name]['x']
		limitY = config.MAP[config.map_name]['y']
		x = int(self.x/config.posdiv)
		y = int(self.y/config.posdiv)
		degrees = 0
		
		if self.wait:
			if time.perf_counter() - self.t_init_move >= self.t_wait_move:
				self.wait = False
		else:
			
			if  10 < x < limitX-10\
			and 10 < y < limitY-10:
				
				if self.dir in ['ru','ur']:
					degrees = 0+45
					mov_speed = utils.diagonal(speed, degrees)
					self.x += mov_speed['x']
					self.y -= mov_speed['y']
				elif self.dir in ['lu','ul']:
					degrees = 90+45
					mov_speed_inv = utils.diagonal(speed, degrees, inv=True)
					self.x -= mov_speed_inv['y']
					self.y -= mov_speed_inv['x']
				elif self.dir in ['ld','dl']:
					degrees = 180+45
					mov_speed = utils.diagonal(speed, degrees)
					self.x -= mov_speed['x']
					self.y += mov_speed['y']
				elif self.dir in ['rd','dr']:
					degrees = 270+45
					mov_speed_inv = utils.diagonal(speed, degrees, inv=True)
					self.x += mov_speed_inv['y']
					self.y += mov_speed_inv['x']
				elif 'r' in self.dir:
					degrees = 0
					self.x += speed
				elif 'u' in self.dir:
					degrees = 90
					self.y -= speed
				elif 'l' in self.dir:
					degrees = 180
					self.x -= speed
				elif 'd' in self.dir:
					degrees = 270
					self.y += speed
				
				self.angle = degrees
				
				if random.random() < .001:
					self.dir = random.choice(['r','u','l','d','ru','ul','ld','dr'])
					self.wait = True
					self.t_wait_move = random.randint(1,5)
					self.t_init_move = time.perf_counter()
				
			else:
				
				# ~ self.wait = True
				# ~ self.t_wait_move = random.randint(1,3)
				# ~ self.t_init_move = time.perf_counter()
				
				if x <= 10:
					self.x += speed
					self.dir = random.choice(['r','ru','rd'])
				elif x >= limitX-10:
					self.x -= speed
					self.dir = random.choice(['l','lu','ld'])
				elif y <= 10:
					self.y += speed
					self.dir = random.choice(['d','dl','dr'])
				elif y >= limitY-10:
					self.y -= speed
					self.dir = random.choice(['u','ul','ur'])
	
	def followAndAttack(self, speed, enemy):
		
		x = int(self.x/config.posdiv)
		y = int(self.y/config.posdiv)
		ex = int(enemy['x']/config.posdiv)
		ey = int(enemy['y']/config.posdiv)
		positions = ((self.x,self.y),(enemy['x'],enemy['y']))
		
		self.angle = -utils.getAngle(*positions)
		dist_px = int(utils.euclideanDistance(*positions))
		
		mov_speed = utils.diagonal(speed, self.angle)
		mov_speed_inv = utils.diagonal(speed, self.angle, inv=True)
		
		if dist_px >= 200:
			
			if x > ex and y < ey:
				self.x -= mov_speed['x']
				self.y += mov_speed['y']
			elif x < ex and y < ey:
				self.x += mov_speed_inv['x']
				self.y += mov_speed_inv['y']
			elif x < ex and y > ey:
				self.x += mov_speed['x']
				self.y -= mov_speed['y']
			elif x > ex and y > ey:
				self.x -= mov_speed_inv['x']
				self.y -= mov_speed_inv['y']
			elif x > ex and y == ey:
				self.x -= speed
			elif x < ex and y == ey:
				self.x += speed
			elif y > ey and x == ex:
				self.y -= speed
			elif y < ey and x == ex:
				self.y += speed
	
	def randomMove(self, deltaTime):
		
		speed = self.ship.speed / 100
		# ~ speed *= deltaTime
		
		if not self.dir:
			# ~ print(x, y, self.ship.speed, speed)
			self.wait = False
			self.dir = random.choice(['r','u','l','d','ru','ul','ld','dr'])
		
		for p_id, data in players.items():
			if data['type'] == 'Human':
				self.lookAtPlayer(p_id, data)
		
		if self.selected['id'] >= 0:
			
			self.setAttack()
			
			try:
				enemy = players[self.selected['id']]
			except:
				self.selected['name'] = ''
				self.selected['id']   = -1
				self.selected['dist'] = -1
				self.attacking = False
				return
			
			self.followAndAttack(speed, enemy)
			
		else: self.moveOnMap(speed)

#----------------

utils  = Utils()
config = Config()

# ======================================================================
# FUNCTIONS ============================================================
# ======================================================================

# ~ current_levels = {
	# ~ 'Iken': []
# ~ }

def threaded_bot(stranger_id, stranger_name):
	
	global connections, players, game_time, _id #, current_levels
	
	# ~ while True:
		
		# ~ r = random.randrange(1,224)
		
		# ~ if stranger_name == 'Iken':
			# ~ if     0 <= r <=  28: s_type = 5
			# ~ elif  28 <  r <=  56: s_type = 4
			# ~ elif  56 <  r <=  84: s_type = 3
			# ~ elif  84 <  r <= 112: s_type = 2
			# ~ elif 112 <  r:        s_type = 1
		
		# ~ current_levels[stranger_name].append(r)
	
	while True:
		
		# ~ stranger_info = config.STRANGERS[stranger_name]
		
		r = random.randrange(1,7)
		stranger_info = config.getStranger(stranger_name, r)
		
		map_limits = config.MAP[config.map_name]
		FPS = 240
		
		players[stranger_id] = {
			'x':     random.randrange(20*config.posdiv, (map_limits['x']-20)*config.posdiv),
			'y':     random.randrange(20*config.posdiv, (map_limits['y']-20)*config.posdiv),
			'name':  stranger_name,								# Stranger name
			'type':  'Stranger',								# Type of ship
			'creds': stranger_info['creds'],					# Number of credits
			'exp':   stranger_info['exp'],						# Score
			'ang':   0,											# Angle
			'atk':   False,										# Attacking
			'ship': {
				'name':    stranger_name,						# Ship Name
				'path':    stranger_info['path'],				# Path of ship design
				'lvl':     stranger_info['lvl'],				# Stranger level
				'lhp':     stranger_info['lhp'],				# Health Points
				'lsp':     stranger_info['lsp'],				# Shield Points
				'chp':     stranger_info['lhp']*stranger_info['hp'],	# Current Health Points
				'csp':     stranger_info['lsp']*stranger_info['sp'],	# Current Shield Points
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
		
		deltaTime = 1
		
		while stranger.ship.chp > 0:
			
			# ~ try:
				
				game_time = int(time.perf_counter()-start_time)
				
				stranger.chkDmgRecv()
				stranger.setData()
				stranger.ship.healHP()
				stranger.ship.healSP()
				# ~ stranger.radioactiveZone()
				stranger.randomMove(deltaTime)
				
				deltaTime = stranger.deltaTime(FPS) / config.dtdiv
				
			# ~ except Exception as e:
				# ~ if not str(e).startswith('[WinError 10054]'):
					# ~ print(e, 'Error')
				''# ~ break
		
		print(f'[LOG] Destroyed: {stranger_name}, ID: {stranger_id}')
		
		try:
			players[stranger.primary_atk]['creds'] += players[stranger_id]['creds']
			players[stranger.primary_atk]['exp']   += players[stranger_id]['exp']
		except: pass
		
		time.sleep(1)
		
		del players[stranger_id]
		
		_id += 1
		stranger_id = _id


def threaded_client(conn, _id):
	
	global connections, players, game_time, start
	
	FPS = 1/240
	current_id = _id
	map_limits = config.MAP[config.map_name]
	
	data = conn.recv(24)
	name = data.decode('utf-8')
	print(f"[LOG] '{name}' connected to the server. Client Id: {_id}")
	
	players[current_id] = {
		'x':     random.randrange(20*config.posdiv, (map_limits['x']-20)*config.posdiv),
		'y':     random.randrange(20*config.posdiv, (map_limits['y']-20)*config.posdiv),
		'name':  name,					# Username
		'type':  'Human',				# Type of ship
		'creds': 0,						# Number of credits
		'exp':   0,						# Score
		'ang':   0,						# Angle
		'atk':   False,					# Attacking
		'ship': {
			'lvl':     0,
			'name':    'Prometheus',	# Ship Name
			'lhp':     20,				# Health Points
			'lsp':     20,				# Shield Points
			'chp':     0,				# Current Health Points
			'csp':     0,				# Current Shield Points
			's_unlkd': True,			# Shield Unlocked
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
					print(f"[UNSELECT] '{name}' (ID:{current_id}) unselect to '{unselected}' (ID:{players[current_id]['selected']['id']})")
				else:
					print(f"[SELECT] '{name}' (ID:{current_id}) select to '{selected_name}' (ID:{selected_id})")
				
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

# ======================================================================
# ======================================================================
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
    # ~ S.bind((SERVER_IP, PORT))
    S.bind(('127.0.0.1', PORT))
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

# STRANGERS ============================================================

for i in range(26):
	_id += 1
	thread.start_new_thread(threaded_bot, (_id, 'Iken'))
	time.sleep(.01)

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



