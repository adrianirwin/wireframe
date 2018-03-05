#
#   Abstract
#
#   The purpose of this library is to perform the geometry and
#   meta-data generation on an abstracted version of the source
#   mesh data, allowing for integration with any number of
#   geometry/asset creation tools.
#

#
#   Imports
#

import bpy
import math
import mathutils

#
#   Create New Geometry
#

#   Test Function for Integration
def print_it(value):
    print(value)

#   Create Inset Outline Geometry
# def create_inset_outline_geometry(
#         config, bm,
#         tile, tile_faces, tile_verts,
#         lines_faces, lines_verts,
#         outline_faces, outline_verts,
#         dimensions, bounding_box,
#         tile_bounds, tile_dimensions, tile_offset_from_center):

#     #   Track the added inset outline verts that follow the existing
#     #   geometry (as opposed to the inset verts)
#     #   This is so they may be merged later to remove duplicates
#     lines_outer_verts = set()
#     unconnected_flap_points = set()

#     #   Track the filler faces
#     filler_faces = set()
#     filler_loop_inset_left = set()
#     filler_loop_inset_right = set()
#     filler_loop_outer = set()

#     #   Create the lines geometry on a per-face (not per-tri) basis
#     for face_counter, face in enumerate(tile_faces):

#         #   Set material
#         face.material_index = 0
        
#         #   Add the inset vertices
#         lines_inset_verts = set()
#         lines_perpendicular_verts = []

#         repeating_loop = list(face.loops) * 2
#         for counter, loops in [
#             (
#                 counter,
#                 {
#                     'verts': {
#                         'prev_sharp': repeating_loop[counter - 3].vert,
#                         'prev': repeating_loop[counter - 3].vert,
#                         'a': repeating_loop[counter - 2].vert,
#                         'b': repeating_loop[counter - 1].vert,
#                         'next': repeating_loop[counter].vert,
#                         'next_sharp': repeating_loop[counter].vert,
#                     },
#                     'edges': {
#                         'prev_sharp': repeating_loop[counter - 3].edge,
#                         'prev': repeating_loop[counter - 3].edge,
#                         'curr': repeating_loop[counter - 2].edge,
#                         'next': repeating_loop[counter - 1].edge,
#                         'next_sharp': repeating_loop[counter - 1].edge,
#                     },
#                     'loops': {
#                         'curr': repeating_loop[counter - 2]
#                     },
#                 }
#             ) for counter, loop in enumerate(repeating_loop)
#         ]:

#             #   Skip non-sharp edges
#             #   TODO: Some kind of warning/check if there are no sharp edges on the tile
#             if loops['edges']['curr'].smooth is False:

#                 #   Walk around the vert to find the next sharp edge on the 'fan' of faces
#                 def find_next_sharp_edge(previous_face, previous_edge, vert, depth):
#                     #   NOTE: This recursion depth limiter is arbitrary, change as needed
#                     if depth < 10:
#                         for current_face in previous_edge.link_faces:
#                             if current_face is not previous_face:
#                                 for current_edge in current_face.edges:
#                                     if current_edge is not previous_edge:
#                                         if current_edge.verts[0] is vert or current_edge.verts[1] is vert:
#                                             if current_edge.smooth is False:
#                                                 new_vert = None
#                                                 if current_edge.verts[0] is vert:
#                                                     new_vert = current_edge.verts[1]
#                                                 else:
#                                                     new_vert = current_edge.verts[0]
#                                                 return { 'edge': current_edge, 'vert': new_vert }
#                                             return find_next_sharp_edge(current_face, current_edge, vert, (depth + 1))
#                     return False

#                 #   Find the next sharp edge sharing the same vert
#                 if loops['edges']['prev_sharp'].smooth is True:
#                     found_edge = find_next_sharp_edge(face, loops['edges']['prev_sharp'], loops['verts']['a'], 0)
#                     if found_edge is not False:
#                         loops['edges']['prev_sharp'] = found_edge['edge']
#                         loops['verts']['prev_sharp'] = found_edge['vert']

#                 if loops['edges']['next_sharp'].smooth is True:
#                     found_edge = find_next_sharp_edge(face, loops['edges']['next_sharp'], loops['verts']['b'], 0)
#                     if found_edge is not False:
#                         loops['edges']['next_sharp'] = found_edge['edge']
#                         loops['verts']['next_sharp'] = found_edge['vert']

