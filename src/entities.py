import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *
from functools import cached_property
import random
import json
import math
import time


class Weapon:
    def __init__(self, settings, name) -> None:
        self.name = name
        self.path = settings.WEAPON[name]
        self.dmg  = settings.WEAPON[name]['dmg']
        self.inc  = settings.WEAPON[name]['inc']
        self.dist = settings.WEAPON[name]['dist']
        self.pct_sp = settings.WEAPON[name]['pct_sp']
        self.mult = settings.WEAPON[name]['mult']
        self.lvl  = 0
        self.init_time = 0

    def levelUpDmg(self, lvl=1) -> None:
        self.lvl += lvl
        self.dmg += lvl*self.inc

    def perSecond(self, t=1) -> bool:
        if time.perf_counter() - self.init_time >= t:
            self.init_time = time.perf_counter()
            return True
        return False


class Ship:
    def __init__(self, settings, name, type_='Human'):
        self.settings = settings
        self.name = name
        self.type = type_
        if self.type == 'Human':
            self.base = self.settings.SHIP[name]
            self.weapon = Weapon(self.settings, self.base['weapon'])
        else:
            self.base = self.settings.STRANGERS[name]
            self.weapon = Weapon(self.settings, self.base['wpn_name'])
        self.destroyed = False
        self.spd_lvl = self.base['spd_lvl']
        self.lvl = self.base['lvl']

        # Health
        self.hp  = 0                    # Health points
        self.chp = 0                    # Current Health Points
        self.lhp = 1                    # Level Health Points
        self.pct_hp = .3                # Health Damage Percentage
        self.heal_hp = False
        self.time_hp_init = 0           # Time Counter to heal HP

        # Shield
        self.shield_unlocked = False
        self.sp  = 0                    # Shield points
        self.csp = 0                    # Current Shield Points
        self.lsp = 0                    # Level Shield Points
        self.pct_sp = .7                # Shield Damage Percentage
        self.heal_sp = False
        self.time_sp_init = 0           # Time Counter to heal SP

        self.timeOnBorder = 0
        self.pct_res_dmg_rad = 0        # 0.0~1.0: Percentage of resistance to damage in the radiative zone
        # self.pct_res_dmg_rad = self.getPctResDmgRad()

        self.damageRecv = []
        self.healthRecv = []

    @property
    def speed(self):
        # Aumento de velocidad en forma exponencial y=sqrt(200x+100) tomando en cuenta que
        # el nivel x=112 y=150, todo basado en: y=sqrt(max_lvl*current_lvl)
        init = 10
        speed = self.base['speed']                                      # Velocidad base de la nave
        val = math.sqrt(200*(self.spd_lvl+1)-100)-init                  # Aumento de velocidad en forma de parabola, basado en: y = sqrt(200x+100)
        add = init * (self.spd_lvl/(self.settings.MAX_SPD_LVL))
        speed += val+add
        return int(speed)

    def getPctResDmgRad(self):      # Control del nivel de radiacion
        if self.lvl >= 28:
            if self.lvl//100 > 1:
                return 1
            else:
                return self.lvl//100
        else:
            return 1

    def speedLevelUp(self, lvl=1):
        if self.spd_lvl+lvl <= self.settings.MAX_SPD_LVL:
            self.spd_lvl += lvl
        else:
            self.spd_lvl = self.settings.MAX_SPD_LVL

    def speedLevelDown(self, lvl=-1):
        if self.spd_lvl+lvl >= 0:
            self.spd_lvl += lvl
        else:
            self.spd_lvl = 0

    def levelUpHP(self, lvl=1):                     # Incrementa de nivel el HP
        inc = self.base['hp'] * lvl
        self.hp += inc
        self.chp += inc
        self.lhp += lvl

    def levelUpSP(self, lvl=1):                     # Incrementa de nivel el SP
        if self.shield_unlocked:
            inc = self.base['sp'] * lvl
            self.sp += inc
            self.csp += inc
            self.lsp += lvl

    def recvDamage(self, damage, pct_sp=None, mult=1, draw=True):       # Registra el daño recibido para mostrarlo
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
    def __init__(self, settings, name=None, id_=None):
        self.settings = settings

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
        rect = img.get_rect()           # width       height
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
            self.ship_path = self.settings.SHIP[self.ship_name]['path']
            self.ship = Ship(self.settings, self.ship_name)
        else:
            self.ship_path = player['ship']['path']
            self.ship = Ship(self.settings, self.ship_name, 'Stranger')

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

        self.ship.weapon = Weapon(self.settings, player['ship']['weapon']['name'])
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
                self.ship_path = self.settings.SHIP[self.ship_name]['path']
            else:
                # self.ship_path = self.settings.STRANGERS[self.ship_name]['path']
                self.ship_path = player['ship']['path']
            self.ship = Ship(self.settings, self.ship_name)

        # if not player['ship']['hp'] == self.ship.hp:
        #     self.ship.hp = player['ship']['hp']
        # if not player['ship']['sp'] == self.ship.sp:
        #     self.ship.sp = player['ship']['sp']

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

        # if player['ship']['chp'] <= self.ship.chp:
        #     self.ship.chp = player['ship']['chp']
        # else:
        #     self.ship.chp = self.ship.hp

        # if player['ship']['csp'] <= self.ship.csp:
        #     self.ship.csp = player['ship']['csp']
        # else:
        #     self.ship.csp = self.ship.sp

        if not self.ship.chp == player['ship']['chp']: self.ship.chp = player['ship']['chp']
        if not self.ship.csp == player['ship']['csp']: self.ship.csp = player['ship']['csp']
        #---------------------------------------------------

        if not self.ship.destroyed == player['ship']['dtry']:    self.ship.destroyed = player['ship']['dtry']
        if not self.ship.spd_lvl   == player['ship']['spd_lvl']: self.ship.spd_lvl = player['ship']['spd_lvl']

        # if not self.ship.weapon == player['ship']['weapon']['name']:
        #     self.ship.weapon = Weapon(self.settings, player['ship']['weapon']['name'], settings)
        #     self.ship.weapon.levelUpDmg(player['ship']['weapon']['lvl'])
        # else:
        #     if not self.ship.weapon.lvl == player['ship']['weapon']['lvl']:
        #         lvl = self.ship.weapon.lvl - player['ship']['weapon']['lvl']
        #         self.ship.weapon.levelUpDmg(lvl)

    # TODO: Eliminar color negro absoluto (0,0,0) en diseño de naves.
    def loadImage(self, filename, transparent=True):
        print(filename)
        try: image = pygame.image.load(filename)
        except pygame.error as message: raise SystemError
        image = image.convert()
        # image = self.resize(image, 1.2)
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
                self.angle = -self.settings.utils.getAngle((x,y),(gpx,gpy))
                self.rotate(self.angle)
                self.follow_pos_move = True

            if self.selected['id'] >= 0:
                angle = -self.settings.utils.getAngle((x,y),(gpx,gpy))
                mov_speed = self.settings.utils.diagonal(speed, self.angle)
                if self.attacking:
                    mov_speed = self.settings.utils.diagonal(speed, angle)
                elif not int(angle) == int(self.angle):
                    self.angle = angle
                    self.rotate(self.angle)
            else:
                mov_speed = self.settings.utils.diagonal(speed, self.angle)

            dist_px = int(self.settings.utils.euclideanDistance((x,y),(gpx,gpy)))

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


