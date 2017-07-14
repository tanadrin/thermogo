import random
import shelve
import os.path
import math
#The Doryen Library - Documentation: http://roguecentral.org/doryen/data/libtcod/doc/1.5.1/index2.html
import libtcodpy as libtcod
from decimal import *

class GameObject:

    #GUI and map variables
    SCREEN_WIDTH = 182
    SCREEN_HEIGHT = SCREEN_WIDTH/2+1
    #Height of GUI pane on bottom of the screen, the "infobar"
    INFOBAR_HEIGHT = 10
    #Size of border around game windows and menus
    MARGIN_WIDTH = 1
    #Size of the main game view
    CAMERA_WIDTH = SCREEN_WIDTH-2*MARGIN_WIDTH
    CAMERA_HEIGHT = SCREEN_HEIGHT-2*MARGIN_WIDTH
    #Size of the togglable right-hand menu
    MENU_WIDTH = 20
    #PNG font used for game
    GAME_FONT = 'arial10x10.png'
    #Maximum game FPS; 1 frame is the basic unit of in-game time
    LIMIT_FPS = 20
    #Directory to save map files in
    MAP_DIRECTORY = 'map/'
    #Minimum frame intervals between GUI events
    GUI_WAIT = 0
    
    def __init__(self):
        
        #Game state and GUI control variables
        #Whether the additional views are shown or hidden
        self.show_menu = False
        self.show_infobar = False
        #Whether we're using real time or taking turns
        self.time = "free"
        #Input control variable; used to prevent some actions from happening too often
        self.gui_wait = 0
        #Main camera object
        self.camera = None
        #All objects currently being simulated in the game
        self.objects = []
        
        self.paused = False
        self.loading = False
        self.mapsize = self.SCREEN_WIDTH-self.MARGIN_WIDTH*2
        self.cursor = Cursor(0, 0)
        self.objects.append(self.cursor)
        self.gamemap = GameMap(self.mapsize)
        
        #Main libtcod console and parameters
        libtcod.console_set_custom_font(self.GAME_FONT, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'Thermonuclear Go', False)
        libtcod.sys_set_fps(self.LIMIT_FPS)
        self.con = libtcod.console_new(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        #Libtcod consoles for GUI
        self.game_view = libtcod.console_new(self.CAMERA_WIDTH, self.CAMERA_HEIGHT)
        self.infobar = libtcod.console_new(self.CAMERA_WIDTH, self.INFOBAR_HEIGHT)
        self.menu = libtcod.console_new(self.MENU_WIDTH, self.CAMERA_HEIGHT)
        self.gui_background = libtcod.console_new(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
    #Starting game and running main loop
    def start_game(self):
        self.camera = GameCamera(self.gamemap.WORLD_WIDTH/2,self.gamemap.WORLD_HEIGHT/2)
        while not libtcod.console_is_window_closed():
            #Render the screen
            self.render_all()
            libtcod.console_flush()
            #Erase all objects at their old locations, before they move
            #for object in self.objects:
            #    object.clear()
            #Handle keys and exit game if needed
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
        #Add logic here to display new infobar information as needed
        
    def refresh_main_view(self, main_view, map):
        libtcod.console_clear(main_view)
        self.draw_map(self.gamemap, main_view)
        for obj in self.objects:
            if obj.name != 'Cursor':
                self.draw_object(obj, main_view)
            if obj.name == 'Cursor':
                self.draw_grid_object(obj, main_view)
        #Add logic to display stuff on main view here
        
    def refresh_menu(self, menu):
        libtcod.console_clear(menu)
        #Add logic to change contents of menu here
        
    #While the game is running, render a solid background to use as border between other GUI elements
    def refresh_gui_background(self, gui):
        libtcod.console_clear(gui)
        for x in range(self.SCREEN_WIDTH):
            for y in range(self.SCREEN_HEIGHT):
                libtcod.console_set_char_background(gui, x, y, libtcod.Color(100, 100, 100))
        if self.paused == True:
            pause_text = "***PAUSED***"
            for x in range(12):
                libtcod.console_set_char_background(gui, self.CAMERA_WIDTH-15+x, 0, libtcod.Color(100, 100, 200))
                libtcod.console_put_char(gui, self.CAMERA_WIDTH-15+x, 0, pause_text[x], libtcod.BKGND_NONE)
                libtcod.console_set_char_foreground(gui, self.CAMERA_WIDTH-15+x, 0, libtcod.Color(255, 255, 255))
        if self.loading != False:
            loading_text = "***LOADING***"
            for x in xrange(13):
                libtcod.console_set_char_background(gui, 15+x, 0, libtcod.Color(100, 100, 200))
                libtcod.console_put_char(gui, 15+x, 0, loading_text[x], libtcod.BKGND_NONE)
                libtcod.console_set_char_foreground(gui, 15+x, 0, libtcod.Color(255, 255, 255))
                
    def force_gui_refresh(self):
        libtcod.console_clear(self.gui_background)
        self.refresh_gui_background(self.gui_background)
        libtcod.console_blit(self.gui_background, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)
    
    #Method for drawing the main game map on the world view
    def draw_map(self, map, console):
        for x in range(self.CAMERA_WIDTH):
            for y in range(self.CAMERA_HEIGHT):
                (pos_x, pos_y) = self.camera_to_grid_coordinates(x, y)
                if pos_y < 0 or pos_y >= map.WORLD_HEIGHT:
                    libtcod.console_put_char(console, x, y, " ", libtcod.BKGND_NONE)
                else:
                    pos_x = pos_x % map.WORLD_WIDTH
                    libtcod.console_set_default_foreground(console, map.grid[pos_x][pos_y].color)
                    libtcod.console_put_char(console, x, y, map.grid[pos_x][pos_y].char, libtcod.BKGND_NONE)
        
    #Method for drawing objects in the game world on the main view
    def draw_object(self, obj, console):
        (pos_x, pos_y) = self.spherical_to_camera_coordinates(obj.lo, obj.la)
        if pos_x is not None and obj.char != ' ':
            libtcod.console_set_default_foreground(console, obj.color)
            libtcod.console_put_char(console, pos_x, pos_y, obj.char, libtcod.BKGND_NONE)
            
    def draw_grid_object(self, obj, console):
        (pos_x, pos_y) = self.grid_to_camera_coordinates(obj.x, obj.y)
        if pos_x is not None and obj.char != ' ':
            libtcod.console_set_default_foreground(console, obj.color)
            libtcod.console_put_char(console, pos_x, pos_y, obj.char, libtcod.BKGND_NONE)
        
    #Rendering the main view and GUI elements
    def render_all(self):
        #blit the contents of "con" to the root console
        libtcod.console_blit(self.con, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)
        #blit the contents of the GUI background to the root console
        self.refresh_gui_background(self.gui_background)
        libtcod.console_blit(self.gui_background, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)
        #blit the contents of the game_view to the root console
        self.refresh_main_view(self.game_view, self.gamemap)
        libtcod.console_blit(self.game_view, 0, 0, self.CAMERA_WIDTH, self.CAMERA_HEIGHT, 0, 1, 1)
        #likewise for the infobar, if we're showing it
        if self.show_infobar == True:
            self.refresh_infobar(self.infobar)
            libtcod.console_blit(self.infobar, 0, 0, self.CAMERA_WIDTH, self.INFOBAR_HEIGHT-self.MARGIN_WIDTH, 0, self.MARGIN_WIDTH, self.SCREEN_HEIGHT - self.INFOBAR_HEIGHT)
        #if we're showing the right-side menu, it as well
        if self.show_menu == True:
            self.refresh_menu(self.menu)
            libtcod.console_blit(self.menu, 0, 0, self.MENU_WIDTH - self.MARGIN_WIDTH, self.SCREEN_HEIGHT - self.MARGIN_WIDTH*2, 0, self.SCREEN_WIDTH - self.MENU_WIDTH, 1)
            
    #Handling input and looped elements of the game logic
    def handle_keys(self):

        if self.paused == False:
            
            #Cursor movement keys
            if libtcod.console_is_key_pressed(libtcod.KEY_UP) and self.gui_wait == 0:
                self.cursor.move(0,-1)
         
            elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN) and self.gui_wait == 0:
                self.cursor.move(0,1)
         
            elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT) and self.gui_wait == 0:
                self.cursor.move(-1,0)
         
            elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT) and self.gui_wait == 0:
                self.cursor.move(1,0)
            
            #Keeps cursor bounded within camera view
            (x, y) = self.grid_to_camera_coordinates(self.cursor.x, self.cursor.y)
            if x < 0:
                self.cursor.x, _ = self.camera_to_grid_coordinates(0, 0)
            if x > self.CAMERA_WIDTH-1:
                self.cursor.x, _ = self.camera_to_grid_coordinates(self.CAMERA_WIDTH-1, 0)
            if y < 0:
                _, self.cursor.y = self.camera_to_grid_coordinates(0, 0)
            if y > self.CAMERA_HEIGHT-1:
                _, self.cursor.y = self.camera_to_grid_coordinates(0, self.CAMERA_HEIGHT-1)
            

        if self.gui_wait > 0:
            self.gui_wait -=1
        
        if self.cursor != None:
            self.cursor.blink()

        if self.time == "free":
            key = libtcod.console_check_for_keypress()  #real-time
     
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            #Alt+Enter: toggle fullscreen
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
     
        elif key.vk == libtcod.KEY_ESCAPE:
            return True  #exit game

        #Pause and unpause the game
        '''
        if libtcod.console_is_key_pressed(libtcod.KEY_SPACE):
            if self.gui_wait == 0:
                if self.paused == True:
                    self.paused = False
                elif self.paused == False:
                    self.paused = True
                self.gui_wait = self.GUI_WAIT
            '''
        
        if key.vk == libtcod.KEY_CHAR:
            #Show or hide right-side menu
            if key.c == ord('l') and self.show_menu == False:
                self.show_menu = True
                self.CAMERA_WIDTH = self.CAMERA_WIDTH - self.MENU_WIDTH
            elif key.c == ord('l') and self.show_menu == True:
                self.show_menu = False
                self.CAMERA_WIDTH = self.CAMERA_WIDTH + self.MENU_WIDTH
                
            #Show or hide infobar
            elif key.c == ord('k') and self.show_infobar == False:
                self.show_infobar = True
                self.CAMERA_HEIGHT = self.CAMERA_HEIGHT - self.INFOBAR_HEIGHT
            elif key.c == ord('k') and self.show_infobar == True:
                self.show_infobar = False
                self.CAMERA_HEIGHT = self.CAMERA_HEIGHT + self.INFOBAR_HEIGHT
                
            #Pans game camera left or right
            elif key.c == ord('['):
                self.camera.move(-1,0)
            elif key.c == ord(']'):
                self.camera.move(1,0)
            elif key.c == ord('-'):
                if self.camera.y >= self.gamemap.WORLD_HEIGHT-self.CAMERA_HEIGHT/2:
                    self.camera.y = self.gamemap.WORLD_HEIGHT-self.CAMERA_HEIGHT/2
                else:
                    self.camera.move(0,1)
            elif key.c == ord('='):
                if self.camera.y <= self.CAMERA_HEIGHT/2:
                    self.camera.y = self.CAMERA_HEIGHT/2
                else:
                    self.camera.move(0,-1)
                
            #Save and load maps for later use
            elif key.c == ord("s"):
                self.gamemap.save_map()
            elif key.c == ord("d"):
                self.gamemap.load_map()
            elif key.c == ord("g"):
                self.gamemap.gen_map()

    
    #Converting world coordinates to camera coordinates
    def grid_to_camera_coordinates(self, x, y):
        (x, y) = (x - self.camera.x + self.CAMERA_WIDTH/2, y - self.camera.y + self.CAMERA_HEIGHT/2)
        return (x, y)
        
    def camera_to_grid_coordinates(self, x, y):
        (x, y) = (x - self.CAMERA_WIDTH/2 + self.camera.x, y - self.CAMERA_HEIGHT/2 + self.camera.y)
        return (x, y)
        
    def spherical_to_grid_coordinates(self, lo, la):
        #Given a latitude from -90 to 90 and a longitude from -180 to 180, return x, y on a grid from 0 to world width and 0 to world height
        x = int((lo + 90)*(self.gamemap.WORLD_WIDTH/180))
        y = int((la + 180)*(self.gamemap.WORLD_HEIGHT/90))
        return (x, y)
    
    def spherical_to_camera_coordinates(self, lo, la):
        (x, y) = self.spherical_to_grid_coordinates(lo, la)
        (x2, y2) = self.grid_to_camera_coordinates(x, y)
        return (x2, y2)
        

            
