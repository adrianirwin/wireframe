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

def create_inset_face_cap(
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
    vector_to_sharp_vertex = (vert_nearest_sharp.co - vert.co).normalized()
    vector_to_opposite_side_of_flap_vertex = (vert_opposite_side.co - vert.co).normalized()

    #   Test if the cap is valid, or needs to be wound back from an
    #   invalid angle due to bending around a corner to find the next
    #   sharp edge.
    vector_edge_tangent = (edge.calc_tangent(loop)).normalized()
    angle_from_cap_to_tangent = vector_to_sharp_vertex.angle(vector_edge_tangent, 0)

    inset_face_cap_unconnected = False
    if angle_from_cap_to_tangent > ((math.pi / 2) - 0.1):
        inset_face_cap_unconnected = True
        vector_to_sharp_vertex = (vector_edge_tangent * -1)
        angle_from_cap_to_tangent = vector_to_sharp_vertex.angle(vector_edge_tangent, 0)
    else:
        vector_to_sharp_vertex = (vector_to_sharp_vertex * -1)

    #   Work out the shifting vector and scaling factor for the vertex
    #   The scaling factor of the 'cap' is to ensure it maintains a parallel edge
    scaling_factor = math.fabs(math.sin((math.pi / 2)) / math.sin(((math.pi / 2) - angle_from_cap_to_tangent)))

    #   Vector along the edge of the inset face
    edge_vector = mathutils.Vector((vector_to_opposite_side_of_flap_vertex * -0.5) + mathutils.Vector([0.5, 0.5, 0.5]))

    #   Create the new vertices
    vert_inset = bm.verts.new(mathutils.Vector(
        (vert.co - (vector_to_sharp_vertex * outline_inset * scaling_factor))
    ))
    vert_edge = bm.verts.new(vert.co)

    return {
        'vert_inset': vert_inset, 'vert_edge': vert_edge,
        'edge_vector': edge_vector, 'scaling_factor': scaling_factor,
        'vector_to_sharp_vertex': vector_to_sharp_vertex,
        'inset_face_cap_unconnected': inset_face_cap_unconnected,
    }

# def create_inset_face_filler_between_caps():
#     for cap in unconnected_flap_points:
#         if (cap.outer_vert.co - a_side_cap['vert_edge'].co).magnitude < 0.0001 and (cap.inset_vert.co - a_side_cap['vert_inset'].co).magnitude > 0.0001:
#             new_filler_face_a = bm.faces.new([cap.outer_vert, a_side_cap['vert_inset'], cap.inset_vert])
#             new_filler_face_a.material_index = 1
#             lines_geometry.faces.append(new_filler_face_a)
#             filler_faces.add(new_filler_face_a)

#             #   Add the values stored in the UV layers
#             for loop in new_filler_face_a.loops:
#                 if (loop.vert.co - cap.outer_vert.co).magnitude < 0.0001:
#                     filler_loop_outer.add(loop)
#                 if (loop.vert.co - a_side_cap['vert_inset'].co).magnitude < 0.0001:
#                     filler_loop_inset_right.add(loop)
#                 if (loop.vert.co - cap.inset_vert.co).magnitude < 0.0001:
#                     filler_loop_inset_left.add(loop)
#             break
#     unconnected_flap_points.add(classes.Potential_Cap_Filler_Edge(a_side_cap['vert_edge'], a_side_cap['vert_inset']))


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