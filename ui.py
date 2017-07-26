import libtcodpy as libtcod
from colors import *

class Infobar:

    # Text to display in the infobar, by line number
    TEXT = {
        0 : 'Cursor cartesian: ',
        1 : 'Cursor coordinates: ',
        2 : 'Cursor elevation: ',
        3 : 's: save terrain; d: load terrain; g: gen terrain; k: hide infobar'
    }

    def __init__(self, width, height):
        self.show = False
        self.width = width
        self.height = height
        self.console = libtcod.console_new(width, height)
        self.text = []
        for i in range(0, self.height):
            self.text.append("")
                
        self.cursor_cartesian = ''
        self.cursor_coordinates = ''
        self.cursor_elevation = ''

    def refresh(self):
        self.update_infobar_text()
        libtcod.console_clear(self.console)
        for i in range(0, len(self.text)):
            libtcod.console_print(self.console, 0, i, self.text[i])
        
    def update_infobar_data(self, cursor):
        if cursor != None:
            self.cursor_cartesian = str(cursor.xm)+' ,'+str(cursor.ym)
            self.cursor_coordinates = str(cursor.la)+' ,'+str(cursor.lo)
            if cursor.elevation > 0:
                self.cursor_elevation = str(cursor.elevation*4000)+'m'
            else:
                self.cursor_elevation = "Sea level"
        else:
            pass
        
    def update_infobar_text(self):
        for line, text in self.TEXT.items():
            if line == 0:
                self.text[line] = self.TEXT[line]+self.cursor_cartesian
            elif line == 1:
                self.text[line] = self.TEXT[line]+self.cursor_coordinates
            elif line == 2:
                self.text[line] = self.TEXT[line]+self.cursor_elevation
            else:
                self.text[line] = self.TEXT[line]
        
class Menu:
    def __init__(self, width, height):
        self.show = False
        self.height = height
        self.width = width
        self.console = libtcod.console_new(width, height)
        
    def refresh(self):
        libtcod.console_clear(self.console)
        
class GameView:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.console = libtcod.console_new(width, height)
        
    def refresh(self, gamemap, camera, objects):
        '''
        Refreshes and draws the map and list of objects in the main game view
        from the perspective of the specified camera.
        '''
        libtcod.console_clear(self.console)
        self.draw_map(gamemap, camera)
        if objects != None:
            for object in objects:
                self.draw_cartesian_object(object, camera)
        
    
    def draw_map(self, gamemap, camera):
        for x in range(camera.width):
            for y in range(camera.height):
                pos_x, pos_y = self.camera_to_cartesian(x, y, camera)
                if pos_y < 0 or pos_y >= gamemap.world_height:
                    libtcod.console_put_char(self.console, x, y, ' ', libtcod.BKGND_NONE)
                else:
                    pos_x = pos_x % gamemap.world_width
                    libtcod.console_set_default_foreground(self.console, gamemap.grid[pos_x][pos_y].color)
                    libtcod.console_put_char(self.console, x, y, gamemap.grid[pos_x][pos_y].char, libtcod.BKGND_NONE)
        
    def camera_to_cartesian(self, x, y, camera):
        '''
        Takes a set of x, y coordinates relative to the specified camera and
        returns Cartesian coordinates in the game world. An input of 0, 0
        corresponds to the top left of the camera's FOV.
        '''
        x, y = x - camera.width/2 + camera.x, y - camera.height/2 + camera.y
        return x, y
        
    def cartesian_to_camera(self, x, y, camera):
        '''
        Takes a set of x, y coordinates and returns the coordinates relative to
        the specified camera. The origin is the top left of the camera's FOV
        '''
        x, y = x - camera.x + camera.width/2, y - camera.y + camera.height/2
        return x, y
    
    def draw_cartesian_object(self, object, camera):
        x, y = self.cartesian_to_camera(object.x, object.y, camera)
        if x is not None and object.char != ' ':
            libtcod.console_set_default_foreground(self.console, object.color)
            libtcod.console_put_char(self.console, x, y, object.char, libtcod.BKGND_NONE)
            
    def lock_cursor_to_view(self, camera, cursor):
        '''
        Keeps cursor bounded within camera view
        '''
            
        x, y = self.cartesian_to_camera(cursor.x, cursor.y, camera)
            
        if x < 0:
            cursor.x, _ = self.camera_to_cartesian(0, 0, camera)
        if x > camera.width-1:
            cursor.x, _ = self.camera_to_cartesian(camera.width-1, 0)
        if y < 0:
            _, cursor.y = self.camera_to_cartesian(0, 0, camera)
        if y > camera.height-1:
            _, cursor.y = self.camera_to_cartesian(0, camera.height-1)
            
