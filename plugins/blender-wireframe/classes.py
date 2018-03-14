"""All of the classes required for generating wireframe assets."""

#
#   classes.py
#
#   Commonly used classes for the unique structures.
#


#
#   Imports
#

from collections import namedtuple


#
#   Classes
#

Shifting_Vector = namedtuple('Shifting_Vector', ['vector', 'factor'])
class Shiftable_Vertex:
    """
    Holds both the vertex itself, and the direction and scaling factor,
    of the vertices that make up the wireframe geometry.
    The scaling factor is stored in the colour property, and initially
    defined as a Shifting_Vector.
    """
    def __init__(self, vert, colour):
        self.vert = vert
        self.colour = colour
        self.uv = []

    #   TODO: This may not be used any longer, double-check
    def sharp(self):
        return not self.edge.smooth

class Potential_Cap_Filler_Edge:
    def __init__(self, outer_vert, inset_vert):
        self.outer_vert = outer_vert
        self.inset_vert = inset_vert

class Face_UV:
    """
    Hold a face and a single UV coordinate.
    Used when setting uv coordinates on vertices.
    """
    def __init__(self, face, uv):
        self.face = face
        self.uv = uv

class Lines_Geometry:
    """
    Hold geometry added to create the lines that make up the wireframe.
    """
    def __init__(self, faces=[], verts=[]):
        self.faces = faces
        self.verts = verts


#
#   __main__ Check
#

if __name__ == '__main__':
    print('classes.py is not intended to be run as __main__')