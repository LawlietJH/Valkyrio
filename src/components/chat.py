import time


class Chat:
    def __init__(self, settings):
        self.settings = settings

        self.messages = {
            'global': [],   # list[tuples[str, str]] = [(username, message), ...]
            'team': [],
            'clan': []
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
        self.pct_tr = 50                        # Percentage of transparency
        self.chat_text_active = False
        self.chat_text = ''
        self.chat_tab = 1
        self.chat_msg_tam = 14                  # 12, 14, 16

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

    def perSecond(self, t: int = 1):
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

    def setGlobalMessages(self, messages: list[tuple[str, str]]):
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

    def quadrant(self, w: int, h: int):
        if   self.chat_x > w//2 and self.chat_y < h//2: self.quad = 1           # Upper Right Quadrant
        elif self.chat_x < w//2 and self.chat_y < h//2: self.quad = 2           # Upper Left  Quadrant
        elif self.chat_x < w//2 and self.chat_y > h//2: self.quad = 3           # Lower Left  Quadrant
        elif self.chat_x > w//2 and self.chat_y > h//2: self.quad = 4           # Lower Right Quadrant

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
