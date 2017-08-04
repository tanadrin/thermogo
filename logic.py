import random
import shelve
import os.path
import math
from decimal import *

# The Doryen Library - Documentation:
# http://roguecentral.org/doryen/data/libtcod/doc/1.5.1/index2.html
import libtcodpy as libtcod

# Thermonuclear Go modules
from unit import *
from ui import *
from ui_objects import *
from mapping import *
from colors import *
from player import *

class GameObject(object):
    '''
    Main object for handling information about game objects and the current
    state of the game.
    '''
    BASE_BUILD_COST = 5
    
    def __init__(self, mapsize, max_players, cleanup_interval):
    
        # Game map data
        self.mapsize = mapsize
        self.game_map = None
        
        # Game state control
        self.paused = False
        self.loading = False
        self.active_player = None
        
        # Tracking game elements
        self.max_players = max_players
        self.players = []
        self.interface_objects = set()
        self.armies = set()
        self.bases = set()
        self.fleets = set()
        self.missiles = set()
        self.resources = set()
        self.persistent_objects = [self.armies, self.bases, self.missiles, self.fleets]
        self.round = 0
        
        # Background and cleanup
        self.cleanup_interval = cleanup_interval
        self.cleanup_timer = cleanup_interval
        self.event_queue = EventQueue()
        self.message_queue = MessageQueue()
        
        # Used for tracking and updating UIs
        self.game_uis = []
        
    def run_cleanup(self):
        '''
        Periodic timer to clear all data associated with unused objects
        '''
        if self.cleanup_timer <= 0:
            self.cleanup_timer = self.cleanup_interval
            self.clean_dead_objects()
        else:
            self.cleanup_timer -= 1
        
    def clean_dead_objects(self):
        '''
        Actual cleanup of objects marked for deletion
        '''
        for object in self.active_player.owned_objects:
            if object.char == " " and object.name == "DEAD":
                self.active_player.owned_objects.remove(object)
        
    def update_cursor_cartesian(self, cursor):
       '''
       Updates the cursor's coordinates modulo the size of the world, versus 
       its coordinates as actually stored
       '''
       cursor.xm = cursor.x % self.game_map.world_width
       cursor.ym = cursor.y % self.game_map.world_height
       return cursor.xm, cursor.ym
       
    def update_cursor_coordinates(self, cursor):
        '''
        Updates the cursor's longitude and latitude
        '''
        cursor.la = self.game_map.grid[cursor.x][cursor.y].la
        cursor.lo = self.game_map.grid[cursor.x][cursor.y].lo
        return cursor.la, cursor.lo
        
    def update_cursor_elevation(self, cursor):
        cursor.elevation = self.game_map.grid[cursor.x][cursor.y].elevation
        return cursor.elevation
        
    def update_cursor_data(self, cursor):
        self.update_cursor_cartesian(cursor)
        self.update_cursor_coordinates(cursor)
        self.update_cursor_elevation(cursor)
            
    def save_map(self, ui):
        '''
        Saves all data associated with the current gamemap and all 
        persistent objects but not anything to do with the interface)
        '''
        savefile = shelve.open(str(self.game_map.name), 'n')
        savefile['game_map'] = self.game_map
        savefile['players'] = self.players
        savefile['active_player'] = self.active_player
        savefile['armies'] = self.armies
        savefile['fleets'] = self.fleets
        savefile['bases'] = self.bases
        savefile['missiles'] = self.missiles
        savefile.close()
        self.event_queue.add_event(0, self.clear_loading, (ui,))
                
    def load_map(self, ui, map='map_name'):
        '''
        Loads all saved map data from the specified file, including persistent
        objects, and updates the UI if necessary
        '''
        
        if ui.camera == None:
            ui.camera = GameCamera(0, ui.max_camera_height/2, ui.max_camera_width, ui.max_camera_height)
            
        loadfile = shelve.open(map, 'r')
        self.game_map = loadfile['gamemap']
        self.players = loadfile['players']
        self.active_player = loadfile['active_player']
        self.armies = loadfile['armies']
        self.fleets = loadfile['fleets']
        self.bases = loadfile['bases']
        self.missiles = loadfile['missiles']
        if ui.cursor == None:
            ui.cursor = Cursor(0,0)
            self.interface_objects.add(ui.cursor)
        loadfile.close()
        self.event_queue.add_event(0, self.clear_loading, (ui,))
        self.game_uis.append(ui)
        for ui in self.game_uis:
            ui.game_object = self
            ui.infobar.message_queue = self.message_queue
        
    def gen_map(self, ui):
        '''
        Generates a new map, UI objects, and player list in preparation for 
        a new game.
        '''
        self.armies = set()
        self.fleets = set()
        self.bases = set()
        self.missiles = set()
        self.game_map = GameMap(self.mapsize, self.resources)
        ui.cursor = Cursor(0, 0)
        self.interface_objects.add(ui.cursor)
        ui.camera = GameCamera(
            0, 
            ui.max_camera_height/2, 
            ui.max_camera_width, 
            ui.max_camera_height
        )
        self.players = self.create_players(self.max_players)
        self.active_player = self.players[0]
        self.event_queue.add_event(0, self.clear_loading, (ui,))
        self.game_uis.append(ui)
        for ui in self.game_uis:
            ui.game_object = self
            ui.infobar.message_queue = self.message_queue
            ui.infobar.message_queue.add_message('Round 1', C_SYS)
            ui.infobar.message_queue.add_message(
                'Player 1\'s turn', 
                self.players[0].color
            )
    
    def unload_map(self, ui):
        '''
        Unloads all data associated with the map/current game state, in 
        preparation for exiting the game (but not necessarily the entire 
        program)
        '''
        self.game_map = None
        ui.camera = None
        ui.cursor = None
        self.interface_objects = set()
        self.players = []
        self.active_player = None
        self.armies = set()
        self.fleets = set()
        self.bases = set()
        self.missiles = set()
        self.game_uis = None
        
    def create_players(self, number):
        players = []
        
        for i in range(1, number+1):
            if i == 1:
                players.append(Player(1, RED, "Player 1"))
            if i == 2:
                players.append(Player(2, BLUE, "Player 2"))
            if i == 3:
                players.append(Player(3, GREEN, "Player 3"))
            if i == 4:
                players.append(Player(4, WHITE, "Player 4"))
            if i == 5:
                players.append(Player(5, TEAL, "Player 5"))
            if i == 6:
                players.append(Player(6, PURPLE, "Player 6"))
            if i == 7:
                players.append(Player(7, YELLOW, "Player 7"))
        return players
        
    def pass_turn(self):
        # If the active player isn't last on the player list, pass the turn.
        # Otherwise, end the round completely and hand the turn back to the
        # first player on the player list.
        if self.active_player.number < len(self.players):
            # This is kind of a fucked-up way of doing it, but because the 
            # player numbers are 1-indexed, but the list of players is 
            # 0-indexed, the index of the next active player on the list is 
            # equal to the current player number; no reason to subtract 1
            # then add it again.
            self.active_player = self.players[self.active_player.number]
        else:
            self.active_player = self.players[0]
            self.round += 1
            self.message_queue.add_message('Round '+str(self.round+1), WHITE)
            for player in self.players:
                player.power_projection += 1
        self.wake_player()
        self.message_queue.add_message(
            'Player '+str(self.active_player.number)+'\'s turn', 
            self.active_player.color
        )
            
    def  cycle(self):
        '''
        Periodic game events governed by the main game loop
        '''
        if self.game_map != None:
            self.run_cleanup()
            self.check_wake(self.active_player)
            
        self.event_queue.tick()
        
    def build_base(self, cursor):
        '''
        Spawns a base at cursor x, y, if player has enough power projection
        and action points left (and the location is valid).
        '''
        # Check for valid location
        if self.game_map.grid[cursor.x][cursor.y].elevation > 0:
            if len(self.bases) > 0:
                for unit in self.bases:
                    if cursor.x == unit.x and cursor.y == unit.y:
                        return
                else:
                    # Check for sufficient power projection and actions
                    if self.active_player.actions > 0 and self.active_player.power_projection >= self.BASE_BUILD_COST:
                        self.active_player.actions -= 1
                        self.active_player.power_projection -= self.BASE_BUILD_COST
                        base = Base(cursor.x, cursor.y, self.bases, self.active_player)
                        self.message_queue.add_message(
                            'Player '+str(self.active_player.number)+
                            ' built a base at '+str(cursor.la)+' '+str(cursor.lo)+'.', 
                            self.active_player.color
                        )
            else:
                if self.active_player.actions > 0 and self.active_player.power_projection >= self.BASE_BUILD_COST:
                    self.active_player.actions -= 1
                    self.active_player.power_projection -= self.BASE_BUILD_COST
                    base = Base(cursor.x, cursor.y, self.bases, self.active_player)
                    self.message_queue.add_message(
                        'Player '+str(self.active_player.number)+
                        ' built a base at '+str(cursor.la)+' '+str(cursor.lo)+'.', 
                        self.active_player.color
                    )
                
    def clear_loading(self, ui):
        self.loading = False
        ui.loading = False
        
    def check_wake(self, player):
        '''
        Checks the player for remaining valid moves; if none remain, the wake
        status of the player is set to False, allowing the turn to be passed 
        automatically via the action key. The turn can always be passed 
        manually as well.
        '''
        moves_left = 0
        if player.owned_objects != []:
            for object in player.owned_objects:
                moves_left += object.movement
        if player.actions > 0:
            if player.power_projection >= self.BASE_BUILD_COST or player.supply > player.supply_used:
                moves_left += player.actions
        if moves_left <= 0:
            player.wake = False
            
    def wake_player(self):
        '''
        Used to wake the active player at the start of their turn.
        '''
        self.active_player.wake = True
        self.active_player.actions = self.active_player.MAX_ACTIONS

