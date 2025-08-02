from .weapon import Weapon
import math
import time


class Ship:
    def __init__(self, settings, utils, name: str, type: str = 'Human'):
        self.settings = settings
        self.utils = utils
        self.name = name
        self.type = type
        if self.type == 'Human':
            self.base = self.settings.SHIP[name]
            self.weapon = Weapon(self.settings, self.utils, self.base['weapon'])
        else:
            self.base = self.settings.STRANGERS[name]
            self.weapon = Weapon(self.settings, self.utils, self.base['wpn_name'])
        self.destroyed = False
        self.spd_level = self.base['spd_level']
        self.level = self.base['level']

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
        # el nivel x=112 y=150, todo basado en: y=sqrt(max_level*current_level)
        init = 10
        speed = self.base['speed']                                      # Velocidad base de la nave
        #val = math.sqrt(200*(self.spd_level+1)-100)-init                 # Aumento de velocidad en forma de parabola, basado en: y = sqrt(200x+100)
        val = 1.25*self.spd_level + (math.sqrt(100*self.spd_level)*.25)     # Generador de niveles en: y = 1.25x + sqrt(100x)*0.25 donde x=100 -> y=150
        add = init * (self.spd_level/(self.settings.MAX_SPD_LVL))
        speed += add + val
        return int(speed)

    def getPctResDmgRad(self):              # Control del nivel de radiacion
        if self.level >= 28:
            if self.level//100 > 1:
                return 1
            else:
                return self.level//100
        else:
            return 1

    def speedLevelUp(self, level: int = 1):
        if self.spd_level+level <= self.settings.MAX_SPD_LVL:
            self.spd_level += level
        else:
            self.spd_level = self.settings.MAX_SPD_LVL

    def speedLevelDown(self, level: int = -1):
        if self.spd_level+level >= 0:
            self.spd_level += level
        else:
            self.spd_level = 0

    def levelUpHP(self, level: int = 1):             # Incrementa de nivel el HP
        inc = self.base['hp'] * level
        self.hp += inc
        self.chp += inc
        self.lhp += level

    def levelUpSP(self, level: int = 1):             # Incrementa de nivel el SP
        if self.shield_unlocked:
            inc = self.base['sp'] * level
            self.sp += inc
            self.csp += inc
            self.lsp += level

    # Registra el daño recibido para mostrarlo
    def recvDamage(self, damage: int, pct_sp: int = None, mult: float = 1.0, draw: bool = True):
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

    def healHP(self, pct: int = 10, sec_init: int = 6, sec: int = 3):
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

    def healSP(self, pct: int = 5, sec_init: int = 10, sec: int = 1):
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