class Stranger:
    def __init__(self, settings, name, id_):
        self.settings = settings

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

    def setData(self, players):
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
        self.ship = Ship(self.settings, self.ship_name, 'Stranger')

        self.ship.lvl = stranger['ship']['lvl']
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

        if not stranger['ship']['csp'] == 0 \
        and stranger['ship']['csp'] <= self.ship.lsp:
            self.ship.csp = stranger['ship']['csp']
        else:
            self.ship.csp = self.ship.sp

        self.ship.destroyed = stranger['ship']['dtry']
        self.ship.spd_lvl = stranger['ship']['spd_lvl']

        self.ship.weapon = Weapon(self.settings, stranger['ship']['weapon']['name'])
        self.ship.weapon.levelUpDmg(stranger['ship']['weapon']['lvl'])

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

    def chkDmgRecv(self, players):
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

    def setAttack(self, players, game_time):
        # Draw Laser and damage on enemies:
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

    def lookAtPlayer(self, p_id, data):
        # Gira hacia el enemigo
        if not p_id == self.selected['id']\
        and self.selected['id'] >= 0:
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

    def moveOnMap(self, speed):
        limitX = self.settings.MAP[self.settings.map_name]['x']
        limitY = self.settings.MAP[self.settings.map_name]['y']
        x = int(self.x/self.settings.posdiv)
        y = int(self.y/self.settings.posdiv)
        degrees = 0

        if self.wait:
            if time.perf_counter() - self.t_init_move >= self.t_wait_move:
                self.wait = False
        else:
            if  10 < x < limitX-10 and 10 < y < limitY-10:
                if self.dir in ['ru','ur']:
                    degrees = 0+45
                    mov_speed = self.settings.utils.diagonal(speed, degrees)
                    self.x += mov_speed['x']
                    self.y -= mov_speed['y']
                elif self.dir in ['lu','ul']:
                    degrees = 90+45
                    mov_speed = self.settings.utils.diagonal(speed, degrees)
                    self.x -= mov_speed['y']
                    self.y -= mov_speed['x']
                elif self.dir in ['ld','dl']:
                    degrees = 180+45
                    mov_speed = self.settings.utils.diagonal(speed, degrees)
                    self.x -= mov_speed['x']
                    self.y += mov_speed['y']
                elif self.dir in ['rd','dr']:
                    degrees = 270+45
                    mov_speed = self.settings.utils.diagonal(speed, degrees)
                    self.x += mov_speed['y']
                    self.y += mov_speed['x']
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
                # self.wait = True
                # self.t_wait_move = random.randint(1,3)
                # self.t_init_move = time.perf_counter()

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
        x = int(self.x/self.settings.posdiv)
        y = int(self.y/self.settings.posdiv)
        ex = int(enemy['x']/self.settings.posdiv)
        ey = int(enemy['y']/self.settings.posdiv)
        positions = ((self.x,self.y),(enemy['x'],enemy['y']))

        self.angle = -self.settings.utils.getAngle(*positions)
        dist_px = int(self.settings.utils.euclideanDistance(*positions))

        mov_speed = self.settings.utils.diagonal(speed, self.angle)

        if dist_px >= 200:
            if x > ex and y < ey:
                self.x -= mov_speed['x']
                self.y += mov_speed['y']
            elif x < ex and y < ey:
                self.x += mov_speed['x']
                self.y += mov_speed['y']
            elif x < ex and y > ey:
                self.x += mov_speed['x']
                self.y -= mov_speed['y']
            elif x > ex and y > ey:
                self.x -= mov_speed['x']
                self.y -= mov_speed['y']
            elif x > ex and y == ey:
                self.x -= speed
            elif x < ex and y == ey:
                self.x += speed
            elif y > ey and x == ex:
                self.y -= speed
            elif y < ey and x == ex:
                self.y += speed

    def randomMove(self, players, game_time, deltaTime):
        speed = self.ship.speed / 100
        # speed *= deltaTime

        if not self.dir:
            self.wait = False
            self.dir = random.choice(['r','u','l','d','ru','ul','ld','dr'])

        for p_id, data in players.items():
            if data['type'] == 'Human':
                self.lookAtPlayer(p_id, data)

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

