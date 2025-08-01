import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *
from .repositories import Cache
import binascii
import math
import time
import bz2


class Utils:
    cache = Cache()

    def __init__(self):
        self.init_time = time.perf_counter()
        self.bz2 = Bz2()

    def perSecond(self, t: int = 1) -> bool:
        if time.perf_counter() - self.init_time >= t:
            self.init_time = time.perf_counter()
            return True
        return False

    def cos(self, deg: int = 45) -> float:
        rad = math.radians(deg)
        return math.cos(rad)

    def sin(self, deg: int = 45) -> float:
        rad = math.radians(deg)
        return math.sin(rad)

    @cache.cache
    def diagonal(self, speed: int | float, deg: int = 45, rounded: bool | int = False) -> dict:
        inv = True if deg//90 in [1,-1,3,-3] else False 
        deg = deg % 90

        if inv:
            y = speed * self.cos(deg)
            x = speed * self.sin(deg)
        else:
            x = speed * self.cos(deg)
            y = speed * self.sin(deg)

        if rounded:
            if str(rounded).isnumeric():
                return {'x': round(x, rounded), 'y': round(y, rounded)}
            else:
                return {'x': round(x, 4), 'y': round(y, 4)}
        else:
            return {'x': x, 'y': y}

    def euclideanDistance(self, A: int, B: int) -> int:
        ''' Formula: d(A,B) = sqrt( (Xb-Xa)^2 + (Yb-Ya)^2 )
        Donde: A=(Xa,Ya), B=(Xb,Yb)
        '''
        Xa, Ya = A
        Xb, Yb = B
        X = (Xb-Xa)**2
        Y = (Yb-Ya)**2
        d = math.sqrt(X+Y)
        return d

    def getAngle(self, A: int, B: int) -> int:
        ''' Donde: A=(Xa,Ya), B=(Xb,Yb) '''
        Xa, Ya = A
        Xb, Yb = B
        X = (Xb-Xa)
        Y = (Yb-Ya)
        atan2 = math.atan2(Y, X)
        angle = math.degrees(atan2)
        return round(angle)

    @cache.cache
    def convertTime(self, t: str | int) -> str:
        if type(t) == str: return t
        if int(t) < 60: return str(t) + 's'
        else:
            minutes = str(t // 60)
            seconds = str(t % 60)
            if int(seconds) < 10:
                seconds = '0' + seconds
            return minutes + ':' + seconds

    def roundRect(self, rect: pygame.Rect, color: tuple, rad: int = 20, border: int = 0, inside: tuple = (0,0,0,0)) -> tuple[pygame.Surface, pygame.Rect]:
        rect = pygame.Rect(rect)
        zeroed_rect = rect.copy()
        zeroed_rect.topleft = 0,0
        image = pygame.Surface(rect.size).convert_alpha()
        image.fill((0,0,0,0))
        self._renderRegion(image, zeroed_rect, color, rad)
        if border:
            zeroed_rect.inflate_ip(-2*border, -2*border)
            self._renderRegion(image, zeroed_rect, inside, rad)
        return (image, rect)

    def _renderRegion(self, image: pygame.Surface, rect: pygame.Rect, color: tuple, rad: int):
        corners = rect.inflate(-2*rad, -2*rad)
        for attribute in ('topleft', 'topright', 'bottomleft', 'bottomright'):
            pygame.draw.circle(image, color, getattr(corners,attribute), rad)
        image.fill(color, rect.inflate(-2*rad,0))
        image.fill(color, rect.inflate(0,-2*rad))

    def moveWindow(self, win_x: int, win_y: int, win_w: int, win_h: int):
        from ctypes import windll
        # NOSIZE = 1
        # NOMOVE = 2
        # TOPMOST = -1
        # NOT_TOPMOST = -2
        # windll.user32.SetWindowPos(hwnd, NOT_TOPMOST, 0, 0, 0, 0, NOMOVE|NOSIZE)
        # w, h = pygame.display.get_surface().get_size()
        hwnd = pygame.display.get_wm_info()['window']
        windll.user32.MoveWindow(hwnd, win_x, win_y, win_w, win_h, False)

    def splitText(self, text: str, chunk_size: int = 32) -> list:
        output = []
        chunks  = len(text)//chunk_size
        chunks += 1 if len(text)%chunk_size > 0 else 1

        while text:
            p = chunk_size
            br = 1

            try:
                while not text[p] == ' ':
                    p -= 1
                    if p == 0:
                        br = 0
                        p = chunk_size
                        break
            except: pass

            chunk = text[:p]
            text = text[p+br:]
            output.append(chunk)

        return output

    def colorMask(self, surf: pygame.Surface, color: tuple, color_to_replace: tuple = (255,255,255)):
        ''' pygame.transform.threshold(
            mask_image, img, color_to_replace,
            (0,0,0,0), color, 1, None, True)
        '''
        pygame.transform.threshold(
            surf, surf, color_to_replace,
            (0,0,0,0), color, 1, None, True
        )

    def perfectOutline(self, WIN: pygame.Surface, img: pygame.Surface, loc: tuple, color: tuple = (0,0,0), alpha: int = 255, br: int = 1):
        mask = pygame.mask.from_surface(img)
        mask_surf = mask.to_surface()

        # Remplaza el color en la imagen y agrega transparencia (alpha: 0~255)
        self.colorMask(mask_surf, (*color, alpha))

        # Agrega la transparencia de la imagen
        mask_surf.set_colorkey((0,0,0))

        WIN.blit(mask_surf, (loc[0]-br, loc[1]))
        WIN.blit(mask_surf, (loc[0]+br, loc[1]))
        WIN.blit(mask_surf, (loc[0], loc[1]-br))
        WIN.blit(mask_surf, (loc[0], loc[1]+br))

        WIN.blit(mask_surf, (loc[0]-br, loc[1]-br))
        WIN.blit(mask_surf, (loc[0]+br, loc[1]+br))
        WIN.blit(mask_surf, (loc[0]-br, loc[1]+br))
        WIN.blit(mask_surf, (loc[0]+br, loc[1]-br))

    @property
    def curWinRect(self):
        from ctypes import POINTER, WINFUNCTYPE, windll
        from ctypes.wintypes import BOOL, HWND, RECT

        hwnd = pygame.display.get_wm_info()['window']
        prototype = WINFUNCTYPE(BOOL, HWND, POINTER(RECT))
        paramflags = (1, 'hwnd'), (2, 'lprect')
        GetWindowRect = prototype(('GetWindowRect', windll.user32), paramflags)
        rect = GetWindowRect(hwnd)
        return [rect.left, rect.top, rect.right, rect.bottom]

    @property
    def curWinSize(self):
        info = pygame.display.Info()
        return [info.current_w, info.current_h]


class Bz2:
    cache = Cache('Bz2')

    def hexlify(self, text):
        return binascii.hexlify(text)

    @cache.cache
    def compress(self, text):
        compress = bz2.compress(text)
        return compress

    @cache.cache
    def decompress(self, text):
        decompress = bz2.decompress(text).decode()
        return decompress

    @cache.cache
    def compressHexlify(self, text):
        compress = bz2.compress(text.encode())
        return self.hexlify(compress)
