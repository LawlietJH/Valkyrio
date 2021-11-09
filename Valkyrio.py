
import contextlib
with contextlib.redirect_stdout(None):
	import pygame
from pygame.locals import *
from Client import Network
import atexit
import random
import math
import time
import os

#=======================================================================

__project__ = 'Valkyrio'
__author__  = 'LawlietJH'
__version__ = '0.0.7 (Alfa)'

__license__ = 'MIT'
__status__  = 'Development'
__framework__    = 'Pygame'
__description__  = 'Juego 2D online con pygame inspirado en los juegos clásicos de destruir naves.'
__version_date__ = '06/09/2021'

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
	
	def cos(self, deg=45):
		rad = math.radians(deg)
		return math.cos(rad)
	
	def sin(self, deg=45):
		rad = math.radians(deg)
		return math.sin(rad)
	
	def diagonal(self, h, deg=45, rounded=True):
		
		inv = True if deg//90 in [1,-1,3,-3] else False 
		deg = deg%90
		
		if inv:
			co = h * self.cos(deg)
			ca = h * self.sin(deg)
		else:
			ca = h * self.cos(deg)
			co = h * self.sin(deg)
		
		if rounded:
			if str(rounded).isnumeric():
				return {'x': round(ca, rounded), 'y': round(co, rounded)}
			else:
				return {'x': round(ca, 2), 'y': round(co, 2)}
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
		''' Donde: A=(Xa,Ya), B=(Xb,Yb) '''
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
	
	def roundRect(self, rect, color, rad=20, border=0, inside=(0,0,0,0)):
		rect = pygame.Rect(rect)
		zeroed_rect = rect.copy()
		zeroed_rect.topleft = 0,0
		image = pygame.Surface(rect.size).convert_alpha()
		image.fill((0,0,0,0))
		self._renderRegion(image, zeroed_rect, color, rad)
		if border:
			zeroed_rect.inflate_ip(-2*border, -2*border)
			self._renderRegion(image, zeroed_rect, inside, rad)
		return (image, rect)
	
	def _renderRegion(self, image, rect, color, rad):
		corners = rect.inflate(-2*rad, -2*rad)
		for attribute in ('topleft', 'topright', 'bottomleft', 'bottomright'):
			pygame.draw.circle(image, color, getattr(corners,attribute), rad)
		image.fill(color, rect.inflate(-2*rad,0))
		image.fill(color, rect.inflate(0,-2*rad))
	
	def moveWindow(self, win_x, win_y, win_w, win_h):
		from ctypes import windll
		# ~ NOSIZE = 1
		# ~ NOMOVE = 2
		# ~ TOPMOST = -1
		# ~ NOT_TOPMOST = -2
		# ~ windll.user32.SetWindowPos(hwnd, NOT_TOPMOST, 0, 0, 0, 0, NOMOVE|NOSIZE)
		# ~ w, h = pygame.display.get_surface().get_size()
		hwnd = pygame.display.get_wm_info()['window']
		windll.user32.MoveWindow(hwnd, win_x, win_y, win_w, win_h, False)
	
	def splitText(self, text, chunk_size=32):
		
		output = []
		chunks  = len(text)//chunk_size
		chunks += 1 if len(text)%chunk_size > 0 else 1
		
		while text:
			
			p = chunk_size
			br = 1
			
			try:
				while not text[p] == ' ':
					p -= 1
					if p == 0:
						br = 0
						p = chunk_size
						break
			except: pass
			
			chunk = text[:p]
			text = text[p+br:]
			output.append(chunk)
		
		return output
	
	def colorMask(self, surf, color, color_to_replace=(255,255,255)):
		''' pygame.transform.threshold(
			mask_image, img, color_to_replace,
			(0,0,0,0), color, 1, None, True)
		'''
		pygame.transform.threshold(
			surf, surf, color_to_replace,
			(0,0,0,0), color, 1, None, True
		)
	
	def perfectOutline(self, img, loc, color=(0,0,0), alpha=255, br=1):
		
		mask = pygame.mask.from_surface(img)
		mask_surf = mask.to_surface()
		
		# Remplaza el color en la imagen y agrega transparencia (alpha: 0~255)
		self.colorMask(mask_surf, (*color, alpha))
		
		# Agrega la transparencia de la imagen
		mask_surf.set_colorkey((0,0,0))
		
		WIN.blit(mask_surf, (loc[0]-br, loc[1]))
		WIN.blit(mask_surf, (loc[0]+br, loc[1]))
		WIN.blit(mask_surf, (loc[0], loc[1]-br))
		WIN.blit(mask_surf, (loc[0], loc[1]+br))
		
		WIN.blit(mask_surf, (loc[0]-br, loc[1]-br))
		WIN.blit(mask_surf, (loc[0]+br, loc[1]+br))
		WIN.blit(mask_surf, (loc[0]-br, loc[1]+br))
		WIN.blit(mask_surf, (loc[0]+br, loc[1]-br))
	
	@property
	def curWinRect(self):
		from ctypes import POINTER, WINFUNCTYPE, windll
		from ctypes.wintypes import BOOL, HWND, RECT
		
		hwnd = pygame.display.get_wm_info()['window']
		prototype = WINFUNCTYPE(BOOL, HWND, POINTER(RECT))
		paramflags = (1, 'hwnd'), (2, 'lprect')
		GetWindowRect = prototype(('GetWindowRect', windll.user32), paramflags)
		rect = GetWindowRect(hwnd)
		return [rect.left, rect.top, rect.right, rect.bottom]
	
	@property
	def curWinSize(self):
		info = pygame.display.Info()
		return [info.current_w, info.current_h]


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
			'Rojo Opaco':   (127,  0,  0),
			'Verde':        (  0,255,  0),
			'Azul':         (  0,  0,255),
			'Cyan':         (  0,180,200),
			'Cyan Opaco':   (  0,130,140),
			'Verde Claro':  (  0,210,  0),
			'Verde Opaco':  (  0,150,  0),
			
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
			'Inc-R 13': pygame.font.Font('font/Inconsolata-Regular.ttf', 13),
			'Inc-R 14': pygame.font.Font('font/Inconsolata-Regular.ttf', 14),
			'Inc-R 15': pygame.font.Font('font/Inconsolata-Regular.ttf', 15),
			'Inc-R 16': pygame.font.Font('font/Inconsolata-Regular.ttf', 16),
			'Inc-R 18': pygame.font.Font('font/Inconsolata-Regular.ttf', 18),
			'Inc-R 20': pygame.font.Font('font/Inconsolata-Regular.ttf', 20),
			'Inc-R 24': pygame.font.Font('font/Inconsolata-Regular.ttf', 24),
			'Retro 12': pygame.font.Font('font/Retro Gaming.ttf', 12),
			'Retro 14': pygame.font.Font('font/Retro Gaming.ttf', 14),
			'Retro 16': pygame.font.Font('font/Retro Gaming.ttf', 16),
			'Retro 18': pygame.font.Font('font/Retro Gaming.ttf', 18),
			'Retro 20': pygame.font.Font('font/Retro Gaming.ttf', 20),
			'Retro 24': pygame.font.Font('font/Retro Gaming.ttf', 24),
			'Wendy 12': pygame.font.Font('font/Wendy.ttf', 12),
			'Wendy 14': pygame.font.Font('font/Wendy.ttf', 14),
			'Wendy 16': pygame.font.Font('font/Wendy.ttf', 16),
			'Wendy 18': pygame.font.Font('font/Wendy.ttf', 18),
			'Wendy 20': pygame.font.Font('font/Wendy.ttf', 20),
			'Wendy 24': pygame.font.Font('font/Wendy.ttf', 24),
			'Comic 12': pygame.font.SysFont('comicsans', 12),
			'Comic 14': pygame.font.SysFont('comicsans', 14),
			'Comic 16': pygame.font.SysFont('comicsans', 16),
			'Comic 18': pygame.font.SysFont('comicsans', 18),
			'Comic 20': pygame.font.SysFont('comicsans', 20),
			'Comic 24': pygame.font.SysFont('comicsans', 24)
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
			'name':          True,		# Show the name of the player and the name of the enemies
			'speed':         True,		# Show player speed 
			'fps':           True,		# Show fps
			'pos':           True,		# Show player coordinates
			'hp-sp':         True,		# Show player's HP and SP numbers
			'weapon':        True,		# Displays the name and level of the weapon
			'creds_exp':     True,		# Show credits and experience
			'acc_dmg':       True,		# Show accumulated damage
			'map_enemies':   True,		# Show all enemies on minimap
			'matrix_bg_fix': True,		# Show background matrix fixed
			'chat':          False		# Show Chat
		}
		
		self.WEAPON = {
			'Laser-mid': {
				'path': 'img/weapons/laser.png',
				'dmg': 50,			# Base damage
				'inc': 5,			# Damage increment per level
				'ammo': 1000,		# Ammunition
				'dist': 250,		# Minimum distance to attack enemies
				'pct_sp': .7,		# Damage percentage to SP
				'mult': 1			# Damage multiplier
			},
			'Laser': {
				'path': 'img/weapons/laser.png',
				'dmg': 100,			# Base damage
				'inc': 10,			# Damage increment per level
				'ammo': 1000,		# Ammunition
				'dist': 400,		# Minimum distance to attack enemies
				'pct_sp': .7,		# Damage percentage to SP
				'mult': 1			# Damage multiplier
			},
			'Plasma': {
				'path': 'img/weapons/plasma.png',
				'dmg': 1000,		# Base damage
				'inc': 50,			# Damage increment per level
				'ammo': 100,		# Ammunition
				'dist': 200,		# Minimum distance to attack enemies
				'pct_sp': .6,		# Damage percentage to SP
				'mult': 1			# Damage multiplier
			}
		}
		
		self.baseHP = 350
		self.baseSP = 250
		self.SHIP = {
			'Prometheus': {
				'path': 'img/Prometheus.png',
				'weapon': 'Laser',
				'min_dist_sel': 40,
				'lvl':     1,
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
			'Zwem':   { 'x': 200, 'y': 150 },
			'Karont': { 'x': 250, 'y': 200 },
			'Arkont': { 'x': 300, 'y': 250 }
		}
		
		self.roundRects = {}							# Created round rects
		
		# Username settings
		self.name_min_char_len = 1						# Minimum Character Length
		self.name_max_char_len = 24						# Maximum Character Length
		
		# Data settings
		self.MAX_SPD_LVL = 112							# Max Speed level of Ships
		self.dtdiv = 1000								# Detla Time Divide
		self.posdiv = 30								# Divide the actual position of pixels X and Y to generate coordinates for the map
		self.rad_dmg = 500								# Radioactive Damage 
		self.open_menu = False							# Is open menu
		self.pos_tab_menu = 1							# Position of menu tab
		
		# Counters
		self.curr_frame = 0								# Current Frame
		
		# Background matrix settings
		self.matrix_bg_sqr = 15							# Type: False = variable. Squares on Background. Example: 15x15
		self.xy_pixels_sqr = 50							# Type: True = fixed.     X and Y pixels in squares on background
		
		# Screen settings
		self.min_w = 600								# Minimum width resolution
		self.min_h = 400								# Minimum height resolution
		self.full_screen = False						# Full Screen
		self.RESOLUTION = (720, 480)					# Resolution
		self.screen_full_size = pygame.display.list_modes()[0]	# Resolution
		self.windowed_pos = []							# Current window pos and size (Windowed)
		self.init_time_windowed = 0
		self.antialiasing = True						# Anti-aliasing is a method by which you can remove irregularities that appear in objects in PC games.
		self.run = False								# Game Run
		self.MFPS = 120									# Max Frames per Second
		self.fps = 60									# Number of Frames per Second
		
		# Music settings
		self.music_vol = 20							# Music volume
		
		# Map settings
		self.map_name = 'Zwem'
	
	# Properties ---------------------------------
	
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
	def map_limits(self): # Actual map coordinates in number of pixels
		return {
			'x': self.MAP[self.map_name]['x'] * self.posdiv,
			'y': self.MAP[self.map_name]['y'] * self.posdiv
		}
	
	@property
	def limit_obj_dist(self):
		# Objects that are off the screen disappear
		limit_obj_dist = int(utils.euclideanDistance((
								self.CENTER['x'], self.CENTER['y']),
								(0, 0)
							)) + 100
		return limit_obj_dist
	
	# Functions ----------------------------------
	
	def videoResize(self, event):
		if not self.RESOLUTION == event.size:
			if not self.full_screen \
			and time.perf_counter() - self.init_time_windowed > 1:
				mw = self.min_w
				mh = self.min_h
				w, h = event.size
				if w < mw: w = mw
				if h < mh: h = mh
				self.RESOLUTION = (w, h)
				WIN = pygame.display.set_mode((w, h), HWSURFACE | DOUBLEBUF | RESIZABLE)
			else:
				self.RESOLUTION = event.size
	
	def switchFullScreen(self):
		
		if not self.full_screen:
			self.full_screen = True
			self.windowed_pos = utils.curWinRect[:2] + utils.curWinSize
			WIN = pygame.display.set_mode(
				self.screen_full_size,
				HWSURFACE | DOUBLEBUF | FULLSCREEN
			)
		else:
			self.init_time_windowed = time.perf_counter()
			self.full_screen = False
			win_x = self.windowed_pos[0]
			win_y = self.windowed_pos[1]
			win_w = self.windowed_pos[2]
			win_h = self.windowed_pos[3]
			
			self.RESOLUTION = (win_w, win_h)
			WIN = pygame.display.set_mode(
				(win_w, win_h),
				HWSURFACE | DOUBLEBUF | RESIZABLE
			)
			
			add_w  = utils.curWinRect[2]
			add_w += abs(utils.curWinRect[0])
			add_w -= utils.curWinSize[0]
			
			add_h  = utils.curWinRect[3]
			add_h += abs(utils.curWinRect[1])
			add_h -= utils.curWinSize[1]
			
			utils.moveWindow(win_x, win_y, win_w+add_w, win_h+add_h)
			WIN = pygame.display.set_mode(
				self.RESOLUTION,
				HWSURFACE | DOUBLEBUF | RESIZABLE
			)


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
		self.type = type_
		if self.type == 'Human':
			self.base = config.SHIP[name]
			self.weapon = Weapon(self.base['weapon'])
		else:
			self.base = config.STRANGERS[name]
			self.weapon = Weapon(self.base['wpn_name'])
		self.destroyed = False
		self.spd_lvl = self.base['spd_lvl']
		self.lvl = self.base['lvl']
		
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
		self.pct_res_dmg_rad = 0		# 0.0~1.0: Percentage of resistance to damage in the radiative zone
		
		self.damageRecv = []
		self.healthRecv = []
	
	@property
	def speed(self):
		# Aumento de velocidad en forma exponencial y=sqrt(200x+100) tomando en cuenta que
		# el nivel x=112 y=150, todo basado en: y=sqrt(max_lvl*current_lvl)
		init = 10
		speed = self.base['speed']										# Velocidad base de la nave
		val = math.sqrt(200*(self.spd_lvl+1)-100)-init					# Aumento de velocidad en forma de parabola, basado en: y = sqrt(200x+100)
		add = init * (self.spd_lvl/(config.MAX_SPD_LVL))
		speed += val+add
		return int(speed)
	
	def speedLevelUP(self, lvl=1):
		if self.spd_lvl+lvl <= config.MAX_SPD_LVL:
			self.spd_lvl += lvl
		else:
			self.spd_lvl = config.MAX_SPD_LVL
	
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
		
		self.follow_pos = False
		self.follow_pos_move = False
		self.follow_pos_xy = (0,0)
		
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
		if player['type'] == 'Human':
			self.ship_path = config.SHIP[self.ship_name]['path']
			self.ship = Ship(self.ship_name)
		else:
			self.ship_path = player['ship']['path']
			self.ship = Ship(self.ship_name, 'Stranger')
		
		self.ship.lvl = player['ship']['lvl']
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
		
		if not player['ship']['csp'] == 0 \
		and player['ship']['csp'] <= self.ship.lsp:
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
			if player['type'] == 'Human':
				self.ship_path = config.SHIP[self.ship_name]['path']
			else:
				# ~ self.ship_path = config.STRANGERS[self.ship_name]['path']
				self.ship_path = player['ship']['path']
			self.ship = Ship(self.ship_name)
		
		# ~ if not player['ship']['hp'] == self.ship.hp:
			# ~ self.ship.hp = player['ship']['hp']
		# ~ if not player['ship']['sp'] == self.ship.sp:
			# ~ self.ship.sp = player['ship']['sp']
		
		if not self.ship.lvl == player['ship']['lvl']: self.ship.lvl = player['ship']['lvl']
		
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
		''		# ~ self.ship.weapon.levelUpDmg(lvl)
	
	def loadImage(self, filename, transparent=True):
		try: image = pygame.image.load(filename)
		except pygame.error as message: raise SystemError
		image = image.convert()
		# ~ image = self.resize(image, 1.2)
		if transparent:
			color = image.get_at((0,0))
			image.set_colorkey(color, RLEACCEL)
		return image
	
	def followPos(self, speed):
		
		if self.follow_pos:
			
			x = int(self.x)
			y = int(self.y)
			gpx, gpy = self.follow_pos_xy
			
			if not self.follow_pos_move:
				self.angle = -utils.getAngle((x,y),(gpx,gpy))
				self.rotate(self.angle)
				self.follow_pos_move = True
			
			if self.selected['id'] >= 0:
				angle = -utils.getAngle((x,y),(gpx,gpy))
				mov_speed = utils.diagonal(speed, self.angle)
				if self.attacking:
					mov_speed = utils.diagonal(speed, angle)
				elif not int(angle) == int(self.angle):
					self.angle = angle
					self.rotate(self.angle)
			else:
				mov_speed = utils.diagonal(speed, self.angle)
			
			dist_px = int(utils.euclideanDistance((x,y),(gpx,gpy)))
			
			if dist_px > 5:
				if x > gpx and y < gpy:
					self.x -= mov_speed['x']
					self.y += mov_speed['y']
				elif x < gpx and y < gpy:
					self.x += mov_speed['x']
					self.y += mov_speed['y']
				elif x < gpx and y > gpy:
					self.x += mov_speed['x']
					self.y -= mov_speed['y']
				elif x > gpx and y > gpy:
					self.x -= mov_speed['x']
					self.y -= mov_speed['y']
				elif x > gpx and y == gpy:
					self.x -= speed
				elif x < gpx and y == gpy:
					self.x += speed
				elif y > gpy and x == gpx:
					self.y -= speed
				elif y < gpy and x == gpx:
					self.y += speed
			else:
				self.cancelFollowPos()
	
	def cancelFollowPos(self):
		self.follow_pos = False
		self.follow_pos_move = False
		self.follow_pos_xy = (0,0)

#-------------------------------------------------

class Minimap:
	
	def __init__(self):
		
		# Map settings
		self.map_name = 'Zwem'
		self.map_name_rect = (0,0)
		self.map_w = 150
		self.map_h = 120
		self.map_x = config.W - self.map_w - 5
		self.map_y = config.H - self.map_h - 5
		self.map_move = False
		self.map_move_pos = (0,0)
		self.map_move_x = config.W - self.map_w - 5
		self.map_move_y = config.H - self.map_h - 5
		
		# Current Quadrant on Screen
		self.quad = 4
		
		# Tamaño del minimapa
		self.btn_col     = 'Cyan'
		self.btn_col_off = 'Rojo Opaco'
		self.btn_plus  = []
		self.btn_minus = []
		self.map_resize = False
		self.map_size = 1
		self.map_size_max = 6
		self.map_size_x = 25
		self.map_size_y = 20
		self.set_size(mult=self.map_size)
	
	def setFollowPos(self, event):
		
		x, y = event.pos
		
		# Distancia en coordenadas falsas (las coordenadas falsas son las mostradas al usuario en gameplay)
		dif_x = x-self.map_x
		dif_y = y-self.map_y
		
		# Distancia en coordenadas reales basado en el tamaño del mapa
		dif_x = int(round(config.MAP[self.map_name]['x'] * (dif_x/self.map_w)))
		dif_y = int(round(config.MAP[self.map_name]['y'] * (dif_y/self.map_h)))
		
		if  1 < dif_x < config.MAP[self.map_name]['x']-1\
		and 1 < dif_y < config.MAP[self.map_name]['y']-1:
			player.follow_pos = True
			player.follow_pos_move = False
			player.follow_pos_xy = (	# Ahora se toman las cordenadas reales (en pixeles)
				dif_x*config.posdiv,
				dif_y*config.posdiv
			)
		# ~ else:
			# ~ if player.follow_pos:
		''		# ~ player.cancelFollowPos()
	
	def scrPosOnMap(self, x, y, add=2):
		return (
			x-add-((config.CENTER['x']/config.posdiv) / config.MAP[self.map_name]['x'] * self.map_w),
			y-add-((config.CENTER['y']/config.posdiv) / config.MAP[self.map_name]['y'] * self.map_h),
			(add*2)+(config.W/config.posdiv) / config.MAP[self.map_name]['x'] * self.map_w,
			(add*2)+(config.H/config.posdiv) / config.MAP[self.map_name]['y'] * self.map_h
		)
	
	def set_size(self, add=True, mult=1):
		
		self.map_w = 150 + (self.map_size_x*self.map_size)
		self.map_h = 120 + (self.map_size_y*self.map_size)
		
		if add:
			if self.quad in [1,4]:
				self.map_x -= self.map_size_x * mult
			if self.quad in [3,4]:
				self.map_y -= self.map_size_y * mult
		else:
			if self.quad in [1,4]:
				self.map_x += self.map_size_x * mult
			if self.quad in [3,4]:
				self.map_y += self.map_size_y * mult
		
		# ~ self.quadrant(*config.RESOLUTION)
		self.map_resize = True
		self.map_move_x = self.map_x
		self.map_move_y = self.map_y
	
	def resize(self, event):
		
		x, y = event.pos
		
		if  self.btn_minus[1][0]-5 < x < self.btn_minus[1][0]+self.btn_minus[0][0]+3\
		and self.btn_minus[1][1]   < y < self.btn_minus[1][1]+self.btn_minus[0][1]:
			if not self.map_size == 0:
				self.map_size -= 1
				self.set_size(add=False)
		
		if  self.btn_plus[1][0]-5 < x < self.btn_plus[1][0]+self.btn_plus[0][0]+5\
		and self.btn_plus[1][1]   < y < self.btn_plus[1][1]+self.btn_plus[0][1]:
			if not self.map_size == self.map_size_max:
				self.map_size += 1
				self.set_size(add=True)
	
	def limitMove(self): # Limita el movimiento del mapa para que no pueda salir de la pantalla
		if self.map_x > self.map_x_orig:
			self.map_x = self.map_x_orig
		if self.map_x-5 < 0:
			self.map_x = 5
		if self.map_y > self.map_y_orig:
			self.map_y = self.map_y_orig
		if self.map_y-self.map_name_rect[1]-5 < 0:
			self.map_y = self.map_name_rect[1]+5
	
	def quadrant(self, w, h):
		if   self.map_x > w//2 and self.map_y < h//2: self.quad = 1			# Right Upper Quadrant
		elif self.map_x < w//2 and self.map_y < h//2: self.quad = 2			# Left  Upper Quadrant
		elif self.map_x < w//2 and self.map_y > h//2: self.quad = 3			# Left  Lower Quadrant
		elif self.map_x > w//2 and self.map_y > h//2: self.quad = 4			# Right Lower Quadrant
	
	def onResizeScreen(self, orig_res):
		
		w, h = orig_res
		
		self.quadrant(w, h)
		
		if self.quad in [1,4]:
			dif_x = w - self.map_x
			self.map_x = config.W - dif_x
		if self.quad in [3,4]:
			dif_y = h - self.map_y
			self.map_y = config.H - dif_y
		
		self.limitMove()
		
		self.map_move_x = self.map_x
		self.map_move_y = self.map_y
	
	def mouseButtonDown(self, event):
		pos_x, pos_y = event.pos
		if  self.map_move_x < pos_x < self.map_move_x+self.map_name_rect[0]\
		and self.map_move_y-self.map_name_rect[1] < pos_y < self.map_move_y:
			self.map_move = True
			self.map_move_pos = event.pos
	
	def mouseButtonUp(self):
		if self.map_move:
			self.map_move_x = self.map_x
			self.map_move_y = self.map_y
			self.map_move = False
	
	def mouseMotion(self, event):
		
		if self.map_move:
			
			pos_x, pos_y = event.pos
			clic_pos_x, clic_pos_y = self.map_move_pos
			x = pos_x-self.map_move_x
			y = pos_y-self.map_move_y
			d_x = abs(self.map_move_x-clic_pos_x)
			d_y = abs(self.map_move_y-clic_pos_y)
			
			self.map_x = self.map_move_x+x-d_x
			self.map_y = self.map_move_y+y+d_y
			
			self.quadrant(*config.RESOLUTION)
			
			self.limitMove()
	
	def windowLeave(self):
		if self.map_move:
			self.map_move_x = self.map_x
			self.map_move_y = self.map_y
			self.map_move = False
	
	@property
	def map_pos(self):
		return [
			self.map_x, self.map_y,
			self.map_w, self.map_h
		]
	
	@property
	def player_pos(self):
		return (
			round((player.x/config.posdiv) / config.MAP[self.map_name]['x'] * self.map_w + self.map_x, 2),
			round((player.y/config.posdiv) / config.MAP[self.map_name]['y'] * self.map_h + self.map_y, 2)
		)
	
	@property
	def map_x_orig(self):
		return config.W - self.map_w - 5
	
	@property
	def map_y_orig(self):
		return config.H - self.map_h - 5


class Chat:
	
	def __init__(self):
		
		self.messages = {
			'global': [
				('Enylaine','Hola :D'),
				('LOL','xD')
			]
		}
		
		self.chat_name = 'Chat'
		self.chat_name_rect = (0,0)
		self.chat_global_name_rect = (0,0)
		self.chat_min_w = 150
		self.chat_min_h = 120
		self.chat_max_w = 300
		self.chat_max_h = 240
		self.chat_w = 225
		self.chat_h = 150
		self.chat_x = 5
		self.chat_y = 20
		self.chat_x_orig = self.chat_x
		self.chat_y_orig = self.chat_y
		self.chat_move = False
		self.chat_move_pos = (0,0)
		self.chat_move_x = self.chat_x
		self.chat_move_y = self.chat_y
		self.pct_tr = 50					# Percentage of transparency
		self.chat_text_active = False
		self.chat_text = ''
		self.chat_tab = 1
		self.chat_msg_tam = 14				# 12, 14, 16
		
		self.init_time = time.perf_counter()
	
	@property
	def chat_pos(self):
		return [
			self.chat_x, self.chat_y,
			self.chat_w, self.chat_h
		]
	
	@property
	def chat_input_pos(self):
		anc = 4
		return [
			self.chat_x + anc*1.5, self.chat_h - anc*1.5,
			self.chat_w -(anc*3),  anc*5
		]
	
	@property
	def chat_inner_pos(self):
		anc, tab = 4, 18
		return [
			self.chat_x + anc,    self.chat_y + tab,
			self.chat_w -(anc*2), self.chat_h - tab - anc
		]
	
	def perSecond(self, t=1):
		if time.perf_counter() - self.init_time >= t:
			self.init_time = time.perf_counter()
			return True
		return False
	
	def activeInput(self, event):
		if event.button == 1:
			x, y = event.pos
			inp_pos = self.chat_input_pos
			if  inp_pos[0] < x < inp_pos[0]+inp_pos[2]\
			and inp_pos[1] < y < inp_pos[1]+inp_pos[3]:
				self.chat_text_active = True
			else:
				self.chat_text_active = False
		else:
			if chat.chat_text_active:
				chat.chat_text_active = False
	
	def setGlobalMessages(self, messages):
		self.messages['global'] = messages
	
	def limitMove(self): # Limita el movimiento del mapa para que no pueda salir de la pantalla
		if self.chat_x > self.chat_x_orig:
			self.chat_x = self.chat_x_orig
		if self.chat_x-5 < 0:
			self.chat_x = 5
		if self.chat_y > self.chat_y_orig:
			self.chat_y = self.chat_y_orig
		if self.chat_y-self.chat_name_rect[1]-5 < 0:
			self.chat_y = self.chat_name_rect[1]+5
	
	def quadrant(self, w, h):
		if   self.chat_x > w//2 and self.chat_y < h//2: self.quad = 1			# Right Upper Quadrant
		elif self.chat_x < w//2 and self.chat_y < h//2: self.quad = 2			# Left  Upper Quadrant
		elif self.chat_x < w//2 and self.chat_y > h//2: self.quad = 3			# Left  Lower Quadrant
		elif self.chat_x > w//2 and self.chat_y > h//2: self.quad = 4			# Right Lower Quadrant
	
	def mouseButtonDown(self, event):
		pos_x, pos_y = event.pos
		if  self.chat_move_x < pos_x < self.chat_move_x+self.chat_name_rect[0]\
		and self.chat_move_y-self.chat_name_rect[1] < pos_y < self.chat_move_y:
			self.chat_move = True
			self.chat_move_pos = event.pos
	
	def mouseButtonUp(self):
		if self.chat_move:
			self.chat_move_x = self.chat_x
			self.chat_move_y = self.chat_y
			self.chat_move = False
	
	def mouseMotion(self, event):
		
		if self.chat_move:
			
			pos_x, pos_y = event.pos
			clic_pos_x, clic_pos_y = self.chat_move_pos
			x = pos_x-self.chat_move_x
			y = pos_y-self.chat_move_y
			d_x = abs(self.chat_move_x-clic_pos_x)
			d_y = abs(self.chat_move_y-clic_pos_y)
			
			self.chat_x = self.chat_move_x+x-d_x
			self.chat_y = self.chat_move_y+y+d_y
			
			self.quadrant(*config.RESOLUTION)
			
			self.limitMove()

#=======================================================================
#=======================================================================
#=======================================================================

pygame.init()
pygame.mixer.init()
pygame.font.init()

# Basic Objects
server  = Network()
utils   = Utils()
config  = Config()
player  = Player()

# General Objects
minimap = Minimap()
chat = Chat()

# Dynamic Variables
enemies = {}
game_time = None
WIN = None

#=======================================================================
#=======================================================================
#=======================================================================

# Events -----------------------------------------

def keysDown(event):
	
	if event.key == pygame.K_ESCAPE:						# ESC - Close Game
		config.run = False
	
	if event.key == pygame.K_LSHIFT:						# LShift- Attack
		if player.selected['id'] >= 0:
			player.attacking = not player.attacking
	
	# Hide/Show ---------------
	if event.key == pygame.K_TAB:
		
		# Control de menu ------------------------
		config.open_menu = not config.open_menu
		
		# Control de input del chat ------------------------
		if chat.chat_text_active:
			chat.chat_text_active = False
	
	if not config.open_menu:
		if event.key == pygame.K_o:								# O - Hide/Show Names
			config.show['name'] = not config.show['name']
		if event.key == pygame.K_p:								# P - Hide/Show HP-SP
			config.show['hp-sp'] = not config.show['hp-sp']
	
	#--------------------------
	
	if event.key == pygame.K_F11:
		config.switchFullScreen()
			
	#--------------------------
	
	if event.key == pygame.K_1:
		if config.open_menu:
			config.pos_tab_menu = 1
	if event.key == pygame.K_2:
		if config.open_menu:
			config.pos_tab_menu = 2
	if event.key == pygame.K_3:
		if config.open_menu:
			config.pos_tab_menu = 3
	if event.key == pygame.K_4:
		if config.open_menu:
			config.pos_tab_menu = 4
	if event.key == pygame.K_5:
		if config.open_menu:
			config.pos_tab_menu = 5
	if event.key == pygame.K_6:
		if config.open_menu:
			config.pos_tab_menu = 6
	if event.key == pygame.K_7:
		if config.open_menu:
			config.pos_tab_menu = 7
	if event.key == pygame.K_8:
		if config.open_menu:
			config.pos_tab_menu = 8
	if event.key == pygame.K_9:
		if config.open_menu:
			config.pos_tab_menu = 9
	if event.key == pygame.K_0:
		if config.open_menu:
			config.pos_tab_menu = 0
	
	#--------------------------
	
	if event.key == pygame.K_BACKSPACE:
		# Control de input del chat ------------------------
		if chat.chat_text_active and chat.chat_text:
			chat.chat_text = chat.chat_text[:-1]
	
	if event.key == pygame.K_RETURN:
		# Control de input del chat ------------------------
		if chat.chat_text_active and chat.chat_text:
			
			if chat.chat_tab == 1: chat_type = 'global'
			
			msg = 'msg:'+chat_type+':'+player.name+':'+chat.chat_text
			chat.messages = server.send(msg)
			chat.chat_text = ''
	
	if event.key == pygame.K_PLUS:							# +
		if chat.chat_w < chat.chat_max_w:
			chat.chat_w += 5
		print(chat.chat_w)
	if event.key == pygame.K_MINUS:							# -
		if chat.chat_w > chat.chat_min_w:
			chat.chat_w -= 5
		print(chat.chat_w)
	
	if event.key == pygame.K_t:								# t
		if chat.chat_h < chat.chat_max_h:
			chat.chat_h += 5
		print(chat.chat_h)
	if event.key == pygame.K_y:								# y
		if chat.chat_h > chat.chat_min_h:
			chat.chat_h -= 5
		print(chat.chat_h)
	
	#--------------------------
	if event.key == pygame.K_j:								# J - Speed level down
		if player.ship.spd_lvl > 0:
			cost = player.ship.spd_lvl
			player.creds += cost
			player.ship.speedLevelUP(-10)
	if event.key == pygame.K_k:								# J - Speed level up
		# ~ cost = (player.ship.spd_lvl+1)
		# ~ if player.creds >= cost:
			# ~ player.creds -= cost
			player.ship.speedLevelUP(10)
	
	if event.key == pygame.K_u:								# U - HP level up
		cost = (player.ship.lhp+1) * 10
		if player.creds >= cost:
			player.creds -= cost
			player.ship.levelUpHP()
	if event.key == pygame.K_i:								# I - SP level up
		cost = (player.ship.lsp+1) * 10
		if player.creds >= cost:
			player.creds -= cost
			if not player.ship.shield_unlocked:
				player.ship.shield_unlocked = True
			player.ship.levelUpSP()
	
	if event.key == pygame.K_h:								# H - Dmg level up
		cost = (player.ship.weapon.lvl+1)
		if player.creds >= cost:
			player.creds -= cost
			player.ship.weapon.levelUpDmg()
	
	if event.key == pygame.K_l:								# L - receive 100 Dmg
		player.ship.recvDamage(100, pct_sp=1, mult=1)

def detectEvents():
	
	con = True
	
	for event in pygame.event.get():
		
		if event.type == pygame.TEXTINPUT:
			# Control de input del chat --------------------
			if chat.chat_text_active:
				chat.chat_text += event.text
		
		if event.type == pygame.QUIT:
			config.run = False
			
			#-----------------------------------------------------------
			if con: continue
		
		if event.type == VIDEORESIZE:
			
			temp_res = config.RESOLUTION
			
			# Cambio de resolución -------------------------------------
			config.videoResize(event)
			
			# Control del movimimiento del minimapa --------------------
			minimap.onResizeScreen(temp_res)
			
			#-------------------------------------
			if con: continue
		
		if event.type == pygame.KEYDOWN:
			
			keysDown(event)
			
			#-------------------------------------
			if con: continue
		
		if event.type == pygame.MOUSEMOTION:
			
			# Control del movimimiento del minimapa --------------------
			minimap.mouseMotion(event)
			
			# Control del movimimiento del chat ------------------------
			chat.mouseMotion(event)
			
			#-------------------------------------
			if con: continue
		
		if event.type == pygame.MOUSEBUTTONDOWN:
			
			if not config.open_menu:
				
				# Control de seleccion del enemigo ---------------------
				if not chat.chat_text_active:
					players = selectEnemy(event)
					if players: updateOtherPlayers(players)
				
				# Control del movimimiento del minimapa ----------------
				minimap.mouseButtonDown(event)
				
				# Control del movimimiento del chat --------------------
				chat.mouseButtonDown(event)
				
				# Control del tamaño del minimapa ----------------------
				minimap.resize(event)
				
				# Control de seguimiento en el minimapa ----------------
				if not minimap.map_resize:
					minimap.setFollowPos(event)
				
				# Control de input del chat ----------------------------
				chat.activeInput(event)
				
				#-------------------------------------------------------
				if minimap.map_resize: minimap.map_resize = False
			
			#-------------------------------------
			if con: continue
		
		if event.type == pygame.MOUSEBUTTONUP:
			
			# Control del movimimiento del minimapa --------------------
			minimap.mouseButtonUp()
			
			# Control del movimimiento del chat ------------------------
			chat.mouseButtonUp()
			
			#-------------------------------------
			if con: continue
		
		if event.type == pygame.WINDOWLEAVE:
			
			# Control del movimimiento del minimapa --------------------
			minimap.windowLeave()
			
			#-------------------------------------
			if con: continue

def movements(deltaTime):
		
		# Control de input del chat --------------
		if chat.chat_text_active: return
		#-----------------------------------------
		
		keys = pygame.key.get_pressed()
		speed = player.ship.speed
		speed *= deltaTime
		
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
		
		if leftMove and not rightMove:
			movements = True
			if not upDownMove and (upMove or downMove):
				if   upMove:   degrees = 90
				elif downMove: degrees = 270
				x -= utils.diagonal(speed)['x']
			else:
				degrees = 180
				x -= speed
		
		if rightMove and not leftMove:
			movements = True
			if not upDownMove and (upMove or downMove):
				if   upMove:   degrees = 90
				elif downMove: degrees = 270
				x += utils.diagonal(speed)['x']
			else:
				degrees = 0
				x += speed
		
		if upMove and not downMove:
			movements = True
			if not leftRightMove and (leftMove or rightMove):
				if leftMove:  degrees += 45
				if rightMove: degrees -= 45
				y -= utils.diagonal(speed)['y']
			else:
				degrees = 90
				y -= speed
		
		if downMove and not upMove:
			movements = True
			if not leftRightMove and (leftMove or rightMove):
				if leftMove:  degrees -= 45
				if rightMove: degrees += 45
				y += utils.diagonal(speed)['y']
			else:
				degrees = 270
				y += speed
		
		if movements:
			
			# Control de seguimiento en el minimapa --------------------
			if player.follow_pos: player.cancelFollowPos()
			#-----------------------------------------------------------
			
			player.ship.time_hp_init = 0
			player.angle = degrees
			player.rotate(degrees)
			player.x += round(x)
			player.y += round(y)
		else:
			# Recibir HP bajo sus reglas -------------------------------
			player.ship.healHP()
			
			# Control de seguimiento en el minimapa --------------------
			player.followPos(speed)
			#-----------------------------------------------------------
		
		# Recibir SP bajo sus reglas:
		player.ship.healSP()

# Rules ------------------------------------------

def radioactiveZone():
	
	if (player.x < 0 or config.map_limits['x'] < player.x)\
	or (player.y < 0 or config.map_limits['y'] < player.y):
		if player.ship.timeOnBorder == 0:
			player.ship.timeOnBorder = time.perf_counter()
		if time.perf_counter() - player.ship.timeOnBorder > 2:
			player.ship.timeOnBorder = time.perf_counter()
			player.ship.recvDamage(config.rad_dmg*(1-player.ship.pct_res_dmg_rad), pct_sp=0)
	else:
		if player.ship.timeOnBorder > 0:
			player.ship.timeOnBorder = 0

# Actions ----------------------------------------

def setAttack():
	
	# Draw Laser and damage on enemies:
	if player.selected['id'] >= 0 and player.attacking:
		
		if player.selected['dist'] < player.ship.weapon.dist:
			
			id_ = player.selected['id']
			enemy = enemies[id_]
			
			if player.ship.weapon.perSecond():
				
				if enemy.ship.chp > 0:
					
					if enemy.ship.chp+enemy.ship.csp < player.ship.weapon.dmg:
						dmg = enemy.ship.chp+enemy.ship.csp
					else:
						dmg = player.ship.weapon.dmg
					
					pct_sp = player.ship.weapon.pct_sp
					mult = player.ship.weapon.mult
					
					player.selected['dmginfo']['dmg']    = dmg
					player.selected['dmginfo']['pct_sp'] = pct_sp
					player.selected['dmginfo']['mult']   = mult
					player.selected['dmginfo']['time']   = game_time
			
			if enemy.ship.chp == 0:
				player.creds += enemy.creds
				player.exp   += enemy.exp
				player.selected['name'] = ''
				player.selected['id']   = -1
				player.selected['dist'] = -1
				player.attacking = False

def lookAtEnemy():
	
	# Gira hacia el enemigo
	if player.selected['id'] >= 0 and player.attacking:
		
		desX = (int(config.CENTER['x'])-int(player.x))	# Desplazamiento en X
		desY = (int(config.CENTER['y'])-int(player.y))	# Desplazamiento en Y
		
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
			if other_player.ship.chp == 0: continue
			
			pposX = other_player.x+desX
			pposY = other_player.y+desY
			
			dist = utils.euclideanDistance((posX, posY), (pposX,pposY))
			
			if dist < other_player.ship.base['min_dist_sel']:
				dists.append(( dist, other_player.name, other_player_id ))
		
		min_dist      = other_player.ship.base['min_dist_sel']
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

# Menu -------------------------------------------

def drawMenuTabConstellations(x, y, w, h):				# Tab 3
	pass

def drawMenuTabEnhance(x, y, w, h):						# Tab 2
	
	CYAN   = config.COLOR['Cyan']
	VERDEC = config.COLOR['Verde Claro']
	font   = config.FONT['Inc-R 16']
	despX  = 100			# Desplazamiento en X
	despY  = 30				# Desplazamiento en Y
	
	texts = [
		('Experience',                         font, CYAN),
		(str(player.exp),                      font, VERDEC),
		('Credits',                            font, CYAN),
		(str(player.creds),                    font, VERDEC),
		('Weapon',                             font, CYAN),
		(f'{str(player.ship.weapon.name)} '\
			f'({player.ship.weapon.lvl})',     font, VERDEC),
		('Damage',                             font, CYAN),
		(str(player.ship.weapon.dmg),          font, VERDEC),
		('Speed',                              font, CYAN),
		(str(player.ship.speed),               font, VERDEC),
		('FPS',                                font, CYAN),
		(str(config.fps),                      font, VERDEC),
		('Coords',                             font, CYAN),
		('({},{})'.format(
				int(player.x/config.posdiv),
				int(player.y/config.posdiv)
			).ljust(11),                       font, VERDEC)
	]
	
	# Draw background ----------------------------
	# ~ positions = [ x, y, w, h ]
	
	# ~ drawRoundrect('background tab', positions, config.COLOR['Verde F'],
		# ~ 3, 1, (*config.COLOR['Verde S'], 50)
	# ~ )
	
	# Draw texts ---------------------------------
	x = x+20
	y = y+20
	for i, text in enumerate(texts):
		WIN.blit(renderText(*text), (x+(despX*(i%2)), y+(despY*(i//2))))

def drawMenuTabInfo(x, y, w, h):						# Tab 1
	
	CYAN   = config.COLOR['Cyan']
	VERDEC = config.COLOR['Verde Claro']
	font   = config.FONT['Inc-R 16']
	despX  = 120			# Desplazamiento en X
	despY  = 30				# Desplazamiento en Y
	
	texts = [
		('Experience',                         font, CYAN  ),
		(str(player.exp),                      font, VERDEC),
		('Credits',                            font, CYAN  ),
		(str(player.creds),                    font, VERDEC),
		('Weapon',                             font, CYAN  ),
		(f'{str(player.ship.weapon.name)} '\
			f'({player.ship.weapon.lvl})',     font, VERDEC),
		('Damage',                             font, CYAN  ),
		(str(player.ship.weapon.dmg),          font, VERDEC),
		('Speed',                              font, CYAN  ),
		(str(player.ship.speed),               font, VERDEC),
		('FPS',                                font, CYAN  ),
		(str(config.fps),                      font, VERDEC),
		('Coords',                             font, CYAN  ),
		('({},{})'.format(
				int(player.x/config.posdiv),
				int(player.y/config.posdiv)
			).ljust(11),                       font, VERDEC),
		('Rad. rest.',                         font, CYAN  ),
		('{}%'.format(str(
				player.ship.pct_res_dmg_rad*100
			)),                                font, VERDEC)
	]
	
	# Draw background ----------------------------
	# ~ positions = [ x, y, w, h ]
	
	# ~ drawRoundrect('background tab', positions, config.COLOR['Verde F'],
		# ~ 3, 1, (*config.COLOR['Verde S'], 50)
	# ~ )
	
	# Draw texts ---------------------------------
	x = x+20
	y = y+20
	for i, text in enumerate(texts):
		WIN.blit(renderText(*text), (x+(despX*(i%2)), y+(despY*(i//2))))

def drawMenu():
	
	if config.open_menu:
		
		font14 = config.FONT['Inc-R 14']
		font16 = config.FONT['Inc-R 16']
		font18 = config.FONT['Inc-R 18']
		font20 = config.FONT['Inc-R 20']
		font24 = config.FONT['Inc-R 24']
		
		if   len(player.name) > 20: name_font = font14
		elif len(player.name) > 16: name_font = font16
		elif len(player.name) > 12: name_font = font18
		elif len(player.name) > 8:  name_font = font20
		else: name_font = font24
		
		BLANCO  = config.COLOR['Blanco']
		CYAN    = config.COLOR['Cyan']
		CYANOP  = config.COLOR['Cyan Opaco']
		VERDE   = config.COLOR['Verde Claro']
		VERDEOP = config.COLOR['Verde Opaco']
		
		# Draw background ----------------------------------------------
		pos = { 'x': 20, 'y': 20, 'w': 20, 'h': 20 }
		pos['w'] = config.W - pos['w'] - pos['x']
		pos['h'] = config.H - pos['h'] - pos['y']
		menu_pos = [ pos['x'], pos['y'], pos['w'], pos['h'] ]
		
		drawRoundrect('background menu', menu_pos, config.COLOR['Verde F'],
			2, 2, (*config.COLOR['Verde S'], 180)
		)
		
		# Draw tabs ----------------------------------------------------
		despX = 180
		tx, ty = menu_pos[0]+1, menu_pos[0]
		tw, th = despX, 50
		tabs = ['Information', 'Enhance', 'Constellations']
		
		pygame.draw.line(WIN, config.COLOR['Linea Bg'], 
			(pos['x']+despX, pos['y']+2),
			(pos['x']+despX, pos['h']+pos['y']-2),
		2)
		
		text = f'{player.name}'
		text = renderText(text, name_font, VERDE)
		WIN.blit(text, (
				tx + tw//2 - text.get_width()//2,
				ty + th//2 - text.get_height()//2
			)
		)
		
		for i, tab in enumerate(tabs):
			
			i+=1
			tab_y = ty + (th-1) * i
			
			if config.pos_tab_menu == i:
				tr = 50
				color = CYAN
			else:
				tr = 10
				color = CYANOP
			
			tab_pos = [tx, tab_y, tw, th]
			drawRoundrect('tab on menu', tab_pos, config.COLOR['Verde F'],
				2, 1, (*CYANOP, tr)
			)
			
			text = renderText(tab, font18, color, 'bold')
			WIN.blit(text, (
					tx    + tw//2 - text.get_width()//2,
					tab_y + th//2 - text.get_height()//2
				)
			)
		
		# Draw tab Content ---------------------------------------------
		
		positions = [
			tx+tw,
			ty,
			pos['w']-despX,
			pos['h']
		]
		
		if   config.pos_tab_menu == 1: drawMenuTabInfo(*positions)
		elif config.pos_tab_menu == 2: drawMenuTabEnhance(*positions)
		elif config.pos_tab_menu == 3: drawMenuTabConstellations(*positions)

# Global Chat ------------------------------------

def drawChatTabGlobal():
	
	# Draw Global Chat Background ----------------
	pos = chat.chat_inner_pos
	drawRoundrect('global chat background', pos, config.COLOR['Verde F'],
		3, 1, (*config.COLOR['Negro'], 100-chat.pct_tr)
	)
	
	# Draw Global Chat Name ----------------------
	font = config.FONT['Inc-R 14']
	text = renderText('Global', font, config.COLOR['Blanco'], 'bold')
	if not chat.chat_global_name_rect == (text.get_width(), text.get_height()):
		chat.chat_global_name_rect = (text.get_width(), text.get_height())
	WIN.blit(text, (pos[0], pos[1]-text.get_height()-1))
	
	# Draw Messages in Global Chat ---------------
	BLANCO = config.COLOR['Blanco']
	CYAN   = config.COLOR['Cyan']
	x, y = pos[0]+4, pos[0]+text.get_height()
	font = config.FONT['Inc-R {}'.format(chat.chat_msg_tam)]
	
	# Obtiene los mensajes recortados para evitar que se desborden
	temp = renderText(' ', font, CYAN)
	plus = 2
	qty = int((chat.chat_h-45)//(temp.get_height()+plus))	# Se adapta a lo alto del chat para limitar las lineas en el
	tam = int((chat.chat_w-20)// temp.get_width())			# Se adapta al ancho del chat para limitar los caracteres por linea
	del temp
	msgs = []
	
	for user, msg in chat.messages['global'][-qty:]:
		for i, part in enumerate(utils.splitText(user+':'+msg, tam)):
			if not i == 0: user = ''
			else: part = part[len(user)+1:]
			msgs.append((user, part))
	
	# Muestra en pantalla los mensajes de forma ordenada
	add  = 1
	for user, msg in msgs[-qty:]:
		
		if user:
			add = 1
			ruser = renderText(user+':', font, CYAN, 'bold')
			y += ruser.get_height()+add
			WIN.blit(ruser, (x,y))
			x += ruser.get_width()+2
			y -= ruser.get_height()+add
		else:
			add = 0
		
		rmsg = renderText(msg, font, BLANCO)
		y += rmsg.get_height()+add
		WIN.blit(rmsg, (x,y))
		
		x = pos[0]+4
		y += 1
	#---------------------------------------------

def drawChat():
	
	# Draw Chat Background -----------------------
	drawRoundrect('chat background', chat.chat_pos, config.COLOR['Verde F'],
		3, 1, (*config.COLOR['Verde S'], 100)
	)
	
	# Draw Chat Name -----------------------------
	font = config.FONT['Inc-R 14']
	text = renderText(chat.chat_name, font, config.COLOR['Blanco'], 'bold')
	if not chat.chat_name_rect == (text.get_width(), text.get_height()):
		chat.chat_name_rect = (text.get_width(), text.get_height())
		print(chat.chat_name_rect)
	WIN.blit(text, (chat.chat_x, chat.chat_y-text.get_height()))
	
	# Draw Global Chat Messages ------------------
	if chat.chat_tab == 1:
		drawChatTabGlobal()
	
	# Draw Chat Input Text Background ------------
	drawRoundrect('chat write text', chat.chat_input_pos, config.COLOR['Verde F'],
		3, 1, (*config.COLOR['Verde S'], 20)
	)
	
	# Draw Chat Input Text -----------------------
	font = config.FONT['Inc-R 14']
	limit = (chat.chat_w-24)//7
	text = renderText(chat.chat_text[-limit:], font, config.COLOR['Blanco'])
	pos = chat.chat_input_pos
	WIN.blit(text, (pos[0]+4, pos[1]+2))

# Window -----------------------------------------

def drawRoundrect(rect_name, pos, bcolor, ba, br, bgcolor):
	# rect_name: nombre del componente
	# pos: posiciones para el rectangulo
	# bcolor: color del borde
	# ba: anchura del borde
	# br: redondeado del borde
	# bgcolor: Color del fondo y transparencia de 0 a 255
	
	if not config.roundRects.get(rect_name):
		rr_img, rr_rect = utils.roundRect(pos, bcolor, ba, br, bgcolor)
		config.roundRects[rect_name] = rr_img, rr_rect
	else:
		rr_img, rr_rect = config.roundRects.get(rect_name)
		if not pos == rr_rect:
			rr_img, rr_rect = utils.roundRect(pos, bcolor, ba, br, bgcolor)
			config.roundRects[rect_name] = rr_img, rr_rect
	
	WIN.blit(rr_img, rr_rect)

def renderText(text, font, color, _type=''):
	if 'bold' in _type:        font.set_bold(True)
	elif font.get_bold():      font.set_bold(False)
	if 'italic' in _type:      font.set_italic(True)
	elif font.get_italic():    font.set_italic(False)
	if 'underline' in _type:   font.set_underline(True)
	elif font.get_underline(): font.set_underline(False)
	return font.render(text, config.antialiasing, color)

def drawMinimap(map_enemies_pos):
	
	x, y = minimap.player_pos
	
	# Draw player screen on minimap
	drawRoundrect('screen on minimap', minimap.scrPosOnMap(x,y), config.COLOR['Verde S'],
		2, 1, (*config.COLOR['Verde F'], 100)
	)
	
	# Draw minimap background
	drawRoundrect('minimap', minimap.map_pos, config.COLOR['Verde F'],
		3, 1, (*config.COLOR['Verde S'], 150)
	)
	
	# Draw player position on minimap
	pygame.draw.circle(WIN, config.COLOR['Blanco'], (x,y), 1, 1)
	
	# Draw Map Name
	font = config.FONT['Retro 14']
	text = minimap.map_name
	text = renderText(text, font, config.COLOR['Blanco'])
	if not minimap.map_name_rect == (text.get_width(), text.get_height()):
		minimap.map_name_rect = (text.get_width(), text.get_height())
	WIN.blit(text, (minimap.map_x, minimap.map_y-text.get_height()))
	
	# Dibuja de desplazamiento mediante clic en el minimapa:
	if player.follow_pos:
		pass
	
	# Control del tamaño del minimapa ----------------------
	font24 = config.FONT['Wendy 24']
	color_m = minimap.btn_col_off if minimap.map_size == 0 else minimap.btn_col
	color_p = minimap.btn_col_off if minimap.map_size == minimap.map_size_max else minimap.btn_col
	text1 = renderText('-', font24, config.COLOR[color_m])
	text2 = renderText('+', font24, config.COLOR[color_p])
	minimap.btn_minus = [(text1.get_width(),text1.get_height()),(minimap.map_x+minimap.map_w-text1.get_width()-text2.get_width()-15, minimap.map_y-text1.get_height())]
	minimap.btn_plus  = [(text2.get_width(),text2.get_height()),(minimap.map_x+minimap.map_w-text2.get_width()-5, minimap.map_y-text2.get_height())]
	WIN.blit(text1, minimap.btn_minus[1])
	WIN.blit(text2, minimap.btn_plus[1])
	
	# Draw enemies positions on minimap
	for x, y in map_enemies_pos:
		x = (x/config.posdiv) / config.MAP[minimap.map_name]['x'] * minimap.map_w + minimap.map_x
		y = (y/config.posdiv) / config.MAP[minimap.map_name]['y'] * minimap.map_h + minimap.map_y
		pygame.draw.circle(WIN, config.COLOR['Rojo'], (x,y), 1, 1)

def drawShipAndData(ship, des, name_color):
	
	# Draw red circle ----------------------------
	if player.selected['id'] == ship.id:	# Circulo de selección
		pygame.draw.circle(WIN,
			(255,0,0), (
				int(ship.x)+des[0],
				int(ship.y)+des[1]
			), ship.ship.base['min_dist_sel'], 1
		)
	
	# Draw Ship ----------------------------------
	rect = ship.img.get_rect(
		center = (
			int(ship.x)+des[0],
			int(ship.y)+des[1]
		)
	)
	
	# Draw the outline ---------------------------
	if player.id == ship.id:
		color = config.COLOR['Rojo']
		# ~ utils.perfectOutline(ship.img, rect, color, alpha=25, br=4)			# Contorno Negro
		utils.perfectOutline(ship.img, rect, color, alpha=25, br=3)			# Contorno Negro
		# ~ utils.perfectOutline(ship.img, rect, color, alpha=25, br=2)			# Contorno Negro
		utils.perfectOutline(ship.img, rect, color, alpha=25, br=1)			# Contorno Negro
	
	WIN.blit(ship.img, rect)
	
	desp = 50
	
	# Draw Name ----------------------------------
	if config.show['name']:
		font = config.FONT['Inc-R 18']
		if ship.ship.type == 'Stranger':
			text_lvl = f' ({ship.ship.lvl})'
		else:
			text_lvl = ''
		text = f'-- [{ship.name}]{text_lvl} --'
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
			
			name = 'HP' if i == 0 else 'SP'
			
			x = int(ship.x)+des[0] - width/2
			y = int(ship.y)+des[1] - desp
			position = [x, y, width, height]
			drawRoundrect(name, position, config.COLOR['Verde F'],
				2, 1, (*color, 50)
			)
			
			x = int(ship.x)+des[0] - width/2
			y = int(ship.y)+des[1] - desp
			
			pct = cp / p
			position = [x, y, int(width*pct), height]
			drawRoundrect(name+' bg', position, config.COLOR['Verde F'],
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
	
	if config.show['matrix_bg_fix']:
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
	
	drawRoundrect('config data', positions, config.COLOR['Verde F'],
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
	
	map_enemies_pos = []
	
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
		
		if config.show['map_enemies']:
			map_enemies_pos.append((other_player.x, other_player.y))
		
		if other_player_dist < config.limit_obj_dist:
			if not config.show['map_enemies']:
				map_enemies_pos.append((other_player.x, other_player.y))
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
	
	# Draw mini map ====================================================
	
	drawMinimap(map_enemies_pos)
	
	# Draw global chat =================================================
	
	drawChat()
	
	# Draw other info on main layer data: ==============================
	
	#drawOtherInfo(game_time)
	
	# Draw player menu: ================================================
	
	drawMenu()

#=======================================================================

def createWindow():
	
	global WIN
	
	# Make window start in top left hand corner
	
	os.environ['SDL_VIDEO_WINDOW_POS'] = f'{10},{40}'
	# ~ os.environ['SDL_VIDEO_WINDOW_POS'] = f'{840},{40}'
	# ~ os.environ['SDL_VIDEO_CENTERED'] = '1'
	
	# Setup pygame window
	WIN = pygame.display.set_mode((config.W,config.H), HWSURFACE | DOUBLEBUF | RESIZABLE)
	pygame.display.set_caption(f'{__project__} Online v{__version__} - By: {__author__}')
	
	# Music
	# ~ config.music.load(config.MUSIC['JNATHYN - Genesis'])
	# ~ config.music.set_volume(config.music_vol/100)
	''# ~ config.music.play(-1)

#=======================================================================

def main():
	
	global game_time
	
	config.run = True
	deltaTime = 1					# Delta Time
	lastDeltaTime = 999

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
	
	chat.messages = server.send('get msg')
	
	#---------------------------------------------
	
	while config.run:
		
		# Control de input del chat --------------
		if chat.perSecond(3):
			chat.messages = server.send('get msg')
		#-----------------------------------------
		
		players, game_time = server.send(player.data)		# Envia datos al servidor y recibe la información de los otros jugadores
		
		#---------------------------------------------------------------
		# Add damages received:
		for enemy_id, values in players[player.id]['dmginfo'].items():
			for dmg, pct_sp, mult, t in values:
				player.ship.recvDamage(dmg, pct_sp, mult)
		#---------------------------------------------------------------
		
		# Update Data:
		updateOtherPlayers(players)							# Actualiza los datos de los enemigos
		
		# Actions:
		lookAtEnemy()										# Si el enemigo esta seleccionado o el jugador es seleccionado, las naves giran apuntandose.
		setAttack()											# Agrega el daño causado al enemigo
		radioactiveZone()									# Reglas para la zona radioactiva
		calcFrames()										# Calcula la cantidad de fotogramas por segundo.
		
		# Draw Window:
		redrawWindow()										# Redibuja todo (1 Fotograma)
		
		# Events:
		if not deltaTime > lastDeltaTime*10:
			movements(deltaTime)							# Detecta los movimientos direccionales
		lastDeltaTime = deltaTime
		detectEvents()										# Detecta los eventos de Mouse y Teclado
		
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

# Start Game
main()

#=======================================================================
# Añadido el: 06/09/2021
# + Agregado el poder seleccionar el nombre del mapa y mover el minimapa.
# + Mejorado el ataque de los Strangers.
# 
# Añadido el: 07/09/2021
# + Mejorada el posicionamiento del minimapa por cuadrante en la pantalla al cambiar la resolución.
#   El minimapa mantendra la relación con los bordes aunque cambie la resolución de la pantalla,
#   basado en el cuadrante en que se encuentre:
#     Si esta en el primer  cuadrante de la pantalla se movera solo en X. map_x > width//2 & map_y < hight//2
#     Si esta en el segundo cuadrante de la pantalla no se moverá.        map_x < width//2 & map_y < hight//2
#     Si esta en el tercer  cuadrante de la pantalla se moverá solo en Y. map_x < width//2 & map_y > hight//2
#     Si esta en el cuarto  cuadrante de la pantalla se moverá en X e Y.  map_x > width//2 & map_y > hight//2
# 
# Añadido el: 08/09/2021
# + Todos los valores para el minimapa ahora estan en su propia clase 'Minimapa'.
# + Todos los valores para el cambio de resolucion movido a la clase 'Config'.
# 
# Añadido el: 09/09/2021
# + Agregados los botones para cambiar el tamaño del minimapa. El minimapa cambia de 25x20 píxeles por clic,
#     pasando de un minimo de 150x120 a un máximo de 300x240 píxeles.
# + El minimapa se adapta al cambio de tamaño sin desbordarse y el aumento siempre apunta al centro de la pantalla (basado en cuadrante de la pantalla en el que esté).
# 
# Añadido el: 13/09/2021
# + Código un poco más optimizado en los movimientos de los objetos.
# + Agregado desplazamiento con clic en mini mapa.
# + Agregado sistema de porcentaje de resistencia al daño por radiación.
# + Solucionado: Al derrotar enemigos se podian volver a seleccionar antes de que desaparecieran.
# + Solucionado: Al seleccionar un enemigo y desplazarse desde el minimapa, el movimiento de avance esta mal.
# + Agregada base de Chat
# 
# Añadido el: 14/09/2021
# + Agregado poder escribir en el chat.
# + Agregado poder mandar los mensajes al servidor.
# + Agregado poder recibir los mensajes dle servidor.
# + Agregado y adaptado sistema para cambiar tamaño de fuente del chat de entre 12 y 18.
# + Agregado y adaptado sistema para cambiar tamaño de la venta de chat y que se ajuste el texto.
# + (En progreso) Agregado poder mover la ventana de chat.
# + (En progreso) Agregado poder manipular el tamaño ventana de chat usando el mouse.
# 
# Para futuro desarrollo:
# + [Ok] Agregar el poder seleccionar el nombre del mapa y mover el minimapa.
# + [Ok] Agregar botones '+' y '-' para cambiar el tamaño del minimapa.
# + [Ok] Agregar desplazamiento con clic en mini mapa.
# + [Ok] Agregar sistema resistencia a la zona radioactiva.
# + [Ok] Agregar Chat Global.
# + [] Agregar Loot random en mapa.
# + [] Agregar sistema de constelaciones aleatorias para mejoras aleatorias (HP, SP, Dmg, Speed).
# + [] Agregar tiempo de inmortalidad al iniciar sesión.
# + [] Agregar más variedad enemigos.
# + [] Agregar más mapas.
# + [] Agregar portales entre mapas.
# + [] Agregar distintas armas.
# + [] Agregar limite de municiónes por armas.
# + [] Agregar laseres visuales.
# + [] Agregar Efectos de Sonido (SFX).
# + [] Agregar Zona Segura.
# + [] Agregar Menú vinculado a zona segura para recargas y mejoras.
# + [] Diseñar contenido del menú.
# + [] Agregar subida de niveles en el menú.
# + [] Los otros personajes (NPCs y Otros jugadores) deberán seguir coordenadas para generar fluides con los movimientos en la pantalla del jugador.
# + [] Agregar base de datos de usuarios
# + [] Agregar inicio de sesión.
# + [] Agregar misiles.
# + [] Agregar animación para los misiles.
# + [] Agregar variación de daño (con posibilidad de fallo).
# + [] Agregar Compra de objetos para la resistencia a la zona radioactiva.
# 
# Bugs Detectados:
# + [Ok] Al seleccionar un enemigo y desplazarse desde el minimapa, el movimiento de avance esta mal.
# + [Ok] Al seleccionar agrandar o encojer el minimapa se detecta el clic y afecta el movimiento.
# + [] Al atacar un enemigo, si no entras en su rango de visión, no te ataca.
# + [] El recuadro de pantalla en el minimapa, se desborda.
# + [] Daño causado de enemigos a enemigos no carga correctamente.
# + [] Cuando un enemigo te ataca no se ve correctamente la animación.
# + [] Cambiar color negro absoluto de los pixel arts. Se elimina al cargar la imagen (remplaza por vacio como el fondo)
