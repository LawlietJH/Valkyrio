from .weapon import Weapon
from .ship import Ship
import random
import json
import time


class Stranger:
    def __init__(self, settings, utils, name: str, id: int):
        self.settings = settings
        self.utils = utils

        self.name = name
        self.ship = None
        self.ship_name = None

        self.creds = 0
        self.exp = 0
        self.id = id
        self.x = 0
        self.y = 0

        self.delta_t_init = time.perf_counter()
        self.t_init_move = 0
        self.t_wait_move = 0
        self.primary_atk = None     # Primary attacker
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
                'dmg':     0,       # Damage caused by the player.
                'pct_sp': .7,       # Damage distributed in percentage of SP and HP.
                'mult':    1,       # Damage multiplier.
                'time':    0
            }
        }

        self.curr_pos = (
            int(self.x/self.settings.posdiv),
            int(self.y/self.settings.posdiv)
        )

    def setData(self, players: dict):
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

        # print(data)

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

        players[self.id]['dmginfo'] = {}

        return data

    def loadData(self, players: dict):
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

        self.ship = Ship(self.settings, self.utils, self.ship_name, 'Stranger')

        self.ship.level = stranger['ship']['level']
        self.ship.base_hp = self.ship.hp = stranger['ship']['bhp']
        self.ship.base_sp = self.ship.sp = stranger['ship']['bsp']
        self.ship.levelUpHP(stranger['ship']['lhp'])
        self.ship.shield_unlocked = stranger['ship']['s_unlkd']
        self.ship.levelUpSP(stranger['ship']['lhp'])

        # if not stranger['ship']['chp'] == 0 and stranger['ship']['chp'] <= self.ship.lhp:
        #     self.ship.chp = stranger['ship']['chp']
        # else:
        #     self.ship.chp = self.ship.hp

        # if not stranger['ship']['csp'] == 0 \
        # and stranger['ship']['csp'] <= self.ship.lsp:
        #     self.ship.csp = stranger['ship']['csp']
        # else:
        #     self.ship.csp = self.ship.sp

        self.ship.destroyed = stranger['ship']['dtry']
        self.ship.base_speed = stranger['ship']['base_speed']
        self.ship.spd_level = stranger['ship']['spd_level']

        self.ship.weapon = Weapon(self.settings, self.utils, stranger['ship']['weapon']['name'])
        self.ship.weapon.levelUpDmg(stranger['ship']['weapon']['level'])

    def radioactiveZone(self):
        if (self.x < 0 or self.settings.map_limits['x'] < self.x)\
        or (self.y < 0 or self.settings.map_limits['y'] < self.y):
            if self.ship.timeOnBorder == 0:
                self.ship.timeOnBorder = time.perf_counter()
            if time.perf_counter() - self.ship.timeOnBorder > 2:
                self.ship.timeOnBorder = time.perf_counter()
                self.ship.recvDamage(self.settings.rad_dmg*(1-self.ship.pct_res_dmg_rad), pct_sp=0)
        else:
            if self.ship.timeOnBorder > 0:
                self.ship.timeOnBorder = 0

    def chkDmgRecv(self, players: dict):
        for enemy_id, values in players[self.id]['dmginfo'].items():
            for dmg, pct_sp, mult, t in values:
                self.ship.recvDamage(dmg, pct_sp, mult)

            if (self.primary_atk == None and enemy_id in players) \
            or (not self.primary_atk == None and not self.primary_atk in players):
                self.primary_atk = enemy_id

    def deltaTime(self, FPS: int, mili: bool = True):
        delta = time.perf_counter() - self.delta_t_init
        self.delta_t_init = time.perf_counter()

        if mili: delta = int(delta * 1000)

        time.sleep(1/FPS)

        return delta

    def setAttack(self, players: dict, game_time: int):
        # Draw Laser and damage on enemies:
        # print(self.selected['id'])
        if self.selected['id'] >= 0 and self.attacking:
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

    def lookAtPlayer(self, p_id: str, data: dict):
        # Gira hacia el enemigo
        if not p_id == self.selected['id'] and self.selected['id'] >= 0:
            return

        desX = (int(self.settings.CENTER['x'])-int(self.x))     # Desplazamiento en X
        desY = (int(self.settings.CENTER['y'])-int(self.y))     # Desplazamiento en Y

        selected_pos = data['x']+desX, data['y']+desY
        pposX, pposY = int(self.settings.CENTER['x']), int(self.settings.CENTER['y'])

        dist = round(self.settings.utils.euclideanDistance((pposX,pposY), selected_pos), 2)

        if self.primary_atk:
            self.selected['name'] = data['name']
            self.selected['id']   = p_id
            self.selected['dist'] = dist
            self.attacking = True

        if dist < self.ship.base['min_dist']:
            self.angle = -round(self.settings.utils.getAngle((pposX,pposY), selected_pos), 2)
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

    def moveOnMap(self, speed: int):
        limitX = self.settings.MAP[self.settings.map_name]['x']
        limitY = self.settings.MAP[self.settings.map_name]['y']
        x = int(self.x/self.settings.posdiv)
        y = int(self.y/self.settings.posdiv)
        degrees = speedX = speedY = 0

        if self.wait:
            if time.perf_counter() - self.t_init_move >= self.t_wait_move:
                self.wait = False
        else:
            if  10 < x < limitX-10 and 10 < y < limitY-10:
                if self.dir in ['ru','ur']:
                    degrees = 0+45
                    mov_speed = self.settings.utils.diagonal(speed, degrees)
                    speedX += mov_speed['x']
                    speedY -= mov_speed['y']
                elif self.dir in ['lu','ul']:
                    degrees = 90+45
                    mov_speed = self.settings.utils.diagonal(speed, degrees)
                    speedX -= mov_speed['y']
                    speedY -= mov_speed['x']
                elif self.dir in ['ld','dl']:
                    degrees = 180+45
                    mov_speed = self.settings.utils.diagonal(speed, degrees)
                    speedX -= mov_speed['x']
                    speedY += mov_speed['y']
                elif self.dir in ['rd','dr']:
                    degrees = 270+45
                    mov_speed = self.settings.utils.diagonal(speed, degrees)
                    speedX += mov_speed['y']
                    speedY += mov_speed['x']
                elif 'r' in self.dir:
                    degrees = 0
                    speedX += speed
                elif 'u' in self.dir:
                    degrees = 90
                    speedY -= speed
                elif 'l' in self.dir:
                    degrees = 180
                    speedX -= speed
                elif 'd' in self.dir:
                    degrees = 270
                    speedY += speed

                self.angle = degrees

                if random.random() < .001:
                    self.dir = random.choice(['r','u','l','d','ru','ul','ld','dr'])
                    self.wait = True
                    self.t_wait_move = random.randint(1,5)
                    self.t_init_move = time.perf_counter()
            else:
                # self.wait = True
                # self.t_wait_move = random.randint(1,3)
                # self.t_init_move = time.perf_counter()

                if x <= 10:
                    speedX += speed
                    self.dir = random.choice(['r','ru','rd'])
                elif x >= limitX-10:
                    speedX -= speed
                    self.dir = random.choice(['l','lu','ld'])
                elif y <= 10:
                    speedY += speed
                    self.dir = random.choice(['d','dl','dr'])
                elif y >= limitY-10:
                    speedY -= speed
                    self.dir = random.choice(['u','ul','ur'])

            self.x += speedX
            self.y += speedY

    def followAndAttack(self, speed: int, enemy: dict):
        x = int(self.x/self.settings.posdiv)
        y = int(self.y/self.settings.posdiv)
        ex = int(enemy['x']/self.settings.posdiv)
        ey = int(enemy['y']/self.settings.posdiv)
        positions = ((self.x,self.y),(enemy['x'],enemy['y']))

        self.angle = -self.settings.utils.getAngle(*positions)
        dist_px = int(self.settings.utils.euclideanDistance(*positions))

        mov_speed = self.settings.utils.diagonal(speed, self.angle)

        speedX = speedY = 0

        if dist_px >= 200:
            if x > ex and y < ey:
                speedX -= mov_speed['x']
                speedY += mov_speed['y']
            elif x < ex and y < ey:
                speedX += mov_speed['x']
                speedY += mov_speed['y']
            elif x < ex and y > ey:
                speedX += mov_speed['x']
                speedY -= mov_speed['y']
            elif x > ex and y > ey:
                speedX -= mov_speed['x']
                speedY -= mov_speed['y']
            elif x > ex and y == ey:
                speedX -= speed
            elif x < ex and y == ey:
                speedX += speed
            elif y > ey and x == ex:
                speedY -= speed
            elif y < ey and x == ex:
                speedY += speed

            self.x += speedX
            self.y += speedY

    def randomMove(self, players: dict, game_time: int, server_fps: int):
        speed = round(self.ship.speed / server_fps, 2)

        if not self.dir:
            self.wait = False
            self.dir = random.choice(['r','u','l','d','ru','ul','ld','dr'])

        # print(players)
        try:
            for p_id, data in players.items():
                if data['type'] == 'Human':
                    self.lookAtPlayer(p_id, data)
        except Exception as e:
            print(players, p_id, data)
            print('Error', e)

        if self.selected['id'] >= 0:
            self.setAttack(players, game_time)

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
