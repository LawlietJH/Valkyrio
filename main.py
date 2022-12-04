from src import Network, Player, Settings, Utils, Chat, Minimap
import contextlib
with contextlib.redirect_stdout(None):
	import pygame
from pygame.locals import *
import atexit
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

pygame.init()
pygame.mixer.init()
pygame.font.init()

# Basic Objects
server  = Network()
utils   = Utils()
config  = Settings(utils)
player  = Player(config)

# General Objects
minimap = Minimap(config)
chat = Chat(config, player)

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
			cost = player.ship.spd_lvl*10
			player.creds += cost
			player.ship.speedLevelDown(-10)
	if event.key == pygame.K_k:								# K - Speed level up
		# ~ cost = (player.ship.spd_lvl+1)
		# ~ if player.creds >= cost:
			# ~ player.creds -= cost
			player.ship.speedLevelUp(10)
	
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

def getUsername() -> str:
	# Get users name
	while True:
		# name = input('[+] Please enter your Username: ')
		name = 'Eny'
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
			other_player = Player(config, name, id_)
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
		# ~ utils.perfectOutline(WIN, ship.img, rect, color, alpha=25, br=4)			# Contorno Negro
		utils.perfectOutline(WIN, ship.img, rect, color, alpha=25, br=3)			# Contorno Negro
		# ~ utils.perfectOutline(WIN, ship.img, rect, color, alpha=25, br=2)			# Contorno Negro
		utils.perfectOutline(WIN, ship.img, rect, color, alpha=25, br=1)			# Contorno Negro
	
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
	# os.environ['SDL_VIDEO_WINDOW_POS'] = f'{840},{40}'
	# os.environ['SDL_VIDEO_CENTERED'] = '1'
	
	# Setup pygame window
	WIN = pygame.display.set_mode((config.W,config.H), HWSURFACE | DOUBLEBUF | RESIZABLE)
	pygame.display.set_caption(f'{__project__} Online v{__version__} - By: {__author__}')
	
	# Music
	# config.music.load(config.MUSIC['JNATHYN - Genesis'])
	# config.music.set_volume(config.music_vol/100)
	''# config.music.play(-1)

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
# TODO Para futuro desarrollo:
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
# TODO Bugs Detectados:
# + [Ok] Al seleccionar un enemigo y desplazarse desde el minimapa, el movimiento de avance esta mal.
# + [Ok] Al seleccionar agrandar o encojer el minimapa se detecta el clic y afecta el movimiento.
# + [] Al atacar un enemigo, si no entras en su rango de visión, no te ataca.
# + [] El recuadro de pantalla en el minimapa, se desborda.
# + [] Daño causado de enemigos a enemigos no carga correctamente.
# + [] Cuando un enemigo te ataca no se ve correctamente la animación.
# + [] Cambiar color negro absoluto de los pixel arts. Se elimina al cargar la imagen (remplaza por vacio como el fondo)
