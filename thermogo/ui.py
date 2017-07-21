import tcod as libtcod

from thermogo.mobs import Unit
from thermogo.colors import YELLOW

class Cursor(Unit):

    def __init__(self, x, y):
        self.x, self.y = x, y

        self.char0 = "X"
        self.char1 = " "
        self.char = self.char0

        self.color = YELLOW
        self.wait = 5
        self.name = "Cursor"
    
    def move(self, x, y):
        """
        Uses Decimal() since this is actual game-world coords. on surface of the 
        sphere
        """
        self.x += x
        self.y += y
        self.char = "X"
        self.wait = 4

    def switch_char(self):
        self.char = self.char0 if self.char == self.char1 else self.char0

    def blink(self):
        if self.wait > 0:
            self.wait -= 1

        if not self.wait:
            self.switch_char()
            self.wait = 5


class GameCamera:
    """
    Used to keep track of what to render onscreen, and to differentiate the 
    position of the camera from the position of the player, in case we want to 
    move one and not the other
    """

    def __init__(self, x = 0, y = 0, width = 1, height = 1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def move(self, dx, dy):
        """
        Doesn't use Decimal() since it's only relative to the grid projection of 
        the gameworld sphere
        """
        self.x += dx
        self.y += dy

    def zoom(self, dz, world_height):
        if dz < 0:
            if self.camera.y >= world_height - self.height/2:
                self.camera.y = world_height - self.height/2
            else:
                self.camera.move(0,1)
        else:
            if self.camera.y <= self.height/2:
                self.camera.y = self.height/2
            else:
                self.camera.move(0,-1)
                