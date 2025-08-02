
class Minimap:
    def __init__(self, settings, player):
        self.settings = settings
        self.player = player

        # Configuraciones del Minimapa
        self.map_name = self.settings.map_name
        self.map_name_rect = (0,0)
        self.map_w = 150
        self.map_h = 120
        self.map_x = self.settings.W - self.map_w - 5
        self.map_y = self.settings.H - self.map_h - 5
        self.map_move = False
        self.map_move_pos = (0,0)
        self.map_move_x = self.settings.W - self.map_w - 5
        self.map_move_y = self.settings.H - self.map_h - 5

        # Cuadrante Actual en Pantalla
        self.quad = 4

        # Tamaño del minimapa
        self.btn_col     = 'Cyan'
        self.btn_col_off = 'Rojo Opaco'
        self.btn_plus  = []
        self.btn_minus = []
        self.map_resize = False
        self.map_size = 1
        self.map_size_max = 6
        self.map_size_x = 25
        self.map_size_y = 20
        self.set_size(mult=self.map_size)

    def setFollowPos(self, event): # TODO: Revisar por qué cuando se destruye un enemigo y esta siguiendo una posición, se devia u no cambia su angulo.
        x, y = event.pos

        # Distancia en coordenadas falsas (las coordenadas falsas son las mostradas al usuario en gameplay)
        dif_x = x-self.map_x
        dif_y = y-self.map_y

        # Distancia en coordenadas reales basado en el tamaño del mapa
        dif_x = int(round(self.settings.MAP[self.map_name]['x'] * (dif_x/self.map_w)))
        dif_y = int(round(self.settings.MAP[self.map_name]['y'] * (dif_y/self.map_h)))

        if  1 < dif_x < self.settings.MAP[self.map_name]['x']-1\
        and 1 < dif_y < self.settings.MAP[self.map_name]['y']-1:
            self.player.follow_pos = True
            self.player.follow_pos_move = False
            self.player.follow_pos_xy = (   # Ahora se toman las cordenadas reales (en pixeles)
                dif_x*self.settings.posdiv,
                dif_y*self.settings.posdiv
            )
        # else:
        #     if self.player.follow_pos:
        #         self.player.cancelFollowPos()

    def scrPosOnMap(self, x, y, add=2):
        return (
            x-add-((self.settings.CENTER['x']/self.settings.posdiv) / self.settings.MAP[self.map_name]['x'] * self.map_w),
            y-add-((self.settings.CENTER['y']/self.settings.posdiv) / self.settings.MAP[self.map_name]['y'] * self.map_h),
            (add*2)+(self.settings.W/self.settings.posdiv) / self.settings.MAP[self.map_name]['x'] * self.map_w,
            (add*2)+(self.settings.H/self.settings.posdiv) / self.settings.MAP[self.map_name]['y'] * self.map_h
        )

    def set_size(self, add=True, mult=1):
        self.map_w = 150 + (self.map_size_x*self.map_size)
        self.map_h = 120 + (self.map_size_y*self.map_size)

        if add:
            if self.quad in [1,4]:
                self.map_x -= self.map_size_x * mult
            if self.quad in [3,4]:
                self.map_y -= self.map_size_y * mult
        else:
            if self.quad in [1,4]:
                self.map_x += self.map_size_x * mult
            if self.quad in [3,4]:
                self.map_y += self.map_size_y * mult

        # self.quadrant(*self.settings.RESOLUTION)
        self.map_resize = True
        self.map_move_x = self.map_x
        self.map_move_y = self.map_y

    def resize(self, event):
        x, y = event.pos

        if  self.btn_minus[1][0]-5 < x < self.btn_minus[1][0]+self.btn_minus[0][0]+3\
        and self.btn_minus[1][1]   < y < self.btn_minus[1][1]+self.btn_minus[0][1]:
            if not self.map_size == 0:
                self.map_size -= 1
                self.set_size(add=False)

        if  self.btn_plus[1][0]-5 < x < self.btn_plus[1][0]+self.btn_plus[0][0]+5\
        and self.btn_plus[1][1]   < y < self.btn_plus[1][1]+self.btn_plus[0][1]:
            if not self.map_size == self.map_size_max:
                self.map_size += 1
                self.set_size(add=True)

    def limitMove(self): # Limita el movimiento del mapa para que no pueda salir de la pantalla
        if self.map_x > self.map_x_orig:
            self.map_x = self.map_x_orig
        if self.map_x-5 < 0:
            self.map_x = 5
        if self.map_y > self.map_y_orig:
            self.map_y = self.map_y_orig
        if self.map_y-self.map_name_rect[1]-5 < 0:
            self.map_y = self.map_name_rect[1]+5

    def quadrant(self, w: int, h: int):
        if   self.map_x > w//2 and self.map_y < h//2: self.quad = 1            # Right Upper Quadrant
        elif self.map_x < w//2 and self.map_y < h//2: self.quad = 2            # Left  Upper Quadrant
        elif self.map_x < w//2 and self.map_y > h//2: self.quad = 3            # Left  Lower Quadrant
        elif self.map_x > w//2 and self.map_y > h//2: self.quad = 4            # Right Lower Quadrant

    def onResizeScreen(self, orig_res: tuple):
        w, h = orig_res

        self.quadrant(w, h)

        if self.quad in [1,4]:
            dif_x = w - self.map_x
            self.map_x = self.settings.W - dif_x
        if self.quad in [3,4]:
            dif_y = h - self.map_y
            self.map_y = self.settings.H - dif_y

        self.limitMove()

        self.map_move_x = self.map_x
        self.map_move_y = self.map_y

    def mouseButtonDown(self, event):
        pos_x, pos_y = event.pos
        if  self.map_move_x < pos_x < self.map_move_x+self.map_name_rect[0]\
        and self.map_move_y-self.map_name_rect[1] < pos_y < self.map_move_y:
            self.map_move = True
            self.map_move_pos = event.pos

    def mouseButtonUp(self):
        if self.map_move:
            self.map_move_x = self.map_x
            self.map_move_y = self.map_y
            self.map_move = False

    def mouseMotion(self, event):
        if self.map_move:
            pos_x, pos_y = event.pos
            clic_pos_x, clic_pos_y = self.map_move_pos
            x = pos_x-self.map_move_x
            y = pos_y-self.map_move_y
            d_x = abs(self.map_move_x-clic_pos_x)
            d_y = abs(self.map_move_y-clic_pos_y)

            self.map_x = self.map_move_x+x-d_x
            self.map_y = self.map_move_y+y+d_y

            self.quadrant(*self.settings.RESOLUTION)

            self.limitMove()

    def windowLeave(self):
        if self.map_move:
            self.map_move_x = self.map_x
            self.map_move_y = self.map_y
            self.map_move = False

    @property
    def map_pos(self):
        return [
            self.map_x, self.map_y,
            self.map_w, self.map_h
        ]

    @property
    def player_pos(self):
        return (
            round((self.player.x/self.settings.posdiv) / self.settings.MAP[self.map_name]['x'] * self.map_w + self.map_x, 2),
            round((self.player.y/self.settings.posdiv) / self.settings.MAP[self.map_name]['y'] * self.map_h + self.map_y, 2)
        )

    @property
    def map_x_orig(self):
        return self.settings.W - self.map_w - 5

    @property
    def map_y_orig(self):
        return self.settings.H - self.map_h - 5