#                 #   Add the new vertices
#                 new_vert_a_inset = bm.verts.new(mathutils.Vector([0.0, 0.0, 0.0]))
#                 new_vert_b_inset = bm.verts.new(mathutils.Vector([0.0, 0.0, 0.0]))

#                 new_vert_a_outer = bm.verts.new(loops['verts']['a'].co)
#                 new_vert_b_outer = bm.verts.new(loops['verts']['b'].co)

#                 #   Scaling factor of the 'cap' to ensure it maintains a parallel edge
#                 scaling_factor_a = 1.0
#                 scaling_factor_b = 1.0
 
#                 #   Vector along which the line will grow
#                 shifting_vector_a = mathutils.Vector([0.0, 0.0, 0.0])
#                 shifting_vector_b = mathutils.Vector([0.0, 0.0, 0.0])

#                 #   Vector along the edge of the flap
#                 flap_edge_vector = mathutils.Vector([0.0, 0.0, 0.0])

#                 #   Calculate the vectors describing the 'cap' edges on each end of the new face
#                 vector_to_prev_a = (loops['verts']['prev_sharp'].co - loops['verts']['a'].co).normalized()
#                 vector_to_next_a = (loops['verts']['b'].co - loops['verts']['a'].co).normalized()

#                 vector_to_prev_b = (loops['verts']['a'].co - loops['verts']['b'].co).normalized()
#                 vector_to_next_b = (loops['verts']['next_sharp'].co - loops['verts']['b'].co).normalized()

#                 #   Test if the cap is valid, or needs to be wound back from an invalid angle due to bending around a corner to find the next sharp edge
#                 #   TODO: Currently only triggers if the angle for the cap 'edge' is closing in on 180* - need to change it to only allow up to 90* and add a filler piece if the angle is greater than that.
#                 vector_edge_tangent = (loops['edges']['curr'].calc_tangent(loops['loops']['curr'])).normalized()

#                 cap_angle_from_tangent_a = vector_to_prev_a.angle(vector_edge_tangent, 0)
#                 cap_angle_from_tangent_b = vector_to_next_b.angle(vector_edge_tangent, 0)

#                 #   TODO: Might need to change this check to math.pi / 4, double check the math!
#                 cap_a_flap_unconnected = False
#                 if cap_angle_from_tangent_a > ((math.pi / 2) - 0.1):
#                     cap_a_flap_unconnected = True
#                     vector_to_prev_a = (vector_edge_tangent * -1)
#                     cap_angle_from_tangent_a = vector_to_prev_a.angle(vector_edge_tangent, 0)
#                 else:
#                     vector_to_prev_a = (vector_to_prev_a * -1)

#                 cap_b_flap_unconnected = False
#                 if cap_angle_from_tangent_b > ((math.pi / 2) - 0.1):
#                     cap_b_flap_unconnected = True
#                     vector_to_next_b = (vector_edge_tangent * -1)
#                     cap_angle_from_tangent_b = vector_to_next_b.angle(vector_edge_tangent, 0)
#                 else:
#                     vector_to_next_b = (vector_to_next_b * -1)

#                 #   DEBUG
#                 # if (
#                 #     True and
#                 #     (face.normal - mathutils.Vector([0.0, -1.0, 0.0])).magnitude < 0.0001 and (
#                 #         (loops['edges']['curr'].verts[0].co - mathutils.Vector([0.5, -1.0, 2.0])).magnitude < 0.0001 or
#                 #         (loops['edges']['curr'].verts[1].co - mathutils.Vector([0.5, -1.0, 2.0])).magnitude < 0.0001
#                 #     )
#                 # ):
#                 #     print(' ')
#                 #     print('Edge')
#                 #     print(' Edge Verts: ' + str(loops['edges']['curr'].verts[0].co) + ' : ' + str(loops['edges']['curr'].verts[1].co))
#                 #     print(' ')
#                 #     print(' Prev Sharp: ' + str(loops['verts']['prev_sharp'].co))
#                 #     print(' Next Sharp: ' + str(loops['verts']['next_sharp'].co))
#                 #     print(' ')
#                 #     print(' Tangent: ' + str(vector_edge_tangent))
#                 #     print(' Tan Ang A: ' + str(cap_angle_from_tangent_a))
#                 #     print(' Tan Ang B: ' + str(cap_angle_from_tangent_b))
#                 #     print(' ')

