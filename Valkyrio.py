
import contextlib
with contextlib.redirect_stdout(None):
	import pygame
from pygame.locals import *
pygame.font.init()
from Client import Network
import atexit
import random
import math
import time
import os

#=======================================================================

__project__ = 'Valkyrio'
__author__  = 'LawlietJH'
__version__ = '0.0.2 (Alfa)'

__license__ = 'MIT'
__status__  = 'Development'
__framework__    = 'pygame'
__description__  = 'Juego 2D online con pygame inspirado en los juegos clasicos de destruir naves.'
__version_date__ = '2021/08/23'

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
			'Cyan':         (  0,200,220),
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
		
		# Configs: -----------------------------------------------------
		
		self.show = {
			'name': True,
			'speed': True,
			'fps': True,
			'pos': True,
			'hp-sp': True
		}
		
		WEAPON = {
			'Laser': {
				'path': 'img/weapons/laser.png',
				'dmg': 100,
				'dist': 400
			}
		}
		
		self.speedmul = 100								# Speed multiplier
		self.SHIP = {
			'Prometheus': {
				'path': 'img/Prometheus.png',
				'speed': int(.5 * self.speedmul),
				'hp':    350,
				'sp':    250
			}
		}
		
		self.limitX     = 10000							# Limit on X Coord
		self.limitY     = 10000							# Limit on Y Coord
		self.run        = False							# Game Run
		self.dtdiv      = 10 * self.speedmul			# Detla Time Divide
		self.posdiv     = 20							# Real pixel posicion X and Y divided
		self.MFPS       = 120							# Max Frames per Second
		self.fps        = 60							# Number of Frames per Second
		self.matrix_bg  = 15							# Squares on Backgrand. Example: 15x15
		self.radDmg     = 50							# Radioactive Damage 
		
		self.BASE_SPEED = 1 * self.speedmul				# Base Speed of Ships
		self.MAX_SPEED  = 2 * self.speedmul				# Max Speed of Ships
		self.RESOLUTION = (1280, 768)					# Resolution
		# ~ self.RESOLUTION = (720, 480)					# Resolution
		self.W = self.RESOLUTION[0]
		self.H = self.RESOLUTION[1]
		self.CENTER = {'x': self.W//2, 'y': self.H//2}	# Center Position
		self.SELECT_MIN_DIST = 40
		
		self.limit_obj_dist = int(utils.euclideanDistance((
								self.CENTER['x'], self.CENTER['y']),
								(0, 0)
							)) + 200


class Weapon:
	
	def __init__(self, name):
		self.name = name
		self.path = config.WEAPON[name]


class Ship:
	
	def __init__(self, name):
		
		self.name = name
		self.base = config.SHIP[name]
		self.destroyed = False
		
		self.speed  = config.BASE_SPEED
		self.speed += self.base['speed']
		
		# Health
		self.hp  = self.base['hp']		# Health points
		self.chp = self.hp				# Current Health Points
		self.lhp = 1					# Level Health Points
		self.pct_hp = .3				# Health Damage Percentage
		self.wait_hp_init = 0
		self.wait_hp_init_ini = 0
		self.wait_hp_init_max = 3
		self.wait_hp_max  = 3
		self.wait_hp_pct  = .1			# Health+ Percentage
		
		# Shield
		self.shield_unlocked = True
		self.sp  = self.base['sp']		# Shield points
		self.csp = self.sp				# Current Shield Points
		self.lsp = 0					# Level Shield Points
		self.pct_sp = .7				# Shield Damage Percentage
		self.wait_sp_init = 0
		self.wait_sp_init_ini = 0
		self.wait_sp_init_max = 10
		self.wait_sp_max  = 1
		self.wait_sp_pct  = .05			# Shield+ Percentage
		
		self.timeOnBorder = 0
		
		# ~ self.damageRecv = [[50, time.perf_counter()],[150, time.perf_counter()]]
		self.damageRecv = []
		self.healthRecv = []
	
	def levelUpHP(self, lvl=1):					# Incrementa de nivel el HP
		inc = self.base['hp'] * lvl
		self.hp += inc
		self.chp += inc
		self.lhp += lvl
	
	def levelUpSP(self, lvl=1):					# Incrementa de nivel el SP
		if self.shield_unlocked:
			inc = self.base['hp'] * lvl
			self.sp += inc
			self.csp += inc
			self.lsp += lvl
	
	def recvDamage(self, damage, pct_sp=None, mult=1, draw=True):			# Registra el daño recibido para mostrarlo
		
		self.wait_hp_init = 0
		self.wait_sp_init = 0
		
		if player.ship.chp == 0:
			self.destroyed = True
			return
		
		if pct_sp == None:
			dhp = damage * self.pct_hp * mult
			dsp = damage * self.pct_sp * mult
		else:
			dhp = damage * (1-pct_sp) * mult
			dsp = damage *    pct_sp  * mult
		
		if self.csp > 0:
			self.csp = int(self.csp - dsp)
			if self.csp < 0:
				self.chp += self.csp
				self.csp = 0
		else: self.chp = int(self.chp - dsp)
		if self.chp > 0: self.chp = int(self.chp - dhp)
		if self.chp < 0: self.chp = 0
		
		if draw: self.damageRecv.append([damage*mult, time.perf_counter()])


class Player:
	
	def __init__(self, name=None, id_=None):
		
		self.name = name
		self.ship = None
		self.ship_name = None
		self.ship_path = None
		self.img_orig = None
		self.img = None
		
		self.score = None
		self.id = id_
		self.x = None
		self.y = None
		
		self.angle = 0
		self.attacking = False
		self.under_attack = False
		
		self.selected = {
			'id': '',
			'name': '',
			'dist': ''
		}
	
	def __str__(self):
		text = f"<'Name':'{self.name}', 'ID':'{self.id}'>"
		return text
	
	@property
	def data(self):
		
		data_f  = 'data:{{'
		data_f +=   '"x":{},'
		data_f +=   '"y":{},'
		data_f +=   '"chp":{},'
		data_f +=   '"csp":{},'
		data_f +=   '"dtry":"{}",'
		data_f +=   '"ang":{},'
		data_f +=   '"atk":"{}"'
		data_f += '}}'
		
		data = data_f.format(
			round(self.x, 2),
			round(self.y, 2),
			self.ship.chp,
			self.ship.csp,
			self.ship.destroyed,
			self.angle,
			self.attacking
		)
		
		return data
	
	def rotate(self, angle):
		img = self.img_orig
		self.img = pygame.transform.rotate(img, angle)
	
	def loadData(self, player):
		
		self.x = player['x']
		self.y = player['y']
		
		self.angle = player['ang']
		
		self.attacking = bool(player['atk'])
		
		self.score = player['score']
		self.score = player['score']
		
		self.selected['name'] = player['selected']['name']
		self.selected['id']   = player['selected']['id']
		
		self.ship_name = player['ship']['name']
		self.ship_path = config.SHIP[self.ship_name]['path']
		self.ship = Ship(self.ship_name)
		
		if not player['ship']['hp'] == self.ship.hp:
			self.ship.hp = player['ship']['hp']
		if not player['ship']['sp'] == self.ship.sp:
			self.ship.sp = player['ship']['sp']
		
		self.ship.chp = player['ship']['chp']
		self.ship.csp = player['ship']['csp']
		
		self.ship.destroyed = player['ship']['dtry']
		
		self.img_orig = self.loadImage(self.ship_path)
		self.img = self.img_orig
	
	def updateData(self, player):
		
		if not self.x == player['x']: self.x = player['x']
		if not self.y == player['y']: self.y = player['y']
		
		if not self.angle == player['ang']:
			self.angle = player['ang']
			self.rotate(self.angle)
		
		if not self.attacking == bool(player['atk']): self.attacking = bool(player['atk'])
		
		if not self.score == player['score']: self.score = player['score']
		
		if not self.selected == player['selected']: self.selected = player['selected']
		
		if not self.ship_name == player['ship']['name']:
			self.ship_name = player['ship']['name']
			self.ship_path = config.SHIP[self.ship_name]['path']
			self.ship = Ship(self.ship_name)
		
		if not player['ship']['hp'] == self.ship.hp: self.ship.hp = player['ship']['hp']
		if not player['ship']['sp'] == self.ship.sp: self.ship.sp = player['ship']['sp']
		
		if not self.ship.chp == player['ship']['chp']: self.ship.chp = player['ship']['chp']
		if not self.ship.csp == player['ship']['csp']: self.ship.csp = player['ship']['csp']
		
		if not self.ship.destroyed == player['ship']['dtry']: self.ship.destroyed = player['ship']['dtry']
	
	def loadImage(self, filename, transparent=True):
		try: image = pygame.image.load(filename)
		except pygame.error as message: raise SystemError
		image = image.convert()
		if transparent:
			color = image.get_at((0,0))
			image.set_colorkey(color, RLEACCEL)
		return image


#=======================================================================
#=======================================================================
#=======================================================================

server = Network()
utils  = Utils()
config = Config()
player = Player()

# Dynamic Variables
players = {}
enemies = {}

# get users name
while True:
 	name = input('Please enter your name: ')
 	if 0 < len(name) < 20:
 		break
 	else:
 		print('Error, this name is not allowed (must be between 1 and 19 characters [inclusive])')

# make window start in top left hand corner
# os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (0,30)
os.environ['SDL_VIDEO_CENTERED'] = '1'

# setup pygame window
WIN = pygame.display.set_mode((config.W,config.H))
pygame.display.set_caption('Valkyrio')

#=======================================================================
#=======================================================================
#=======================================================================

def drawWithDeep(text, xy, deep=1):
	WIN.blit(text, (xy[0],   xy[1]))
	if deep >= 1:
		WIN.blit(text, (xy[0]-1, xy[1]-1))
	if deep >= 2:
		WIN.blit(text, (xy[0]-2, xy[1]-2))
	if deep >= 3:
		WIN.blit(text, (xy[0]-3, xy[1]-3))

def drawShipAndData(ship, des, name_color):
	
	# Draw Ship ----------------------------------
	rect = ship.img.get_rect(
		center = (
			int(ship.x)+des[0],
			int(ship.y)+des[1]
		)
	)
	WIN.blit(ship.img, rect)
	
	desp = 50
	
	if config.show['name']:
		# Draw Name ----------------------------------
		font = config.FONT['Inc-R 18']
		text = '-- [' + ship.name + '] --'
		text = font.render(text, 1, name_color)
		drawWithDeep(text, (
				int(ship.x)+des[0] - text.get_width() /2,
				int(ship.y)+des[1] - text.get_height()/2 + desp
			), 0
		)
		desp += text.get_height()-5
	
	if config.show['hp-sp']:
		# Draw HP ------------------------------------
		font = config.FONT['Inc-R 14']
		text = f'{ship.ship.chp}/{ship.ship.hp}'
		text = font.render(text, 1, config.COLOR['Verde'])
		drawWithDeep(text, (
				int(ship.x)+des[0] - text.get_width() /2,
				int(ship.y)+des[1] - text.get_height()/2 + desp
			), 0
		)
		desp += text.get_height()-3
		
		# Draw SP ------------------------------------
		font = config.FONT['Inc-R 14']
		text = f'{ship.ship.csp}/{ship.ship.sp}'
		text = font.render(text, 1, config.COLOR['Cyan'])
		drawWithDeep(text, (
				int(ship.x)+des[0] - text.get_width() /2,
				int(ship.y)+des[1] - text.get_height()/2 + desp
			), 0
		)
	else:
		
		desp -= 3
		
		width = 100
		height = 10
		
		x = int(ship.x)+des[0] - width/2
		y = int(ship.y)+des[1] + desp
		position = [x, y, width, height]
		utils.roundRect(WIN, position, config.COLOR['Verde F'],
			3, 1, (*config.COLOR['Verde S'], 50)
		)
		x = int(ship.x)+des[0] - width/2
		y = int(ship.y)+des[1] + desp
		pct_hp = ship.ship.chp / ship.ship.hp
		position = [x, y, int(width*pct_hp), height]
		utils.roundRect(WIN, position, config.COLOR['Verde F'],
			3, 1, (*config.COLOR['Verde'], 200)
		)
		
		desp += height + 1
		
		x = int(ship.x)+des[0] - width/2
		y = int(ship.y)+des[1] + desp
		position = [x, y, width, height]
		utils.roundRect(WIN, position, config.COLOR['Verde F'],
			3, 1, (*config.COLOR['Verde S'], 50)
		)
		x = int(ship.x)+des[0] - width/2
		y = int(ship.y)+des[1] + desp
		pct_sp = ship.ship.csp / ship.ship.sp
		position = [x, y, int(width*pct_sp), height]
		utils.roundRect(WIN, position, config.COLOR['Verde F'],
			3, 1, (*config.COLOR['Cyan'], 200)
		)
	
	# Draw red circle: -----------------------------
	if player.selected['id'] == ship.id:
		pygame.draw.circle(WIN,
			(255,0,0), (
				int(ship.x)+des[0],
				int(ship.y)+des[1]
			), config.SELECT_MIN_DIST, 1
		)
	
	#===================================================================
	
	if ship.ship.damageRecv:
		
		len_dmg = len(ship.ship.damageRecv)
		for i in range(len_dmg):
			if ship.ship.damageRecv[i]:
				t1 = ship.ship.damageRecv[i][1]
				if time.perf_counter()-t1 < 1:
					if i+1 < len_dmg:
						dmg = ship.ship.damageRecv[i+1][0]
						t2  = ship.ship.damageRecv[i+1][1]
						if abs(t2-t1) < 1:
							ship.ship.damageRecv[i][0] += dmg
							ship.ship.damageRecv[i+1] = None
		
		while None in ship.ship.damageRecv:
			ship.ship.damageRecv.remove(None)
		
		out = -1
		for i, (damage, t) in enumerate(ship.ship.damageRecv):
			t = time.perf_counter()-t
			if t > 2: out = i
			font = config.FONT['Inc-R 18']
			text = str(damage)
			text = font.render(text, 1, config.COLOR['Rojo'])
			t_h = text.get_height()
			drawWithDeep(text, (
					int(ship.x)+des[0] - text.get_width() /2,
					int(ship.y)+des[1] - text.get_height()/2 -t_h -int(t*12)
				)
			)
		
		if out >= 0: ship.ship.damageRecv.pop(out)

def redrawWindow(game_time):
	
	BLANCO = config.COLOR['Blanco']
	ROJO   = config.COLOR['Rojo']
	WIN.fill(config.COLOR['Background'])
	
	desX = (int(config.CENTER['x'])-int(player.x))	# Desplazamiento en X
	desY = (int(config.CENTER['y'])-int(player.y))	# Desplazamiento en Y
	
	drawMatrix(desX, desY)										# Dibuja las lineas del fondo
	
	# Draw Other Players: ==============================================
	
	enemies_sorted = sorted(enemies, key=lambda x: enemies[x].score)
	
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
	
	# Draw info on main layer data: ====================================
	
	if False:
		
		font = config.FONT['Retro 18']
		
		# Draw scoreboard: -------------------------------------------------
		sort_enemies = list(reversed(enemies_sorted))
		text = font.render('Scoreboard', 1, BLANCO)
		start_y = 25
		x = config.W - text.get_width() - 10
		WIN.blit(text, (x, 5))
		
		ran = min(len(enemies), 3)
		for count, i in enumerate(sort_enemies[:ran]):
			text = str(count+1) + '. ' + str(enemies[i].name)
			text = font.render(text, 1, BLANCO)
			WIN.blit(text, (x, start_y + count * 20))
		
		# Draw time: -------------------------------------------------------
		text = 'Time: ' + utils.convertTime(game_time)
		text = font.render(text, 1, BLANCO)
		WIN.blit(text,(10, 10))
		
		# Draw player score: -----------------------------------------------
		text = 'Score: ' + str(round(player.score))
		text = font.render(text,1,BLANCO)
		WIN.blit(text,(10, 15 + text.get_height()))
	
	# Draw Game Info on main layer data: ===============================
	
	despX = 10			# Desplazamiento en X
	despY = 15			# Desplazamiento en Y
	texts = {}
	widest = 0
	
	if config.show['pos']:
		texts['pos'] = '({},{})'.format(
			int(player.x/config.posdiv),
			int(player.y/config.posdiv)
		).ljust(11)
	if config.show['fps']:
		texts['fps'] = 'FPS: '+str(config.fps)
	if config.show['speed']:
		texts['speed'] = 'Speed: ' + str(player.ship.speed)
	
	for i, text in enumerate(texts.values()):
		font = config.FONT['Inc-R 14']
		text = font.render(text, 1, BLANCO)
		if text.get_width() > widest:
			widest = text.get_width()
		WIN.blit(text, (despX, config.H-text.get_height()-10 -(despY*i)))
	i+=1
	# ~ round_rect(screen, rect_pos1, COLOR['VF'], 3, 1, (*COLOR['VS'], 50))
	positions = [
		despX - 5,
		config.H - 10 - despY*i - 5,
		widest + 10,
		despY*i + 10
	]
	utils.roundRect(WIN, positions, config.COLOR['Verde F'],
		3, 1, (*config.COLOR['Verde S'], 50)
	)
	
	if player.ship.timeOnBorder:
		font = config.FONT['Retro 18']
		text = 'Radioactive Zone'
		text = font.render(text, 1, BLANCO)
		WIN.blit(text, (config.CENTER['x']-text.get_width()/2, 30))
	
	if player.ship.destroyed:
		font = config.FONT['Retro 18']
		text = 'Destroyed'
		text = font.render(text, 1, BLANCO)
		WIN.blit(text, (config.CENTER['x']-text.get_width()/2, 60))

def drawMatrix(desX, desY):
	
	lines = config.matrix_bg
	per = config.H/config.W
	
	x_r = int(config.W / lines)
	y_r = int(config.H / (lines*per))
	
	for x in range(lines+3):
		
		x1 = -x_r + x_r * x + desX%x_r
		y1 = -y_r
		
		x2 = -x_r + x_r * x + desX%x_r
		y2 = config.H + y_r
		
		pygame.draw.line(WIN, config.COLOR['Linea Bg'], (x1,y1), (x2,y2), 1)
	
	for y in range(int((lines*per))+3):
		
		x1 = -x_r
		y1 = -y_r + y_r * y + desY%y_r
		
		x2 = config.W + x_r
		y2 = -y_r + y_r * y + desY%y_r
		
		pygame.draw.line(WIN, config.COLOR['Linea Bg'], (x1,y1), (x2,y2), 1)

def healing(chp, hp, wait_hp_init, wait_hp_max, wait_hp_pct):
	if not chp == hp:
		if wait_hp_init == 0:
			wait_hp_init = time.perf_counter()
		if time.perf_counter()-wait_hp_init >= wait_hp_max:
			hp_add = hp * wait_hp_pct
			if chp < hp: chp += int(hp_add)
			if chp > hp: chp = hp
			wait_hp_init = 0
	return chp, wait_hp_init

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
		
		if leftMove and not rightMove:
			movements = True
			if not upDownMove and (upMove or downMove):
				if   upMove:   degrees = 90
				elif downMove: degrees = 270
				x -= utils.diagonal(speed)[0]
			else:
				degrees = 180
				x -= speed
		
		if rightMove and not leftMove:
			movements = True
			if not upDownMove and (upMove or downMove):
				if   upMove:   degrees = 90
				elif downMove: degrees = 270
				x += utils.diagonal(speed)[0]
			else:
				degrees = 0
				x += speed
		
		if upMove and not downMove:
			movements = True
			if not leftRightMove and (leftMove or rightMove):
				if leftMove:  degrees += 45
				if rightMove: degrees -= 45
				y -= utils.diagonal(speed)[1]
			else:
				degrees = 90
				y -= speed
		
		if downMove and not upMove:
			movements = True
			if not leftRightMove and (leftMove or rightMove):
				if leftMove:  degrees -= 45
				if rightMove: degrees += 45
				y += utils.diagonal(speed)[1]
			else:
				degrees = 270
				y += speed
		
		if movements:
			player.ship.wait_hp_init = 0
			player.angle = degrees
			player.rotate(degrees)
			player.x += round(x, 2)
			player.y += round(y, 2)
		else:
			# Recibir curación:
			_chp, _wait_hp_init = healing(
				player.ship.chp,
				player.ship.hp,
				player.ship.wait_hp_init,
				player.ship.wait_hp_max,
				player.ship.wait_hp_pct
			)
			player.ship.chp = _chp
			player.ship.wait_hp_init = _wait_hp_init
		
		# Recibir curación:
		_csp, _wait_sp_init = healing(
			player.ship.csp,
			player.ship.sp,
			player.ship.wait_sp_init,
			player.ship.wait_sp_max,
			player.ship.wait_sp_pct
		)
		player.ship.csp = _csp
		player.ship.wait_sp_init = _wait_sp_init

def selectObj(event):
	
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
			
			if dist < config.SELECT_MIN_DIST:
				dists.append(( dist, other_player.name, other_player_id ))
		
		min_dist      = config.SELECT_MIN_DIST
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
				player.selected['name'] = min_dist_name
				player.selected['id']   = min_dist_id
				data = data_f.format(min_dist_name, min_dist_id)
		elif dists:
			if not dists[0][2] == player.selected['id']:
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

def detectEvents():
	
	for event in pygame.event.get():
		
		if event.type == pygame.QUIT:
			config.run = False
		
		if event.type == pygame.KEYDOWN:
			
			if event.key == pygame.K_ESCAPE:
				config.run = False
			
			if event.key == pygame.K_LSHIFT:
				if player.selected['id'] >= 0:
					player.attacking = not player.attacking
			
			if event.key == pygame.K_j:
				player.ship.speed -= 10
			if event.key == pygame.K_k:
				player.ship.speed += 10
			if event.key == pygame.K_o:
				config.show['name'] = not config.show['name']
			if event.key == pygame.K_p:
				config.show['hp-sp'] = not config.show['hp-sp']
			
			if event.key == pygame.K_l:
				player.ship.recvDamage(10, pct_sp=1, mult=5)
		
		# ~ if event.type == pygame.MOUSEMOTION:
		
		if event.type == pygame.MOUSEBUTTONDOWN:
			
			players_ = selectObj(event)
			if players_: updateOtherPlayers(players_)

def updateOtherPlayers(players):
	
	# Update enemies
	ids_removed = []
	for id_ in enemies:
		if enemies[id_].__class__.__name__ == 'Player':
			if id_ in players:
				enemies[id_].updateData(players[id_])
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
			other_player.loadData(players[id_])
			enemies[id_] = other_player

def rotateToEnemy():
	
	desX = (int(config.CENTER['x'])-int(player.x))	# Desplazamiento en X
	desY = (int(config.CENTER['y'])-int(player.y))	# Desplazamiento en Y
	
	# Gira hacia el enemigo
	if player.selected['id'] >= 0 and player.attacking:
		
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
	
	# ~ selected_by_enemies = []
	# ~ for id_ in enemies:
		# ~ angle = enemies[id_].angle
		# ~ enemies[id_].rotate(angle)
		# ~ selected_name = enemies[id_].selected['name']
		# ~ if selected_name == player.name:
			# ~ selected_by_enemies.append(id_)
	
	# ~ if selected_by_enemies:
		
		# ~ for enemy_id in selected_by_enemies:
			# ~ px, py = config.CENTER['x'],       config.CENTER['y']
			# ~ x,  y  = enemies[enemy_id].x+desX, enemies[enemy_id].y+desY
			
			# ~ dist  = round(utils.euclideanDistance((x,y), (px,py)), 2)
			# ~ angle = -round(utils.getAngle((x,y), (px,py)), 2)
			
			# ~ enemies[enemy_id].selected['dist'] = dist
			# ~ enemies[enemy_id].angle = angle
			# ~ enemies[enemy_id].rotate(angle)
	''

def borderRules():
	
	if (player.x < 0 or config.limitX < player.x)\
	or (player.y < 0 or config.limitX < player.y):
		if player.ship.timeOnBorder == 0:
			player.ship.timeOnBorder = time.perf_counter()
		if time.perf_counter() - player.ship.timeOnBorder > 2:
			player.ship.timeOnBorder = time.perf_counter()
			player.ship.recvDamage(config.radDmg, pct_sp=0)
	else:
		if player.ship.timeOnBorder > 0:
			player.ship.timeOnBorder = 0

#=======================================================================

def main():
	
	global players
	
	config.run = True
	deltaTime = 1					# Delta Time
	frames = 0						# Number of Frames
	clock = pygame.time.Clock()
	
	# start by connecting to the network
	player.name = name
	player.id = server.connect(player.name)
	players, game_time = server.send('get')
	player.loadData(players[player.id])
	
	while config.run:
		
		players, game_time = server.send(player.data)				# Envia datos al servidor y recibe la información de los otros jugadores
		
		updateOtherPlayers(players)							# Actualiza los datos de los enemigos
		movements(deltaTime)								# Detecta los movimientos direccionales
		borderRules()										# Reglas para la zona radioactiva
		detectEvents()										# Detecta los eventos de Mouse y Teclado
		rotateToEnemy()										# Si el enemigo esta seleccionado o el jugador es seleccionado, las naves giran apuntandose.
		redrawWindow(game_time)								# Redibuja todo (1 Fotograma)
		pygame.display.update()								# Actualiza la ventana con todos los cambios
		
		deltaTime = clock.tick(config.MFPS) / config.dtdiv	# Hace una breve pausa para respetar los Fotogramas por segundo y devuelve el "Delta Time"/1000
		
		if utils.perSecond():
			config.fps = frames
			frames = 0
			# ~ for _, e in enemies.items(): print(e, end=' ')
			# ~ print()
		else:
			frames += 1
	
	server.disconnect()
	pygame.quit()
	quit()



# Ejecuta esto despues de terminar la ejecución del programa.
@atexit.register
def close():
	time.sleep(1)



# start game
main()


