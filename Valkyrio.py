
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
#=======================================================================
#=======================================================================

class Config:
	
	def __init__(self):
		
		# Cons:
		
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
		}
		
		self.FONT = {
			'Inc-R 12': pygame.font.Font("font/Inconsolata-Regular.ttf", 12),
			'Inc-R 14': pygame.font.Font("font/Inconsolata-Regular.ttf", 14),
			'Inc-R 16': pygame.font.Font("font/Inconsolata-Regular.ttf", 16),
			'Inc-R 18': pygame.font.Font("font/Inconsolata-Regular.ttf", 18),
			'Retro 12': pygame.font.Font("font/Retro Gaming.ttf", 12),
			'Retro 14': pygame.font.Font("font/Retro Gaming.ttf", 14),
			'Retro 16': pygame.font.Font("font/Retro Gaming.ttf", 16),
			'Retro 18': pygame.font.Font("font/Retro Gaming.ttf", 18),
			'Wendy 12': pygame.font.Font("font/Wendy.ttf", 12),
			'Wendy 14': pygame.font.Font("font/Wendy.ttf", 14),
			'Wendy 16': pygame.font.Font("font/Wendy.ttf", 16),
			'Wendy 18': pygame.font.Font("font/Wendy.ttf", 18)
		}	# Diccionario de Fuentes.
		
		self.SHIP = {
			'Prometheus': {
				'path': 'img/Prometheus.png',
				'speed': 50,
				'hp':    350,
				'sp':    250
			}
		}
		
		# Configs:
		self.limitX = 10000
		self.limitY = 10000
		self.run   = False
		self.dtdiv = 1000				# Detla Time Divide
		self.MFPS  = 120				# Max Frames per Second
		self.fps   = 60					# Number of Frames per Second
		self.matrix_bg = 15
		self.show = {
			'name': True,
			'fps': True,
			'pos': True
		}
		
		self.BASE_SPEED = 100
		self.MAX_SPEED  = 300
		self.RESOLUTION = 1280, 768
		self.W, self.H  = 1280, 768
		self.CENTER = {'x': self.W//2, 'y': self.H//2}


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
	
	def convert_time(self, t):
		if type(t) == str: return t
		if int(t) < 60: return str(t) + 's'
		else:
			minutes = str(t // 60)
			seconds = str(t % 60)
			if int(seconds) < 10:
				seconds = '0' + seconds
			return minutes + ':' + seconds


class Ship:
	
	def __init__(self, name):
		
		self.name = name
		self.base = config.SHIP[name]
		
		self.speed  = config.BASE_SPEED
		self.speed += self.base['speed']
		
		# Health
		self.hp  = self.base['hp']		# Health points
		self.chp = self.hp				# Current Health Points
		self.lhp = 1					# Level Health Points
		
		# Shield
		self.shield_unlocked = True
		self.sp  = self.base['sp']		# Shield points
		self.csp = self.sp				# Current Shield Points
		self.lsp = 0					# Level Shield Points
	
	def levelUpHP(lvl=1):				# Incrementa de nivel el HP
		inc = self.base['hp'] * lvl
		self.hp += inc
		self.chp += inc
		self.lhp += lvl
	
	def levelUpSP(lvl=1):				# Incrementa de nivel el SP
		if self.shield_unlocked:
			inc = self.base['hp'] * lvl
			self.sp += inc
			self.csp += inc
			self.lsp += lvl


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
		self.divpos = 30
		
		self.angle = None
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
	
	def rotate(self, angle):
		
		img = self.img_orig
		self.img = pygame.transform.rotate(img, angle)
	
	def loadData(self, player):
		
		self.x = player['x']
		self.y = player['y']
		self.score = player['score']
		self.selected['name'] = player['selected']['name']
		self.selected['id']   = player['selected']['id']
		
		self.ship_name = player['ship']
		self.ship_path = config.SHIP[self.ship_name]['path']
		self.ship = Ship(self.ship_name)
		
		self.img_orig = self.load_image(self.ship_path)
		self.img = self.img_orig
	
	def updateData(self, player):
		
		self.x = player['x']
		self.y = player['y']
		self.score = player['score']
		self.selected = player['selected']
		
		self.ship_name = player['ship']
		self.ship_path = config.SHIP[self.ship_name]['path']
		self.ship = Ship(self.ship_name)
		
	
	def load_image(self, filename, transparent=True):
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

config = Config()
server = Network()
player_ = Player()
utils  = Utils()

NAME_FONT = config.FONT['Inc-R 18']
TIME_FONT = config.FONT['Retro 18']
SCORE_FONT = config.FONT['Wendy 18']

# ~ NAME_FONT = pygame.font.SysFont('comicsans', 20)
# ~ TIME_FONT = pygame.font.SysFont('comicsans', 24)
# ~ SCORE_FONT = pygame.font.SysFont('comicsans', 18)

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

player_.name = name

# make window start in top left hand corner
# os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (0,30)
os.environ['SDL_VIDEO_CENTERED'] = '1'

# setup pygame window
WIN = pygame.display.set_mode((config.W,config.H))
pygame.display.set_caption('Valkyrie')

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
	
	# Draw Name --------------
	text = '-- [' + ship.name + '] --'
	text = NAME_FONT.render(text, 1, name_color)
	drawWithDeep(text, (
			int(ship.x)+des[0] - text.get_width() /2,
			int(ship.y)+des[1] - text.get_height()/2 - 50
		)
	)
	
	# Draw Ship --------------
	rect = ship.img.get_rect(
		center = (
			int(ship.x)+des[0],
			int(ship.y)+des[1]
		)
	)
	WIN.blit(ship.img, rect)
	
	# Draw HP ----------------
	font = config.FONT['Inc-R 16']
	text = f'{ship.ship.chp}/{ship.ship.hp}'
	text = font.render(text, 1, config.COLOR['Verde'])
	drawWithDeep(text, (
			int(ship.x)+des[0] - text.get_width() /2,
			int(ship.y)+des[1] - text.get_height()/2 + 50
		), 0
	)
	
	# Draw SP ----------------
	font = config.FONT['Inc-R 16']
	text = f'{ship.ship.csp}/{ship.ship.sp}'
	text = font.render(text, 1, config.COLOR['Cyan'])
	drawWithDeep(text, (
			int(ship.x)+des[0] - text.get_width() /2,
			int(ship.y)+des[1] - text.get_height()/2 + 50 + text.get_height()
		), 0
	)

def redraw_window(game_time):
	
	BLANCO = config.COLOR['Blanco']
	ROJO   = config.COLOR['Rojo']
	WIN.fill(config.COLOR['Background'])
	
	desX = (int(config.CENTER['x'])-int(player_.x))	# Desplazamiento en X
	desY = (int(config.CENTER['y'])-int(player_.y))	# Desplazamiento en Y
	
	drawMatrix(desX, desY)										# Dibuja las lineas del fondo
	
	# Draw Other Players: ==============================================
	
	enemies_sorted = sorted(enemies, key=lambda x: enemies[x].score)
	
	for other_player_id in enemies_sorted:
		
		if other_player_id == player_.id: continue
		
		other_player = enemies[other_player_id]
		
		# Draw the ship: -------------------------------
		drawShipAndData(other_player, (desX,desY), ROJO)
		
		# Draw red circle: -----------------------------
		if player_.selected['id'] == other_player_id:
			pygame.draw.circle(WIN,
				(255,0,0), (
					int(other_player.x)+desX,
					int(other_player.y)+desY
				), 20, 2
			)
	
	# Draw Player: =====================================================
	
	drawShipAndData(player_, (desX,desY), BLANCO)
	
	# Draw info on main layer data: ====================================
	
	# Draw scoreboard: -------------------------------------------------
	sort_enemies = list(reversed(enemies_sorted))
	text = TIME_FONT.render('Scoreboard', 1, BLANCO)
	start_y = 25
	x = config.W - text.get_width() - 10
	WIN.blit(text, (x, 5))
	
	ran = min(len(enemies), 3)
	for count, i in enumerate(sort_enemies[:ran]):
		text = str(count+1) + '. ' + str(players[i]['name'])
		text = TIME_FONT.render(text, 1, BLANCO)
		WIN.blit(text, (x, start_y + count * 20))
	
	# Draw time: -------------------------------------------------------
	text = 'Time: ' + utils.convert_time(game_time)
	text = TIME_FONT.render(text, 1, BLANCO)
	WIN.blit(text,(10,10))
	
	# Draw player score: -----------------------------------------------
	text = 'Score: ' + str(round(player_.score))
	text = TIME_FONT.render(text,1,BLANCO)
	WIN.blit(text,(10,15 + text.get_height()))
	
	if config.show['pos']:
		# Draw position:
		x = int(player_.x/player_.divpos)
		y = int(player_.y/player_.divpos)
		text = '({},{})'.format(x, y)
		text = SCORE_FONT.render(text, 1, BLANCO)
		WIN.blit(text, (
				10,
				config.H-text.get_height()-25
			)
		)
	
	if config.show['fps']:
		# Draw FPS:
		text = 'FPS: '+str(config.fps)
		text = SCORE_FONT.render(text, 1, BLANCO)
		WIN.blit(text, (
				10, 
				config.H-text.get_height()-5
			)
		)

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
	
def movements(deltaTime):
		
		# get key presses
		keys = pygame.key.get_pressed()
		speed = player_.ship.speed
		speed = speed * deltaTime
		
		# movement based on key presses
		if keys[pygame.K_LEFT] or keys[pygame.K_a]:
			if keys[pygame.K_DOWN] or keys[pygame.K_s]\
			or keys[pygame.K_UP]   or keys[pygame.K_w]:
				player_.x -= utils.diagonal(speed)[0]
			else:
				player_.rotate(180)
				player_.x -= speed
		
		if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
			if keys[pygame.K_DOWN] or keys[pygame.K_s]\
			or keys[pygame.K_UP]   or keys[pygame.K_w]:
				player_.x += utils.diagonal(speed)[0]
			else:
				player_.rotate(0)
				player_.x += speed
		
		if keys[pygame.K_UP] or keys[pygame.K_w]:
			if keys[pygame.K_LEFT]  or keys[pygame.K_a]\
			or keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				player_.y -= utils.diagonal(speed)[1]
			else:
				player_.rotate(90)
				player_.y -= speed
		
		if keys[pygame.K_DOWN] or keys[pygame.K_s]:
			if keys[pygame.K_LEFT]  or keys[pygame.K_a]\
			or keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				player_.y += utils.diagonal(speed)[1]
			else:
				player_.rotate(270)
				player_.y += speed
		
		player_.x = round(player_.x, 2)
		player_.y = round(player_.y, 2)

def selectObj(event):
	
	if event.button == 1:
		
		desX = (int(config.CENTER['x'])-int(player_.x))	# Desplazamiento en X
		desY = (int(config.CENTER['y'])-int(player_.y))	# Desplazamiento en Y
		
		posX, posY = event.pos
		dists = []
		for other_player_id in enemies:
			if other_player_id == player_.id: continue
			other_player = enemies[other_player_id]
			pposX = other_player.x+desX
			pposY = other_player.y+desY
			
			dist = utils.euclideanDistance((posX, posY), (pposX,pposY))
			
			if dist < 20:
				dists.append((
					dist,
					other_player.name,
					other_player_id #, (
						# ~ other_player.x,
						# ~ other_player.y
					# ~ )
				))
		
		min_dist      = 20
		min_dist_name = ''
		min_dist_id   = 0
		# ~ min_dist_pos  = []
		
		data_f = 'selected:{{"name":"{}","id":{}}}'#,"x":{},"y":{}}}'
		data = ''
		
		if len(dists) > 1:
			for dist, name, p_id in dists: #, pos in dists:
				if dist < min_dist:
					min_dist      = dist
					min_dist_name = name
					min_dist_id   = p_id
					# ~ min_dist_pos  = pos
			if not min_dist_id == player_.selected['id']:
				player_.selected['name'] = min_dist_name
				player_.selected['id']   = min_dist_id
				# ~ player_.selected['x']    = min_dist_pos[0]
				# ~ player_.selected['y']    = min_dist_pos[1]
				data = data_f.format(min_dist_name, min_dist_id)#, *min_dist_pos)
		elif dists:
			if not dists[0][2] == player_.selected['id']:
				player_.selected['name'] = dists[0][1]
				player_.selected['id']   = dists[0][2]
				# ~ player_.selected['x']    = dists[0][3][0]
				# ~ player_.selected['y']    = dists[0][3][1]
				data = data_f.format(dists[0][1], dists[0][2])#, *dists[0][3])
		
		if data:
			players = server.send(data)
	
	if event.button == 3:
		if player_.selected['name']:
			player_.selected['name'] = ''
			player_.selected['id']   = -1
			player_.selected['dist'] = -1
			data = 'selected:{"name":"","id":-1}'#,"x":0,"y":0}'
			players = server.send(data)
			return players

def detectEvents():
	
	for event in pygame.event.get():
		
		if event.type == pygame.QUIT:
			config.run = False
		
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				config.run = False
			if event.key == pygame.K_ESCAPE:
				config.run = False
		
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
		if id_ == player_.id: continue
		if not id_ in enemies:
			name = players[id_]['name']
			other_player = Player(name, id_)
			other_player.loadData(players[id_])
			enemies[id_] = other_player

def rotateToEnemy():
	
	selected_by_enemies = []
	for id_ in enemies:
		selected_name = enemies[id_].selected['name']
		if selected_name == player_.name:
			selected_by_enemies.append(id_)
	
	desX = (int(config.CENTER['x'])-int(player_.x))	# Desplazamiento en X
	desY = (int(config.CENTER['y'])-int(player_.y))	# Desplazamiento en Y
	
	# Gira hacia el enemigo
	if player_.selected['name']:
		
		p_id = player_.selected['id']
		
		try:
			selected_pos = enemies[p_id].x+desX, enemies[p_id].y+desY
		except:
			player_.selected['name'] = ''
			player_.selected['id']   = -1
			player_.selected['dist'] = -1
			return
		
		pposX, pposY = int(config.CENTER['x']), int(config.CENTER['y'])
		
		dist  = round(utils.euclideanDistance((pposX,pposY), selected_pos), 2)
		angle = -round(utils.getAngle((pposX,pposY), selected_pos), 2)
		
		# ~ data_f = 'angle_dist:{{"angle":{},"dist":{}}}'#,"x":{},"y":{}}}'
		# ~ data = data_f.format(angle, dist)#, *selected_pos)
		# ~ players = server.send(data)
		
		player_.selected['dist'] = dist
		player_.angle = angle
		player_.rotate(angle)
	
	if selected_by_enemies:
		
		for enemy_id in selected_by_enemies:
			px, py = config.CENTER['x'],       config.CENTER['y']
			x,  y  = enemies[enemy_id].x+desX, enemies[enemy_id].y+desY
			
			dist  = round(utils.euclideanDistance((x,y), (px,py)), 2)
			angle = -round(utils.getAngle((x,y), (px,py)), 2)
			
			enemies[enemy_id].selected['dist'] = dist
			enemies[enemy_id].angle = angle
			enemies[enemy_id].rotate(angle)

#=======================================================================

def main(name):
	
	global players
	
	config.run = True
	deltaTime = 1					# Delta Time
	frames = 0						# Number of Frames
	clock = pygame.time.Clock()
	
	# start by connecting to the network
	player_.id = server.connect(name)
	players, game_time = server.send('get')
	player_.loadData(players[player_.id])
	
	while config.run:
		
		data_f = 'move:{{"x":{},"y":{}}}'
		data = data_f.format(player_.x, player_.y)
		players, game_time = server.send(data)				# Envia datos al servidor y recibe la información de los otros jugadores
		
		updateOtherPlayers(players)							# Actualiza los datos de los enemigos
		movements(deltaTime)								# Detecta los movimientos direccionales
		detectEvents()										# Detecta los eventos de Mouse y Teclado
		rotateToEnemy()										# Si el enemigo esta seleccionado o el jugador es seleccionado, las naves giran apuntandose.
		redraw_window(game_time)							# Redibuja todo (1 Fotograma)
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
main(name)