class Unit:
    def __init__(self, x, y, objects):
        self.x = x
        self.y = y
        self.char = "@"
        self.color = libtcod.Color(255,255,255)
        self.name = "Unit"
    
    #Generic movement on a sphere. Kind of.
    #Uses Decimal() since this is actual game-world coords. on surface of the sphere
    def move(self, dlo, dla):
        self.lo += Decimal(dlo)
        if self.lo < Decimal(-180):
            self.lo += Decimal(360)
        elif self.lo > Decimal (180):
            self.lo += Decimal (-360)
        self.la += Decimal(dla)
        if self.la < Decimal(-90):
            self.la = Decimal(-90)
        elif self.la > Decimal(90):
            self.la = Decimal(90)
                
    #Hide the object; draw_object won't draw objects represented by " ".
    #def clear(self):
    #    libtcod.console_put_char(game.con, self.x, self.y, " ", libtcod.BKGND_NONE)

class Cursor(Unit):
    def __init__(self, x, y):
        #lo and la are longitude and latitude
        self.x = x
        self.y = y
        self.char = "X"
        self.color = libtcod.Color(255,255,0)
        self.wait = 5
        self.name = "Cursor"
    
    #Uses Decimal() since this is actual game-world coords. on surface of the sphere
    def move(self, x, y):
        self.x += x
        self.y += y
        self.char = "X"
        self.wait = 4
    def blink(self):
        if self.wait > 0:
            self.wait += -1
        elif self.wait == 0 and self.char == "X":
            self.char = " "
            self.wait = 5
        elif self.wait == 0 and self.char == " ":
            self.char = "X"
            self.wait = 5

