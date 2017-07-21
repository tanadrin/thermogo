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


class GameObject:

    # GUI and map variables
    SCREEN_WIDTH = 182
    SCREEN_HEIGHT = SCREEN_WIDTH/2+1
    # Height of GUI pane on bottom of the screen, the "infobar"
    INFOBAR_HEIGHT = 10
    # Size of border around game windows and menus
    MARGIN_WIDTH = 1
    # Size of the main game view
    MAX_CAMERA_WIDTH = SCREEN_WIDTH-2*MARGIN_WIDTH
    MAX_CAMERA_HEIGHT = SCREEN_HEIGHT-2*MARGIN_WIDTH
    # Size of the togglable right-hand menu
    MENU_WIDTH = 20
    # PNG font used for game
    GAME_FONT = 'assets/arial10x10.png'
    # Maximum game FPS; 1 frame is the basic unit of in-game time
    LIMIT_FPS = 20
    # Directory to save map files in
    MAP_DIRECTORY = 'map/'
    # Minimum frame intervals between GUI events
    GUI_WAIT = 0
    
    def __init__(self):
        
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
        # All objects currently being simulated in the game
        self.objects = []
        
        self.paused = False
        self.loading = False
        self.mapsize = self.SCREEN_WIDTH-self.MARGIN_WIDTH*2
        self.cursor = Cursor(0, 0)
        self.objects.append(self.cursor)
        self.gamemap = GameMap(self.mapsize)
        
        # Main libtcod console and parameters
        libtcod.console_set_custom_font(self.GAME_FONT, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'Thermonuclear Go', False)
        libtcod.sys_set_fps(self.LIMIT_FPS)
        self.con = libtcod.console_new(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Libtcod consoles for GUI
        self.game_view = libtcod.console_new(self.MAX_CAMERA_WIDTH, self.MAX_CAMERA_HEIGHT)
        self.infobar = libtcod.console_new(self.MAX_CAMERA_WIDTH, self.INFOBAR_HEIGHT)
        self.menu = libtcod.console_new(self.MENU_WIDTH, self.MAX_CAMERA_HEIGHT)
        self.gui_background = libtcod.console_new(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
    # Starting game and running main loop
    def start_game(self):
        self.camera = GameCamera(self.gamemap.WORLD_WIDTH/2,self.gamemap.WORLD_HEIGHT/2, self.MAX_CAMERA_WIDTH, self.MAX_CAMERA_HEIGHT)
        while not libtcod.console_is_window_closed():
            # Render the screen
            self.render_all()
            libtcod.console_flush()
            # Erase all objects at their old locations, before they move
            # for object in self.objects:
            #    object.clear()
            # Handle keys and exit game if needed
            exit = game.handle_keys()
            if exit:
                break
                
    def refresh_infobar(self, infobar):
        libtcod.console_clear(infobar)
        
        actual_x, actual_y = self.cursor.x % self.gamemap.WORLD_WIDTH, self.cursor.y % self.gamemap.WORLD_HEIGHT
        
        infobar_text = "Cursor grid: "+str(actual_x)+ ", "+str(actual_y)
        infobar_text2 = "Cursor lat: "+str(self.gamemap.grid[actual_x][actual_y].la)
        infobar_text3 = "Cursor long: "+str(self.gamemap.grid[actual_x][actual_y].lo)
        
        if self.gamemap.grid[actual_x][actual_y].elevation > 0:
            infobar_text4 = "Elevation: "+str(int(self.gamemap.grid[actual_x][actual_y].elevation*4000))+"m"
        else:
            infobar_text4 = "Elevation: Sea level"
        
        infobar_text5 = "s: save terrain; d: load terrain; g: gen terrain; k: hide infobar"

        libtcod.console_print(infobar, 0, 0, infobar_text)
        libtcod.console_print(infobar, 0, 1, infobar_text2)
        libtcod.console_print(infobar, 0, 2, infobar_text3)
        libtcod.console_print(infobar, 0, 3, infobar_text4)
        libtcod.console_print(infobar, 0, 4, infobar_text5)
        # Add logic here to display new infobar information as needed
        
    def refresh_main_view(self, main_view, map):
        libtcod.console_clear(main_view)
        self.draw_map(self.gamemap, main_view)
        for obj in self.objects:
            if obj.name != 'Cursor':
                self.draw_object(obj, main_view)
            if obj.name == 'Cursor':
                self.draw_grid_object(obj, main_view)
        # Add logic to display stuff on main view here
        
    def refresh_menu(self, menu):
        libtcod.console_clear(menu)
        # Add logic to change contents of menu here
        
    # While the game is running, render a solid background to use as border between other GUI elements
    def refresh_gui_background(self, gui):
        libtcod.console_clear(gui)

        for x in range(self.SCREEN_WIDTH):
            for y in range(self.SCREEN_HEIGHT):
                libtcod.console_set_char_background(gui, x, y, GREY)
        
        if self.paused == True:
            pause_text = "***PAUSED***"
            for x in range(12):
                libtcod.console_set_char_background(gui, self.camera.width-15+x, 0, DARK_BLUE)
                libtcod.console_put_char(gui, self.camera.width-15+x, 0, pause_text[x], libtcod.BKGND_NONE)
                libtcod.console_set_char_foreground(gui, self.MAX_CAMERA_WIDTH-15+x, 0, WHITE)
        
        if self.loading != False:
            loading_text = "***LOADING***"
            for x in xrange(13):
                libtcod.console_set_char_background(gui, 15+x, 0, DARK_BLUE)
                libtcod.console_put_char(gui, 15+x, 0, loading_text[x], libtcod.BKGND_NONE)
                libtcod.console_set_char_foreground(gui, 15+x, 0, WHITE)
                
    def force_gui_refresh(self):
        libtcod.console_clear(self.gui_background)
        self.refresh_gui_background(self.gui_background)
        libtcod.console_blit(self.gui_background, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)
    
    # Method for drawing the main game map on the world view
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
        
    # Method for drawing objects in the game world on the main view
    def draw_object(self, obj, console):
        pos_x, pos_y = self.spherical_to_camera_coordinates(obj.lo, obj.la)
        if pos_x is not None and obj.char != ' ':
            libtcod.console_set_default_foreground(console, obj.color)
            libtcod.console_put_char(console, pos_x, pos_y, obj.char, libtcod.BKGND_NONE)
            
    def draw_grid_object(self, obj, console):
        pos_x, pos_y = self.grid_to_camera_coordinates(obj.x, obj.y)
        if pos_x is not None and obj.char != ' ':
            libtcod.console_set_default_foreground(console, obj.color)
            libtcod.console_put_char(console, pos_x, pos_y, obj.char, libtcod.BKGND_NONE)
        
    # Rendering the main view and GUI elements
    def render_all(self):
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

    # Handling input and looped elements of the game logic
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
            self.camera.width = self.MAX_CAMERA_WIDTH - self.MENU_WIDTH
        else:
            self.camera.width = self.MAX_CAMERA_WIDTH
       
    def toggle_infobar(self):
        self.show_infobar = not self.show_infobar
        if self.show_infobar:
            self.camera.height = self.MAX_CAMERA_HEIGHT - self.INFOBAR_HEIGHT
        else:
            self.camera.height = self.MAX_CAMERA_HEIGHT
    
    # Converting world coordinates to camera coordinates
    def grid_to_camera_coordinates(self, x, y):
        x = x - self.camera.x + self.camera.width/2
        y = y - self.camera.y + self.camera.height/2
        return x, y
        
    def camera_to_grid_coordinates(self, x, y):
        x = x - self.camera.width/2 + self.camera.x
        y = y - self.camera.height/2 + self.camera.y
        return x, y
        
    def spherical_to_grid_coordinates(self, lo, la):
        # Given a latitude from -90 to 90 and a longitude from -180 to 180, return x, y on a grid from 0 to world width and 0 to world height
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