import math

#Given a set of spherical coordinates will return Cartesian coordinates
def spherical_to_cartesian(la, lo, radius):
    x = radius*math.sin(math.radians(90-la))*math.cos(math.radians(lo))
    y = radius*math.sin(math.radians(90-la))*math.sin(math.radians(lo))
    z = radius*math.cos(math.radians(90-la))
    return x, y, z