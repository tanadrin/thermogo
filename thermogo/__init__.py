import random
import shelve
import os.path
import math
import tcod as libtcod

from decimal import Decimal

from thermogo.mobs import Unit
from thermogo.ui import Cursor, GameCamera
from thermogo.map import GameMap
from thermogo.helpers import *
from thermogo.colors import *


class GameUI:
    """
    Class for handling the non-game view UI elements, like menus and overlays.
    """

    # Height of GUI pane on bottom of the screen, the "infobar"
    INFOBAR_HEIGHT = 10
    # Size of border around game windows and menus
    MARGIN_WIDTH = 1
    # Size of the togglable right-hand menu
    MENU_WIDTH = 20
    # PNG font used for game
    GAME_FONT = 'assets/arial10x10.png'
    # Maximum game FPS; 1 frame is the basic unit of in-game time
    LIMIT_FPS = 20
    # Minimum frame intervals between GUI events
    GUI_WAIT = 0

    def __init__(self, game_object):
        self.game_object = game_object

        # Game state and GUI control variables
        # Whether the additional views are shown or hidden
        self.show_menu = False
        self.show_infobar = False
        # Whether we're using real time or taking turns
        self.time = "free"
        # Input control variable; used to prevent some actions from happening too often
        self.gui_wait = 0
        # Main camera object
        self.camera = None

        self.cursor = Cursor(0, 0)
        
        # Main libtcod console and parameters
        libtcod.console_set_custom_font(self.GAME_FONT, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(game_object.SCREEN_WIDTH, game_object.SCREEN_HEIGHT, 'Thermonuclear Go', False)
        libtcod.sys_set_fps(self.LIMIT_FPS)
        self.con = libtcod.console_new(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Libtcod consoles for GUI
        self.infobar = libtcod.console_new(game_object.GAME_WIDTH, self.INFOBAR_HEIGHT)
        self.menu = libtcod.console_new(self.MENU_WIDTH, game_object.GAME_HEIGHT)
        self.gui_background = libtcod.console_new(game_object.SCREEN_WIDTH, game_object.SCREEN_HEIGHT)

    def refresh_infobar(self, infobar):
        libtcod.console_clear(infobar)
        
        gamemap = self.game_object.game_view.gamemap

        actual_x = self.cursor.x % gamemap.WORLD_WIDTH
        actual_y = self.cursor.y % gamemap.WORLD_HEIGHT
        
        infobar_texts = [
            "Cursor grid: %s, %s" % (actual_x, actual_y)
            "Cursor lat: %s" % gamemap.grid[actual_x][actual_y].la
            "Cursor long: %s" % gamemap.grid[actual_x][actual_y].lo
        ]
        
        if self.gamemap.grid[actual_x][actual_y].elevation > 0:
            text = "Elevation: %sm" % int(self.gamemap.grid[actual_x][actual_y].elevation*4000)
        else:
            text = "Elevation: Sea level"
        infobar_texts.append(text)
        
        infobar_texts.append("s: save terrain; d: load terrain; g: gen terrain; k: hide infobar")

        for text, i in enumerate(infobar_texts):
            libtcod.console_print(infobar, 0, i, text)
        # Add logic here to display new infobar information as needed
        
    def refresh_menu(self, menu):
        libtcod.console_clear(menu)
        # Add logic to change contents of menu here

    def _write_banner(self, text, x, y, bgcolor=DARK_BLUE, fgcolor=WHITE):
        for k in range(12):
            libtcod.console_set_char_background(gui, self.camera.width - x + k, 0, bgcolor)
            libtcod.console_put_char(gui, self.camera.width - x + k, 0, pause_text[x], libtcod.BKGND_NONE)
            libtcod.console_set_char_foreground(gui, self.GAME_WIDTH-x+k, 0, fgcolor)

    def refresh_gui_background(self, gui):
        """
        While the game is running, render a solid background to use as border
        between other GUI elements
        """
        libtcod.console_clear(gui)

        for x in range(self.SCREEN_WIDTH):
            for y in range(self.SCREEN_HEIGHT):
                libtcod.console_set_char_background(gui, x, y, GREY)
        
        if self.paused == True:
            self._write_banner("***PAUSED***", 15, 0)
        
        if self.loading != False:
            self._write_banner("***LOADING***", 15, 0)
                
    def force_gui_refresh(self):
        libtcod.console_clear(self.gui_background)
        self.refresh_gui_background(self.gui_background)
        libtcod.console_blit(self.gui_background, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)

        
class GameView:
    """
    Class for handling the main view of the game world
    """

    def __init__(self, game_object):
        self.game_object = game_object
        self.mapsize = game_object.SCREEN_WIDTH - game_object.MARGIN_WIDTH*2
        
        self.gamemap = GameMap(self.mapsize)
        self.view = libtcod.console_new(self.GAME_WIDTH, self.GAME_HEIGHT)

    def create_camera(self):
        self.camera = GameCamera(self.gamemap.WORLD_WIDTH/2,self.gamemap.WORLD_HEIGHT/2, self.GAME_WIDTH, self.GAME_HEIGHT)

    def refresh_main_view(self, main_view, map):
        libtcod.console_clear(main_view)
        self.draw_map(self.gamemap, main_view)
        for obj in self.objects:
            if obj.name != 'Cursor':
                self.draw_world_object(obj, main_view)
            else:
                self.draw_grid_object(obj, main_view)
        # Add logic to display stuff on main view here

    def draw_map(self, map, console):
        for x in range(self.camera.width):
            for y in range(self.camera.height):
                pos_x, pos_y = self.camera_to_grid_coordinates(x, y)
                if pos_y < 0 or pos_y >= map.WORLD_HEIGHT:
                    libtcod.console_put_char(console, x, y, " ", libtcod.BKGND_NONE)
                else:
                    pos_x = pos_x % map.WORLD_WIDTH
                    libtcod.console_set_default_foreground(console, map.grid[pos_x][pos_y].color)
                    libtcod.console_put_char(console, x, y, map.grid[pos_x][pos_y].char, libtcod.BKGND_NONE)

    def _draw_obj(self, pos_x, pos_y, obj):
        if pos_x is not None and obj.char != ' ':
            libtcod.console_set_default_foreground(console, obj.color)
            libtcod.console_put_char(console, pos_x, pos_y, obj.char, libtcod.BKGND_NONE)
        
    def draw_world_object(self, obj, console):
        pos_x, pos_y = self.spherical_to_camera_coordinates(obj.lo, obj.la)
        self._draw_obj(pos_x, pos_y, obj)
            
    def draw_grid_object(self, obj, console):
        pos_x, pos_y = self.grid_to_camera_coordinates(obj.x, obj.y)
        self._draw_obj(pos_x, pos_y, obj)
        
    def render_all(self):
        """
        Rendering the main view and GUI elements
        """
        # blit the contents of "con" to the root console
        libtcod.console_blit(self.con, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)
        # blit the contents of the GUI background to the root console
        self.refresh_gui_background(self.gui_background)
        libtcod.console_blit(self.gui_background, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)
        # blit the contents of the game_view to the root console
        self.refresh_main_view(self.game_view, self.gamemap)
        libtcod.console_blit(self.game_view, 0, 0, self.camera.width, self.camera.height, 0, 1, 1)
        # likewise for the infobar, if we're showing it
        if self.show_infobar == True:
            self.refresh_infobar(self.infobar)
            libtcod.console_blit(self.infobar, 0, 0, self.camera.width, self.INFOBAR_HEIGHT-self.MARGIN_WIDTH, 0, self.MARGIN_WIDTH, self.SCREEN_HEIGHT - self.INFOBAR_HEIGHT)
        # if we're showing the right-side menu, it as well
        if self.show_menu == True:
            self.refresh_menu(self.menu)
            libtcod.console_blit(self.menu, 0, 0, self.MENU_WIDTH - self.MARGIN_WIDTH, self.SCREEN_HEIGHT - self.MARGIN_WIDTH*2, 0, self.SCREEN_WIDTH - self.MENU_WIDTH, 1)
    

class GameObject:
    """
    Wrapper object for the whole shebang
    """

    # GUI and map variables
    SCREEN_WIDTH = 182
    SCREEN_HEIGHT = SCREEN_WIDTH/2+1
    # Size of the main game view
    GAME_WIDTH = SCREEN_WIDTH-2*MARGIN_WIDTH
    GAME_HEIGHT = SCREEN_HEIGHT-2*MARGIN_WIDTH
    # Directory to save map files in
    MAP_DIRECTORY = 'map/'
    
    def __init__(self):
        self.ui = UI(self)
        self.game_view = GameView(self)

        # All objects currently being simulated in the game
        self.objects = []
        
        self.paused = False
        self.loading = False

    # Starting game and running main loop
    def start_game(self):
        self.game_view.create_camera()
        while not libtcod.console_is_window_closed():
            # Render the screen
            self.ui.render_all()
            self.game_view.render_all()
            libtcod.console_flush()
            # Erase all objects at their old locations, before they move
            # for object in self.objects:
            #    object.clear()
            # Handle keys and exit game if needed
            exit = game.handle_keys()
            if exit:
                break
               

    CONSOLE_KEY_ACTIONS = {
        libtcod.KEY_UP: lambda : self.cursor.move(0, -1),
        libtcod.KEY_DOWN: lambda : self.cursor.move(0, 1),
        libtcod.KEY_LEFT: lambda : self.cursor.move(-1, 0),
        libtcod.KEY_RIGHT: lambda : self.cursor.move(1, 0),
    }

    CHAR_KEY_ACTIONS = {
        "l": lambda self: self.toggle_menu(),
        "k": lambda self: self.toggle_infobar(),
        "[": lambda self: self.camera.move(-1,0),
        "]": lambda self: self.camera.move(1,0),
        "-": lambda self: self.camera.zoom(1, self.gamemap.WORLD_HEIGHT),
        "=": lambda self: self.camera.zoom(-1, self.gamemap.WORLD_HEIGHT),
        "s": lambda self: self.gamemap.save_map(),
        "d": lambda self: self.gamemap.load_map(),
        "g": lambda self: self.gamemap.gen_map(),
    }

    def handle_keys(self):

        if self.paused == False:

            if self.gui_wait == 0:
                for key, action in self.CONSOLE_KEY_ACTIONS.items():
                    if libtcod.console_is_key_pressed(key):
                        action()
            
            self.lock_cursor_to_view()

        if self.gui_wait > 0:
            self.gui_wait -=1
        
        if self.cursor != None:
            self.cursor.blink()

        if self.time == "free":
            key = libtcod.console_check_for_keypress()  # real-time

        if key.vk == libtcod.KEY_ENTER and key.lalt:
            # Alt+Enter: toggle fullscreen
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
     
        elif key.vk == libtcod.KEY_ESCAPE:
            return True  # exit game

        # # Pause and unpause the game
        # if libtcod.console_is_key_pressed(libtcod.KEY_SPACE):
        #    if self.gui_wait == 0:
        #        if self.paused == True:
        #            self.paused = False
        #        elif self.paused == False:
        #            self.paused = True
        #        self.gui_wait = self.GUI_WAIT

        if key.vk == libtcod.KEY_CHAR:
            action = self.CHAR_KEY_ACTIONS.get(key.c)
            if action:
                action(self)

    def lock_cursor_to_view(self):
        x, y = self.grid_to_camera_coordinates(self.cursor.x, self.cursor.y)
        
        if x < 0:
            self.cursor.x, _ = self.camera_to_grid_coordinates(0, 0)
        if x > self.camera.width - 1:
            self.cursor.x, _ = self.camera_to_grid_coordinates(self.camera.width - 1, 0)

        if y < 0:
            _, self.cursor.y = self.camera_to_grid_coordinates(0, 0)
        if y > self.camera.height - 1:
            _, self.cursor.y = self.camera_to_grid_coordinates(0, self.camera.height - 1)


    def toggle_menu(self):
        self.show_menu = not self.show_menu
        if self.show_menu:
            self.camera.width = self.GAME_WIDTH - self.MENU_WIDTH
        else:
            self.camera.width = self.GAME_WIDTH
       
    def toggle_infobar(self):
        self.show_infobar = not self.show_infobar
        if self.show_infobar:
            self.camera.height = self.GAME_HEIGHT - self.INFOBAR_HEIGHT
        else:
            self.camera.height = self.GAME_HEIGHT
    
    #
    # Coordinate conversion utility functions
    #

    def grid_to_camera_coordinates(self, x, y):
        x = x - self.camera.x + self.camera.width/2
        y = y - self.camera.y + self.camera.height/2
        return x, y
        
    def camera_to_grid_coordinates(self, x, y):
        x = x - self.camera.width/2 + self.camera.x
        y = y - self.camera.height/2 + self.camera.y
        return x, y
        
    def spherical_to_grid_coordinates(self, lo, la):
        """
        Given a latitude from -90 to 90 and a longitude from -180 to 180, 
        return x, y on a grid from 0 to world width and 0 to world height
        """
        x = int((lo + 90)*(self.gamemap.WORLD_WIDTH/180))
        y = int((la + 180)*(self.gamemap.WORLD_HEIGHT/90))
        return x, y
    
    def spherical_to_camera_coordinates(self, lo, la):
        x, y = self.spherical_to_grid_coordinates(lo, la)
        x2, y2 = self.grid_to_camera_coordinates(x, y)
        return x2, y2
        
        
def main():
    game = GameObject()
    game.start_game()
    
if __name__ == '__main__':
    main()