import math
import time


class Weapon:
    def __init__(self, settings, name) -> None:
        self.name = name
        self.path = settings.WEAPON[name]
        self.dmg = settings.WEAPON[name]['dmg']
        self.inc = settings.WEAPON[name]['inc']
        self.dist = settings.WEAPON[name]['dist']
        self.pct_sp = settings.WEAPON[name]['pct_sp']
        self.mult = settings.WEAPON[name]['mult']
        self.level = 0
        self.init_time = 0
        self.MAX_LEVEL = 120

    def levelUpDmg(self, level: int = 1) -> None:
        self.level += level
        self.dmg += level*self.inc

    def perSecond(self, t: int = 1) -> bool:
        if time.perf_counter() - self.init_time >= t:
            self.init_time = time.perf_counter()
            return True
        return False

    def cost_multiplier(self):
        return round(math.sqrt(100*self.level+100)-10, 2)
