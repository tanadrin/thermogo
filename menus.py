import libtcodpy as libtcod
from colors import *

class Menu(object):
    '''
    Basically just a wrapper for a couple libtcod console functions.
    '''
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.console = libtcod.console_new(width, height)
        
    def refresh(self):
        libtcod.console_clear(self.console)
    
# Main menu that displays on game startup, and when quitting games (but not exiting)
class MainMenu(Menu):

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
        super(MainMenu, self).__init__(width, height)
        libtcod.console_set_default_background(self.console, MENU_BACKGROUND_COLOR)
        libtcod.console_set_default_foreground(self.console, MENU_TEXT_COLOR_1)
        self.text = []
        for i in range(len(self.TEXT)):
            self.text.append(self.TEXT.get(i))
        self.current_option = 0
        
    def refresh(self):
        super(MainMenu, self).refresh()
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

class Credits(Menu):    
    '''
    Non-interacting menu; replaces main menu when active 
    '''
    
    # Text to display in the menu, by line number
    BANNER_TEXT = 'Credits:'
    TEXT = {
        0 : 'Design & programming by Tanadrin',
        1 : 'using the Doryen library',
        2 : 'http://roguecentral.org/doryen/libtcod/',
        3 : 'Thanks to Petronius & Kekrops for Python help',
        4 : '',
        5 : '',
        6 : 'Esc to quit, enter to return to main menu'
    }
    
    def __init__(self, width, height):
        super(Credits, self).__init__(width, height)
        libtcod.console_set_default_background(self.console, MENU_BACKGROUND_COLOR)
        libtcod.console_set_default_foreground(self.console, MENU_TEXT_COLOR_1)
        self.text = []
        for i in range(len(self.TEXT)):
            self.text.append(self.TEXT.get(i))
        
    def refresh(self):
        super(Credits, self).refresh()
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

class Infobar(Menu):
    '''
    In-game panel displaying messages at the bottom of the screen
    '''
    
    LINE_START = "> "
    
    def __init__(self, width, height):
        super(Infobar, self).__init__(width, height)
        
        self.show = False
        
        # Where to retrieve messages for display
        self.message_queue = None
        
        # Where to store messages being displayed
        self.messages = []
        self.max_messages = self.height
        for i in range(0, self.max_messages):
            self.messages.append(["", WHITE])

    def refresh(self):
        super(Infobar, self).refresh()
        if self.message_queue != None:
            self.update_infobar_text()
            for i in range(0, len(self.messages)):
                libtcod.console_set_default_foreground(self.console, self.messages[i][1])
                libtcod.console_print(self.console, 0, (self.height-2)-i, self.LINE_START + self.messages[i][0])
        
    def update_infobar_text(self, step_or_all = 'all'):
        '''
        Takes messages off the front of the message queue and adds them to the
        front of self.text. Can either do it with one message ('step') or with
        all messages. Default behavior is all.
        '''
        queue = self.message_queue.queue
        if step_or_all == 'all':
            for i in range(0, len(queue)):
                message = self.message_queue.retrieve_latest()
                self.messages.insert(0, message)
        elif step_or_all == 'step':
                message = self.message_queue.retrieve_latest()
                self.messages.insert(0, message)
        else:
            print 'Please specify \'step\' or \'all\' for Infobar.update_infobar_text()'
            return
        del self.messages[self.max_messages - 1:]

           
class SideMenu(Menu):
    '''
    In-game panel that displays unit and map information, along the right side
    of the screen
    '''
    # Text to display in the sidemenu, by line number
    TEXT = {
        0 : 'Power Projection:',
        1 : 'Total supplies: ',
        2 : 'Owned bases: ',
        3 : 'Owned armies: ',
        4 : 'Owned fleets: ',
        5 : '////////////////////',
        6 : '', # Lat and long
        7 : '', # Elevation
        8 : '', # Territory owner
        9 : '////////////////////'
    }
    def __init__(self, width, height):
        super(SideMenu, self).__init__(width, height)
        self.show = False
        self.text = []
        for i in range(0, self.height):
            self.text.append("")
                
        self.cursor_coordinates = ''
        self.cursor_elevation = ''
        
        self.power_projection = '0'
        
    def refresh(self):
        super(SideMenu, self).refresh()
        self.update_sidemenu_text()
        for i in range(0, len(self.text)):
            libtcod.console_print(self.console, 0, i, self.text[i])
        
    def update_sidemenu_data(self, cursor, active_player):
        if active_player.power_projection < 10:
            self.power_projection = ' '+str(active_player.power_projection)
        else:
            self.power_projection = str(active_player.power_projection)
        if cursor != None:
            self.cursor_coordinates = str(cursor.la)+' ,'+str(cursor.lo)
            if cursor.elevation > 0:
                self.cursor_elevation = str(cursor.elevation*4000)+'m'
            elif cursor.elevation <= 0:
                self.cursor_elevation = "Sea level"
        else:
            pass
            
    def update_sidemenu_text(self):
        for line, text in self.TEXT.items():
            if line == 0:
                self.text[line] = self.TEXT[line]+self.power_projection
            elif line == 6:
                self.text[line] = self.TEXT[line]+self.cursor_coordinates
            elif line == 7:
                self.text[line] = self.TEXT[line]+self.cursor_elevation
            else:
                self.text[line] = self.TEXT[line]