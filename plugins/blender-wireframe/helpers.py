#   TODO: Docstring for the module, functions, and classes

#
#   helpers.py
#
#   Commonly used functions that perform mundane manipulation and
#   management tasks.
#


#
#   Imports
#

import bmesh
import math
import mathutils


#
#   BMesh Functions
#

def object_to_bmesh(object):
    bm = bmesh.new()
    bm.from_mesh(object.data)
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    return bm

def bmesh_to_object(bm, object):
    bm.to_mesh(object.data)
    bm.free()
    object.data.update()

def list_geometry(bm):
    return {
        'faces': list(bm.faces),
        'edges': list(bm.edges),
        'verts': list(bm.verts),
    }

#
#   Geometry Functions
#

def find_next_sharp_edge(previous_face, previous_edge, vert, depth):
    """
    Walk around a vertex to find the next sharp edge on the 'fan' of
    faces that surrounds the vertex.
    """
    #   TODO: This recursion depth limiter is currently arbitrary
    if depth < 10:
        for current_face in previous_edge.link_faces:
            if current_face is not previous_face:
                for current_edge in current_face.edges:
                    if (
                        current_edge is not previous_edge
                        and (
                            current_edge.verts[0] is vert
                            or current_edge.verts[1] is vert
                        )
                        and current_edge.smooth is False
                    ):
                        new_vert = None
                        if current_edge.verts[0] is vert:
                            new_vert = current_edge.verts[1]
                        else:
                            new_vert = current_edge.verts[0]
                        return {'edge': current_edge, 'vert': new_vert}
                    else:
                        return find_next_sharp_edge(current_face,
                            current_edge, vert, (depth + 1))
    return False

def create_inset_face_vertices(
    bm,
    outline_inset,
    loop, edge,
    vert, vert_opposite_side, vert_nearest_sharp
):
    """
    Create the two vertices that delineate one of the 'cap' edge of
    an inset face.
    """

    #   Calculate the vectors describing the 'cap' edges on each end
    #   of the new face.
    vector_to_nearest_sharp_vertex = (vert_nearest_sharp.co - vert.co).normalized()
    vector_to_opposite_side_of_flap_vertex = (vert_opposite_side.co - vert.co).normalized()

    #   Test if the cap is valid, or needs to be wound back from an
    #   invalid angle due to bending around a corner to find the next
    #   sharp edge.
    #   TODO: Currently only triggers if the angle for the cap 'edge'
    #   is closing in on 180* - need to change it to only allow up
    #   to 90* and add a filler piece if the angle is greater than that.
    vector_edge_tangent = (edge.calc_tangent(loop)).normalized()
    cap_angle_from_tangent = vector_to_nearest_sharp_vertex.angle(vector_edge_tangent, 0)

    #   TODO: Might need to change this check to math.pi / 4,
    #   double check the math!
    cap_flap_unconnected = False
    if cap_angle_from_tangent > ((math.pi / 2) - 0.1):
        cap_flap_unconnected = True
        vector_to_nearest_sharp_vertex = (vector_edge_tangent * -1)
        cap_angle_from_tangent = vector_to_nearest_sharp_vertex.angle(vector_edge_tangent, 0)
    else:
        vector_to_nearest_sharp_vertex = (vector_to_nearest_sharp_vertex * -1)

    #   Work out the shifting vector and scaling factor for the vertex
    #   The scaling factor of the 'cap' is to ensure it maintains a parallel edge
    scaling_factor = math.fabs(math.sin((math.pi / 2)) / math.sin(((math.pi / 2) - cap_angle_from_tangent)))

    #   Vector along the edge of the flap
    flap_edge_vector = mathutils.Vector((vector_to_opposite_side_of_flap_vertex * -0.5) + mathutils.Vector([0.5, 0.5, 0.5]))

    #   Create the new vertices
    new_vert_inset = bm.verts.new(mathutils.Vector(
        (vert.co - (vector_to_nearest_sharp_vertex * outline_inset * scaling_factor))
    ))
    new_vert_edge = bm.verts.new(vert.co)

    return {
        'inset': new_vert_inset,'edge': new_vert_edge,
        'TEMP_vec': vector_to_nearest_sharp_vertex,
        'flap_edge_vector': flap_edge_vector,
        'cap_flap_unconnected': cap_flap_unconnected,
        'scaling_factor': scaling_factor,
    }


#
#   Metadata Functions
#

def vertex_groups_lock(object, groups, lock=True):
    for group in groups:
        object.vertex_groups[group].lock_weight = lock


#
#   __main__ Check
#

if __name__ == '__main__':
    print('helpers.py is not intended to be run as __main__')