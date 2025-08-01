import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *
import time
import os


class Settings:
    def __init__(self, utils, RESOLUTION=(1280, 720), is_client=True):
        self.utils = utils

        # Cons: --------------------------------------------------------

        self.specs = ''

        self.COLOR = { # https://htmlcolorcodes.com/es/
            'Negro':        (  0,  0,  0),
            'Blanco':       (255,255,255),
            'Azul Galaxia': ( 26, 59, 85),
            'Background':   ( 15, 35, 50),
            'Linea Bg':     ( 26, 90, 85),
            'Azul Celeste': ( 34,113,179),
            'Azul Noche':   ( 25, 28, 50),
            'Rojo':         (255,  0,  0),
            'Rojo Opaco':   (127,  0,  0),
            'Verde':        (  0,255,  0),
            'Azul':         (  0,  0,255),
            'Cyan':         (  0,180,200),
            'Cyan Opaco':   (  0,130,140),
            'Verde Claro':  (  0,210,  0),
            'Verde Opaco':  (  0,150,  0),

            'HP':           (  0,210,  0),      # HP
            'HP Opaco':     (  0,150,  0),      # HP 0
            'SP':           (  0,180,200),      # SP
            'SP Opaco':     (  0,130,140),      # SP 0

            'Verde S':      ( 24, 25, 30),
            'Verde N':      (  0, 50, 30),
            'Verde C':      (  0, 75, 30),
            'Verde F':      (  0,100, 30),
        }

        self.DIR = {
            'Music':  'src/resources/sounds/music',
            'SFX':    'src/resources/sounds/SFX',
            'Fonts':  'src/resources/fonts',
            'Images': 'src/resources/images'
        }

        if is_client:
            self.FONT = {
                'Inc-R 12': pygame.font.Font(f'{self.DIR["Fonts"]}/Inconsolata-Regular.ttf', 12),
                'Inc-R 13': pygame.font.Font(f'{self.DIR["Fonts"]}/Inconsolata-Regular.ttf', 13),
                'Inc-R 14': pygame.font.Font(f'{self.DIR["Fonts"]}/Inconsolata-Regular.ttf', 14),
                'Inc-R 15': pygame.font.Font(f'{self.DIR["Fonts"]}/Inconsolata-Regular.ttf', 15),
                'Inc-R 16': pygame.font.Font(f'{self.DIR["Fonts"]}/Inconsolata-Regular.ttf', 16),
                'Inc-R 18': pygame.font.Font(f'{self.DIR["Fonts"]}/Inconsolata-Regular.ttf', 18),
                'Inc-R 20': pygame.font.Font(f'{self.DIR["Fonts"]}/Inconsolata-Regular.ttf', 20),
                'Inc-R 24': pygame.font.Font(f'{self.DIR["Fonts"]}/Inconsolata-Regular.ttf', 24),
                'Retro 12': pygame.font.Font(f'{self.DIR["Fonts"]}/Retro Gaming.ttf', 12),
                'Retro 14': pygame.font.Font(f'{self.DIR["Fonts"]}/Retro Gaming.ttf', 14),
                'Retro 16': pygame.font.Font(f'{self.DIR["Fonts"]}/Retro Gaming.ttf', 16),
                'Retro 18': pygame.font.Font(f'{self.DIR["Fonts"]}/Retro Gaming.ttf', 18),
                'Retro 20': pygame.font.Font(f'{self.DIR["Fonts"]}/Retro Gaming.ttf', 20),
                'Retro 24': pygame.font.Font(f'{self.DIR["Fonts"]}/Retro Gaming.ttf', 24),
                'Wendy 12': pygame.font.Font(f'{self.DIR["Fonts"]}/Wendy.ttf', 12),
                'Wendy 14': pygame.font.Font(f'{self.DIR["Fonts"]}/Wendy.ttf', 14),
                'Wendy 16': pygame.font.Font(f'{self.DIR["Fonts"]}/Wendy.ttf', 16),
                'Wendy 18': pygame.font.Font(f'{self.DIR["Fonts"]}/Wendy.ttf', 18),
                'Wendy 20': pygame.font.Font(f'{self.DIR["Fonts"]}/Wendy.ttf', 20),
                'Wendy 24': pygame.font.Font(f'{self.DIR["Fonts"]}/Wendy.ttf', 24),
                'Comic 12': pygame.font.SysFont('comicsans', 12),
                'Comic 14': pygame.font.SysFont('comicsans', 14),
                'Comic 16': pygame.font.SysFont('comicsans', 16),
                'Comic 18': pygame.font.SysFont('comicsans', 18),
                'Comic 20': pygame.font.SysFont('comicsans', 20),
                'Comic 24': pygame.font.SysFont('comicsans', 24)
            }   # Diccionario de Fuentes.

            self.MUSIC = self._get_music_files()

            # Sound Effects
            self.SFX = {}

            # Music
            self.music = pygame.mixer.music
            self.sound = pygame.mixer.Sound

        # Configs: -----------------------------------------------------

        self.show = {
            'name':          True,      # Show the name of the player and the name of the enemies
            'speed':         True,      # Show player speed 
            'fps':           True,      # Show fps
            'pos':           True,      # Show player coordinates
            'hp-sp':         True,      # Show player's HP and SP numbers
            'weapon':        True,      # Displays the name and level of the weapon
            'creds_exp':     True,      # Show credits and experience
            'acc_dmg':       True,      # Show accumulated damage
            'map_enemies':   True,      # Show all enemies on minimap
            'matrix_bg_fix': True,      # Show background matrix fixed
            'chat':          True       # Show Chat
        }

        self.WEAPON = {
            'Laser-mid': {
                'path': f'{self.DIR["Images"]}/weapons/laser-red.png',
                'dmg': 50,          # Base damage
                'inc': 5,           # Damage increment per level
                'ammo': 1000,       # Ammunition
                'dist': 250,        # Minimum distance to attack enemies
                'pct_sp': .7,       # Damage percentage to SP
                'mult': 1           # Damage multiplier
            },
            'Laser': {
                'path': f'{self.DIR["Images"]}/weapons/laser-red.png',
                'dmg': 100,         # Base damage
                'inc': 10,          # Damage increment per level
                'ammo': 1000,       # Ammunition
                'dist': 400,        # Minimum distance to attack enemies
                'pct_sp': .7,       # Damage percentage to SP
                'mult': 1           # Damage multiplier
            },
            'Plasma': {
                'path': f'{self.DIR["Images"]}/weapons/plasma-green.png',
                'dmg': 1000,        # Base damage
                'inc': 50,          # Damage increment per level
                'ammo': 100,        # Ammunition
                'dist': 200,        # Minimum distance to attack enemies
                'pct_sp': .6,       # Damage percentage to SP
                'mult': 1           # Damage multiplier
            }
        }

        self.baseHP = 350
        self.baseSP = 250
        self.SHIP = {
            'Prometheus': {
                'path': f'{self.DIR["Images"]}/Prometheus.png',
                'weapon': 'Laser',
                'min_dist_sel': 40,
                'level':     1,
                'speed':   100,
                'spd_level': 0,
                'hp':      self.baseHP,
                'sp':      self.baseSP
            }
        }

        self.STRANGERS = {
            'Iken': {
                'path':     f'{self.DIR["Images"]}/Iken (Epsilon).png',
                'level':      1,
                'creds':    2,
                'exp':      10,
                'min_dist': 350,
                'min_dist_sel': 40,
                'wpn_name': 'Laser-mid',
                'wpn_level':  0,
                'speed':    50,
                'spd_level':  0,
                'lhp':      1,
                'lsp':      1,
                'hp':       50,
                'sp':       100
            }
        }

        self.MAP = {
            'Zwem':  { 'x': 200, 'y': 150 },
            'Karon': { 'x': 250, 'y': 200 },
            'Arkon': { 'x': 300, 'y': 250 }
        }

        self.roundRects = {}                # Created round rects

        # Username settings
        self.name_min_char_len = 1          # Minimum Character Length
        self.name_max_char_len = 24         # Maximum Character Length

        # Data settings
        self.MAX_SPD_LVL = 112              # Max Speed level of Ships
        self.dtdiv = 1000                   # Detla Time Divide
        self.posdiv = 30                    # Divide the actual position of pixels X and Y to generate coordinates for the map
        self.rad_dmg = 500                  # Radioactive Damage 
        self.open_menu = False              # Is open menu
        self.pos_tab_menu = 1               # Position of menu tab

        # Counters
        self.curr_frame = 0                 # Current Frame

        # Background matrix settings
        self.matrix_bg_sqr = 15             # Type: False = variable. Squares on Background. Example: 15x15
        self.xy_pixels_sqr = 50             # Type: True = fixed.     X and Y pixels in squares on background

        # Screen settings
        if is_client:
            self.screen_full_size = pygame.display.list_modes()[0]      # Resolution
        self.min_w = 600                    # Minimum width resolution
        self.min_h = 400                    # Minimum height resolution
        self.full_screen = False            # Full Screen
        self.RESOLUTION = RESOLUTION        # Resolution
        self.windowed_pos = []              # Current window pos and size (Windowed)
        self.init_time_windowed = 0
        self.antialiasing = True            # Anti-aliasing is a method by which you can remove irregularities that appear in objects in PC games.
        self.run = False                    # Game Run
        self.MAX_FPS = 240                  # Max Frames per Second
        self.MIN_FPS = 30                   # Max Frames per Second
        self.FPS = 240                      # Max Frames per Second
        self.current_fps = self.FPS         # Number of Frames per Second

        # Music settings
        self.music_vol = 20                 # Music volume

        # Map settings
        self.map_name = 'Arkon'

    # Properties ---------------------------------

    @property
    def CENTER(self):
        return {'x': self.RESOLUTION[0]//2, 'y': self.RESOLUTION[1]//2}

    @property
    def W(self):
        return self.RESOLUTION[0]

    @property
    def H(self):
        return self.RESOLUTION[1]

    @property
    def map_limits(self): # Actual map coordinates in number of pixels
        return {
            'x': self.MAP[self.map_name]['x'] * self.posdiv,
            'y': self.MAP[self.map_name]['y'] * self.posdiv
        }

    @property
    def limit_obj_dist(self):
        # Objects that are off the screen disappear
        limit_obj_dist = int(self.utils.euclideanDistance((
                                self.CENTER['x'], self.CENTER['y']),
                                (0, 0)
                            )) + 100
        return limit_obj_dist

    # Private Methods ----------------------------

    def _get_music_files(self):
        music_dir = self.DIR['Music']
        files = os.listdir(music_dir)
        music_files = filter(lambda file: file.endswith('.mp3'), files)
        music_paths = map(lambda file: f'{self.DIR["Music"]}/{file}', music_files)
        return list(music_paths)

    # Functions ----------------------------------

    def getStranger(self, s_name, level):
        STRANGERS = {
            'Iken': {
                'type':     '',
                'path':     f'{self.DIR["Images"]}/Iken ({{}}).png',
                'level':      1,
                'creds':    1,
                'exp':      10,
                'min_dist': 350,
                'min_dist_sel': 40,
                'wpn_name': 'Laser-mid',
                'wpn_level':  0,
                'speed':    50,
                'spd_level':  0,
                'lhp':      1,
                'lsp':      1,
                'hp':       self.baseHP,
                'sp':       self.baseSP
            }
        }

        stgr_type = {
            'Iken': {
                1: 'Alfa',
                2: 'Beta',
                3: 'Gamma',
                4: 'Delta',
                5: 'Epsilon'
            }
        }

        if s_name == 'Iken':
            if     0 <= level <  28: s_type = 5
            elif  28 <= level <  56: s_type = 4
            elif  56 <= level <  84: s_type = 3
            elif  84 <= level < 112: s_type = 2
            elif 112 <= level:       s_type = 1

        stranger = STRANGERS[s_name]
        stranger['type']      = stgr_type[s_name][s_type]
        stranger['level']     = level
        stranger['path']      = stranger['path'].format(stranger['type'])
        stranger['creds']    *= level
        stranger['exp']      *= level
        stranger['wpn_level'] = level-1
        stranger['spd_level'] = level-1
        stranger['lhp']       = level
        stranger['lsp']       = level
        # stranger['lhp']      *= level//2 + level%2
        # stranger['lsp']      *= level//2

        return stranger

    def videoResize(self, event):
        if not self.RESOLUTION == event.size:
            if not self.full_screen \
            and time.perf_counter() - self.init_time_windowed > 1:
                mw = self.min_w
                mh = self.min_h
                w, h = event.size
                if w < mw: w = mw
                if h < mh: h = mh
                self.RESOLUTION = (w, h)
                WIN = pygame.display.set_mode((w, h), HWSURFACE | DOUBLEBUF | RESIZABLE)
            else:
                self.RESOLUTION = event.size

    def switchFullScreen(self):
        if not self.full_screen:
            self.full_screen = True
            self.windowed_pos = self.utils.curWinRect[:2] + self.utils.curWinSize
            WIN = pygame.display.set_mode(
                self.screen_full_size,
                HWSURFACE | DOUBLEBUF | FULLSCREEN
            )
        else:
            self.init_time_windowed = time.perf_counter()
            self.full_screen = False
            win_x = self.windowed_pos[0]
            win_y = self.windowed_pos[1]
            win_w = self.windowed_pos[2]
            win_h = self.windowed_pos[3]

            self.RESOLUTION = (win_w, win_h)
            WIN = pygame.display.set_mode(
                (win_w, win_h),
                HWSURFACE | DOUBLEBUF | RESIZABLE
            )

            add_w  = self.utils.curWinRect[2]
            add_w += abs(self.utils.curWinRect[0])
            add_w -= self.utils.curWinSize[0]

            add_h  = self.utils.curWinRect[3]
            add_h += abs(self.utils.curWinRect[1])
            add_h -= self.utils.curWinSize[1]

            self.utils.moveWindow(win_x, win_y, win_w+add_w, win_h+add_h)
            WIN = pygame.display.set_mode(
                self.RESOLUTION,
                HWSURFACE | DOUBLEBUF | RESIZABLE
            )
