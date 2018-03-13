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

#   Shiftable Vertex models
Shifting_Vector = namedtuple('Shifting_Vector', ['vector', 'factor'])
class Shiftable_Vertex:
    def __init__(self, vert, colour):
        self.vert = vert
        self.colour = colour
        self.uv = []
    def sharp(self):
        return not self.edge.smooth

#   TODO: Comment
class Potential_Cap_Filler_Edge:
    def __init__(self, outer_vert, inset_vert):
        self.outer_vert = outer_vert
        self.inset_vert = inset_vert

#   TODO: Comment
class Face_UV:
    def __init__(self, face, uv):
        self.face = face
        self.uv = uv

#   TODO: Comment
class Lines_Geometry:
    def __init__(self, faces=[], verts=[]):
        self.faces = faces
        self.verts = verts


#
#   __main__ Check
#

if __name__ == '__main__':
    print('classes.py is not intended to be run as __main__')