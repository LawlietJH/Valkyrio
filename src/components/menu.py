import contextlib
with contextlib.redirect_stdout(None):
    import pygame


class Menu:
    def __init__(self, window, settings, player):
        self.window = window
        self.settings = settings
        self.player = player

    def drawMenu(self):
        font14 = self.settings.FONT['Inc-R 14']
        font16 = self.settings.FONT['Inc-R 16']
        font18 = self.settings.FONT['Inc-R 18']
        font20 = self.settings.FONT['Inc-R 20']
        font24 = self.settings.FONT['Inc-R 24']

        if   len(self.player.name) > 20: name_font = font14
        elif len(self.player.name) > 16: name_font = font16
        elif len(self.player.name) > 12: name_font = font18
        elif len(self.player.name) > 8:  name_font = font20
        else: name_font = font24

        BLANCO  = self.settings.COLOR['Blanco']
        CYAN    = self.settings.COLOR['Cyan']
        CYANOP  = self.settings.COLOR['Cyan Opaco']
        VERDE   = self.settings.COLOR['Verde Claro']
        VERDEOP = self.settings.COLOR['Verde Opaco']

        # Draw background ----------------------------------------------
        pos = { 'x': 20, 'y': 20, 'w': 20, 'h': 20 }
        pos['w'] = self.settings.W - pos['w'] - pos['x']
        pos['h'] = self.settings.H - pos['h'] - pos['y']
        menu_pos = [ pos['x'], pos['y'], pos['w'], pos['h'] ]

        self.window.drawRoundrect('background menu', menu_pos, self.settings.COLOR['Verde F'],
            2, 2, (*self.settings.COLOR['Verde S'], 180)
        )

        # Draw tabs ----------------------------------------------------
        despX = 180
        tx, ty = menu_pos[0]+1, menu_pos[0]
        tw, th = despX, 50
        tabs = ['Information', 'Enhance', 'Constellations']

        pygame.draw.line(self.window.WIN, self.settings.COLOR['Linea Bg'], 
            (pos['x']+despX, pos['y']+2),
            (pos['x']+despX, pos['h']+pos['y']-2),
        2)

        text = f'{self.player.name}'
        text = self.window.renderText(text, name_font, VERDE)
        self.window.WIN.blit(text, (
                tx + tw//2 - text.get_width()//2,
                ty + th//2 - text.get_height()//2
            )
        )

        for i, tab in enumerate(tabs):
            i+=1
            tab_y = ty + (th-1) * i

            if self.settings.pos_tab_menu == i:
                tr = 50
                color = CYAN
            else:
                tr = 10
                color = CYANOP

            tab_pos = [tx, tab_y, tw, th]
            self.window.drawRoundrect('tab on menu', tab_pos, self.settings.COLOR['Verde F'],
                2, 1, (*CYANOP, tr)
            )

            text = self.window.renderText(tab, font18, color, 'bold')
            self.window.WIN.blit(text, (
                    tx    + tw//2 - text.get_width()//2,
                    tab_y + th//2 - text.get_height()//2
                )
            )

        # Draw tab Content ---------------------------------------------

        positions = [
            tx+tw,
            ty,
            pos['w']-despX,
            pos['h']
        ]

        if   self.settings.pos_tab_menu == 1: self.drawMenuTabInfo(*positions)
        elif self.settings.pos_tab_menu == 2: self.drawMenuTabEnhance(*positions)
        elif self.settings.pos_tab_menu == 3: self.drawMenuTabConstellations(*positions)

    def drawMenuTabInfo(self, x: int, y: int, w: int, h: int):  # Tab 1
        CYAN   = self.settings.COLOR['Cyan']
        VERDEC = self.settings.COLOR['Verde Claro']
        font   = self.settings.FONT['Inc-R 16']
        despX  = 120            # Desplazamiento en X
        despY  = 30             # Desplazamiento en Y

        texts = [
            ('Experience',                              font, CYAN  ),
            (str(self.player.exp),                      font, VERDEC),
            ('Credits',                                 font, CYAN  ),
            (str(self.player.creds),                    font, VERDEC),
            ('Weapon',                                  font, CYAN  ),
            (f'{str(self.player.ship.weapon.name)} '\
                f'({self.player.ship.weapon.lvl})',     font, VERDEC),
            ('Damage',                                  font, CYAN  ),
            (str(self.player.ship.weapon.dmg),          font, VERDEC),
            ('Speed',                                   font, CYAN  ),
            (str(self.player.ship.speed),               font, VERDEC),
            ('FPS',                                     font, CYAN  ),
            (str(self.settings.current_fps),            font, VERDEC),
            ('Coords',                                  font, CYAN  ),
            ('({},{})'.format(
                    int(self.player.x/self.settings.posdiv),
                    int(self.player.y/self.settings.posdiv)
                ).ljust(11),                            font, VERDEC),
            ('Rad. rest.',                              font, CYAN  ),
            ('{}%'.format(str(
                    self.player.ship.pct_res_dmg_rad*100
                )),                                     font, VERDEC)
        ]

        # Draw background ----------------------------
        # positions = [ x, y, w, h ]

        # self.window.drawRoundrect('background tab', positions, self.settings.COLOR['Verde F'],
        #     3, 1, (*self.settings.COLOR['Verde S'], 50)
        # )

        # Draw texts ---------------------------------
        x = x+20
        y = y+20
        for i, text in enumerate(texts):
            self.window.WIN.blit(self.window.renderText(*text), (x+(despX*(i%2)), y+(despY*(i//2))))

    def drawMenuTabEnhance(self, x: int, y: int, w: int, h: int):   # Tab 2
        CYAN   = self.settings.COLOR['Cyan']
        VERDEC = self.settings.COLOR['Verde Claro']
        font   = self.settings.FONT['Inc-R 16']
        despX  = 100            # Desplazamiento en X
        despY  = 30             # Desplazamiento en Y

        texts = [
            ('Experience',                              font, CYAN),
            (str(self.player.exp),                      font, VERDEC),
            ('Credits',                                 font, CYAN),
            (str(self.player.creds),                    font, VERDEC),
            ('Weapon',                                  font, CYAN),
            (f'{str(self.player.ship.weapon.name)} '\
                f'({self.player.ship.weapon.lvl})',     font, VERDEC),
            ('Damage',                                  font, CYAN),
            (str(self.player.ship.weapon.dmg),          font, VERDEC),
            ('Speed',                                   font, CYAN),
            (str(self.player.ship.speed),               font, VERDEC),
            ('FPS',                                     font, CYAN),
            (str(self.settings.current_fps),            font, VERDEC),
            ('Coords',                                  font, CYAN),
            ('({},{})'.format(
                    int(self.player.x/self.settings.posdiv),
                    int(self.player.y/self.settings.posdiv)
                ).ljust(11),                       font, VERDEC)
        ]

        # Draw background ----------------------------
        # positions = [ x, y, w, h ]

        # self.window.drawRoundrect('background tab', positions, self.settings.COLOR['Verde F'],
        #     3, 1, (*self.settings.COLOR['Verde S'], 50)
        # )

        # Draw texts ---------------------------------
        x = x+20
        y = y+20
        for i, text in enumerate(texts):
            self.window.WIN.blit(self.window.renderText(*text), (x+(despX*(i%2)), y+(despY*(i//2))))

    def drawMenuTabConstellations(self, x: int, y: int, w: int, h: int):    # Tab 3
        pass

