import libtcodpy as libtcod
from decimal import Decimal
from colors import *
from sphere import *
from unit import *

# A latitude-longitude grid with height data
class GameMap(object):

    RESOURCE_THRESHHOLD = 0.9

    # Radius in km; determines distances on the surface
    WORLD_RADIUS = 5000
    
    def __init__(self, mapsize, resources):
        self.world_width = mapsize
        self.world_height = self.world_width/2
        self.grid = []
        self.world_noise = libtcod.noise_new(3)
        self.resource_noise = libtcod.noise_new(3)
        self.name = 'map_name'
        for x in xrange(self.world_width):
            row = []
            for y in xrange(self.world_height):
                row.append(GridCoordinate(x, y, self.world_width, self.world_height, self.world_noise, self.resource_noise))
            self.grid.append(row)
        libtcod.noise_delete(self.world_noise)
        libtcod.noise_delete(self.resource_noise)
        for x in xrange(self.world_width):
            for y in xrange(self.world_height):
                self.grid[x][y].neighbors = get_neighbors(self, x, y)
                
        # Spawn resource nodes where the resource density is sufficiently high
        for x in xrange(self.world_width):
            for y in xrange(self.world_height):
                if self.grid[x][y].resource_density > self.RESOURCE_THRESHHOLD:
                    new_node = ResourceNode(x, y, resources)
                    print x, y
        
        # Pathfinding graph for all land tiles; remove sea tiles and delete
        # neighbor, cost entry in the neighbors list
        self.land_graph = self.grid
        for x in xrange(self.world_width):
            for y in xrange(self.world_height):
                cell = self.land_graph[x][y]
                if cell.elevation >= 0:
                    cell.neighbors = {}
                for key in cell.neighbors.copy():
                    if key.elevation >= 0:
                        if key in cell.neighbors:
                            del cell.neighbors[key]
        
        # Pathfinding graph for all sea tiles
        self.sea_graph = self.grid
        for x in xrange(self.world_width):
            for y in xrange(self.world_height):
                cell = self.sea_graph[x][y]
                if cell.elevation > 0:
                    cell.neighbors = {}
                for key in cell.neighbors.copy():
                    if key.elevation > 0:
                        if key in cell.neighbors:
                            del cell.neighbors[key]
                        
    def get_cost(self, graph, current_node, next_node):
        '''
        Gets the cost to move from the current node to a given neighbor node
        '''
        return graph[current.x][current.y].neighbors[next_node]
            
class GridCoordinate(object):
    '''
    Elevation parameters, can be freely altered. Max elevation will affect
    what appears as mountains; min elevation what appears as deep sea.
    LANDMASS_SIZE is actually the radius of the spherical surface used to
    sample the noise function; a larger radius means smaller apparent
    landmass sizes. DETAIL is the number of octaves in the noise and affects
    how crinkly the landmasses are.
    '''
    LANDMASS_SIZE = 2
    DETAIL = 64.0
    RESOURCE_DISTRIBUTION = 32
    
    ELEVATIONS = {
        (1, 0.8): {
            'color': C_HIGH_ELEVATION,
            'char': 'A'
        },
        (0.8, 0.6): {
            'color': C_MIDHIGH_ELEVATION,
            'char': 'a'
        },
        (0.6, 0.4): {
            'color': C_MID_ELEVATION,
            'char': 'n'
        },
        (0.4, 0.2): {
            'color': C_MIDLOW_ELEVATION,
            'char': '8'
        },
        (0.2, 0): {
            'color': C_LOW_ELEVATION,
            'char': '8'
        },
        (0, -0.5): {
            'color': C_SEA_ELEVATION,
            'char': 'S'
        },
        (-0.5, -1): {
            'color': C_DEEPSEA_ELEVATION,
            'char': 's'
        },
    }
    
    def __init__(self, x, y, world_width, world_height, world_noise, resource_noise):
        
        self.x = x
        self.y = y
        self.la = ((Decimal(self.y)*180)/Decimal(world_height))-90
        self.lo = ((Decimal(self.x)*360)/Decimal(world_width))-180
        self.char = '#'
        self.color = WHITE
        self.neighbors = {}
        
        # Sampling 3d noise to get the shape of the landmasses
        x, y, z = spherical_to_cartesian(self.la, self.lo, self.LANDMASS_SIZE)
        self.elevation = libtcod.noise_get_fbm(world_noise,[
            float(x),
            float(y),
            float(z)
        ],self.DETAIL)
        
        # Sampling 3d noise to find out where to spawn resource nodes
        x, y, z = spherical_to_cartesian(self.la, self.lo, self.RESOURCE_DISTRIBUTION)
        if self.elevation > 0:
            self.resource_density = libtcod.noise_get(resource_noise,[
                float(x),
                float(y),
                float(z)
        ])
        else:
            self.resource_density = 0
        
        for elev_range, elev_info in self.ELEVATIONS.items():
            max_, min_ = elev_range
            if max_ >= self.elevation > min_:
                self.color = elev_info['color']
                self.char = elev_info['char']
    
    def get_neighbors(self):
        return neighbors

