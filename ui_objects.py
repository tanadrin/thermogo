# The Doryen Library - Documentation:
# http://roguecentral.org/doryen/data/libtcod/doc/1.5.1/index2.html
import libtcodpy as libtcod
from colors import *

class Cursor():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = 'X'
        self.color = YELLOW
        self.wait = 5
        self.name = 'Cursor'
        
        # The cursor doesn't calculate this directly, only stores it for quick
        # lookup by other functions
        self.la = 0
        self.lo = 0
        # The x, y coordinates on the gameworld, with the modulo of the map size
        # applied
        self.xm = x
        self.ym = y
        # The elevation of the current location of the cursor
        self.elevation = 0
        
    
    def move(self, x, y):
        self.x += x
        self.y += y
        self.char = 'X'
        self.wait = 4
        
    def blink(self):
        if self.wait > 0:
            self.wait += -1
        elif self.wait == 0 and self.char == 'X':
            self.char = ' '
            self.wait = 5
        elif self.wait == 0 and self.char == ' ':
            self.char = 'X'
            self.wait = 5

class GameCamera:
    '''
    Used to keep track of what to render onscreen, and to differentiate the 
    position of the camera from the position of the player, in case we want 
    to move one and not the other
    '''
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    def move(self, dx, dy, world_height):
        '''
        Allows endless horizontal camera pan (because the camera wraps 
        around horizontally), but limited vertical pan (since there'seek
        no vertical wraparound).
        '''
        if dy == 0:
            self.x += dx
        elif dy < 0:
            if self.y <= self.height/2:
                self.y = self.height/2
            else:
                self.y += dy
                self.x += dx
        elif dy > 0:
            if self.y >= world_height - self.height/2:
                self.y = world_height - self.height/2
            else:
                self.y += dy
                self.x += dx