import contextlib
with contextlib.redirect_stdout(None):
    import pygame


class Window:
    def __init__(self, settings, player, utils):
        self.WIN = None
        self.settings = settings
        self.player = player
        self.utils = utils

    def drawRoundrect(self, rect_name, pos, bcolor, ba, br, bgcolor):
        # rect_name: nombre del componente
        # pos: posiciones para el rectangulo
        # bcolor: color del borde
        # ba: anchura del borde
        # br: redondeado del borde
        # bgcolor: Color del fondo y transparencia de 0 a 255

        if not self.settings.roundRects.get(rect_name):
            rr_img, rr_rect = self.utils.roundRect(pos, bcolor, ba, br, bgcolor)
            self.settings.roundRects[rect_name] = rr_img, rr_rect
        else:
            rr_img, rr_rect = self.settings.roundRects.get(rect_name)
            if not pos == rr_rect:
                rr_img, rr_rect = self.utils.roundRect(pos, bcolor, ba, br, bgcolor)
                self.settings.roundRects[rect_name] = rr_img, rr_rect

        self.WIN.blit(rr_img, rr_rect)

    def renderText(self, text: str, font: pygame.font.Font, color: tuple, type: str = ''):
        if 'bold' in type:         font.set_bold(True)
        elif font.get_bold():      font.set_bold(False)
        if 'italic' in type:       font.set_italic(True)
        elif font.get_italic():    font.set_italic(False)
        if 'underline' in type:    font.set_underline(True)
        elif font.get_underline(): font.set_underline(False)
        return font.render(text, self.settings.antialiasing, color)
