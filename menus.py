import libtcodpy as libtcod
from colors import *

# Main menu that displays on game startup, and when quitting games (but not exiting)
class MainMenu:

    # Text to display in the menu, by line number
    BANNER_TEXT = 'Thermonuclear Go'
    TEXT = {
        0 : 'N: New game ',
        1 : 'L: Load game ',
        2 : 'M: Multiplayer ',
        3 : 'O: Options',
        4 : 'H: Help',
        5 : 'C: Credits',
        6 : 'Esc: Exit'
    }
    HOTKEYS = {
        0 : 'new_game',
        1 : 'load_game',
        2 : 'multiplayer',
        3 : 'options',
        4 : 'help',
        5 : 'credits',
        6 : 'exit'
    }

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.console = libtcod.console_new(width, height)
        libtcod.console_set_default_background(self.console, MENU_BACKGROUND_COLOR)
        libtcod.console_set_default_foreground(self.console, MENU_TEXT_COLOR_1)
        self.text = []
        for i in range(len(self.TEXT)):
            self.text.append(self.TEXT.get(i))
        self.current_option = 0
        
    def refresh(self):
        libtcod.console_clear(self.console)
        libtcod.console_print(
            self.console,
            self.width/2 - len(self.BANNER_TEXT)/2, 
            self.height/2 - len(self.text)/2 - 2, 
            self.BANNER_TEXT
        )
        
        for i in range(0, len(self.text)):
            if i == self.current_option:
                libtcod.console_set_default_background(self.console, MENU_HIGHLIGHT_COLOR)
                libtcod.console_set_default_foreground(self.console, MENU_TEXT_COLOR_2)
            libtcod.console_print(
                self.console,
                self.width/2 - len(self.BANNER_TEXT)/2, 
                self.height/2 - len(self.text)/2 + i, 
                self.text[i]
            )
            libtcod.console_set_default_background(self.console, MENU_BACKGROUND_COLOR)
            libtcod.console_set_default_foreground(self.console, MENU_TEXT_COLOR_1)
            
            
    def scroll(self, i):
        self.current_option += i
        if self.current_option > len(self.text)-1:
            self.current_option = 0
        if self.current_option < 0:
            self.current_option = len(self.text)-1
            
    def action_select(self):
        return self.HOTKEYS.get(self.current_option)
        
    def key_select(self, char):
        if char == 'n':
            return self.HOTKEYS.get(0)
        elif char == 'l':
            return self.HOTKEYS.get(1)
        elif char == 'm':
            return self.HOTKEYS.get(2)
        elif char == 'o':
            return self.HOTKEYS.get(3)
        elif char == 'h':
            return self.HOTKEYS.get(4)
        elif char == 'c':
            return self.HOTKEYS.get(5)

# Non-interacting menu; replaces main menu when active 
class Credits:    
    # Text to display in the menu, by line number
    BANNER_TEXT = 'Credits:'
    TEXT = {
        0 : 'Design & Programming by Tanadrin',
        1 : 'Using the Doryen library',
        2 : 'http://roguecentral.org/doryen/libtcod/',
        3 : '',
        4 : '',
        5 : '',
        6 : 'Esc to quit, enter to return to main menu'
    }
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.console = libtcod.console_new(width, height)
        libtcod.console_set_default_background(self.console, MENU_BACKGROUND_COLOR)
        libtcod.console_set_default_foreground(self.console, MENU_TEXT_COLOR_1)
        self.text = []
        for i in range(len(self.TEXT)):
            self.text.append(self.TEXT.get(i))
        
    def refresh(self):
        libtcod.console_clear(self.console)
        libtcod.console_print(
            self.console,
            self.width/2 - len(self.BANNER_TEXT)/2, 
            self.height/2 - len(self.text)/2 - 1, 
            self.BANNER_TEXT
        )
        
        for i in range(0, len(self.text)):
            libtcod.console_print(
                self.console,
                self.width/2 - len(self.BANNER_TEXT)/2, 
                self.height/2 - len(self.text)/2 + i, 
                self.text[i]
            )
            libtcod.console_set_default_background(self.console, MENU_BACKGROUND_COLOR)
            libtcod.console_set_default_foreground(self.console, MENU_TEXT_COLOR_1)
    
    def scroll(self, i):
        pass
        
    def action_select(self):
        return 'return_to_main_menu'
        
    def key_select(self, char_ord):
        pass

#In-game panel across bottom of the screen
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

#In-game panel on right side of screen                
class SideMenu:
    def __init__(self, width, height):
        self.show = False
        self.height = height
        self.width = width
        self.console = libtcod.console_new(width, height)
        
    def refresh(self):
        libtcod.console_clear(self.console)