class GameUI:
    
    def __init__(self, screen_width, screen_height, menu_width, infobar_height, margin_width = 1, game_font = 'assets/arial10x10.png'):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.margin_width = margin_width
        self.max_camera_width = self.screen_width-2*self.margin_width
        self.max_camera_height = self.screen_height-2*self.margin_width
        
        self.paused = False
        self.loading = False
        self.cursor = None
        self.camera = None
    
        # Main console
        libtcod.console_set_custom_font(game_font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(self.screen_width, self.screen_height, 'Thermonuclear Go', False)
        self.main_console = libtcod.console_new(self.screen_width, self.screen_height)
        # Libtcod consoles for GUI
        self.game_view = GameView(self.max_camera_width, self.max_camera_height)
        self.infobar = Infobar(self.max_camera_width, infobar_height)
        self.menu = Menu(menu_width, self.max_camera_height)
        self.gui_background = libtcod.console_new(self.screen_width, self.screen_height)
        
    def refresh_all(self, gamemap, camera, objects, cursor):
        self.render_all(gamemap, camera, objects, cursor)
        libtcod.console_flush()
        
    # While the game is running, render a solid background to use as border between other GUI elements
    def refresh_gui_background(self, console):
    
        libtcod.console_clear(console)
        
        self.background_color = DARK_GRAY
        for x in range(self.screen_width):
            for y in range(self.screen_height):
                libtcod.console_set_char_background(
                    console, 
                    x, 
                    y, 
                    self.background_color
                )
                
        if self.paused == True:
            pause_text = '***PAUSED***'
            for x in range(12):
                libtcod.console_set_char_background(
                    console, 
                    self.camera.width-15+x, 
                    0, 
                    DARK_GRAY
                )
                libtcod.console_put_char(
                    console, 
                    self.camera.width-15+x, 
                    0, 
                    pause_text[x], 
                    libtcod.BKGND_NONE
                )
                libtcod.console_set_char_foreground(
                    console, 
                    self.camera.width-15+x, 
                    0, 
                    WHITE
                )
                
        if self.loading != False:
        
            loading_text = '***LOADING***'
            
            for x in xrange(13):
                libtcod.console_set_char_background(
                    console, 
                    15+x, 
                    0, 
                    DARK_TEAL
                )
                libtcod.console_put_char(
                    console, 
                    15+x, 
                    0, 
                    loading_text[x], 
                    libtcod.BKGND_NONE
                )
                libtcod.console_set_char_foreground(
                    console, 
                    15+x, 
                    0, 
                    WHITE
                 )
                 
    def force_gui_refresh(self):
        libtcod.console_clear(self.gui_background)
        self.refresh_gui_background(self.gui_background)
        libtcod.console_blit(self.gui_background, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)

    # Rendering the main view and GUI elements
    def render_all(self, gamemap = None, camera = None, objects = None, cursor = None):
        # blit the contents of 'con' to the root console
        libtcod.console_blit(
            self.main_console, 
            0, 
            0, 
            self.screen_width, 
            self.screen_height, 
            0, 
            0, 
            0
        )
        # blit the contents of the GUI background to the root console
        self.refresh_gui_background(self.gui_background)
        libtcod.console_blit(
            self.gui_background, 
            0, 
            0, 
            self.screen_width, 
            self.screen_height, 
            0, 
            0, 
            0
        )
        # blit the contents of the game_view to the root console
        if gamemap != None and camera != None:
            self.game_view.refresh(
                gamemap, 
                camera, 
                objects
            )
            libtcod.console_blit(
                self.game_view.console, 
                0, 
                0, 
                camera.width, 
                camera.height, 
                0, 
                1, 
                1
            )
            
        # likewise for the infobar, if we're showing it
        if self.infobar.show == True and gamemap != None and camera != None:
            self.infobar.update_infobar_data(self.cursor)
            self.infobar.refresh()
            libtcod.console_blit(
                self.infobar.console, 
                0, 
                0, 
                camera.width, 
                self.infobar.height-self.margin_width, 
                0, self.margin_width, 
                self.screen_height - self.infobar.height
            )
            
        # if we're showing the right-side menu, it as well
        if self.menu.show == True and gamemap != None and camera != None:
            self.menu.refresh()
            libtcod.console_blit(
                self.menu.console, 
                0, 
                0, 
                self.menu.width - self.margin_width, 
                self.screen_height - self.margin_width*2, 
                0, 
                self.screen_width - self.menu.width, 
                1
            )
            
    def toggle_menu(self, camera):
        self.menu.show = not self.menu.show
        if self.menu.show:
            camera.width = self.max_camera_width - self.menu.width
        else:
            camera.width = self.max_camera_width
    
    def toggle_infobar(self, camera):
        self.infobar.show = not self.infobar.show
        if self.infobar.show:
            camera.height = self.max_camera_height - self.infobar.height
        else:
            camera.height = self.max_camera_height

    def cycle(self):
        '''
        Periodic UI events governed by the main game loop
        '''
        if self.cursor != None:
            self.cursor.blink()