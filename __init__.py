'''
TO-DO LIST:
    1. Refactor code so that on startup:
        a. a splash screen appears with the Chicken Movers logo (item deleted)
        b. a main menu appears with singleplayer, multiplayer, and config options (done)
        c. plus exit and credits (done)
        d. you can enter SP, MP, or any of those submenus and return to the main menu (done sorta)
    2. Sever-client architecture for the singleplayer game, with separate interfaces for each player
    3. A multiplayer mode that starts a server and connects to it, and listens for other connections
    4. Plus a multiplayer mode that just hsots the server (and can be started from the command line)
'''
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
import socket

class GameController:
    # GUI and map variables
    SCREEN_WIDTH = 182
    SCREEN_HEIGHT = SCREEN_WIDTH/2+1
    # Height of GUI pane on bottom of the screen, the 'infobar'
    INFOBAR_HEIGHT = 10
    # Thickness of pane borders
    MARGIN_WIDTH = 1
    # Size of the togglable right-hand menu
    SIDEMENU_WIDTH = 20
    # PNG font used for game
    GAME_FONT = 'assets/arial10x10.png'
    
    # Game settings
    # Maximum game FPS; 1 frame is the basic unit of in-game time
    LIMIT_FPS = 20
    # Minimum frame intervals between certain GUI events
    MAX_GUI_WAIT = 5
    # Minimum frame interval for certain background processes, like cleaning up dead objects
    MAX_BACKGROUND_WAIT = 20
    # Maximum number of players in a hotseat multiplayer game
    MAX_PLAYERS = 2 
    
    def __init__(self):
    
        self.gui_wait = self.MAX_GUI_WAIT
        self.game_object = None
        self.prepare_to_quit = False
        
        self.game_ui = GameUI(
            self.SCREEN_WIDTH, 
            self.SCREEN_HEIGHT, 
            self.SIDEMENU_WIDTH, 
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
            self.game_ui.refresh_all(self.game_object, self.game_ui)
            
            exit = game_controller.system_loop()
            
            if exit:
                print 'Thermonuclear Go closed gracefully.'
                break
        
    
    CONSOLE_KEY_ACTIONS = {
        libtcod.KEY_UP: lambda self : self.arrow_key( 0,-1),
        libtcod.KEY_DOWN: lambda self : self.arrow_key( 0, 1),
        libtcod.KEY_LEFT: lambda self : self.arrow_key(-1, 0),
        libtcod.KEY_RIGHT: lambda self : self.arrow_key( 1 ,0),
        libtcod.KEY_ENTER: lambda self : self.action_key(),
        libtcod.KEY_ESCAPE: lambda self : self.escape_key()
    }

    CHAR_KEY_ACTIONS = {
        ord('m'): lambda self : self.game_ui.toggle_menu(self.game_ui.camera),
        ord('i'): lambda self : self.game_ui.toggle_infobar(self.game_ui.camera),
        ord('['): lambda self : self.camera_pan(-1, 0),
        ord(']'): lambda self : self.camera_pan( 1, 0),
        ord('-'): lambda self : self.camera_pan( 0, 1),
        ord('='): lambda self : self.camera_pan( 0,-1),
        ord('s'): lambda self : self.begin_save(self.game_ui, self.MAX_GUI_WAIT),
        ord('q'): lambda self : self.game_object.pass_turn(),
        ord('w'): lambda self : self.game_object.force_spawn(self.game_ui.cursor),
        ord('e'): lambda self : self.game_object.force_kill(),
    }
    
    # Handling input and dispatch periodic UI and game logic functions
    def system_loop(self):
        if self.game_ui.current_menu != None:
            key = libtcod.console_wait_for_keypress(True)  # Loop waits for a key to be pressed
            self.gui_wait = 0
            
        else:
            key = libtcod.console_check_for_keypress() # Loop runs continuously
            if self.gui_wait > 0:
                self.gui_wait -= 1
        
        # Throttled input cooldown
        
        
        # Handling console key input (i.e., non-character key input)
        for input, action in self.CONSOLE_KEY_ACTIONS.items():
            if libtcod.console_is_key_pressed(input):
                action(self)
                
        # Handling character key input (a-z keys and other printable chars, but
        # not numeric keys)
        if self.game_ui.current_menu != None:
            # All character input for out-of-game menus
            if key.vk == libtcod.KEY_CHAR:
                self.character_key(key.c)
        else:
            # All character input in-game
            if key.vk == libtcod.KEY_CHAR:
                action = self.CHAR_KEY_ACTIONS.get(key.c)
                if action:
                    action(self)
                
        # If a game is loaded, execute periodic UI and game logic functions
        if self.game_object != None:
        
            self.game_ui.cycle()
            self.game_object.cycle()
            
                
        return self.prepare_to_quit
    
    # Throttle camera movement according to GUI input limits to keep commands from
    # piling up
    def camera_pan(self, x, y):
        if self.gui_wait <= 0:
            self.gui_wait = self.MAX_GUI_WAIT
            self.game_ui.camera.move(x , y, self.game_object.game_map.world_height)
    
    # Dispatches load order and indicates to the UI and game state loading has begun
    def begin_load(self, ui, delay):
        self.game_ui.loading = True
        self.game_object.loading = True
        self.game_object.event_queue.add_event(delay, self.game_object.load_map, (ui,))
    
    # Dispatches save order and indicates to the UI and game state saving has begun
    def begin_save(self, ui, delay):
        self.game_ui.loading = True
        self.game_object.loading = True
        self.game_object.event_queue.add_event(delay, self.game_object.save_map, (ui,))
    
    # Dispatches gen order and indicates to the UI and game state saving has begun
    def begin_gen(self, ui, delay):
        self.game_ui.loading = True
        self.game_object.loading = True
        self.game_object.event_queue.add_event(delay, self.game_object.gen_map, (ui,))
    
    # Handles arrow key input depending on if we're looking at a menu or at a running game
    def arrow_key(self, x, y):
        if self.game_object != None and self.game_ui.cursor != None:
            self.game_ui.cursor.move(x, y)
            self.game_ui.game_view.lock_cursor_to_view(self.game_ui.camera, self.game_ui.cursor)
            self.game_object.update_cursor_cartesian(self.game_ui.cursor)
            self.game_object.update_cursor_coordinates(self.game_ui.cursor)
        elif self.game_ui.current_menu != None:
            self.game_ui.current_menu.scroll(y)
                
    # Handles action key (default ENTER) input depending on circumstances
    def action_key(self):
        # If the action key is being used on a menu item
        if self.game_ui.current_menu != None:
            selection = self.game_ui.current_menu.action_select()
            self.run_selection(selection)
        # If the action key is being used in-game
        else:
            pass
            
    def escape_key(self):
        # If the escape key is pressed while no game is loaded:
        if self.game_object == None:
            selection = 'exit'
            self.run_selection(selection)
        else:
            selection = 'return_to_main_menu'
            self.run_selection(selection)

    # Handles character key input for menu hotkeys
    def character_key(self, char):
        # If we're getting character key input on a menu
        if self.game_ui.current_menu != None:
            selection = self.game_ui.current_menu.key_select(chr(char))
            self.run_selection(selection)
        # In other circumstances
        else:
            pass
    
    # Runs the menu selection returned from an out-of-game or in-game menu
    def run_selection(self, selection):
    
            # Includes condition to unload current game, if we're starting a new
            # game from inside a running one
            if selection == 'new_game':
                if self.game_object != None:
                    self.game_object.unload_map(self.game_ui)
                self.game_ui.setup_ingame_ui()
                self.game_object = GameObject(
                    self.SCREEN_WIDTH-self.MARGIN_WIDTH*2, 
                    self.MAX_PLAYERS,
                    self.MAX_BACKGROUND_WAIT
                )
                self.begin_gen(self.game_ui, 3)

            # Includes condition to unload current game, if we're loading a new
            # game from inside a running one
            elif selection == 'load_game':
                if self.game_object != None:
                    self.game_object.unload_map(self.game_ui)
                self.game_ui.setup_ingame_ui()
                self.game_object = GameObject(
                    self.SCREEN_WIDTH-self.MARGIN_WIDTH*2, 
                    self.MAX_PLAYERS,
                    self.MAX_BACKGROUND_WAIT
                )
                self.begin_load(self.game_ui, 3)
                    
            elif selection == 'multiplayer':
                print 'Multiplayer functionality is not yet ready.'
                    
            elif selection == 'options':
                print 'No in-game options available yet.'
                    
            elif selection == 'help':
                print 'We all need help, buddy'
                    
            elif selection == 'credits':
                self.game_ui.show_credits()
                    
            elif selection == 'exit':
                self.prepare_to_quit = True
                    
            elif selection == 'return_to_main_menu':
                self.return_to_main_menu()
                
    def return_to_main_menu(self):
        if self.game_object != None:
            self.game_object.unload_map(self.game_ui)
            self.game_object = None
        self.game_ui.create_main_menu()
        
                    
                
def main():
    global game_controller
    game_controller = GameController()
    game_controller.start_game()
    
if __name__ == '__main__':
    main()