#Used to keep track of what to render onscreen, and to differentiate the position of the camera from the position of the player, in case we want to move one and not the other
class GameCamera:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    #Doesn't use Decimal() since it's only relative to the grid projection of the gameworld sphere
    def move(self, dx, dy):
        self.x += dx
        self.y += dy

#Given a set of spherical coordinates will return Cartesian coordinates
def spherical_to_cartesian(la, lo, radius):
    x = radius*math.sin(math.radians(90-la))*math.cos(math.radians(lo))
    y = radius*math.sin(math.radians(90-la))*math.sin(math.radians(lo))
    z = radius*math.cos(math.radians(90-la))
    return x, y, z
        
class GridCoordinate:
    def __init__(self, x, y, world_width, world_height, world_noise):
        #Elevation parameters, can be freely altered. Max elevation will affect what appears as mountains; min elevation what appears as deep sea.
        #LANDMASS_SIZE is actually the radius of the spherical surface used to sample the noise function; a larger radius means smaller apparent
        #landmass sizes. DETAIL is the number of octaves in the noise and affects how crinkly the landmasses are.
        self.LANDMASS_SIZE = 2
        self.DETAIL = 64.0
        
        self.x = x
        self.y = y
        self.la = ((Decimal(self.y)*180)/Decimal(world_height))-90
        self.lo = ((Decimal(self.x)*360)/Decimal(world_width))-180
        self.char = "#"
        self.color = libtcod.Color(255,255,255)
        
        #Sampling 3d noise to get the shape of the landmasses
        (x, y, z) = spherical_to_cartesian(self.la, self.lo, self.LANDMASS_SIZE)
        self.elevation = libtcod.noise_get_fbm(world_noise,[float(x),float(y),float(z)],self.DETAIL)
        if 1 >= self.elevation > 0.8:
            self.color = libtcod.Color(202,163,85)
            self.char = "A"
        elif 0.8 >= self.elevation > 0.6:
            self.color = libtcod.Color(145,162,78)
            self.char = "a"
        elif 0.6 >= self.elevation > 0.4:
            self.color = libtcod.Color(129,162,76)
            self.char = "n"
        elif 0.4 >= self.elevation > 0.2:
            self.color = libtcod.Color(82,162,71)
            self.char = "8"
        elif 0.2 >= self.elevation > 0.0:
            self.color = libtcod.Color(49,162,67)
            self.char = "8"
        elif 0.0 >= self.elevation > -0.5:
            self.color = libtcod.Color(50,50,220)
            self.char = "S"
        elif -0.5 >= self.elevation >= -1:
            self.color = libtcod.Color(0,0,150)
            self.char = "s"
            
    


