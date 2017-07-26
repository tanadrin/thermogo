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



# Game state and game logic, except input,
class GameObject:
    
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
        self.interface_objects = []
        self.persistent_objects = []
        
        # Background cleanup
        self.cleanup_interval = cleanup_interval
        self.cleanup_timer = cleanup_interval
        
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
        for object in self.persistent_objects:
            if object.char == " " and object.name == "DEAD":
                self.persistent_objects.remove(object)
        for object in self.active_player.owned_objects:
            if object.char == " " and object.name == "DEAD":
                self.persistent_objects.remove(object)
                
    
        
    def update_cursor_cartesian(self, cursor):
       '''
       Updates the cursor's coordinates modulo the size of the world, versus its
       coordinates as actually stored
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
            
    def save_map(self):
        '''
        Saves all data associated with the current gamemap and all persistent objects
        (but not anything to do with the interface)
        '''
        savefile = shelve.open(str(self.game_map.name), 'n')
        savefile['game_map'] = self.game_map
        savefile['players'] = self.players
        savefile['active_player'] = self.active_player
        
        if self.persistent_objects != []:
            savefile['persistent_objects'] = self.persistent_objects
        else:
            savefile['persistent_objects'] = None
        savefile.close()
                
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
        
        if loadfile['persistent_objects'] != None:
            self.persistent_objects = loadfile['persistent_objects']
        else:
            self.persistent_objects = []
        if ui.cursor == None:
            ui.cursor = Cursor(0,0)
            self.interface_objects.append(ui.cursor)
        loadfile.close()
        
    def gen_map(self, ui):
        self.persistent_objects = []
        self.game_map = GameMap(self.mapsize)
        ui.cursor = Cursor(0, 0)
        self.interface_objects.append(ui.cursor)
        ui.camera = GameCamera(0, ui.max_camera_height/2, ui.max_camera_width, ui.max_camera_height)
        self.players = self.create_players(self.max_players)
        self.active_player = self.players[0]
    
    def unload_map(self, ui):
        self.game_map = None
        ui.camera = None
        ui.cursor = None
        self.interface_objects = []
        self.players = []
        self.active_player = None
        self.persistent_objects = []
        
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
        if self.active_player.number < len(self.players):
            # This is kind of a fucked-up way of doing it, but because the player
            # numbers are 1-indexed, but the list of players is 0-indexed, the 
            # index of the next active player on the list is equal to the current
            # player number; no reason to subtract 1 then add it again.
            self.active_player = self.players[self.active_player.number]
        else:
            self.active_player = self.players[0]
            
    def  cycle(self):
        '''
        Periodic game events governed by the main game loop
        '''
        if self.game_map != None and self.persistent_objects != None:
            self.run_cleanup()

    # Force spawn a base for debugging purposes
    def force_spawn(self, cursor):
        base = Base(cursor.x, cursor.y, self.persistent_objects, self.active_player)
    
    # Kill all objects for debugging purposes
    def force_kill(self):
        for object in self.persistent_objects:
            object.remove_unit()
        
    def remove_dead_units(self):
        for object in self.persistent_objects:
            if object.char == " " and object.name == "DEAD":
                self.persistent_objects.remove(object)
                self.active_player.owned_objects.remove(object)