#                 #   Create 'flap' style geometry that overlaps on the corners and expands straight up the neighbouring edge
#                 if config["outline_inset_type"] == 'FLAP':

#                     #   Work out the shifting vector and scaling factor for the vertex
#                     scaling_factor_a = math.fabs(math.sin((math.pi / 2)) / math.sin(((math.pi / 2) - cap_angle_from_tangent_a)))
#                     scaling_factor_b = math.fabs(math.sin((math.pi / 2)) / math.sin(((math.pi / 2) - cap_angle_from_tangent_b)))

#                     flap_edge_vector = (vector_to_next_a * -0.5) + mathutils.Vector([0.5, 0.5, 0.5])
        
#                 #   Create 'bevel' style geometry that splits the angle between the neighbouring edge and expands along this vector
#                 elif config["outline_inset_type"] == 'BEVEL':

#                     #   Calculate the mid-point angles for the end 'caps' of the edge
#                     radians_between_vectors_a = vector_to_prev_a.angle(vector_to_next_a, 0)
#                     radians_between_vectors_b = vector_to_prev_b.angle(vector_to_next_b, 0)

#                     degrees_to_cap_a = math.degrees(radians_between_vectors_a)
#                     degrees_to_cap_b = math.degrees(radians_between_vectors_b)

#                     face_overlap_test_offset_a = mathutils.Vector([0.0, 0.0, 0.0])
#                     face_overlap_test_offset_b = mathutils.Vector([0.0, 0.0, 0.0])

#                     #   Handle smooth edges on the A point
#                     if loops['edges']['prev_sharp'].smooth is True:
#                         face_overlap_test_offset_a = (vector_to_next_a * 0.1)
#                     else:
#                         vector_to_prev_a = vector_to_prev_a + vector_to_next_a
#                         degrees_to_cap_a = (math.degrees(radians_between_vectors_a) / 2)

#                     #   Handle smooth edges on the B point
#                     if loops['edges']['next_sharp'].smooth is True:
#                         face_overlap_test_offset_b = (vector_to_prev_b * 0.1)
#                     else:
#                         vector_to_next_b = vector_to_prev_b + vector_to_next_b
#                         degrees_to_cap_b = (math.degrees(radians_between_vectors_b) / 2)

#                     #   Scale the vector to the new vertex
#                     vector_cap_length_a = (1 / math.sin(math.radians(degrees_to_cap_a)))
#                     vector_cap_length_b = (1 / math.sin(math.radians(degrees_to_cap_b)))

#                     #   If this portion of the inset line is straight, the vector to the midpoint must be calulated a bit differently
#                     if abs(vector_to_prev_a.length) > config["float_point_rounding_threshold"]:
#                         vector_to_prev_a = vector_to_prev_a * (vector_cap_length_a / vector_to_prev_a.length)
#                     else:
#                         vector_to_prev_a = ((vector_to_next_a.cross(face.normal) * (vector_cap_length_a / vector_to_next_a.cross(face.normal).length)) * -1)

#                     if abs(vector_to_next_b.length) > config["float_point_rounding_threshold"]:
#                         vector_to_next_b = vector_to_next_b * (vector_cap_length_b / vector_to_next_b.length)
#                     else:
#                         vector_to_next_b = ((vector_to_next_b.cross(face.normal) * (vector_cap_length_b / vector_to_next_b.cross(face.normal).length)) * -1)

#                     #   Test to see if the new vertex will be within the bounds of the containing face
#                     if bmesh.geometry.intersect_face_point(face, (new_vert_co_a - face_overlap_test_offset_a)) is False:
#                         # new_vert_co_a = (loops['verts']['a'].co - ((vector_to_prev_a * -1) * config["outline_inset"]))
#                         vector_to_prev_a = (vector_to_prev_a * -1)

#                     if bmesh.geometry.intersect_face_point(face, (new_vert_co_b - face_overlap_test_offset_b)) is False:
#                         # new_vert_co_b = (loops['verts']['b'].co - ((vector_to_next_b * -1) * config["outline_inset"]))
#                         vector_to_next_b = (vector_to_next_b * -1)
                
