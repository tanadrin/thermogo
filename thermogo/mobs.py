
from decimal import Decimal

from thermogo.colors import WHITE

class Unit:
    def __init__(self, x, y, objects):
        self.x, self.y = x, y
        self.char = "@"
        self.color = WHITE
        self.name = "Unit"
    
    # Generic movement on a sphere. Kind of.
    # Uses Decimal() since this is actual game-world coords. on surface of the sphere
    def move(self, dlo, dla):
        
        self.lo += Decimal(dlo)
        
        if self.lo < Decimal(-180):
            self.lo += Decimal(360)
        elif self.lo > Decimal(180):
            self.lo += Decimal(-360)
        
        self.la += Decimal(dla)

        if self.la < Decimal(-90):
            self.la = Decimal(-90)
        elif self.la > Decimal(90):
            self.la = Decimal(90)
                
    # # Hide the object; draw_object won't draw objects represented by " ".
    # def clear(self):
    #    libtcod.console_put_char(game.con, self.x, self.y, " ", libtcod.BKGND_NONE)