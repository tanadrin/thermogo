import math
from decimal import *

# Given a set of spherical coordinates will return Cartesian coordinates

def spherical_to_cartesian(la, lo, radius):
    '''
    Converts spherical coordinates in 3D space to cartesian coordinates in 3D 
    space
    '''
    x = radius*math.sin(math.radians(90-la))*math.cos(math.radians(lo))
    y = radius*math.sin(math.radians(90-la))*math.sin(math.radians(lo))
    z = radius*math.cos(math.radians(90-la))
    return x, y, z

# We need to alter this algorithm so it stores the cost *to* each node *from* each node
def get_neighbors(gamemap, x, y):
    '''
    Given the gamemap and a set of x,y coordinates, will return every cell immediately
    adjacent. Takes a long time; it's much better to store these values for later use
    again whenever possible.
    '''
    x = gamemap.grid[x][y].x
    y = gamemap.grid[x][y].y
    world_width = gamemap.world_width-1
    world_height = gamemap.world_height-1
    grid = gamemap.grid
    neighbors = {}
    
    # For x cells not at the edges, x neighbors are directly left and right
    if world_width > x > 0:
        neighbors[grid[x+1][y]] = 1
        neighbors[grid[x-1][y]] = 1
        
    # On the sides, add the cells on the opposite edge as neighbors
    if x == 0:
        neighbors[grid[x+1][y]]         = 1
        neighbors[grid[world_width][y]] = 1
        
    if x == world_width:
        neighbors[grid[0][y]]   = 1
        neighbors[grid[x-1][y]] = 1
        
    # Now we do the same with the y coordinate
    if world_height > y > 0:
        neighbors[grid[x][y+1]] = 1
        neighbors[grid[x][y-1]] = 1
        
    # Except rather than wrapping around at the poles (which would create)
    # a torus), the neighbor above or below the top or bottom edge
    # respectively is at the same y coordinate, and at an x coordinate equal
    # to the present x coordinate, plus one half the world width, modulo the
    # total world width--i.e., halfway around, like the prime meridian and
    # the international date line.
    if y == 0:
        neighbors[grid[(x+world_width/2)%world_width][y]] = 1
        neighbors[grid[x][y+1]] = 1
        
    if y == world_height:
        neighbors[grid[x][y-1]]                           = 1
        neighbors[grid[(x+world_width/2)%world_width][y]] = 1
        
    # The same principles hold for the diagonals away from the margins...
    if world_width > x > 0 and world_height > y > 0:
        neighbors[grid[x+1][y+1]] = 1.41
        neighbors[grid[x-1][y-1]] = 1.41
        neighbors[grid[x-1][y+1]] = 1.41
        neighbors[grid[x+1][y-1]] = 1.41
        
    #...and each corner case is different. Starting with (0,0)
    elif x == 0 and y == 0:
        neighbors[grid[x+1][y+1]]                           = 1.41
        neighbors[grid[(x+world_width/2)%world_width-1][y]] = 1.41
        neighbors[grid[world_width][y+1]]                   = 1.41
        neighbors[grid[(x+world_width/2)%world_width+1][y]] = 1.41
    # (world_width, world_height)
    elif x == world_width and y == world_height:
        neighbors[grid[(x+world_width/2)%world_width+1][y]] = 1.41
        neighbors[grid[x-1][y-1]]                           = 1.41
        neighbors[grid[(x+world_width/2)%world_width-1][y]] = 1.41
        neighbors[grid[world_width][y-1]]                   = 1.41
    # (0, world_height)
    elif x == world_width and y == 0:
        neighbors[grid[0][y+1]]                             = 1.41
        neighbors[grid[(x+world_width/2)%world_width-1][y]] = 1.41
        neighbors[grid[x-1][y+1]]                           = 1.41
        neighbors[grid[(x+world_width/2)%world_width+1][y]] = 1.41
    # (world_width, 0)
    elif x == 0 and y == world_height:
        neighbors[grid[(x+world_width/2)%world_width+1][y]] = 1.41
        neighbors[grid[x-1][y-1]]                           = 1.41
        neighbors[grid[(x+world_width/2)%world_width+1][y]] = 1.41
        neighbors[grid[x+1][y-1]]                           = 1.41
        
    return neighbors

def get_longitude_length(latitude, degrees_longitude, r = 1):
    # Assumes a radius of a sphere of 1; for a different radius, multiply the result
    # by the actual radius of the sphere
    return (3.14/180)*r*math.cos(latitude)
    
# Haversine function (sine squared of an angle divided by two)
def hav(theta):
    math.sin(theta/2)**2
    
# For two coordinates in latitude and longitude, returns the distance between the two
def hav_distance(la1, lo1, la2, lo2, r = 1):
    return 2*r*math.asin((hav(la2-la1)+math.cos(la1)*math.cos(la2)*hav(lo2-lo1))**(0.5))