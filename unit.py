from colors import *
from player import *

class Unit(object):
    '''
    Basic unit object, used for other game objects.
    '''
    MAX_MOVEMENT = 0
    ATTACK_CHAR = '@'
    DEFEND_CHAR = '@'
    SUPPORT_CHAR = '@'
    MOVE_CHAR = '@'
    HOLD_CHAR = '@'
    DEFAULT_CHAR = '@'
    def __init__(self, x, y, unit_list, player = no_player):
        unit_list.add(self)
        self.unit_list = unit_list
        player.owned_objects.add(self)
        self.x = x
        self.y = y
        self.char = self.DEFAULT_CHAR
        self.color = player.color
        self.name = 'Unit'
        owner = player
        self.movement = self.MAX_MOVEMENT
        self.movement_type = None
        self.order = None
        self.wait = 5
        self.supply_cost = 0
        self.active = False
    
    # Basic movement on the game grid
    def move(self, x, y):
        self.x += x
        self.y += y
        self.movement -= 10
        
    def kill(self):
        self.owner.owned_objects.remove(self)
        self.unit_list.remove(self)
        
    def blink(self):
        if self.wait > 0:
            self.wait += -1
        elif self.wait == 0 and self.char == 'X':
            self.char = ' '
            self.wait = 5
        elif self.wait == 0 and self.char == ' ':
            self.update_char
            self.wait = 5
            
    def set_order(self, order):
        self.order = order
        self.update_char()
        
    def update_char(self):
        if self.order == 'attack':
            self.char = self.ATTACK_CHAR
        elif self.order == 'defend':
            self.char = self.DEFEND_CHAR
        elif self.order == 'hold':
            self.char = self.HOLD_CHAR
        elif self.order == 'wait':
            self.char = self.DEFAULT_CHAR
        elif self.order == 'support':
            self.char = self.SUPPORT_CHAR
        elif self.order == 'move':
            self.char = self.MOVE_CHAR
            
    
class Base(Unit):
    DEFAULT_CHAR = '#'
    def __init__(self, x, y, unit_list, player = no_player):
        super(Base, self).__init__(x, y, unit_list, player)
        self.supply_cost = -1
        
        
class ResourceNode(Unit):
    DEFAULT_CHAR = '^'
    def __init__(self, x, y, unit_list, player = no_player):
        super(ResourceNode, self).__init__(x, y, unit_list, player)
        self.color = GOLD
        
class Army(Unit):
    MAX_MOVEMENT = 100
    ATTACK_CHAR = '>'
    DEFEND_CHAR = 'X'
    SUPPORT_CHAR = '$'
    MOVE_CHAR = '/'
    HOLD_CHAR = '*'
    DEFAULT_CHAR = '&'
    def __init__(self, x, y, unit_list, player):
        super(Army, self).__init__(x, y, unit_list, player)
        self.name = 'Army'
        self.movement_type = 'land'
        self.supply_cost = 1
        
        
class Fleet(Unit):
    MAX_MOVEMENT = 100
    ATTACK_CHAR = '<'
    DEFEND_CHAR = '@'
    SUPPORT_CHAR = 'S'
    MOVE_CHAR = '\\'
    HOLD_CHAR = '*'
    DEFAULT_CHAR = 'V'
    def __init__(self, x, y, unit_list, player):
        super(Fleet, self).__init__(x, y, unit_list, player)
        self.name = 'Fleet'
        self.movement_type = 'sea'
        self.supply_cost = 1