#A latitude-longitude grid with height data
class GameMap:
    def __init__(self, mapsize):
        self.WORLD_WIDTH = mapsize
        self.WORLD_HEIGHT = self.WORLD_WIDTH/2
        self.world_radius = 5000 #Radius in km; determines distances on the surface
        self.grid = []
        self.world_noise = libtcod.noise_new(3)
        self.name = "map_name"
        for x in xrange(self.WORLD_WIDTH):
            row = []
            for y in xrange(self.WORLD_HEIGHT):
                row.append(GridCoordinate(x, y, self.WORLD_WIDTH, self.WORLD_HEIGHT, self.world_noise))
            self.grid.append(row)
        libtcod.noise_delete(self.world_noise)
            
    def save_map(self):
        file = shelve.open(str(self.name), "n")
        file["grid"] = self.grid
        file.close()
                
    def load_map(self, map="map_name"):
        file = shelve.open(map, "r")
        self.grid = file["grid"]
        file.close()
        
    def gen_map(self):
        self.grid = []
        self.world_noise = libtcod.noise_new(3)
        for x in xrange(self.WORLD_WIDTH):
            row = []
            for y in xrange(self.WORLD_HEIGHT):
                row.append(GridCoordinate(x, y, self.WORLD_WIDTH, self.WORLD_HEIGHT, self.world_noise))
            self.grid.append(row)
        libtcod.noise_delete(self.world_noise)
        
def main():
    global game
    game = GameObject()
    game.start_game()
    
if __name__ == '__main__':
    main()