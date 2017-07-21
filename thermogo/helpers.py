from math import sin, cos, radians

def spherical_to_cartesian(la, lo, radius):
    """
    Given a set of spherical coordinates will return Cartesian coordinates
    """
    x = radius * sin(radians(90-la)) * cos(radians(lo))
    y = radius * sin(radians(90 - la)) * sin(radians(lo))
    z = radius * cos(radians(90 - la))
    return x, y, z