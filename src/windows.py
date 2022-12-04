import time


class Minimap:
    
    def __init__(self, settings, player):
        
        self.settings = settings
        self.player = player

        # Map settings
        self.map_name = 'Zwem'
        self.map_name_rect = (0,0)
        self.map_w = 150
        self.map_h = 120
        self.map_x = self.settings.W - self.map_w - 5
        self.map_y = self.settings.H - self.map_h - 5
        self.map_move = False
        self.map_move_pos = (0,0)
        self.map_move_x = self.settings.W - self.map_w - 5
        self.map_move_y = self.settings.H - self.map_h - 5
        
        # Current Quadrant on Screen
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
    
    def setFollowPos(self, event):
        
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
            self.player.follow_pos_xy = (	# Ahora se toman las cordenadas reales (en pixeles)
                dif_x*self.settings.posdiv,
                dif_y*self.settings.posdiv
            )
        # ~ else:
            # ~ if self.player.follow_pos:
        ''		# ~ self.player.cancelFollowPos()
    
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
        
        # ~ self.quadrant(*self.settings.RESOLUTION)
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
    
    def quadrant(self, w, h):
        if   self.map_x > w//2 and self.map_y < h//2: self.quad = 1			# Right Upper Quadrant
        elif self.map_x < w//2 and self.map_y < h//2: self.quad = 2			# Left  Upper Quadrant
        elif self.map_x < w//2 and self.map_y > h//2: self.quad = 3			# Left  Lower Quadrant
        elif self.map_x > w//2 and self.map_y > h//2: self.quad = 4			# Right Lower Quadrant
    
    def onResizeScreen(self, orig_res):
        
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


class Chat:
    
    def __init__(self, settings):
        
        self.settings = settings

        self.messages = {
            'global': [
                ('Enylaine','Hola :D'),
                ('LOL','xD')
            ]
        }
        
        self.chat_name = 'Chat'
        self.chat_name_rect = (0,0)
        self.chat_global_name_rect = (0,0)
        self.chat_min_w = 150
        self.chat_min_h = 120
        self.chat_max_w = 300
        self.chat_max_h = 240
        self.chat_w = 225
        self.chat_h = 150
        self.chat_x = 5
        self.chat_y = 20
        self.chat_x_orig = self.chat_x
        self.chat_y_orig = self.chat_y
        self.chat_move = False
        self.chat_move_pos = (0,0)
        self.chat_move_x = self.chat_x
        self.chat_move_y = self.chat_y
        self.pct_tr = 50					# Percentage of transparency
        self.chat_text_active = False
        self.chat_text = ''
        self.chat_tab = 1
        self.chat_msg_tam = 14				# 12, 14, 16
        
        self.init_time = time.perf_counter()
    
    @property
    def chat_pos(self):
        return [
            self.chat_x, self.chat_y,
            self.chat_w, self.chat_h
        ]
    
    @property
    def chat_input_pos(self):
        anc = 4
        return [
            self.chat_x + anc*1.5, self.chat_h - anc*1.5,
            self.chat_w -(anc*3),  anc*5
        ]
    
    @property
    def chat_inner_pos(self):
        anc, tab = 4, 18
        return [
            self.chat_x + anc,    self.chat_y + tab,
            self.chat_w -(anc*2), self.chat_h - tab - anc
        ]
    
    def perSecond(self, t=1):
        if time.perf_counter() - self.init_time >= t:
            self.init_time = time.perf_counter()
            return True
        return False
    
    def activeInput(self, event):
        if event.button == 1:
            x, y = event.pos
            inp_pos = self.chat_input_pos
            if  inp_pos[0] < x < inp_pos[0]+inp_pos[2]\
            and inp_pos[1] < y < inp_pos[1]+inp_pos[3]:
                self.chat_text_active = True
            else:
                self.chat_text_active = False
        else:
            if self.chat_text_active:
                self.chat_text_active = False
    
    def setGlobalMessages(self, messages):
        self.messages['global'] = messages
    
    def limitMove(self): # Limita el movimiento del mapa para que no pueda salir de la pantalla
        if self.chat_x > self.chat_x_orig:
            self.chat_x = self.chat_x_orig
        if self.chat_x-5 < 0:
            self.chat_x = 5
        if self.chat_y > self.chat_y_orig:
            self.chat_y = self.chat_y_orig
        if self.chat_y-self.chat_name_rect[1]-5 < 0:
            self.chat_y = self.chat_name_rect[1]+5
    
    def quadrant(self, w, h):
        if   self.chat_x > w//2 and self.chat_y < h//2: self.quad = 1			# Right Upper Quadrant
        elif self.chat_x < w//2 and self.chat_y < h//2: self.quad = 2			# Left  Upper Quadrant
        elif self.chat_x < w//2 and self.chat_y > h//2: self.quad = 3			# Left  Lower Quadrant
        elif self.chat_x > w//2 and self.chat_y > h//2: self.quad = 4			# Right Lower Quadrant
    
    def mouseButtonDown(self, event):
        pos_x, pos_y = event.pos
        if  self.chat_move_x < pos_x < self.chat_move_x+self.chat_name_rect[0]\
        and self.chat_move_y-self.chat_name_rect[1] < pos_y < self.chat_move_y:
            self.chat_move = True
            self.chat_move_pos = event.pos
    
    def mouseButtonUp(self):
        if self.chat_move:
            self.chat_move_x = self.chat_x
            self.chat_move_y = self.chat_y
            self.chat_move = False
    
    def mouseMotion(self, event):
        
        if self.chat_move:
            
            pos_x, pos_y = event.pos
            clic_pos_x, clic_pos_y = self.chat_move_pos
            x = pos_x-self.chat_move_x
            y = pos_y-self.chat_move_y
            d_x = abs(self.chat_move_x-clic_pos_x)
            d_y = abs(self.chat_move_y-clic_pos_y)
            
            self.chat_x = self.chat_move_x+x-d_x
            self.chat_y = self.chat_move_y+y+d_y
            
            self.quadrant(*self.settings.RESOLUTION)
            
            self.limitMove()

