from colors import *

class Player:
    MAX_POWER_PROJECTION = 20
    MAX_ACTIONS = 1
    def __init__(self, number, color, name):
        self.number = number
        self.color = color
        self.name = name
        self.owned_objects = set()
        self.active_objects = []
        self.power_projection = 5
        self.supply = 0 # Our Shepherd will supply our needs if on him we relyyyy
        self.supply_used = 0
        self.actions = self.MAX_ACTIONS
        self.wake = True # If the player has valid actions left, wake = True 
        # and the turn must be force-passed. Otherwise, wake = False, and the 
        # turn can be auto-passed by hitting enter. A player will always have 
        # valid actions right after waking, and so wake can safely be 
        # initialized as true.
        self.active = True # active = True at the beginning; if the player did 
        # at least one thing during their turn, or it's the start of the game, 
        # active = True. If for all players active = False, the game ends.

# Dummy player variable used for unowned objects
no_player = Player(0, WHITE, 'No Player')