#                     #   Work out the shifting vector and scaling factor for the vertex
#                     scaling_factor_a = min([1 / math.fabs(axis) if (math.fabs(axis) > 1) else 1 for axis in vector_to_prev_a])
#                     scaling_factor_b = min([1 / math.fabs(axis) if (math.fabs(axis) > 1) else 1 for axis in vector_to_next_b])
                
#                 #   Initial position of new inset vertices
#                 new_vert_co_a = (loops['verts']['a'].co - (vector_to_prev_a * config["outline_inset"] * scaling_factor_a))
#                 new_vert_co_b = (loops['verts']['b'].co - (vector_to_next_b * config["outline_inset"] * scaling_factor_b))

#                 #   Position the new vertices
#                 new_vert_a_inset.co = new_vert_co_a
#                 new_vert_b_inset.co = new_vert_co_b

#                 #   Store the new vertices
#                 lines_inset_verts.add(new_vert_a_inset)
#                 lines_inset_verts.add(new_vert_b_inset)

#                 lines_outer_verts.add(new_vert_a_outer)
#                 lines_outer_verts.add(new_vert_b_outer)

#                 #   Create the inset outline face
#                 new_face = bm.faces.new([new_vert_a_outer, new_vert_b_outer, new_vert_b_inset, new_vert_a_inset])
#                 new_face.material_index = 1
#                 lines_faces.append(new_face)


#                 #   Find out which edge on the face provides the best border to limit expansion of this line segment
#                 maximum_limit = 10
#                 limit_a = maximum_limit
#                 limit_b = maximum_limit
#                 # print('')
#                 # print('Loop Check')
#                 # print(str(face.normal) + str(face.calc_center_median_weighted()))
#                 # print('')

#                 #   Gather all of the edges of the coplanar faces attached to this one
#                 coplanar_faces_edges = set()
#                 for edge in face.edges:
#                     coplanar_faces_edges.add(edge)
#                 for tile_face in tile_faces:
#                     if (tile_face.normal - face.normal).magnitude < 0.0001 and -0.001 < face.normal.dot(tile_face.calc_center_median_weighted() - face.calc_center_median_weighted()) < 0.001:
#                         for edge in tile_face.edges:
#                             coplanar_faces_edges.add(edge)

#                 #   Check all coplanar edges to find which one the flap's caps intersect with first
#                 for edge in coplanar_faces_edges:
#                     if edge is not loops['edges']['curr'] and edge.smooth is False:

#                         #   Compare edges for A cap
#                         if edge is not loops['edges']['prev_sharp'] and edge is not loops['edges']['prev']:
#                             intersecting_points = mathutils.geometry.intersect_line_line(loops['verts']['a'].co, (loops['verts']['a'].co + vector_to_prev_a), edge.verts[0].co, edge.verts[1].co)
                    
#                             #   Check if the intersection with the line defined by the edge actually occurs between the the verts making up the edge
#                             if intersecting_points is not None and (intersecting_points[0] - intersecting_points[1]).magnitude < 0.00001:
#                                 if (
#                                     #   First, check for an exact hit on a vertex
#                                     (intersecting_points[1] - edge.verts[0].co).magnitude < 0.00001 or (intersecting_points[1] - edge.verts[1].co).magnitude < 0.00001 or
#                                     #   Next, check for a hit on the midpoint of an edge    
#                                     (edge.verts[0].co - intersecting_points[1]).dot(edge.verts[1].co - intersecting_points[1]) < 0
#                                 ):
#                                     # print(' A+ ' + str(intersecting_points[1]) + ' : ' + str(loops['verts']['a'].co))
#                                     # possible_edges_a.add(edge)
#                                     limit_a = min(limit_a, (loops['verts']['a'].co - intersecting_points[1]).magnitude)
#                                 # else:
#                                 #     print(' A- ' + str(intersecting_points[0]) + ' : ' + str(intersecting_points[1]) + ' : ' + str(loops['verts']['a'].co))
#                                 #     print(' Ae ' + str(edge.verts[0].co) + ' : ' + str(edge.verts[1].co))
#                                 #     print(' Ad ' + str((edge.verts[0].co - intersecting_points[1]).dot(edge.verts[1].co - intersecting_points[1])))

#                         #   Compare edges for B cap
#                         if edge is not loops['edges']['next_sharp'] and edge is not loops['edges']['next']:
#                             intersecting_points = mathutils.geometry.intersect_line_line(loops['verts']['b'].co, (loops['verts']['b'].co + vector_to_next_b), edge.verts[0].co, edge.verts[1].co)

