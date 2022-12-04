import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *
from functools import cached_property
import math
import time


class Weapon:
    
    def __init__(self, settings, name):
        self.name = name
        self.path = settings.WEAPON[name]
        self.dmg  = settings.WEAPON[name]['dmg']
        self.inc  = settings.WEAPON[name]['inc']
        self.dist = settings.WEAPON[name]['dist']
        self.pct_sp = settings.WEAPON[name]['pct_sp']
        self.mult = settings.WEAPON[name]['mult']
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
    
    def __init__(self, settings, name, type_='Human'):
        self.settings = settings
        self.name = name
        self.type = type_
        if self.type == 'Human':
            self.base = settings.SHIP[name]
            self.weapon = Weapon(self.settings, self.base['weapon'])
        else:
            self.base = settings.STRANGERS[name]
            self.weapon = Weapon(self.settings, self.base['wpn_name'])
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
        add = init * (self.spd_lvl/(self.settings.MAX_SPD_LVL))
        speed += val+add
        return int(speed)
    
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
                'dmg':     0,		# Damage caused by the player.
                'pct_sp': .7,		# Damage distributed in percentage of SP and HP.
                'mult':    1,		# Damage multiplier.
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
        rect = img.get_rect()			#	width		height
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
                # ~ self.ship_path = self.settings.STRANGERS[self.ship_name]['path']
                self.ship_path = player['ship']['path']
            self.ship = Ship(self.settings, self.ship_name)
        
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
            # ~ self.ship.weapon = Weapon(player['ship']['weapon']['name'], settings)
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