class EventQueue(object):
    '''
    Used to handle function calls that don't need to be immediately executed.
    '''
    def __init__(self):
        self.queue = []
        self.delay = 0
        
    def add_event(self, delay, event, args = ()):
        self.queue.append([event, args])
        self.add_delay(delay)
        
    def execute_event(self):
        if self.queue != []:
            function, args = self.queue[0]
            if args != ():
                function(*args)
            elif function != None:
                function()
            self.queue.pop(0)
        else:
            pass
        
    def execute_all(self):
        if self.queue != False:
            for function, args in self.queue:
                if args != ():
                    function(args)
                else:
                    function()
            self.queue = []
                
    def add_delay(self, i):
        self.delay = i
        
    def tick(self):
        if self.delay == 0:
            self.execute_event()
        elif self.delay > 0:
            self.delay -= 1
        
class MessageQueue(object):
    '''
    Messages are passed to the MessageQueue, which stores them and passes them
    to the infobar to be displayed. Each message is stored with a color (uses
    default message color unless specified otherwise) in which it is displayed.
    '''
    def __init__(self):
        self.queue = []
        
    def add_message(self, text, color = C_SYS):
        self.queue.append((text, color))
    
    def retrieve_latest(self):
        message = self.queue.pop(0)
        return message
        
    def clear_queue(self):
        self.queue = []