#                             #   Check if the two lines actually intersect, mark the point that they do as a corner
#                             if intersecting_points is not None and (intersecting_points[0] - intersecting_points[1]).magnitude < 0.00001:
#                                 if (
#                                     #   First, check for an exact hit on a vertex
#                                     (intersecting_points[1] - edge.verts[0].co).magnitude < 0.00001 or (intersecting_points[1] - edge.verts[1].co).magnitude < 0.00001 or
#                                     #   Next, check for a hit on the midpoint of an edge    
#                                     (edge.verts[0].co - intersecting_points[1]).dot(edge.verts[1].co - intersecting_points[1]) < 0
#                                 ):
#                                     # print(' B+ ' + str(intersecting_points[1]) + ' : ' + str(loops['verts']['b'].co))
#                                     # possible_edges_b.add(edge)
#                                     limit_b = min(limit_b, (loops['verts']['b'].co - intersecting_points[1]).magnitude)
#                                 # else:
#                                 #     print(' B- ' + str(intersecting_points[0]) + ' : ' + str(intersecting_points[1]) + ' : ' + str(loops['verts']['b'].co))
#                                 #     print(' Be ' + str(edge.verts[0].co) + ' : ' + str(edge.verts[1].co))
#                                 #     print(' Bd ' + str((edge.verts[0].co - intersecting_points[1]).dot(edge.verts[1].co - intersecting_points[1])))

#                 # print('')
#                 # print('Matches')
#                 # print(' A ' + str(list(possible_edges_a)))
#                 # print(' B ' + str(list(possible_edges_b)))
#                 # print('')
#                 # print('Distance')
#                 # print(' A Limit ' + str(limit_a))
#                 # print(' B Limit ' + str(limit_b))
#                 # print('')
#                 # print(' A Scale ' + str(scaling_factor_a))
#                 # print(' B Scale ' + str(scaling_factor_b))
#                 # print(' ')


#                 #   Store a vector representing the direction of the line's edge
#                 if config["outline_inset_type"] == 'FLAP':

#                     # print('NF: ' + str(new_face))
#                     # print('FEV: ' + str(flap_edge_vector))
#                     for flap_loop in new_face.loops:
#                         # print('FL: ' + str(flap_loop))
#                         if flap_loop.vert is new_vert_a_inset or flap_loop.vert is new_vert_b_inset:
#                             flap_loop[bm.loops.layers.uv.get('Tile Top Texture + Lines Edge XY')].uv = [flap_edge_vector.x, flap_edge_vector.y]

#                             limit = maximum_limit
#                             if flap_loop.vert is new_vert_a_inset:
#                                 limit = limit_a
#                             elif flap_loop.vert is new_vert_b_inset:
#                                 limit = limit_b
#                             limit = (limit / maximum_limit)

#                             flap_loop[bm.loops.layers.uv.get('Tile Pattern Texture + Lines Edge Z + Lines Offset Limit')].uv = [flap_edge_vector.z, limit]
#                         if flap_loop.vert is new_vert_a_outer or flap_loop.vert is new_vert_b_outer:
#                             flap_loop[bm.loops.layers.uv.get('Tile Top Texture + Lines Edge XY')].uv = [0.5, 0.5]
#                             flap_loop[bm.loops.layers.uv.get('Tile Pattern Texture + Lines Edge Z + Lines Offset Limit')].uv = [0.5, 0.0]
#                     # print(' ')

#                     #   Find vertices of flap caps that are unconnected (have a gap due to a convex join), and join them
#                     if cap_a_flap_unconnected is True:
#                         for cap in unconnected_flap_points:
#                             if (cap.outer_vert.co - new_vert_a_outer.co).magnitude < 0.0001 and (cap.inset_vert.co - new_vert_a_inset.co).magnitude > 0.0001:
#                                 new_filler_face_a = bm.faces.new([cap.outer_vert, new_vert_a_inset, cap.inset_vert])
#                                 new_filler_face_a.material_index = 1
#                                 lines_faces.append(new_filler_face_a)
#                                 filler_faces.add(new_filler_face_a)
                                
