import tcod as libtcod

from thermogo.mobs import Unit

class Cursor(Unit):
    def __init__(self, x, y):
        #lo and la are longitude and latitude
        self.x = x
        self.y = y
        self.char = "X"
        self.color = libtcod.Color(255,255,0)
        self.wait = 5
        self.name = "Cursor"
    
    #Uses Decimal() since this is actual game-world coords. on surface of the sphere
    def move(self, x, y):
        self.x += x
        self.y += y
        self.char = "X"
        self.wait = 4
    def blink(self):
        if self.wait > 0:
            self.wait += -1
        elif self.wait == 0 and self.char == "X":
            self.char = " "
            self.wait = 5
        elif self.wait == 0 and self.char == " ":
            self.char = "X"
            self.wait = 5

#Used to keep track of what to render onscreen, and to differentiate the position of the camera from the position of the player, in case we want to move one and not the other
class GameCamera:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    #Doesn't use Decimal() since it's only relative to the grid projection of the gameworld sphere
    def move(self, dx, dy):
        self.x += dx
        self.y += dy