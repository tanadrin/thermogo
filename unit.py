class Unit:
    def __init__(self, x, y, objects):
        self.x = x
        self.y = y
        self.char = '@'
        self.color = libtcod.Color(255,255,255)
        self.name = 'Unit'
    
    #Marks object to be removed by cleanup function
    def remove_unit(self):
        self.char = " "
        self.name = "DEAD"
        self.x = -1
        self.y = -1
        
    def move(self, x, y):
        self.x += x
        self.y += y
    
    #Generic movement on a sphere. Kind of.
    #Uses Decimal() since this is actual game-world coords. on surface of the sphere
    '''def move(self, dlo, dla):
        self.lo += Decimal(dlo)
        if self.lo < Decimal(-180):
            self.lo += Decimal(360)
        elif self.lo > Decimal (180):
            self.lo += Decimal (-360)
        self.la += Decimal(dla)
        if self.la < Decimal(-90):
            self.la = Decimal(-90)
        elif self.la > Decimal(90):
            self.la = Decimal(90)'''
                
    #Hide the object; draw_object won't draw objects represented by ' '.
    #def clear(self):
    #    libtcod.console_put_char(game.con, self.x, self.y, ' ', libtcod.BKGND_NONE)
    
class Base(Unit):
    def __init__(self, x, y, objects, player):
        self.x = x
        self.y = y
        self.char = "#"
        owner = player
        self.color = player.color
        objects.append(self)
        player.owned_objects.append(self)