#                                 #   Add the values stored in the UV layers
#                                 for loop in new_filler_face_a.loops:
#                                     if (loop.vert.co - cap.outer_vert.co).magnitude < 0.0001:
#                                         filler_loop_outer.add(loop)
#                                     if (loop.vert.co - new_vert_a_inset.co).magnitude < 0.0001:
#                                         filler_loop_inset_right.add(loop)
#                                     if (loop.vert.co - cap.inset_vert.co).magnitude < 0.0001:
#                                         filler_loop_inset_left.add(loop)
#                                 break
#                         unconnected_flap_points.add(Potential_Cap_Filler_Edge(new_vert_a_outer, new_vert_a_inset))

#                     if cap_b_flap_unconnected is True:
#                         for cap in unconnected_flap_points:
#                             if (cap.outer_vert.co - new_vert_b_outer.co).magnitude < 0.0001 and (cap.inset_vert.co - new_vert_b_inset.co).magnitude > 0.0001:
#                                 new_filler_face_b = bm.faces.new([cap.outer_vert, cap.inset_vert, new_vert_b_inset])
#                                 new_filler_face_b.material_index = 1
#                                 lines_faces.append(new_filler_face_b)
#                                 filler_faces.add(new_filler_face_b)

#                                 #   Add the values stored in the UV layers
#                                 for loop in new_filler_face_b.loops:
#                                     if (loop.vert.co - cap.outer_vert.co).magnitude < 0.0001:
#                                         filler_loop_outer.add(loop)
#                                     if (loop.vert.co - new_vert_b_inset.co).magnitude < 0.0001:
#                                         filler_loop_inset_left.add(loop)
#                                     if (loop.vert.co - cap.inset_vert.co).magnitude < 0.0001:
#                                         filler_loop_inset_right.add(loop)
#                                 break
#                         unconnected_flap_points.add(Potential_Cap_Filler_Edge(new_vert_b_outer, new_vert_b_inset))

#                 #   Vector along which the edge will slide to grow the line
#                 #   TODO: Why is the scaling factor being applied here, and then stored as a separate value?
#                 # shifting_vector_a = ((((vector_to_prev_a * -1) * scaling_factor_a) * 0.5) + mathutils.Vector([0.5, 0.5, 0.5]))
#                 # shifting_vector_b = ((((vector_to_next_b * -1) * scaling_factor_b) * 0.5) + mathutils.Vector([0.5, 0.5, 0.5]))

#                 shifting_vector_a = (vector_to_prev_a * -0.5) + mathutils.Vector([0.5, 0.5, 0.5])
#                 shifting_vector_b = (vector_to_next_b * -0.5) + mathutils.Vector([0.5, 0.5, 0.5])


#                 #   Assign the UV location for each vertex on the new face's loops
#                 lines_verts.append(Shiftable_Vertex(new_vert_a_outer, Shifting_Vector(mathutils.Vector(([0.5, 0.5, 0.5])), 1.0)))
#                 new_vert_a_outer_index = len(lines_verts) - 1
#                 lines_verts[-1].uv.append(Face_UV(new_face, [0.015625, 0.015625]))

#                 lines_verts.append(Shiftable_Vertex(new_vert_b_outer, Shifting_Vector(mathutils.Vector(([0.5, 0.5, 0.5])), 1.0)))
#                 new_vert_b_outer_index = len(lines_verts) - 1
#                 lines_verts[-1].uv.append(Face_UV(new_face, [0.015625, 0.109375]))

#                 lines_verts.append(Shiftable_Vertex(new_vert_a_inset, Shifting_Vector(shifting_vector_a, (1 / scaling_factor_a))))
#                 lines_verts[-1].uv.append(Face_UV(new_face, [0.75, 0.015625]))

#                 lines_verts.append(Shiftable_Vertex(new_vert_b_inset, Shifting_Vector(shifting_vector_b, (1 / scaling_factor_b))))
#                 lines_verts[-1].uv.append(Face_UV(new_face, [0.75, 0.109375]))

#                 #   In certain circumstances, add two perpendicular inset outline faces if:
#                 #   - the angle between this face's normal and the normal of the face sharing the edge is < 89* (usually concave angles on the interior of the tile), and;
#                 #   - not a bounding edge on the outside
#                 if config["outline_inset_type"] == 'BEVEL':

