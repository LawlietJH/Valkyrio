
import contextlib
with contextlib.redirect_stdout(None):
	import pygame
from pygame.locals import *
# ~ pygame.font.init()
from Client import Network
import atexit
import random
import math
import time
import os

#=======================================================================

__project__ = 'Valkyrio'
__author__  = 'LawlietJH'
__version__ = '0.0.4 (Alfa)'

__license__ = 'MIT'
__status__  = 'Development'
__framework__    = 'Pygame'
__description__  = 'Juego 2D online con pygame inspirado en los juegos clásicos de destruir naves.'
__version_date__ = '28/08/2021'

#=======================================================================
#=======================================================================
#=======================================================================

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
	
	def diagonal(self, h, deg=45, dec=None):
		deg = deg%90
		ca = h * self.cos(deg, dec)
		co = h * self.sin(deg, dec)
		return ca, co
	
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
		
		# Cons: --------------------------------------------------------
		
		self.specs = ''
		
		self.COLOR = { # https://htmlcolorcodes.com/es/
			'Negro':        (  0,  0,  0),
			'Blanco':       (255,255,255),
			'Azul Galaxia': ( 26, 59, 85),
			'Background':   ( 15, 35, 50),
			'Linea Bg':     ( 26, 90, 85),
			'Azul Celeste': ( 34,113,179),
			'Azul Noche':   ( 25, 28, 50),
			'Rojo':         (255,  0,  0),
			'Verde':        (  0,255,  0),
			'Azul':         (  0,  0,255),
			
			'HP':           (  0,210,  0),		# HP
			'HP Opaco':     (  0,150,  0),		# HP 0
			'SP':           (  0,180,200),		# SP
			'SP Opaco':     (  0,130,140),		# SP 0
			
			'Verde S':      ( 24, 25, 30),
			'Verde N':      (  0, 50, 30),
			'Verde C':      (  0, 75, 30),
			'Verde F':      (  0,100, 30),
		}
		
		self.FONT = {
			'Inc-R 12': pygame.font.Font('font/Inconsolata-Regular.ttf', 12),
			'Inc-R 14': pygame.font.Font('font/Inconsolata-Regular.ttf', 14),
			'Inc-R 16': pygame.font.Font('font/Inconsolata-Regular.ttf', 16),
			'Inc-R 18': pygame.font.Font('font/Inconsolata-Regular.ttf', 18),
			'Retro 12': pygame.font.Font('font/Retro Gaming.ttf', 12),
			'Retro 14': pygame.font.Font('font/Retro Gaming.ttf', 14),
			'Retro 16': pygame.font.Font('font/Retro Gaming.ttf', 16),
			'Retro 18': pygame.font.Font('font/Retro Gaming.ttf', 18),
			'Wendy 12': pygame.font.Font('font/Wendy.ttf', 12),
			'Wendy 14': pygame.font.Font('font/Wendy.ttf', 14),
			'Wendy 16': pygame.font.Font('font/Wendy.ttf', 16),
			'Wendy 18': pygame.font.Font('font/Wendy.ttf', 18),
			'Comic 12': pygame.font.SysFont('comicsans', 12),
			'Comic 14': pygame.font.SysFont('comicsans', 14),
			'Comic 16': pygame.font.SysFont('comicsans', 16),
			'Comic 18': pygame.font.SysFont('comicsans', 18)
		}	# Diccionario de Fuentes.
		
		self.MUSIC = {
			'JNATHYN - Genesis': 'sound/music/JNATHYN - Genesis.mp3'
		}
		
		# Sound Effects
		self.SFX = {}
		
		# Music
		self.music = pygame.mixer.music
		self.sound = pygame.mixer.Sound
		
		# Configs: -----------------------------------------------------
		
		self.show = {
			'name':      True,		# Show the name of the player and the name of the enemies
			'speed':     True,		# Show player speed 
			'fps':       True,		# Show fps
			'pos':       True,		# Show player coordinates
			'hp-sp':     True,		# Show player's HP and SP numbers
			'weapon':    True,		# Displays the name and level of the weapon
			'creds_exp': True,		# Show accumulated damage
			'acc_dmg':   False		# Show accumulated damage
		}
		
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
				'path':   'img/Prometheus.png',
				'weapon': 'Laser',
				'speed':   int(.5 * self.speedmul),
				'spd_lvl': 0,
				'hp':      15,
				'sp':      25
			}
		}
		
		self.MAP = {
			'Zwem':   { 'x': 200, 'y': 200 },
			'Karont': { 'x': 300, 'y': 300 },
			'Arkont': { 'x': 400, 'y': 400 }
		}
		
		# Username settings
		self.name_min_char_len = 1						# Minimum Character Length
		self.name_max_char_len = 24						# Maximum Character Length
		
		# Data settings
		self.BASE_SPEED = 1 * self.speedmul				# Base Speed of Ships
		self.MAX_SPEED  = 2 * self.speedmul				# Max Speed of Ships
		self.dtdiv = 10 * self.speedmul					# Detla Time Divide
		self.posdiv = 20								# Divide the actual position of pixels X and Y to generate coordinates for the map
		self.rad_dmg = 500								# Radioactive Damage 
		self.min_select_dist = 32						# Minimum target selection distance (on pixels)
		self.acc_dmg = False							#
		
		# Counters
		self.curr_frame = 0								# Current Frame
		
		# Background matrix settings
		self.matrix_bg_sqr = 15							# Type: False = variable. Squares on Background. Example: 15x15
		self.xy_pixels_sqr = 50							# Type: True = fixed.     X and Y pixels in squares on background
		self.matrix_bg_fix = True						# Select Type: fixed or variable
		
		# Screen settings
		# ~ self.RESOLUTION = (1280, 768)					# Resolution
		self.RESOLUTION = (600, 450)					# Resolution
		self.antialiasing = True						# Anti-aliasing is a method by which you can remove irregularities that appear in objects in PC games.
		self.run = False								# Game Run
		self.MFPS = 120									# Max Frames per Second
		self.fps = 60									# Number of Frames per Second
		
		# Music settings
		self.music_vol = 20							# Music volume
		
		# Map settings
		self.map_name = 'Zwem'
		
		# Objects that are off the screen disappear
		self.limit_obj_dist = int(utils.euclideanDistance((
								self.CENTER['x'], self.CENTER['y']),
								(0, 0)
							)) + 200
	
	@property
	def CENTER(self):
		return {'x': self.RESOLUTION[0]//2, 'y': self.RESOLUTION[1]//2}
	
	@property
	def W(self):
		return self.RESOLUTION[0]
	
	@property
	def H(self):
		return self.RESOLUTION[1]
	
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
	
	def recvDamage(self, damage, pct_sp=None, mult=1, draw=True):			# Registra el daño recibido para mostrarlo
		
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
		
		if draw: self.damageRecv.append([damage*mult, time.perf_counter()])
	
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


class Player:
	
	def __init__(self, name=None, id_=None):
		
		self.name = name
		self.ship = None
		self.ship_name = None
		self.ship_path = None
		self.img_orig = None
		self.img = None
		
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
	
	def __str__(self):
		text = f"<'Name':'{self.name}', 'ID':'{self.id}'>"
		return text
	
	@property
	def data(self):
		
		data_f  = 'data:{{'
		data_f +=   '"x":{},'
		data_f +=   '"y":{},'
		data_f +=   '"creds":{},'
		data_f +=   '"exp":{},'
		data_f +=   '"ang":{},'
		data_f +=   '"atk":"{}",'
		data_f +=   '"shipdata":{{'
		data_f +=     '"name":"{}",'
		data_f +=     '"lhp":{},'
		data_f +=     '"lsp":{},'
		data_f +=     '"chp":{},'
		data_f +=     '"csp":{},'
		data_f +=     '"s_unlkd":"{}",'
		data_f +=     '"dtry":"{}",'
		data_f +=     '"spd_lvl":{},'
		data_f +=     '"weapon":{{'
		data_f +=       '"name":"{}",'
		data_f +=       '"lvl":{}'
		data_f +=     '}}'
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
			self.creds,
			self.exp,
			self.angle,
			self.attacking,
			self.ship.name,
			self.ship.lhp,
			self.ship.lsp,
			self.ship.chp,
			self.ship.csp,
			self.ship.shield_unlocked,
			self.ship.destroyed,
			self.ship.spd_lvl,
			self.ship.weapon.name,
			self.ship.weapon.lvl,
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
		
		return data
	
	def rotate(self, angle):
		img = self.img_orig
		self.img = pygame.transform.rotate(img, angle)
	
	def resize(self, image, scale=1):
		rect = image.get_rect()
		wdth_hgt = (int(rect[2]*scale), int(rect[3]*scale))
		image = pygame.transform.scale(image, wdth_hgt)
		return image
	
	def antialiasing(self, img):
		"""
		Anti-aliasing by average of color code in four pixels
		with subsequent use of the average in a smaller surface
		"""
		rect = image.get_rect()			#	width		height
		new_img = pygame.surface.Surface((rect[2]//1, rect[3]//1))
		
		for y in range(0, rect[3]-1):
			for x in range(0, rect[2]-1):
				r1, g1, b1, a1 = img.get_at((x,   y))
				r2, g2, b2, a2 = img.get_at((x+1, y))
				r3, g3, b3, a3 = img.get_at((x,   y+1))
				r4, g4, b4, a4 = img.get_at((x+1, y+1))
				r = (r1 + r2 + r3 + r4) / 4
				g = (g1 + g2 + g3 + g4) / 4
				b = (b1 + b2 + b3 + b4) / 4
				new_img.set_at((x, y), (r, g, b, 255))
		
		return new_img
	
	def loadData(self, players):
		
		player = players[self.id]
		
		self.x = player['x']
		self.y = player['y']
		
		self.selected['name'] = player['selected']['name']
		self.selected['id']   = player['selected']['id']
		
		self.creds = player['creds']
		self.exp = player['exp']
		
		self.angle = player['ang']
		self.attacking = player['atk']
			
		self.ship_name = player['ship']['name']
		self.ship_path = config.SHIP[self.ship_name]['path']
		self.ship = Ship(self.ship_name)
		
		self.ship.hp = 0
		self.ship.sp = 0
		self.ship.lhp = 0
		self.ship.lsp = 0
		self.ship.levelUpHP(player['ship']['lhp'])
		self.ship.shield_unlocked = player['ship']['s_unlkd']
		self.ship.levelUpSP(player['ship']['lsp'])
		
		if not player['ship']['chp'] == 0 \
		and player['ship']['chp'] <= self.ship.lhp:
			self.ship.chp = player['ship']['chp']
		else:
			self.ship.chp = self.ship.hp
		
		if player['ship']['csp'] <= self.ship.lsp:
			self.ship.csp = player['ship']['csp']
		else:
			self.ship.csp = self.ship.sp
		
		self.ship.destroyed = player['ship']['dtry']
		self.ship.spd_lvl = player['ship']['spd_lvl']
		
		self.ship.weapon = Weapon(player['ship']['weapon']['name'])
		self.ship.weapon.levelUpDmg(player['ship']['weapon']['lvl'])
		
		self.img_orig = self.loadImage(self.ship_path)
		self.img = self.img_orig
		self.rotate(self.angle)
	
	def updateData(self, players):
		
		player = players[self.id]
		
		if not self.x == player['x']: self.x = player['x']
		if not self.y == player['y']: self.y = player['y']
		
		if not self.angle == player['ang']:
			self.angle = player['ang']
			self.rotate(self.angle)
		
		if not self.attacking == player['atk']: self.attacking = player['atk']
		
		if not self.creds == player['creds']: self.creds = player['creds']
		if not self.exp == player['exp']: self.exp = player['exp']
		
		if not self.selected == player['selected']: self.selected = player['selected']
		
		# Add damages received -----------------------------------------
		if not self.under_attack:
			for enemy_id, values in player['dmginfo'].items():
				for dmg, pct_sp, mult, t in values:
					self.under_attack = True
					self.ship.recvDamage(dmg, pct_sp, mult)
		else: self.under_attack = False
		#---------------------------------------------------------------
		
		if not self.ship_name == player['ship']['name']:
			self.ship_name = player['ship']['name']
			self.ship_path = config.SHIP[self.ship_name]['path']
			self.ship = Ship(self.ship_name)
		
		# ~ if not player['ship']['hp'] == self.ship.hp:
			# ~ self.ship.hp = player['ship']['hp']
		# ~ if not player['ship']['sp'] == self.ship.sp:
			# ~ self.ship.sp = player['ship']['sp']
		
		# HP and SP ----------------------------------------
		if not self.ship.lhp == player['ship']['lhp']:
			self.ship.hp = 0
			self.ship.lhp = 0
			self.ship.levelUpHP(player['ship']['lhp'])
		
		if not self.ship.shield_unlocked == player['ship']['s_unlkd']: self.ship.shield_unlocked = player['ship']['s_unlkd']
		
		if not self.ship.lsp == player['ship']['lsp']:
			self.ship.sp = 0
			self.ship.lsp = 0
			self.ship.levelUpSP(player['ship']['lsp'])
		
		# ~ if player['ship']['chp'] <= self.ship.chp:
			# ~ self.ship.chp = player['ship']['chp']
		# ~ else:
			# ~ self.ship.chp = self.ship.hp
		
		# ~ if player['ship']['csp'] <= self.ship.csp:
			# ~ self.ship.csp = player['ship']['csp']
		# ~ else:
			# ~ self.ship.csp = self.ship.sp
		
		if not self.ship.chp == player['ship']['chp']: self.ship.chp = player['ship']['chp']
		if not self.ship.csp == player['ship']['csp']: self.ship.csp = player['ship']['csp']
		#---------------------------------------------------
		
		if not self.ship.destroyed == player['ship']['dtry']:    self.ship.destroyed = player['ship']['dtry']
		if not self.ship.spd_lvl   == player['ship']['spd_lvl']: self.ship.spd_lvl = player['ship']['spd_lvl']
		
		# ~ if not self.ship.weapon == player['ship']['weapon']['name']:
			# ~ self.ship.weapon = Weapon(player['ship']['weapon']['name'])
			# ~ self.ship.weapon.levelUpDmg(player['ship']['weapon']['lvl'])
		# ~ else:
			# ~ if not self.ship.weapon.lvl == player['ship']['weapon']['lvl']:
				# ~ lvl = self.ship.weapon.lvl - player['ship']['weapon']['lvl']
				# ~ self.ship.weapon.levelUpDmg(lvl)
	
	def loadImage(self, filename, transparent=True):
		try: image = pygame.image.load(filename)
		except pygame.error as message: raise SystemError
		image = image.convert()
		# ~ image = self.resize(image, 1.2)
		if transparent:
			color = image.get_at((0,0))
			image.set_colorkey(color, RLEACCEL)
		return image

#=======================================================================
#=======================================================================
#=======================================================================

pygame.init()
pygame.mixer.init()
pygame.font.init()

server = Network()
utils  = Utils()
config = Config()
player = Player()

# Dynamic Variables
enemies = {}
game_time = None
WIN = None

#=======================================================================
#=======================================================================
#=======================================================================

# Rules ------------------------------------------

def radioactiveZone():
	
	if (player.x < 0 or config.map_limits['x'] < player.x)\
	or (player.y < 0 or config.map_limits['y'] < player.y):
		if player.ship.timeOnBorder == 0:
			player.ship.timeOnBorder = time.perf_counter()
		if time.perf_counter() - player.ship.timeOnBorder > 2:
			player.ship.timeOnBorder = time.perf_counter()
			player.ship.recvDamage(config.rad_dmg, pct_sp=0)
	else:
		if player.ship.timeOnBorder > 0:
			player.ship.timeOnBorder = 0

# Actions ----------------------------------------

def setAttack():
	
	# Draw Laser and damage on enemies:
	if player.selected['id'] >= 0 and player.attacking:
		
		if player.selected['dist'] < player.ship.weapon.dist:
			
			if player.ship.weapon.perSecond():
				
				id_ = player.selected['id']
				enemy = enemies[id_]
				
				if enemy.ship.chp > 0:
					
					if enemy.ship.chp < player.ship.weapon.dmg:
						dmg = enemy.ship.chp
						# ~ enemy.ship.recvDamage(dmg, pct_sp)
					else:
						dmg = player.ship.weapon.dmg
					
					pct_sp = player.ship.weapon.pct_sp
					mult = player.ship.weapon.mult
					
					player.selected['dmginfo']['dmg']    = dmg
					player.selected['dmginfo']['pct_sp'] = pct_sp
					player.selected['dmginfo']['mult']   = mult
					player.selected['dmginfo']['time']   = game_time
					
				else:
					print(enemy.id, enemy.creds, enemy.exp)
					player.creds += enemy.creds
					player.exp   += enemy.exp
					enemy.creds = 0
					enemy.exp   = 0

def lookAtEnemy():
	
	desX = (int(config.CENTER['x'])-int(player.x))	# Desplazamiento en X
	desY = (int(config.CENTER['y'])-int(player.y))	# Desplazamiento en Y
	
	# Gira hacia el enemigo
	if player.selected['id'] >= 0 and player.attacking:
		
		player.ship.time_hp_init = 0									# Reinicia el contador para regenracion de HP
		
		p_id = player.selected['id']
		
		try:
			selected_pos = enemies[p_id].x+desX, enemies[p_id].y+desY
		except:
			player.selected['name'] = ''
			player.selected['id']   = -1
			player.selected['dist'] = -1
			return
		
		pposX, pposY = int(config.CENTER['x']), int(config.CENTER['y'])
		
		dist  = round(utils.euclideanDistance((pposX,pposY), selected_pos), 2)
		angle = -round(utils.getAngle((pposX,pposY), selected_pos), 2)
		
		player.selected['dist'] = dist
		player.angle = angle
		player.rotate(angle)

def selectEnemy(event):
	
	if event.button == 1:
		
		desX = (int(config.CENTER['x'])-int(player.x))	# Desplazamiento en X
		desY = (int(config.CENTER['y'])-int(player.y))	# Desplazamiento en Y
		
		posX, posY = event.pos
		dists = []
		for other_player_id in enemies:
			if other_player_id == player.id: continue
			other_player = enemies[other_player_id]
			pposX = other_player.x+desX
			pposY = other_player.y+desY
			
			dist = utils.euclideanDistance((posX, posY), (pposX,pposY))
			
			if dist < config.min_select_dist:
				dists.append(( dist, other_player.name, other_player_id ))
		
		min_dist      = config.min_select_dist
		min_dist_name = ''
		min_dist_id   = 0
		
		data_f = 'selected:{{"name":"{}","id":{}}}'
		data = ''
		
		if len(dists) > 1:
			for dist, name, p_id in dists:
				if dist < min_dist:
					min_dist      = dist
					min_dist_name = name
					min_dist_id   = p_id
			if not min_dist_id == player.selected['id']:
				player.attacking = False
				player.selected['name'] = min_dist_name
				player.selected['id']   = min_dist_id
				data = data_f.format(min_dist_name, min_dist_id)
		elif dists:
			if not dists[0][2] == player.selected['id']:
				player.attacking = False
				player.selected['name'] = dists[0][1]
				player.selected['id']   = dists[0][2]
				data = data_f.format(dists[0][1], dists[0][2])
		
		if data:
			players = server.send(data)
			return players
	
	if event.button == 3:
		player.attacking = False
		if player.selected['id'] >= 0:
			player.selected['name'] = ''
			player.selected['id']   = -1
			player.selected['dist'] = -1
			data = 'selected:{"name":"","id":-1}'
			players = server.send(data)
			return players

def calcFrames():
	
	if utils.perSecond():
		config.fps = config.curr_frame
		config.curr_frame = 0
	else:
		config.curr_frame += 1

def getUsername():
	# Get users name
	while True:
		name = input('[+] Please enter your Username: ')
		if config.name_min_char_len <= len(name) <= config.name_max_char_len:
			break
		else:
			msg  = '[NameError] Error, this name is not allowed (must be between '
			msg += f'{config.name_min_char_len} and {config.name_max_char_len}'
			msg += ' characters [inclusive])'
			print(msg)
	return name

# Events -----------------------------------------

def detectEvents():
	
	for event in pygame.event.get():
		
		if event.type == pygame.TEXTINPUT: continue
		
		if event.type == pygame.QUIT:
			config.run = False
		
		if event.type == VIDEORESIZE:
			config.RESOLUTION = event.dict['size']
		
		if event.type == pygame.KEYDOWN:
			
			if event.key == pygame.K_ESCAPE:
				config.run = False
			
			if event.key == pygame.K_LSHIFT:
				if player.selected['id'] >= 0:
					player.attacking = not player.attacking
			
			if event.key == pygame.K_j:
				player.ship.speedLevelUP(-1)
			if event.key == pygame.K_k:
				player.ship.speedLevelUP()
			if event.key == pygame.K_o:
				config.show['name'] = not config.show['name']
			if event.key == pygame.K_p:
				config.show['hp-sp'] = not config.show['hp-sp']
			if event.key == pygame.K_u:
				player.ship.levelUpHP()
			if event.key == pygame.K_i:
				if not player.ship.shield_unlocked:
					player.ship.shield_unlocked = True
				player.ship.levelUpSP()
			
			if event.key == pygame.K_h:
				player.ship.weapon.levelUpDmg()
			
			if event.key == pygame.K_l:
				player.ship.recvDamage(100, pct_sp=1, mult=1)
		
		# ~ if event.type == pygame.MOUSEMOTION:
		
		if event.type == pygame.MOUSEBUTTONDOWN:
			players = selectEnemy(event)
			if players: updateOtherPlayers(players)

def movements(deltaTime):
		
		keys = pygame.key.get_pressed()
		speed = player.ship.speed
		speed = speed * deltaTime
		
		movements = False
		degrees = 0
		x = 0
		y = 0
		
		leftMove  = keys[pygame.K_LEFT]  or keys[pygame.K_a]
		rightMove = keys[pygame.K_RIGHT] or keys[pygame.K_d]
		upMove    = keys[pygame.K_UP]    or keys[pygame.K_w]
		downMove  = keys[pygame.K_DOWN]  or keys[pygame.K_s]
		leftRightMove = leftMove and rightMove
		upDownMove    = upMove and downMove
		player_curr_pos = int(player.x/config.posdiv), int(player.y/config.posdiv)
		
		if leftMove and not rightMove:
			player.curr_pos = player_curr_pos
			movements = True
			if not upDownMove and (upMove or downMove):
				if   upMove:   degrees = 90
				elif downMove: degrees = 270
				x -= utils.diagonal(speed)[0]
			else:
				degrees = 180
				x -= speed
		
		if rightMove and not leftMove:
			# ~ if player.curr_pos[0]+2 < player_curr_pos[0]:
				# ~ x = player.curr_pos[0]
			# ~ else:
				player.curr_pos = player_curr_pos
				movements = True
				if not upDownMove and (upMove or downMove):
					if   upMove:   degrees = 90
					elif downMove: degrees = 270
					x += utils.diagonal(speed)[0]
				else:
					degrees = 0
					x += speed
		
		if upMove and not downMove:
			player.curr_pos = player_curr_pos
			movements = True
			if not leftRightMove and (leftMove or rightMove):
				if leftMove:  degrees += 45
				if rightMove: degrees -= 45
				y -= utils.diagonal(speed)[1]
			else:
				degrees = 90
				y -= speed
		
		if downMove and not upMove:
			player.curr_pos = player_curr_pos
			movements = True
			if not leftRightMove and (leftMove or rightMove):
				if leftMove:  degrees -= 45
				if rightMove: degrees += 45
				y += utils.diagonal(speed)[1]
			else:
				degrees = 270
				y += speed
		
		if movements:
			player.ship.time_hp_init = 0
			player.angle = degrees
			player.rotate(degrees)
			player.x += round(x, 2)
			player.y += round(y, 2)
		else:
			# Recibir HP bajo sus reglas:
			player.ship.healHP()
		
		# Recibir SP bajo sus reglas:
		player.ship.healSP()

# Update Data ------------------------------------

def updateOtherPlayers(players):
	
	# Update enemies
	ids_removed = []
	for id_ in enemies:
		if enemies[id_].__class__.__name__ == 'Player':
			if id_ in players:
				enemies[id_].updateData(players)
			else:
				ids_removed.append(id_)
	
	# Remove expired IDs
	for id_ in ids_removed: del enemies[id_]
	
	# Add new enemies
	for id_ in players:
		if id_ == player.id: continue
		if not id_ in enemies:
			name = players[id_]['name']
			other_player = Player(name, id_)
			other_player.loadData(players)
			enemies[id_] = other_player

# Window -----------------------------------------

def renderText(text, font, color, _type=''):
	
	if 'bold' in _type:   font.set_bold(True)
	elif font.get_bold(): font.set_bold(False)
	if 'italic' in _type:   font.set_italic(True)
	elif font.get_italic(): font.set_italic(False)
	if 'underline' in _type:   font.set_underline(True)
	elif font.get_underline(): font.set_underline(False)
	
	rendered_text = font.render(text, config.antialiasing, color)
	return rendered_text

def drawShipAndData(ship, des, name_color):
	
	# Draw red circle ----------------------------
	if player.selected['id'] == ship.id:	# Circulo de selección
		pygame.draw.circle(WIN,
			(255,0,0), (
				int(ship.x)+des[0],
				int(ship.y)+des[1]
			), config.min_select_dist, 1
		)
	
	# Draw Ship ----------------------------------
	rect = ship.img.get_rect(
		center = (
			int(ship.x)+des[0],
			int(ship.y)+des[1]
		)
	)
	WIN.blit(ship.img, rect)
	
	desp = 50
	
	# Draw Name ----------------------------------
	if config.show['name']:
		font = config.FONT['Inc-R 18']
		text = '-- [' + ship.name + '] --'
		text = renderText(text, font, name_color, 'bold')
		WIN.blit(text, (
				int(ship.x)+des[0] - text.get_width() /2,
				int(ship.y)+des[1] - text.get_height()/2 + desp
			)
		)
		desp += text.get_height()-5
	
	# Draw HP and SP -----------------------------
	if ship.id == player.id:
		# Draw HP ------------------------------------
		font = config.FONT['Inc-R 14']
		if ship.ship.chp == 0:
			color = config.COLOR['HP Opaco']
		else:
			color = config.COLOR['HP']
		text = f'{ship.ship.chp}/{ship.ship.hp}'
		text = renderText(text, font, color, 'bold italic')
		WIN.blit(text, (
				int(ship.x)+des[0] - text.get_width() /2,
				int(ship.y)+des[1] - text.get_height()/2 + desp
			)
		)
		desp += text.get_height()-3
		
		# Draw SP ------------------------------------
		font = config.FONT['Inc-R 14']
		if not ship.ship.shield_unlocked or ship.ship.csp == 0:
			color = config.COLOR['SP Opaco']
		else:
			color = config.COLOR['SP']
		text = f'{ship.ship.csp}/{ship.ship.sp}'
		text = renderText(text, font, color, 'bold italic')
		WIN.blit(text, (
				int(ship.x)+des[0] - text.get_width() /2,
				int(ship.y)+des[1] - text.get_height()/2 + desp
			)
		)
	
	# Draw HP an SP bars -------------------------
	if ship.id == player.id or ship.id == player.selected['id']:
		
		# Draw HP an SP bars -------------------------
		desp = 45
		height = 6
		width = 50
		
		widthHP = width+int(ship.ship.hp/int((350/4)*3))+1
		widthSP = width+int(ship.ship.sp/int((250/4)*3))+1
		
		if widthHP > 200: widthHP = 200
		if widthSP > 200: widthSP = 200
		
		bars = [
			(config.COLOR['HP'], widthHP, ship.ship.chp, ship.ship.hp),
			(config.COLOR['SP'], widthSP, ship.ship.csp, ship.ship.sp)
		]
		
		for i, (color, width, cp, p) in enumerate(bars):
			
			if i == 1 and not ship.ship.shield_unlocked: continue
			
			x = int(ship.x)+des[0] - width/2
			y = int(ship.y)+des[1] - desp
			position = [x, y, width, height]
			utils.roundRect(WIN, position, config.COLOR['Verde F'],
				2, 1, (*color, 50)
			)
			
			x = int(ship.x)+des[0] - width/2
			y = int(ship.y)+des[1] - desp
			# ~ if i == 1:
				# ~ print(cp, '/', p)
			pct = cp / p
			position = [x, y, int(width*pct), height]
			utils.roundRect(WIN, position, config.COLOR['Verde F'],
				2, 1, (*color, 200)
			)
			
			desp -= height
	
	#===================================================================
	# Draw taken damage --------------------------
	if ship.ship.damageRecv:
		
		if config.show['acc_dmg']:
			
			len_dmg = len(ship.ship.damageRecv)
			for i in range(len_dmg):
				if ship.ship.damageRecv[i]:
					t1 = ship.ship.damageRecv[i][1]
					if time.perf_counter()-t1 < 1.3:
						if i+1 < len_dmg:
							dmg = ship.ship.damageRecv[i+1][0]
							t2  = ship.ship.damageRecv[i+1][1]
							if abs(t2-t1) < 1.3:
								ship.ship.damageRecv[i][0] += dmg
								ship.ship.damageRecv[i+1] = None
			
			while None in ship.ship.damageRecv:
				ship.ship.damageRecv.remove(None)
		
		out = -1
		for i, (damage, t) in enumerate(ship.ship.damageRecv):
			
			t = time.perf_counter()-t
			if t >= 2: out = i; break
			font = config.FONT['Inc-R 16']
			color = config.COLOR['Rojo']
			text = str(damage)
			text = renderText(text, font, color, 'bold italic')
			t_h = text.get_height()
			
			# ~ t = t**2
			# ~ movx = int(t*20)
			# ~ movy = int(t*(20-(20*(t/2-1))))
			# ~ WIN.blit(text, (
					# ~ int(ship.x)+des[0] - text.get_width() /2 + movx,
					# ~ int(ship.y)+des[1] - text.get_height()/2 -t_h - movy
				# ~ )
			# ~ )
			
			# _dir = (1 if random.random() > .5 else -1)
			t = t**2
			movx = text.get_width() + t_h + int(t*10) #*_di
			movy = int(t**2)
			WIN.blit(text, (
					int(ship.x)+des[0] - text.get_width() /2 + movx,
					int(ship.y)+des[1] - text.get_height()/2 -t_h - movy
				)
			)
		
		if out >= 0: ship.ship.damageRecv.pop(out)

def drawMatrix(desX, desY):
	
	if config.matrix_bg_fix:
		x_r = config.xy_pixels_sqr
		y_r = config.xy_pixels_sqr
		linesW = int(config.W/x_r)
		linesH = int(config.H/y_r)
	else:
		per = config.H/config.W
		linesW = config.matrix_bg_sqr
		linesH = int(linesW * per)
		x_r = int(config.W / linesW)
		y_r = int(config.H / linesH)
	
	# Lineas Horizontales
	for x in range(linesW+2):
		x1 = -x_r + x_r * x + desX%x_r
		y1 = -y_r
		x2 = -x_r + x_r * x + desX%x_r
		y2 = config.H + y_r
		pygame.draw.line(WIN, config.COLOR['Linea Bg'], (x1,y1), (x2,y2), 1)
	
	# Lineas Verticales
	for y in range(linesH+2):
		x1 = -x_r
		y1 = -y_r + y_r * y + desY%y_r
		x2 = config.W + x_r
		y2 = -y_r + y_r * y + desY%y_r
		pygame.draw.line(WIN, config.COLOR['Linea Bg'], (x1,y1), (x2,y2), 1)

def drawOtherInfo(game_time):
	
	font = config.FONT['Retro 18']
	
	# Draw Experience: -------------------------------------------------
	enemies_sorted = sorted(enemies, key=lambda x: enemies[x].exp)
	sort_enemies = list(reversed(enemies_sorted))
	text = 'Experience'
	text = renderText(text, font, config.COLOR['Blanco'])
	start_y = 25
	x = config.W - text.get_width() - 10
	WIN.blit(text, (x, 5))
	
	ran = min(len(enemies), 3)
	for count, i in enumerate(sort_enemies[:ran]):
		text = str(count+1) + '. ' + str(enemies[i].name)
		text = renderText(text, font, config.COLOR['Blanco'])
		WIN.blit(text, (x, start_y + count * 20))
	
	# Draw time: -------------------------------------------------------
	text = 'Time: ' + utils.convertTime(game_time)
	text = renderText(text, font, config.COLOR['Blanco'])
	WIN.blit(text,(10, 10))
	
	# Draw player Experience: -----------------------------------------------
	text = 'Exp: ' + str(round(player.exp))
	text = renderText(text, font, config.COLOR['Blanco'])
	WIN.blit(text,(10, 15 + text.get_height()))

def drawConfigData():
	
	font  = config.FONT['Inc-R 14']
	color = config.COLOR['Blanco']
	despX = 10			# Desplazamiento en X
	despY = 15			# Desplazamiento en Y
	ftexts = {}
	texts = {}
	widest = 0
	
	# Generate texts -----------------------------
	if config.show['weapon']:
		text = f'Weapon: {player.ship.weapon.name} ({player.ship.weapon.lvl})'
		text = renderText(text, font, color)
		texts['weapon_name'] = text
		text = f'+Damage: {player.ship.weapon.dmg}'
		text = renderText(text, font, color)
		texts['weapon_dmg'] = text
	if config.show['creds_exp']:
		text = 'Exp: ' + str(player.exp)
		text = renderText(text, font, color)
		texts['exp'] = text
		text = 'Creds: ' + str(player.creds)
		text = renderText(text, font, color)
		texts['creds'] = text
	if config.show['speed']:
		text = 'Speed: ' + str(player.ship.speed)
		text = renderText(text, font, color)
		texts['speed'] = text
	if config.show['fps']:
		text = 'FPS: '+str(config.fps)
		text = renderText(text, font, color)
		texts['fps'] = text
	if config.show['pos']:
		text = '({},{})'.format(
			int(player.x/config.posdiv),
			int(player.y/config.posdiv)
		).ljust(11)
		text = renderText(text, font, color)
		texts['pos'] = text
	
	for text in texts.values():
		if text.get_width() > widest:
			widest = text.get_width()
	
	# Draw box -----------------------------------
	ltexts = len(texts)
	positions = [
		despX - 5,
		config.H - 10 - despY*ltexts - 5,
		widest + 10,
		despY*ltexts + 10
	]
	
	utils.roundRect(WIN, positions, config.COLOR['Verde F'],
		3, 1, (*config.COLOR['Verde S'], 50)
	)
	
	# Draw texts ---------------------------------
	for i, text in enumerate(list(texts.values())[::-1]):
		WIN.blit(text, (despX, config.H-text.get_height()-10 -(despY*i)))

def redrawWindow():
	
	BLANCO = config.COLOR['Blanco']
	ROJO   = config.COLOR['Rojo']
	WIN.fill(config.COLOR['Background'])
	
	desX = (int(config.CENTER['x'])-int(player.x))	# Desplazamiento en X
	desY = (int(config.CENTER['y'])-int(player.y))	# Desplazamiento en Y
	
	drawMatrix(desX, desY)										# Dibuja las lineas del fondo
	
	# Draw Other Players: ==============================================
	
	enemies_sorted = sorted(enemies, key=lambda x: enemies[x].exp)
	
	for other_player_id in enemies_sorted:
		
		if other_player_id == player.id: continue
		
		other_player = enemies[other_player_id]
		
		# Draw the ship: -------------------------------
		
		other_player_dist = 0
		if not other_player.id == player.id:
			other_player_dist = utils.euclideanDistance(
				( int(config.CENTER['x']),  int(config.CENTER['y'])  ),
				( int(other_player.x+desX), int(other_player.y+desY) )
			)
			other_player_dist = round(other_player_dist, 2)
		
		if other_player_dist < config.limit_obj_dist:
			drawShipAndData(other_player, (desX,desY), ROJO)
	
	# Draw Player: =====================================================
	
	drawShipAndData(player, (desX,desY), BLANCO)
	
	# Draw Game Info on main layer data: ===============================
	
	drawConfigData()
	
	if player.ship.timeOnBorder:
		font = config.FONT['Retro 18']
		text = 'Radioactive Zone'
		text = renderText(text, font, BLANCO)
		WIN.blit(text, (config.CENTER['x']-text.get_width()/2, 30))
	
	if player.ship.destroyed:
		font = config.FONT['Retro 18']
		text = 'Destroyed'
		text = renderText(text, font, BLANCO)
		WIN.blit(text, (config.CENTER['x']-text.get_width()/2, 60))
	
	# Draw other info on main layer data: ==============================
	
	# ~ drawOtherInfo(game_time)

def createWindow():
	
	global WIN
	
	# Make window start in top left hand corner
	# os.environ['SDL_VIDEO_WINDOW_POS'] = f'{0},{30}'
	
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	
	# Setup pygame window
	WIN = pygame.display.set_mode((config.W,config.H), HWSURFACE | DOUBLEBUF | RESIZABLE)
	pygame.display.set_caption(f'{__project__} Online {__version__} - By: {__author__}')
	
	# Music
	config.music.load(config.MUSIC['JNATHYN - Genesis'])
	config.music.set_volume(config.music_vol/100)
	config.music.play(-1)

#=======================================================================

def main():
	
	global game_time
	
	config.run = True
	deltaTime = 1					# Delta Time
	clock = pygame.time.Clock()
	
	# start by connecting to the network ---------
	while True:
		player.name = getUsername()
		try: player.id = server.connect(player.name); break
		except ConnectionRefusedError as e:
			print(f'[ConnectionRefusedError]: {e}')
	
	#---------------------------------------------
	
	createWindow()
	
	players = server.send('get')
	player.loadData(players)
	
	#---------------------------------------------
	
	while config.run:
		
		players, game_time = server.send(player.data)		# Envia datos al servidor y recibe la información de los otros jugadores
		
		#---------------------------------------------------------------
		# Add damages received:
		for enemy_id, values in players[player.id]['dmginfo'].items():
			for dmg, pct_sp, mult, t in values:
				player.ship.recvDamage(dmg, pct_sp, mult)
		#---------------------------------------------------------------
		
		# Update Data:
		updateOtherPlayers(players)							# Actualiza los datos de los enemigos
		
		# Events:
		movements(deltaTime)								# Detecta los movimientos direccionales
		detectEvents()										# Detecta los eventos de Mouse y Teclado
		
		# Actions:
		lookAtEnemy()										# Si el enemigo esta seleccionado o el jugador es seleccionado, las naves giran apuntandose.
		setAttack()											# Agrega el daño causado al enemigo
		radioactiveZone()									# Reglas para la zona radioactiva
		calcFrames()										# Calcula la cantidad de fotogramas por segundo.
		
		# Draw Window:
		redrawWindow()										# Redibuja todo (1 Fotograma)
		
		# Update Window Data
		pygame.display.update()								# Actualiza la ventana con todos los cambios
		
		# Delta Time:
		deltaTime = clock.tick(config.MFPS) / config.dtdiv	# Hace una breve pausa para respetar los Fotogramas por segundo y devuelve el "Delta Time"/1000
	
	server.disconnect()
	pygame.quit()
	quit()

#=======================================================================

# Ejecuta esto despues de terminar la ejecución del programa.
@atexit.register
def close():
	time.sleep(1)

#=======================================================================

# start game
main()

#=======================================================================
# Añadido el: 26/08/2021
# + Actualizado el titulo de la ventana del juego.
# + Agregados Mapas y sus limites de forma más dinámica.
# + El ataque ya NO se mantiene activo cuando el enemigo se desconecta o selecciona otro objetivo.
# + Arreglado bug en daño (el calculo daba ocasionalmente error con -1 punto en el daño, por los flotantes a enteros)
# + Eliminado Score y agregado 'Experience (exp)' y 'Credits (creds)'
# + Modificado Server para obtención de mejor manera los datos
# + Agregado sistema de niveles en HP y SP más dinámico
# + Corregida actualización de SP y HP en tiempo real en enemigos.
# Añadido el: 28/08/2021
# + Agregada Música de fondo al juego.
# + Agregados los "Strangers" (NPCs) en el mapa. Estos son los seres que vagan por el
#   espacio en sus naves, estos piratas o mercenarios te destruirán sin dudarlo.
# + Mostrados Créditos y experiencia del jugador.
# + Agregados Créditos y Experiencia al jugador al destruir Strangers.
# + Respawn de Strangers al ser destruidos.
# + Optimización en partes del código.
# + Agregada curación automática de NPCs.
# + Arreglado: último golpe no mostraba el daño causado.
# Bugs Detectados:
# + Daño causado de enemigos a enemigos no carga correctamente.



