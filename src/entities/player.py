import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *
from functools import cached_property
from .weapon import Weapon
from .ship import Ship


class Player:
    def __init__(self, settings, utils, name=None, id_=None):
        self.settings = settings
        self.utils = utils

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
        data_f +=     '"spd_level":{},'
        data_f +=     '"weapon":{{'
        data_f +=       '"name":"{}",'
        data_f +=       '"level":{}'
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
            self.ship.spd_level,
            self.ship.weapon.name,
            self.ship.weapon.level,
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

    def rotate(self, angle: int | float):
        img = self.img_orig
        self.img = pygame.transform.rotate(img, angle)

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
            self.ship = Ship(self.settings, self.utils, self.ship_name)
        else:
            self.ship_path = player['ship']['path']
            self.ship = Ship(self.settings, self.utils, self.ship_name, 'Stranger')

        self.ship.level = player['ship']['level']
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
        self.ship.spd_level = player['ship']['spd_level']

        self.ship.weapon = Weapon(self.settings, self.utils, player['ship']['weapon']['name'])
        self.ship.weapon.levelUpDmg(player['ship']['weapon']['level'])

        self.img_orig = self.utils.loadImage(self.ship_path)
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
            self.ship = Ship(self.settings, self.utils, self.ship_name)

        # if not player['ship']['hp'] == self.ship.hp:
        #     self.ship.hp = player['ship']['hp']
        # if not player['ship']['sp'] == self.ship.sp:
        #     self.ship.sp = player['ship']['sp']

        if not self.ship.level == player['ship']['level']: self.ship.level = player['ship']['level']

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

        if not self.ship.destroyed == player['ship']['dtry']:      self.ship.destroyed = player['ship']['dtry']
        if not self.ship.spd_level == player['ship']['spd_level']: self.ship.spd_level = player['ship']['spd_level']

        # if not self.ship.weapon == player['ship']['weapon']['name']:
        #     self.ship.weapon = Weapon(self.settings, self.utils, player['ship']['weapon']['name'], settings)
        #     self.ship.weapon.levelUpDmg(player['ship']['weapon']['level'])
        # else:
        #     if not self.ship.weapon.level == player['ship']['weapon']['level']:
        #         level = self.ship.weapon.level - player['ship']['weapon']['level']
        #         self.ship.weapon.levelUpDmg(level)

    def followPos(self, speed: int, delta_time: float):
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
                self.rotate(self.angle)

            dist_px = int(self.settings.utils.euclideanDistance((x,y),(gpx,gpy)))

            speed_x = speed_y = 0

            if dist_px > 5:
                if x > gpx and y < gpy:
                    speed_x -= mov_speed['x']
                    speed_y += mov_speed['y']
                elif x < gpx and y < gpy:
                    speed_x += mov_speed['x']
                    speed_y += mov_speed['y']
                elif x < gpx and y > gpy:
                    speed_x += mov_speed['x']
                    speed_y -= mov_speed['y']
                elif x > gpx and y > gpy:
                    speed_x -= mov_speed['x']
                    speed_y -= mov_speed['y']
                elif x > gpx and y == gpy:
                    speed_x -= speed
                elif x < gpx and y == gpy:
                    speed_x += speed
                elif y > gpy and x == gpx:
                    speed_y -= speed
                elif y < gpy and x == gpx:
                    speed_y += speed

                self.x += round(speed_x * delta_time, 2)
                self.y += round(speed_y * delta_time, 2)
            else:
                self.cancelFollowPos()

    def cancelFollowPos(self):
        self.follow_pos = False
        self.follow_pos_move = False
        self.follow_pos_xy = (0,0)