#                     edge_center_point = mathutils.Vector([((loops['edges']['curr'].verts[0].co.x + loops['edges']['curr'].verts[1].co.x) / 2), ((loops['edges']['curr'].verts[0].co.y + loops['edges']['curr'].verts[1].co.y) / 2), ((loops['edges']['curr'].verts[0].co.z + loops['edges']['curr'].verts[1].co.z) / 2)])
#                     edges_at_bounds = 0

#                     if (abs(edge_center_point.x - tile_bounds['xp']) < config["float_point_rounding_threshold"] or abs(edge_center_point.x - tile_bounds['xn']) < config["float_point_rounding_threshold"]):
#                         edges_at_bounds += 1

#                     if (abs(edge_center_point.y - tile_bounds['yp']) < config["float_point_rounding_threshold"] or abs(edge_center_point.y - tile_bounds['yn']) < config["float_point_rounding_threshold"]):
#                         edges_at_bounds += 1

#                     if (abs(edge_center_point.z - tile_bounds['zp']) < config["float_point_rounding_threshold"] or abs(edge_center_point.z - tile_bounds['zn']) < config["float_point_rounding_threshold"]):
#                         edges_at_bounds += 1

#                     if edges_at_bounds < 2 and loops['edges']['curr'].is_boundary is False:
#                         angle_between = loops['edges']['curr'].calc_face_angle_signed(None)
                        
#                         if angle_between is not None:

#                             angle_between = math.degrees(angle_between)
                            
#                             if (angle_between > -89 and angle_between < 89):
#                                 outset_perpendicular_vector = face.normal.normalized()
#                                 inset_perpendicular_vector = outset_perpendicular_vector * -1

#                                 outset_perpendicular_vert_co_a = (loops['verts']['a'].co + (outset_perpendicular_vector * config["outline_inset"]))
#                                 outset_perpendicular_vert_co_b = (loops['verts']['b'].co + (outset_perpendicular_vector * config["outline_inset"]))

#                                 inset_perpendicular_vert_co_a = (loops['verts']['a'].co + (inset_perpendicular_vector * config["outline_inset"]))
#                                 inset_perpendicular_vert_co_b = (loops['verts']['b'].co + (inset_perpendicular_vector * config["outline_inset"]))

#                                 outset_new_vert_a_perpendicular = bm.verts.new(outset_perpendicular_vert_co_a)
#                                 outset_new_vert_b_perpendicular = bm.verts.new(outset_perpendicular_vert_co_b)

#                                 inset_new_vert_a_perpendicular = bm.verts.new(inset_perpendicular_vert_co_a)
#                                 inset_new_vert_b_perpendicular = bm.verts.new(inset_perpendicular_vert_co_b)

#                                 lines_perpendicular_verts.append(outset_new_vert_a_perpendicular)
#                                 lines_perpendicular_verts.append(outset_new_vert_b_perpendicular)

#                                 lines_perpendicular_verts.append(inset_new_vert_a_perpendicular)
#                                 lines_perpendicular_verts.append(inset_new_vert_b_perpendicular)

#                                 #   Work out the shifting vector and scaling factor for the vertex
#                                 outset_shifting_vector_a_perpendicular = (outset_perpendicular_vector * 0.5) + mathutils.Vector([0.5, 0.5, 0.5])
#                                 outset_shifting_vector_b_perpendicular = (outset_perpendicular_vector * 0.5) + mathutils.Vector([0.5, 0.5, 0.5])

#                                 inset_shifting_vector_a_perpendicular = (inset_perpendicular_vector * 0.5) + mathutils.Vector([0.5, 0.5, 0.5])
#                                 inset_shifting_vector_b_perpendicular = (inset_perpendicular_vector * 0.5) + mathutils.Vector([0.5, 0.5, 0.5])

#                                 #   Create the perpendicular outline faces
#                                 outset_new_perpendicular_face = bm.faces.new([new_vert_b_outer, new_vert_a_outer, outset_new_vert_a_perpendicular, outset_new_vert_b_perpendicular])
#                                 outset_new_perpendicular_face.material_index = 1
#                                 lines_faces.append(outset_new_perpendicular_face)

#                                 inset_new_perpendicular_face = bm.faces.new([new_vert_a_outer, new_vert_b_outer, inset_new_vert_b_perpendicular, inset_new_vert_a_perpendicular])
#                                 inset_new_perpendicular_face.material_index = 1
#                                 lines_faces.append(inset_new_perpendicular_face)

