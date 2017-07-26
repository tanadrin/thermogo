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
from logic import *

import time


class GameController:
    # GUI and map variables
    SCREEN_WIDTH = 182
    SCREEN_HEIGHT = SCREEN_WIDTH/2+1
    # Height of GUI pane on bottom of the screen, the 'infobar'
    INFOBAR_HEIGHT = 10
    # Thickness of pane borders
    MARGIN_WIDTH = 1
    # Size of the togglable right-hand menu
    MENU_WIDTH = 20
    # PNG font used for game
    GAME_FONT = 'assets/arial10x10.png'
    
    # Game settings
    # Maximum game FPS; 1 frame is the basic unit of in-game time
    LIMIT_FPS = 20
    # Minimum frame intervals between certain GUI events
    MAX_GUI_WAIT = 3
    # Minimum frame interval for certain background processes, like cleaning up dead objects
    MAX_BACKGROUND_WAIT = 20
    # Maximum number of players in a hotseat multiplayer game
    MAX_PLAYERS = 2 
    
    def __init__(self):
        
        self.gui_wait = self.MAX_GUI_WAIT
        
        self.game_object = GameObject(
            self.SCREEN_WIDTH-self.MARGIN_WIDTH*2, 
            self.MAX_PLAYERS,
            self.MAX_BACKGROUND_WAIT
        )
        self.game_ui = GameUI(
            self.SCREEN_WIDTH, 
            self.SCREEN_HEIGHT, 
            self.MENU_WIDTH, 
            self.INFOBAR_HEIGHT, 
            self.MARGIN_WIDTH, 
            self.GAME_FONT
        )
        
        self.max_camera_width = self.SCREEN_WIDTH-2*self.MARGIN_WIDTH
        self.max_camera_height = self.SCREEN_HEIGHT-2*self.MARGIN_WIDTH
        
        # Main libtcod console and parameters
        libtcod.sys_set_fps(self.LIMIT_FPS)
        
        
    # Starting game and running main loop
    def start_game(self):
        
        while not libtcod.console_is_window_closed():
            
            # Render the screen
            self.game_ui.refresh_all(
                self.game_object.game_map, 
                self.game_ui.camera, 
                self.game_object.persistent_objects + self.game_object.interface_objects, 
                self.game_ui.cursor
            )
            
            exit = game_controller.handle_keys()
            
            if exit:
                break
        
    
    CONSOLE_KEY_ACTIONS = {
        libtcod.KEY_UP: lambda self : self.game_ui.cursor.move( 0,-1),
        libtcod.KEY_DOWN: lambda self : self.game_ui.cursor.move( 0, 1),
        libtcod.KEY_LEFT: lambda self : self.game_ui.cursor.move(-1, 0),
        libtcod.KEY_RIGHT: lambda self : self.game_ui.cursor.move( 1 ,0)
    }

    CHAR_KEY_ACTIONS = {
        ord('l'): lambda self : self.game_ui.toggle_menu(self.game_ui.camera),
        ord('k'): lambda self : self.game_ui.toggle_infobar(self.game_ui.camera),
        ord('['): lambda self : self.camera_pan(-1, 0),
        ord(']'): lambda self : self.camera_pan( 1, 0),
        ord('-'): lambda self : self.camera_pan( 0, 1),
        ord('='): lambda self : self.camera_pan( 0,-1),
        ord('s'): lambda self : self.begin_save(self.game_ui, self.MAX_GUI_WAIT),
        ord('d'): lambda self : self.begin_load(self.game_ui, self.MAX_GUI_WAIT),
        ord('g'): lambda self : self.begin_gen(self.game_ui, self.MAX_GUI_WAIT),
        ord('q'): lambda self : self.game_object.pass_turn(),
        ord('w'): lambda self : self.game_object.force_spawn(self.game_ui.cursor),
        ord('e'): lambda self : self.game_object.force_kill(),
    }
    
    # Handling input and run periodic UI and game logic functions
    def handle_keys(self):
        key = libtcod.console_check_for_keypress()  # real-time
        
        if self.game_ui.cursor != None:
            for input, action in self.CONSOLE_KEY_ACTIONS.items():
                if libtcod.console_is_key_pressed(input):
                    action(self)
            self.game_ui.game_view.lock_cursor_to_view(self.game_ui.camera, self.game_ui.cursor)
            self.game_object.update_cursor_cartesian(self.game_ui.cursor)
            self.game_object.update_cursor_coordinates(self.game_ui.cursor)
            
        self.game_ui.cycle()
        self.game_object.cycle()
            
        
        if key.vk == libtcod.KEY_ESCAPE and self.game_object.game_map != None:
            self.game_object.unload_map(self.game_ui)
            
        elif key.vk == libtcod.KEY_ESCAPE and self.game_object.game_map == None:
            return True # Exit game
            
        if key.vk == libtcod.KEY_CHAR:
            action = self.CHAR_KEY_ACTIONS.get(key.c)
            if action:
                action(self)
                
        if self.gui_wait > 0:
            self.gui_wait -= 1
    
    # Throttle camera movement according to GUI input limits
    def camera_pan(self, x, y):
        if self.gui_wait <= 0:
            self.gui_wait = self.MAX_GUI_WAIT
            self.game_ui.camera.move(x , y, self.game_object.game_map.world_height)
            print 'camera moved'
        else:
            print 'camera not moved'
            print self.gui_wait
            
    def begin_load(self, ui, delay):
        self.game_ui.loading = True
        self.game_object.loading = True
        self.game_object.event_queue.add_event(delay, self.game_object.load_map, ui)
        
    def begin_save(self, ui, delay):
        self.game_ui.loading = True
        self.game_object.loading = True
        self.game_object.event_queue.add_event(delay, self.game_object.save_map, ui)
        
    def begin_gen(self, ui, delay):
        self.game_ui.loading = True
        self.game_object.loading = True
        self.game_object.event_queue.add_event(delay, self.game_object.gen_map, ui)
        print 'start gen'
    
                
def main():
    global game_controller
    game_controller = GameController()
    game_controller.start_game()
    
if __name__ == '__main__':
    main()