import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *

class Events:
    def __init__(self, settings, server, player, enemies, minimap, chat, utils):
        self.settings = settings
        self.server = server
        self.player = player
        self.enemies = enemies
        self.utils = utils
        self.minimap = minimap
        self.chat = chat

    def keysDown(self, event):
        if event.key == pygame.K_ESCAPE:                                # ESC - Close Game
            self.settings.run = False

        if event.key == pygame.K_LSHIFT:                                # LShift- Attack
            if self.player.selected['id'] >= 0:
                self.player.attacking = not self.player.attacking

        # Hide/Show ---------------
        if event.key == pygame.K_TAB:

            # Control de menu ------------------------
            self.settings.open_menu = not self.settings.open_menu

            # Control de input del chat ------------------------
            if self.chat.chat_text_active:
                self.chat.chat_text_active = False

        if not self.settings.open_menu:
            if event.key == pygame.K_o:                                 # O - Hide/Show Names
                self.settings.show['name'] = not self.settings.show['name']
            if event.key == pygame.K_p:                                 # P - Hide/Show HP-SP
                self.settings.show['hp-sp'] = not self.settings.show['hp-sp']

        #--------------------------

        if event.key == pygame.K_F11:                                   # F11 - Fullscreen
            self.settings.switchFullScreen()

        #--------------------------

        if event.key == pygame.K_1:
            if self.settings.open_menu:
                self.settings.pos_tab_menu = 1
        if event.key == pygame.K_2:
            if self.settings.open_menu:
                self.settings.pos_tab_menu = 2
        if event.key == pygame.K_3:
            if self.settings.open_menu:
                self.settings.pos_tab_menu = 3
        if event.key == pygame.K_4:
            if self.settings.open_menu:
                self.settings.pos_tab_menu = 4
        if event.key == pygame.K_5:
            if self.settings.open_menu:
                self.settings.pos_tab_menu = 5
        if event.key == pygame.K_6:
            if self.settings.open_menu:
                self.settings.pos_tab_menu = 6
        if event.key == pygame.K_7:
            if self.settings.open_menu:
                self.settings.pos_tab_menu = 7
        if event.key == pygame.K_8:
            if self.settings.open_menu:
                self.settings.pos_tab_menu = 8
        if event.key == pygame.K_9:
            if self.settings.open_menu:
                self.settings.pos_tab_menu = 9
        if event.key == pygame.K_0:
            if self.settings.open_menu:
                self.settings.pos_tab_menu = 0

        #--------------------------

        if event.key == pygame.K_BACKSPACE:
            # Control de input del chat ------------------------
            if self.chat.chat_text_active and self.chat.chat_text:
                self.chat.chat_text = self.chat.chat_text[:-1]

        if event.key == pygame.K_RETURN:
            # Control de input del chat ------------------------
            if self.chat.chat_text_active and self.chat.chat_text:

                if self.chat.chat_tab == 1: chat_type = 'global'

                msg = 'msg:'+chat_type+':'+self.player.name+':'+self.chat.chat_text
                self.chat.messages = self.server.send(msg)
                self.chat.chat_text = ''

        if event.key == pygame.K_PLUS:                             # +
            if self.chat.chat_w < self.chat.chat_max_w:
                self.chat.chat_w += 5
            print(self.chat.chat_w)
        if event.key == pygame.K_MINUS:                            # -
            if self.chat.chat_w > self.chat.chat_min_w:
                self.chat.chat_w -= 5
            print(self.chat.chat_w)

        if event.key == pygame.K_t:                                # t
            if self.chat.chat_h < self.chat.chat_max_h:
                self.chat.chat_h += 5
            print(self.chat.chat_h)
        if event.key == pygame.K_y:                                # y
            if self.chat.chat_h > self.chat.chat_min_h:
                self.chat.chat_h -= 5
            print(self.chat.chat_h)

        #--------------------------
        if event.key == pygame.K_j:                                # J - Speed level down
            # if self.player.ship.spd_lvl > 0:
            #     cost = self.player.ship.spd_lvl*10
            #     self.player.creds += cost
                self.player.ship.speedLevelDown(-10)
        if event.key == pygame.K_k:                                # K - Speed level up
            # ~ cost = (self.player.ship.spd_lvl+1)
            # ~ if self.player.creds >= cost:
                # ~ self.player.creds -= cost
                self.player.ship.speedLevelUp(10)

        if event.key == pygame.K_u:                                # U - HP level up
            # cost = (self.player.ship.lhp+1) * 10
            # if self.player.creds >= cost:
            #     self.player.creds -= cost
                self.player.ship.levelUpHP(10)
        if event.key == pygame.K_i:                                # I - SP level up
            # cost = (self.player.ship.lsp+1) * 10
            # if self.player.creds >= cost:
            #     self.player.creds -= cost
                if not self.player.ship.shield_unlocked:
                    self.player.ship.shield_unlocked = True
                self.player.ship.levelUpSP(10)

        if event.key == pygame.K_h:                                # H - Dmg level up
            # cost = (self.player.ship.weapon.lvl+1)
            # if self.player.creds >= cost:
            #     self.player.creds -= cost
                self.player.ship.weapon.levelUpDmg(50)

        if event.key == pygame.K_l:                                # L - receive 100 Dmg
            self.player.ship.recvDamage(100, pct_sp=1, mult=1)

    def detectEvents(self):
        con = True
        for event in pygame.event.get():
            if event.type == pygame.TEXTINPUT:
                # Control de input del chat --------------------
                if self.chat.chat_text_active:
                    self.chat.chat_text += event.text

            if event.type == pygame.QUIT:
                self.settings.run = False

                #-----------------------------------------------------------
                if con: continue

            if event.type == VIDEORESIZE:
                temp_res = self.settings.RESOLUTION

                # Cambio de resolución -------------------------------------
                self.settings.videoResize(event)

                # Control del movimimiento del minimapa --------------------
                self.minimap.onResizeScreen(temp_res)

                #-------------------------------------
                if con: continue

            if event.type == pygame.KEYDOWN:
                self.keysDown(event)

                #-------------------------------------
                if con: continue

            if event.type == pygame.MOUSEMOTION:
                # Control del movimimiento del minimapa --------------------
                self.minimap.mouseMotion(event)

                # Control del movimimiento del chat ------------------------
                self.chat.mouseMotion(event)

                #-------------------------------------
                if con: continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.settings.open_menu:
                    # Control de seleccion del enemigo ---------------------
                    if not self.chat.chat_text_active:
                        players = self.selectEnemy(event)
                        if players: self.updateOtherPlayers(players)

                    # Control del movimimiento del minimapa ----------------
                    self.minimap.mouseButtonDown(event)

                    # Control del movimimiento del chat --------------------
                    self.chat.mouseButtonDown(event)

                    # Control del tamaño del minimapa ----------------------
                    self.minimap.resize(event)

                    # Control de seguimiento en el minimapa ----------------
                    if not self.minimap.map_resize:
                        self.minimap.setFollowPos(event)

                    # Control de input del chat ----------------------------
                    self.chat.activeInput(event)

                    #-------------------------------------------------------
                    if self.minimap.map_resize: self.minimap.map_resize = False

                #-------------------------------------
                if con: continue

            if event.type == pygame.MOUSEBUTTONUP:
                # Control del movimimiento del minimapa --------------------
                self.minimap.mouseButtonUp()

                # Control del movimimiento del chat ------------------------
                self.chat.mouseButtonUp()

                #-------------------------------------
                if con: continue

            if event.type == pygame.WINDOWLEAVE:
                # Control del movimimiento del minimapa --------------------
                self.minimap.windowLeave()

                #-------------------------------------
                if con: continue

    def movements(self, delta_time: float):
            # Control de input del chat --------------
            if self.chat.chat_text_active: return
            #-----------------------------------------

            keys = pygame.key.get_pressed()
            speed = self.player.ship.speed

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
                    x -= self.utils.diagonal(speed)['x']
                else:
                    degrees = 180
                    x -= speed

            if rightMove and not leftMove:
                movements = True
                if not upDownMove and (upMove or downMove):
                    if   upMove:   degrees = 90
                    elif downMove: degrees = 270
                    x += self.utils.diagonal(speed)['x']
                else:
                    degrees = 0
                    x += speed

            if upMove and not downMove:
                movements = True
                if not leftRightMove and (leftMove or rightMove):
                    if leftMove:  degrees += 45
                    if rightMove: degrees -= 45
                    y -= self.utils.diagonal(speed)['y']
                else:
                    degrees = 90
                    y -= speed

            if downMove and not upMove:
                movements = True
                if not leftRightMove and (leftMove or rightMove):
                    if leftMove:  degrees -= 45
                    if rightMove: degrees += 45
                    y += self.utils.diagonal(speed)['y']
                else:
                    degrees = 270
                    y += speed

            if movements:
                # Control de seguimiento en el minimapa --------------------
                if self.player.follow_pos: self.player.cancelFollowPos()
                #-----------------------------------------------------------

                self.player.ship.time_hp_init = 0
                self.player.angle = degrees
                self.player.rotate(degrees)
                self.player.x += round(x * delta_time, 2)
                self.player.y += round(y * delta_time, 2)
            else:
                # Recibir HP bajo sus reglas -------------------------------
                self.player.ship.healHP()

                # Control de seguimiento en el minimapa --------------------
                self.player.followPos(speed)
                #-----------------------------------------------------------

            # Recibir SP bajo sus reglas:
            self.player.ship.healSP()

    def selectEnemy(self, event):
        if event.button == 1:
            desX = (int(self.settings.CENTER['x'])-int(self.player.x))    # Desplazamiento en X
            desY = (int(self.settings.CENTER['y'])-int(self.player.y))    # Desplazamiento en Y

            posX, posY = event.pos
            dists = []
            for other_player_id in self.enemies:

                if other_player_id == self.player.id: continue

                other_player = self.enemies[other_player_id]
                if other_player.ship.chp == 0: continue

                pposX = other_player.x+desX
                pposY = other_player.y+desY

                dist = self.utils.euclideanDistance((posX, posY), (pposX,pposY))

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
                if not min_dist_id == self.player.selected['id']:
                    self.player.attacking = False
                    self.player.selected['name'] = min_dist_name
                    self.player.selected['id']   = min_dist_id
                    data = data_f.format(min_dist_name, min_dist_id)
            elif dists:
                if not dists[0][2] == self.player.selected['id']:
                    self.player.attacking = False
                    self.player.selected['name'] = dists[0][1]
                    self.player.selected['id']   = dists[0][2]
                    data = data_f.format(dists[0][1], dists[0][2])

            if data:
                players = self.server.send(data)
                return players

        if event.button == 3:
            self.player.attacking = False
            if self.player.selected['id'] >= 0:
                self.player.selected['name'] = ''
                self.player.selected['id']   = -1
                self.player.selected['dist'] = -1
                data = 'selected:{"name":"","id":-1}'
                players = self.server.send(data)
                return players

    def updateOtherPlayers(self, players: dict):
        # Update enemies
        ids_removed = []
        for id_ in self.enemies:
            if self.enemies[id_].__class__.__name__ == 'Player':
                if id_ in players:
                    self.enemies[id_].updateData(players)
                else:
                    ids_removed.append(id_)

        # Remove expired IDs
        for id_ in ids_removed: del self.enemies[id_]

        # Add new enemies
        for id_ in players:
            if id_ == self.player.id: continue
            if not id_ in self.enemies:
                from .entities.entities import Player
                name = players[id_]['name']
                other_player = Player(self.settings, name, id_)
                other_player.loadData(players)
                self.enemies[id_] = other_player