#                                 #   Assign the UV location for each vertex on the new face's loops
#                                 lines_verts[new_vert_a_outer_index].uv.append(Face_UV(outset_new_perpendicular_face, [0.313, 0.063]))
#                                 lines_verts[new_vert_b_outer_index].uv.append(Face_UV(outset_new_perpendicular_face, [0.313, 0.938]))

#                                 lines_verts[new_vert_a_outer_index].uv.append(Face_UV(inset_new_perpendicular_face, [0.313, 0.063]))
#                                 lines_verts[new_vert_b_outer_index].uv.append(Face_UV(inset_new_perpendicular_face, [0.313, 0.938]))

#                                 lines_verts.append(Shiftable_Vertex(outset_new_vert_a_perpendicular, Shifting_Vector(outset_shifting_vector_a_perpendicular, 1.0)))
#                                 lines_verts[-1].uv.append(Face_UV(outset_new_perpendicular_face, [0.563, 0.313]))

#                                 lines_verts.append(Shiftable_Vertex(outset_new_vert_b_perpendicular, Shifting_Vector(outset_shifting_vector_b_perpendicular, 1.0)))
#                                 lines_verts[-1].uv.append(Face_UV(outset_new_perpendicular_face, [0.563, 0.688]))

#                                 lines_verts.append(Shiftable_Vertex(inset_new_vert_a_perpendicular, Shifting_Vector(inset_shifting_vector_a_perpendicular, 1.0)))
#                                 lines_verts[-1].uv.append(Face_UV(inset_new_perpendicular_face, [0.563, 0.313]))

#                                 lines_verts.append(Shiftable_Vertex(inset_new_vert_b_perpendicular, Shifting_Vector(inset_shifting_vector_b_perpendicular, 1.0)))
#                                 lines_verts[-1].uv.append(Face_UV(inset_new_perpendicular_face, [0.563, 0.688]))

#             #   Stop the cycle
#             if (counter + 1) >= len(face.loops):
#                 break

#         #   Create the interior 'filler' faces
#         #   TODO: This is probably no longer needed and can be removed
#         if config["outline_inset_type"] == 'BEVEL':
#             if len(lines_inset_verts) > 2:
#                 new_face = bm.faces.new([vert for vert in lines_inset_verts])
#                 new_face.material_index = 1
#                 lines_faces.append(new_face)

#         #   Remove duplicate vertices that are formed when dealing with flaps that have to form around bends
#         if config["outline_inset_type"] == 'FLAP':
#             bmesh.ops.remove_doubles(bm, verts=list(lines_inset_verts), dist=0.0001)

#     #   Copy values stored in UV Maps to the filler faces that join some flaps
#     #   NOTE: This is the part that does not offset, so having overlapping vertices is pointless
#     if config["outline_inset_type"] == 'FLAP':
#         # print('filler_faces' + str(len(filler_faces)))
#         # print('filler_loop_outer' + str(len(filler_loop_outer)))
#         # print('filler_loop_inset_left' + str(len(filler_loop_inset_left)))
#         # print('filler_loop_inset_right' + str(len(filler_loop_inset_right)))
#         for filler_face in filler_faces:
#             for loop in filler_face.loops:
#                 for reference_loop in loop.vert.link_loops:
#                     if reference_loop is not loop:
#                         loop[bm.loops.layers.uv.get('Tile Top Texture + Lines Edge XY')].uv = reference_loop[bm.loops.layers.uv.get('Tile Top Texture + Lines Edge XY')].uv
#                         loop[bm.loops.layers.uv.get('Tile Pattern Texture + Lines Edge Z + Lines Offset Limit')].uv = reference_loop[bm.loops.layers.uv.get('Tile Pattern Texture + Lines Edge Z + Lines Offset Limit')].uv

#         for loop in filler_loop_outer:
#             loop[bm.loops.layers.uv.get('Lightmap + Lines Texture')].uv = [0.015625, 0.0625]
#         for loop in filler_loop_inset_left:
#             loop[bm.loops.layers.uv.get('Lightmap + Lines Texture')].uv = [0.75, 0.109375]
#         for loop in filler_loop_inset_right:
#             loop[bm.loops.layers.uv.get('Lightmap + Lines Texture')].uv = [0.75, 0.015625]

if __name__ == "__main__":
    print_it("Yo")