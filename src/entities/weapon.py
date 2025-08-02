from functools import cached_property
from ..settings import Settings
from ..utils import Utils
import math
import time


class Weapon:
    def __init__(self, settings: Settings, utils: Utils, name: str) -> None:
        self.utils = utils
        self.name = name
        self.weapon = settings.WEAPON[name]['weapon']
        self.dmg = settings.WEAPON[name]['dmg']
        self.inc = settings.WEAPON[name]['inc']
        self.dist = settings.WEAPON[name]['dist']
        self.pct_sp = settings.WEAPON[name]['pct_sp']
        self.mult = settings.WEAPON[name]['mult']
        self.level = 0
        self.init_time = 0
        self.MAX_LEVEL = 120
        self.img = None
        self.bullet_x = 0
        self.bullet_y = 0
        self.shoot = False

    @cached_property
    def image(self):
        self.img = self.utils.loadImage(self.weapon, antialiasing=True)
        return self.img

    def levelUpDmg(self, level: int = 1) -> None:
        self.level += level
        self.dmg += level*self.inc

    def perSecond(self, t: int = 1) -> bool:
        if not self.init_time:
            self.init_time = time.perf_counter()
        if time.perf_counter() - self.init_time >= t:
            self.init_time = time.perf_counter()
            return True
        return False

    def cost_multiplier(self):
        return round(math.sqrt(100*self.level+100)-10, 2)
