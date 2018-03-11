#
#   generate_wireframe.py
#
#   The purpose of this library is to perform the geometry and
#   meta-data generation on an abstracted version of the source
#   mesh data, allowing for integration with any number of
#   geometry/asset creation tools.
#


#
#   Imports
#

if "bpy" in locals():
    import importlib
    importlib.reload(helpers)
else:
    from . import helpers

import bpy
import bmesh
import math
import mathutils
from collections import namedtuple


#
#   Mesh/Object Metadata Management
#

#   Create Mesh/Object Metadata
def metadata_create(config, object):
    if (config["debug"] == True):
        print("metadata_create")

    #   Create vertex groups if not already present
    if ('Object' in object.vertex_groups) is False:
        object.vertex_groups.new('Object')
    if ('Lines' in object.vertex_groups) is False:
        object.vertex_groups.new('Lines')
    if ('Outline' in object.vertex_groups) is False:
        object.vertex_groups.new('Outline')
        
    #   Create UV maps if not already present
    if ('Object Texture 1 + Lines Edge XY' in object.data.uv_textures) is False:
        object.data.uv_textures.new('Object Texture 1 + Lines Edge XY')
    if ('Lightmap + Lines Texture' in object.data.uv_textures) is False:
        object.data.uv_textures.new('Lightmap + Lines Texture')
    if ('Object Texture 2 + Lines Edge Z + Lines Offset Limit' in object.data.uv_textures) is False:
        object.data.uv_textures.new('Object Texture 2 + Lines Edge Z + Lines Offset Limit')
        
    #   Create vertex colors if not already present
    if ('Col' in object.data.vertex_colors) is False:
        object.data.vertex_colors.new('Col')
    if ('Col_ALPHA' in object.data.vertex_colors) is False:
        object.data.vertex_colors.new('Col_ALPHA')

    #   Add custom split normals
    bpy.ops.mesh.customdata_custom_splitnormals_add()

#   Reset Mesh/Object Metadata
def metadata_reset(config, object):
    if (config["debug"] == True):
        print("metadata_reset")

    #   Remove vertex groups if present
    if ('Object' in object.vertex_groups) is True:
        object.vertex_groups.remove(object.vertex_groups['Object'])
    if ('Lines' in object.vertex_groups) is True:
        object.vertex_groups.remove(object.vertex_groups['Lines'])
    if ('Outline' in object.vertex_groups) is True:
        object.vertex_groups.remove(object.vertex_groups['Outline'])

    #   Remove UV maps if present
    if ('Object Texture 1 + Lines Edge XY' in object.data.uv_textures) is True:
        object.data.uv_textures.remove(object.data.uv_textures['Object Texture 1 + Lines Edge XY'])
    if ('Lightmap + Lines Texture' in object.data.uv_textures) is True:
        object.data.uv_textures.remove(object.data.uv_textures['Lightmap + Lines Texture'])
    if ('Object Texture 2 + Lines Edge Z + Lines Offset Limit' in object.data.uv_textures) is True:
        object.data.uv_textures.remove(object.data.uv_textures['Object Texture 2 + Lines Edge Z + Lines Offset Limit'])

    #   Remove vertex colors if present
    if ('Col' in object.data.vertex_colors) is True:
        object.data.vertex_colors.remove(object.data.vertex_colors['Col'])
    if ('Col_ALPHA' in object.data.vertex_colors) is True:
        object.data.vertex_colors.remove(object.data.vertex_colors['Col_ALPHA'])

    #   Clear custom split normals
    bpy.ops.mesh.customdata_custom_splitnormals_clear()


#
#   Geometry Creation
#

