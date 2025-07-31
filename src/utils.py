import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *
import math
import time


class Utils:
    def __init__(self):
        self.init_time = time.perf_counter()

    def perSecond(self, t=1):
        if time.perf_counter() - self.init_time >= t:
            self.init_time = time.perf_counter()
            return True
        return False

    def cos(self, deg=45):
        rad = math.radians(deg)
        return math.cos(rad)

    def sin(self, deg=45):
        rad = math.radians(deg)
        return math.sin(rad)

    def diagonal(self, h, deg=45, rounded=True):
        inv = True if deg//90 in [1,-1,3,-3] else False 
        deg = deg % 90

        if inv:
            co = h * self.cos(deg)
            ca = h * self.sin(deg)
        else:
            ca = h * self.cos(deg)
            co = h * self.sin(deg)

        if rounded:
            if str(rounded).isnumeric():
                return {'x': round(ca, rounded), 'y': round(co, rounded)}
            else:
                return {'x': round(ca, 2), 'y': round(co, 2)}
        else:
            return {'x': ca, 'y': co}

    def euclideanDistance(self, A, B):
        ''' Formula: d(A,B) = sqrt( (Xb-Xa)^2 + (Yb-Ya)^2 )
        Donde: A=(Xa,Ya), B=(Xb,Yb)
        '''
        Xa, Ya = A
        Xb, Yb = B
        X = (Xb-Xa)**2
        Y = (Yb-Ya)**2
        d = math.sqrt(X+Y)
        return d

    def getAngle(self, A, B):
        ''' Donde: A=(Xa,Ya), B=(Xb,Yb) '''
        Xa, Ya = A
        Xb, Yb = B
        X = (Xb-Xa)
        Y = (Yb-Ya)
        atan2 = math.atan2(Y, X)
        angle = math.degrees(atan2)
        return angle

    def convertTime(self, t):
        if type(t) == str: return t
        if int(t) < 60: return str(t) + 's'
        else:
            minutes = str(t // 60)
            seconds = str(t % 60)
            if int(seconds) < 10:
                seconds = '0' + seconds
            return minutes + ':' + seconds

    def roundRect(self, rect, color, rad=20, border=0, inside=(0,0,0,0)):
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

    def _renderRegion(self, image, rect, color, rad):
        corners = rect.inflate(-2*rad, -2*rad)
        for attribute in ('topleft', 'topright', 'bottomleft', 'bottomright'):
            pygame.draw.circle(image, color, getattr(corners,attribute), rad)
        image.fill(color, rect.inflate(-2*rad,0))
        image.fill(color, rect.inflate(0,-2*rad))

    def moveWindow(self, win_x, win_y, win_w, win_h):
        from ctypes import windll
        # NOSIZE = 1
        # NOMOVE = 2
        # TOPMOST = -1
        # NOT_TOPMOST = -2
        # windll.user32.SetWindowPos(hwnd, NOT_TOPMOST, 0, 0, 0, 0, NOMOVE|NOSIZE)
        # w, h = pygame.display.get_surface().get_size()
        hwnd = pygame.display.get_wm_info()['window']
        windll.user32.MoveWindow(hwnd, win_x, win_y, win_w, win_h, False)

    def splitText(self, text, chunk_size=32):
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

    def colorMask(self, surf, color, color_to_replace=(255,255,255)):
        ''' pygame.transform.threshold(
            mask_image, img, color_to_replace,
            (0,0,0,0), color, 1, None, True)
        '''
        pygame.transform.threshold(
            surf, surf, color_to_replace,
            (0,0,0,0), color, 1, None, True
        )

    def perfectOutline(self, WIN, img, loc, color=(0,0,0), alpha=255, br=1):
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
