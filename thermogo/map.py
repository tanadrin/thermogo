import shelve
import tcod as libtcod

from decimal import Decimal

from thermogo.helpers import spherical_to_cartesian

# A latitude-longitude grid with height data
class GameMap:

    def __init__(self, mapsize):
        self.world_width = mapsize
        self.world_height = self.world_width/2
        self.world_radius = 5000 # Radius in km; determines distances on the surface
        self.grid = []
        self.world_noise = libtcod.noise_new(3)
        self.name = "map_name"
        for x in xrange(self.world_width):
            row = []
            for y in xrange(self.world_height):
                row.append(GridCoordinate(x, y, self.world_width, self.world_height, self.world_noise))
            self.grid.append(row)
        libtcod.noise_delete(self.world_noise)
            
    def save_map(self):
        file_ = shelve.open(str(self.name), "n")
        file_["grid"] = self.grid
        file_.close()
                
    def load_map(self, map="map_name"):
        file_ = shelve.open(map, "r")
        self.grid = file_["grid"]
        file_.close()
        
    def gen_map(self):

        self.grid = []
        self.world_noise = libtcod.noise_new(3)

        for x in xrange(self.world_width):
            row = []
            for y in xrange(self.world_height):
                row.append(GridCoordinate(x, y, self.world_width, self.world_height, self.world_noise))
            self.grid.append(row)

        libtcod.noise_delete(self.world_noise)

        
class GridCoordinate:
        
    # Elevation parameters, can be freely altered. Max elevation will affect 
    # what appears as mountains; min elevation what appears as deep sea.
    #
    # LANDMASS_SIZE is actually the radius of the spherical surface used to 
    # sample the noise function; a larger radius means smaller apparent
    # landmass sizes. DETAIL is the number of octaves in the noise and affects
    # how crinkly the landmasses are.
    LANDMASS_SIZE = 2
    DETAIL = 64.0

    def __init__(self, x, y, world_width, world_height, world_noise):
        
        self.x, self.y = x, y
        self.la = ((Decimal(self.y)*180)/Decimal(world_height))-90
        self.lo = ((Decimal(self.x)*360)/Decimal(world_width))-180
        self.char = "#"
        self.color = libtcod.Color(255,255,255)
        
        # Sampling 3d noise to get the shape of the landmasses
        x, y, z = spherical_to_cartesian(self.la, self.lo, self.LANDMASS_SIZE)
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