def geometry_create_inset(
        config, context, bm, object):
    if (config["debug"] == True):
        print("geometry_create_inset")

    #   TODO: Move to helper function (or an interface/class?)
    #   Stats from the current mesh
    object_geometry = helpers.list_geometry(bm)

    #   Track the added inset outline verts that follow the existing
    #   geometry (as opposed to the inset verts)
    #   This is so they may be merged later to remove duplicates
    lines_verts = []    #   TODO: Evaluate where to put/return this, as it used to be a global thing
    lines_faces = []    #   TODO: Evaluate where to put/return this, as it used to be a global thing
    lines_outer_verts = set()
    unconnected_flap_points = set()

    #   Track the filler faces
    filler_faces = set()
    filler_loop_inset_left = set()
    filler_loop_inset_right = set()
    filler_loop_outer = set()

    #   Create the lines geometry on a per-face (not per-tri) basis
    for face_counter, face in enumerate(object_geometry["faces"]):

        #   Set material
        face.material_index = 0

        #   Add the inset vertices
        lines_inset_verts = set()
        lines_perpendicular_verts = []

        repeating_loop = list(face.loops) * 2
        for counter, loops in [
            (
                counter,
                {
                    'verts': {
                        'prev_sharp': repeating_loop[counter - 3].vert,
                        'prev': repeating_loop[counter - 3].vert,
                        'a': repeating_loop[counter - 2].vert,
                        'b': repeating_loop[counter - 1].vert,
                        'next': repeating_loop[counter].vert,
                        'next_sharp': repeating_loop[counter].vert,
                    },
                    'edges': {
                        'prev_sharp': repeating_loop[counter - 3].edge,
                        'prev': repeating_loop[counter - 3].edge,
                        'curr': repeating_loop[counter - 2].edge,
                        'next': repeating_loop[counter - 1].edge,
                        'next_sharp': repeating_loop[counter - 1].edge,
                    },
                    'loops': {
                        'curr': repeating_loop[counter - 2]
                    },
                }
            ) for counter, loop in enumerate(repeating_loop)
        ]:

            #   Skip non-sharp edges
            #   TODO: Some kind of warning/check if there are no sharp edges on the object
            if loops['edges']['curr'].smooth is False:

                #   Find the next sharp edge sharing the same vert
                if loops['edges']['prev_sharp'].smooth is True:
                    found_edge = helpers.find_next_sharp_edge(face, loops['edges']['prev_sharp'], loops['verts']['a'], 0)
                    if found_edge is not False:
                        loops['edges']['prev_sharp'] = found_edge['edge']
                        loops['verts']['prev_sharp'] = found_edge['vert']

                if loops['edges']['next_sharp'].smooth is True:
                    found_edge = helpers.find_next_sharp_edge(face, loops['edges']['next_sharp'], loops['verts']['b'], 0)
                    if found_edge is not False:
                        loops['edges']['next_sharp'] = found_edge['edge']
                        loops['verts']['next_sharp'] = found_edge['vert']

                #   Add the new vertices
                new_vert_a_inset = bm.verts.new(mathutils.Vector([0.0, 0.0, 0.0]))
                new_vert_b_inset = bm.verts.new(mathutils.Vector([0.0, 0.0, 0.0]))

                new_vert_a_outer = bm.verts.new(loops['verts']['a'].co)
                new_vert_b_outer = bm.verts.new(loops['verts']['b'].co)

                #   Scaling factor of the 'cap' to ensure it maintains a parallel edge
                scaling_factor_a = 1.0
                scaling_factor_b = 1.0
 
                #   Vector along which the line will grow
                shifting_vector_a = mathutils.Vector([0.0, 0.0, 0.0])
                shifting_vector_b = mathutils.Vector([0.0, 0.0, 0.0])

                #   Vector along the edge of the flap
                flap_edge_vector = mathutils.Vector([0.0, 0.0, 0.0])

                #   Calculate the vectors describing the 'cap' edges on each end of the new face
                vector_to_prev_a = (loops['verts']['prev_sharp'].co - loops['verts']['a'].co).normalized()
                vector_to_next_a = (loops['verts']['b'].co - loops['verts']['a'].co).normalized()

                vector_to_prev_b = (loops['verts']['a'].co - loops['verts']['b'].co).normalized()
                vector_to_next_b = (loops['verts']['next_sharp'].co - loops['verts']['b'].co).normalized()

                #   Test if the cap is valid, or needs to be wound back from an invalid angle due to bending around a corner to find the next sharp edge
                #   TODO: Currently only triggers if the angle for the cap 'edge' is closing in on 180* - need to change it to only allow up to 90* and add a filler piece if the angle is greater than that.
                vector_edge_tangent = (loops['edges']['curr'].calc_tangent(loops['loops']['curr'])).normalized()

                cap_angle_from_tangent_a = vector_to_prev_a.angle(vector_edge_tangent, 0)
                cap_angle_from_tangent_b = vector_to_next_b.angle(vector_edge_tangent, 0)

                #   TODO: Might need to change this check to math.pi / 4, double check the math!
                cap_a_flap_unconnected = False
                if cap_angle_from_tangent_a > ((math.pi / 2) - 0.1):
                    cap_a_flap_unconnected = True
                    vector_to_prev_a = (vector_edge_tangent * -1)
                    cap_angle_from_tangent_a = vector_to_prev_a.angle(vector_edge_tangent, 0)
                else:
                    vector_to_prev_a = (vector_to_prev_a * -1)

                cap_b_flap_unconnected = False
                if cap_angle_from_tangent_b > ((math.pi / 2) - 0.1):
                    cap_b_flap_unconnected = True
                    vector_to_next_b = (vector_edge_tangent * -1)
                    cap_angle_from_tangent_b = vector_to_next_b.angle(vector_edge_tangent, 0)
                else:
                    vector_to_next_b = (vector_to_next_b * -1)

                #   Work out the shifting vector and scaling factor for the vertex
                scaling_factor_a = math.fabs(math.sin((math.pi / 2)) / math.sin(((math.pi / 2) - cap_angle_from_tangent_a)))
                scaling_factor_b = math.fabs(math.sin((math.pi / 2)) / math.sin(((math.pi / 2) - cap_angle_from_tangent_b)))

                flap_edge_vector = (vector_to_next_a * -0.5) + mathutils.Vector([0.5, 0.5, 0.5])

                #   Initial position of new inset vertices
                new_vert_co_a = (loops['verts']['a'].co - (vector_to_prev_a * config["outline_inset"] * scaling_factor_a))
                new_vert_co_b = (loops['verts']['b'].co - (vector_to_next_b * config["outline_inset"] * scaling_factor_b))

                #   Position the new vertices
                new_vert_a_inset.co = new_vert_co_a
                new_vert_b_inset.co = new_vert_co_b

                #   Store the new vertices
                lines_inset_verts.add(new_vert_a_inset)
                lines_inset_verts.add(new_vert_b_inset)

                lines_outer_verts.add(new_vert_a_outer)
                lines_outer_verts.add(new_vert_b_outer)

                #   Create the inset outline face
                new_face = bm.faces.new([new_vert_a_outer, new_vert_b_outer, new_vert_b_inset, new_vert_a_inset])
                new_face.material_index = 1
                lines_faces.append(new_face)

                #   Find out which edge on the face provides the best border to limit expansion of this line segment
                maximum_limit = 10
                limit_a = maximum_limit
                limit_b = maximum_limit

                #   Gather all of the edges of the coplanar faces attached to this one
                coplanar_faces_edges = set()
                for edge in face.edges:
                    coplanar_faces_edges.add(edge)
                for object_face in object_geometry["faces"]:
                    if (object_face.normal - face.normal).magnitude < 0.0001 and -0.001 < face.normal.dot(object_face.calc_center_median_weighted() - face.calc_center_median_weighted()) < 0.001:
                        for edge in object_face.edges:
                            coplanar_faces_edges.add(edge)

                #   Check all coplanar edges to find which one the flap's caps intersect with first
                for edge in coplanar_faces_edges:
                    if edge is not loops['edges']['curr'] and edge.smooth is False:

                        #   Compare edges for A cap
                        if edge is not loops['edges']['prev_sharp'] and edge is not loops['edges']['prev']:
                            intersecting_points = mathutils.geometry.intersect_line_line(loops['verts']['a'].co, (loops['verts']['a'].co + vector_to_prev_a), edge.verts[0].co, edge.verts[1].co)

                            #   Check if the intersection with the line defined by the edge actually occurs between the the verts making up the edge
                            if intersecting_points is not None and (intersecting_points[0] - intersecting_points[1]).magnitude < 0.00001:
                                if (
                                    #   First, check for an exact hit on a vertex
                                    (intersecting_points[1] - edge.verts[0].co).magnitude < 0.00001 or (intersecting_points[1] - edge.verts[1].co).magnitude < 0.00001 or
                                    #   Next, check for a hit on the midpoint of an edge    
                                    (edge.verts[0].co - intersecting_points[1]).dot(edge.verts[1].co - intersecting_points[1]) < 0
                                ):
                                    limit_a = min(limit_a, (loops['verts']['a'].co - intersecting_points[1]).magnitude)

                        #   Compare edges for B cap
                        if edge is not loops['edges']['next_sharp'] and edge is not loops['edges']['next']:
                            intersecting_points = mathutils.geometry.intersect_line_line(loops['verts']['b'].co, (loops['verts']['b'].co + vector_to_next_b), edge.verts[0].co, edge.verts[1].co)

                            #   Check if the two lines actually intersect, mark the point that they do as a corner
                            if intersecting_points is not None and (intersecting_points[0] - intersecting_points[1]).magnitude < 0.00001:
                                if (
                                    #   First, check for an exact hit on a vertex
                                    (intersecting_points[1] - edge.verts[0].co).magnitude < 0.00001 or (intersecting_points[1] - edge.verts[1].co).magnitude < 0.00001 or
                                    #   Next, check for a hit on the midpoint of an edge    
                                    (edge.verts[0].co - intersecting_points[1]).dot(edge.verts[1].co - intersecting_points[1]) < 0
                                ):
                                    limit_b = min(limit_b, (loops['verts']['b'].co - intersecting_points[1]).magnitude)

                #   Store a vector representing the direction of the line's edge
                for flap_loop in new_face.loops:
                    # print('FL: ' + str(flap_loop))
                    if flap_loop.vert is new_vert_a_inset or flap_loop.vert is new_vert_b_inset:
                        flap_loop[bm.loops.layers.uv.get('Object Texture 1 + Lines Edge XY')].uv = [flap_edge_vector.x, flap_edge_vector.y]

                        limit = maximum_limit
                        if flap_loop.vert is new_vert_a_inset:
                            limit = limit_a
                        elif flap_loop.vert is new_vert_b_inset:
                            limit = limit_b
                        limit = (limit / maximum_limit)

                        flap_loop[bm.loops.layers.uv.get('Object Texture 2 + Lines Edge Z + Lines Offset Limit')].uv = [flap_edge_vector.z, limit]
                    if flap_loop.vert is new_vert_a_outer or flap_loop.vert is new_vert_b_outer:
                        flap_loop[bm.loops.layers.uv.get('Object Texture 1 + Lines Edge XY')].uv = [0.5, 0.5]
                        flap_loop[bm.loops.layers.uv.get('Object Texture 2 + Lines Edge Z + Lines Offset Limit')].uv = [0.5, 0.0]
                # print(' ')

                #   Find vertices of flap caps that are unconnected (have a gap due to a convex join), and join them
                if cap_a_flap_unconnected is True:
                    for cap in unconnected_flap_points:
                        if (cap.outer_vert.co - new_vert_a_outer.co).magnitude < 0.0001 and (cap.inset_vert.co - new_vert_a_inset.co).magnitude > 0.0001:
                            new_filler_face_a = bm.faces.new([cap.outer_vert, new_vert_a_inset, cap.inset_vert])
                            new_filler_face_a.material_index = 1
                            lines_faces.append(new_filler_face_a)
                            filler_faces.add(new_filler_face_a)

                            #   Add the values stored in the UV layers
                            for loop in new_filler_face_a.loops:
                                if (loop.vert.co - cap.outer_vert.co).magnitude < 0.0001:
                                    filler_loop_outer.add(loop)
                                if (loop.vert.co - new_vert_a_inset.co).magnitude < 0.0001:
                                    filler_loop_inset_right.add(loop)
                                if (loop.vert.co - cap.inset_vert.co).magnitude < 0.0001:
                                    filler_loop_inset_left.add(loop)
                            break
                    unconnected_flap_points.add(Potential_Cap_Filler_Edge(new_vert_a_outer, new_vert_a_inset))

                if cap_b_flap_unconnected is True:
                    for cap in unconnected_flap_points:
                        if (cap.outer_vert.co - new_vert_b_outer.co).magnitude < 0.0001 and (cap.inset_vert.co - new_vert_b_inset.co).magnitude > 0.0001:
                            new_filler_face_b = bm.faces.new([cap.outer_vert, cap.inset_vert, new_vert_b_inset])
                            new_filler_face_b.material_index = 1
                            lines_faces.append(new_filler_face_b)
                            filler_faces.add(new_filler_face_b)

                            #   Add the values stored in the UV layers
                            for loop in new_filler_face_b.loops:
                                if (loop.vert.co - cap.outer_vert.co).magnitude < 0.0001:
                                    filler_loop_outer.add(loop)
                                if (loop.vert.co - new_vert_b_inset.co).magnitude < 0.0001:
                                    filler_loop_inset_left.add(loop)
                                if (loop.vert.co - cap.inset_vert.co).magnitude < 0.0001:
                                    filler_loop_inset_right.add(loop)
                            break
                    unconnected_flap_points.add(Potential_Cap_Filler_Edge(new_vert_b_outer, new_vert_b_inset))

                #   Vector along which the edge will slide to grow the line
                #   TODO: Why is the scaling factor being applied here, and then stored as a separate value?
                # shifting_vector_a = ((((vector_to_prev_a * -1) * scaling_factor_a) * 0.5) + mathutils.Vector([0.5, 0.5, 0.5]))
                # shifting_vector_b = ((((vector_to_next_b * -1) * scaling_factor_b) * 0.5) + mathutils.Vector([0.5, 0.5, 0.5]))

                shifting_vector_a = (vector_to_prev_a * -0.5) + mathutils.Vector([0.5, 0.5, 0.5])
                shifting_vector_b = (vector_to_next_b * -0.5) + mathutils.Vector([0.5, 0.5, 0.5])

                #   Assign the UV location for each vertex on the new face's loops
                lines_verts.append(Shiftable_Vertex(new_vert_a_outer, Shifting_Vector(mathutils.Vector(([0.5, 0.5, 0.5])), 1.0)))
                new_vert_a_outer_index = len(lines_verts) - 1
                lines_verts[-1].uv.append(Face_UV(new_face, [0.015625, 0.015625]))

                lines_verts.append(Shiftable_Vertex(new_vert_b_outer, Shifting_Vector(mathutils.Vector(([0.5, 0.5, 0.5])), 1.0)))
                new_vert_b_outer_index = len(lines_verts) - 1
                lines_verts[-1].uv.append(Face_UV(new_face, [0.015625, 0.109375]))

                lines_verts.append(Shiftable_Vertex(new_vert_a_inset, Shifting_Vector(shifting_vector_a, (1 / scaling_factor_a))))
                lines_verts[-1].uv.append(Face_UV(new_face, [0.75, 0.015625]))

                lines_verts.append(Shiftable_Vertex(new_vert_b_inset, Shifting_Vector(shifting_vector_b, (1 / scaling_factor_b))))
                lines_verts[-1].uv.append(Face_UV(new_face, [0.75, 0.109375]))

            #   Stop the cycle
            if (counter + 1) >= len(face.loops):
                break

        #   Remove duplicate vertices that are formed when dealing with flaps that have to form around bends
        bmesh.ops.remove_doubles(bm, verts=list(lines_inset_verts), dist=0.0001)

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
    
    

    #   TODO: Move to helper function
    # tile_verts_indices = []
    # [tile_verts_indices.append(shiftable_vertex.vert.index) for shiftable_vertex in tile_verts if shiftable_vertex.vert.is_valid is True]
    # tile.vertex_groups['Tile'].add(tile_verts_indices, 1, 'ADD')

    # lines_verts_indices = []
    # [lines_verts_indices.append(shiftable_vertex.vert.index) for shiftable_vertex in lines_verts if shiftable_vertex.vert.is_valid is True]
    # tile.vertex_groups['Lines'].add(lines_verts_indices, 1, 'ADD')
    
    # outline_verts_indices = []
    # [outline_verts_indices.append(shiftable_vertex.vert.index) for shiftable_vertex in outline_verts if shiftable_vertex.vert.is_valid is True]
    # tile.vertex_groups['Outline'].add(outline_verts_indices, 1, 'ADD')

    helpers.vertex_groups_lock(object, ["Object", "Lines", "Outline"])
    helpers.bmesh_to_object(bm, object)


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


#
#   __main__ Check
#

if __name__ == "__main__":
    print("generate_wireframe.py is not intended to be run as __main__")