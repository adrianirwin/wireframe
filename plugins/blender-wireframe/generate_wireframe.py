#   TODO: Docstring for the module, functions, and classes

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

if 'bpy' in locals():
    import importlib
    importlib.reload(helpers)
    importlib.reload(classes)
else:
    from . import helpers
    from . import classes

import bpy
import bmesh
import mathutils


#
#   Mesh/Object Metadata Management
#

#   Create Mesh/Object Metadata
def metadata_create(config, object):
    if (config['debug'] == True):
        print('metadata_create')

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
    if (config['debug'] == True):
        print('metadata_reset')

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
    if (config['debug'] == True):
        print('geometry_create_inset')

    #   Geometry (faces, edges, and verts) from the current
    #   object's mesh.
    object_geometry = helpers.list_geometry(bm)

    #   Track the added inset outline verts that follow the existing
    #   geometry (as opposed to the inset verts).
    #   This is so they may be merged later to remove duplicates.
    lines_geometry = classes.Lines_Geometry()

    lines_outer_verts = set()
    unconnected_flap_points = set()

    #   Track the filler faces.
    filler_faces = set()
    filler_loop_inset_left = set()
    filler_loop_inset_right = set()
    filler_loop_outer = set()

    #   Create the inset lines' geometry on a per-face
    #   (not per-tri) basis.
    for face_counter, face in enumerate(object_geometry['faces']):

        #   Set material.
        face.material_index = 0

        #   Store the inset vertices.
        lines_inset_verts = set()
        lines_perpendicular_verts = []

        #   Prepare a looping structure with extra metadata for
        #   detailed stepping-through.
        #   The iteration is targetted on the loop of each face, and
        #   adds detailed breakdowns of the vertices and edges that are
        #   both 'in front' and 'behind' the current loop's position.
        #   Finally, it is critical to know where the next vertex and
        #   edge that are marked sharp are located. A default value is
        #   set here, and the helpers.find_next_sharp_edge function is
        #   called later to test and replace those values if they are
        #   not correct.
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
                        'current': repeating_loop[counter - 2].edge,
                        'next': repeating_loop[counter - 1].edge,
                        'next_sharp': repeating_loop[counter - 1].edge,
                    },
                    'loops': {
                        'current': repeating_loop[counter - 2]
                    },
                }
            ) for counter, loop in enumerate(repeating_loop)
        ]:

            #   Skip non-sharp edges.
            #   TODO: Some kind of warning/check if there are
            #   no sharp edges on the object.
            if loops['edges']['current'].smooth is False:

                #   Find the next sharp edge sharing the same vert
                if loops['edges']['prev_sharp'].smooth is True:
                    found_edge = helpers.find_next_sharp_edge(
                        face,
                        loops['edges']['prev_sharp'],
                        loops['verts']['a'],
                        0
                    )

                    if found_edge is not False:
                        loops['edges']['prev_sharp'] = found_edge['edge']
                        loops['verts']['prev_sharp'] = found_edge['vert']

                if loops['edges']['next_sharp'].smooth is True:
                    found_edge = helpers.find_next_sharp_edge(face,
                        loops['edges']['next_sharp'],
                        loops['verts']['b'],
                        0
                    )

                    if found_edge is not False:
                        loops['edges']['next_sharp'] = found_edge['edge']
                        loops['verts']['next_sharp'] = found_edge['vert']

                a_side_verts = helpers.create_inset_face_vertices(
                    bm,
                    config['outline_inset'],
                    loops['loops']['current'],
                    loops['edges']['current'],
                    loops['verts']['a'],
                    loops['verts']['b'],
                    loops['verts']['prev_sharp'],
                )

                b_side_verts = helpers.create_inset_face_vertices(
                    bm,
                    config['outline_inset'],
                    loops['loops']['current'],
                    loops['edges']['current'],
                    loops['verts']['b'],
                    loops['verts']['a'],
                    loops['verts']['next_sharp'],
                )

                #   Store the new vertices.
                lines_inset_verts.add(a_side_verts['inset'])
                lines_inset_verts.add(b_side_verts['inset'])

                lines_outer_verts.add(a_side_verts['edge'])
                lines_outer_verts.add(b_side_verts['edge'])

                #   Create the inset outline face.
                new_face = bm.faces.new([
                    a_side_verts['edge'],
                    b_side_verts['edge'],
                    b_side_verts['inset'],
                    a_side_verts['inset'],
                ])
                new_face.material_index = 1
                lines_geometry.faces.append(new_face)

                #   Find out which edge on the face provides the best
                #   border to limit expansion of this line segment
                maximum_limit = 10
                limit_a = maximum_limit
                limit_b = maximum_limit

                #   Gather all of the edges of the coplanar faces
                #   attached to this one
                coplanar_faces_edges = set()
                for edge in face.edges:
                    coplanar_faces_edges.add(edge)
                for object_face in object_geometry['faces']:
                    if (object_face.normal - face.normal).magnitude < 0.0001 and -0.001 < face.normal.dot(object_face.calc_center_median_weighted() - face.calc_center_median_weighted()) < 0.001:
                        for edge in object_face.edges:
                            coplanar_faces_edges.add(edge)

                #   Check all coplanar edges to find which one the flap's caps intersect with first
                for edge in coplanar_faces_edges:
                    if edge is not loops['edges']['current'] and edge.smooth is False:

                        #   Compare edges for A cap
                        if edge is not loops['edges']['prev_sharp'] and edge is not loops['edges']['prev']:
                            intersecting_points = mathutils.geometry.intersect_line_line(loops['verts']['a'].co, (loops['verts']['a'].co + a_side_verts['TEMP_vec']), edge.verts[0].co, edge.verts[1].co)

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
                            intersecting_points = mathutils.geometry.intersect_line_line(loops['verts']['b'].co, (loops['verts']['b'].co + b_side_verts['TEMP_vec']), edge.verts[0].co, edge.verts[1].co)

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
                    if flap_loop.vert is a_side_verts['inset'] or flap_loop.vert is b_side_verts['inset']:
                        flap_loop[bm.loops.layers.uv.get('Object Texture 1 + Lines Edge XY')].uv = [a_side_verts['flap_edge_vector'].x, a_side_verts['flap_edge_vector'].y]

                        limit = maximum_limit
                        if flap_loop.vert is a_side_verts['inset']:
                            limit = limit_a
                        elif flap_loop.vert is b_side_verts['inset']:
                            limit = limit_b
                        limit = (limit / maximum_limit)

                        flap_loop[bm.loops.layers.uv.get('Object Texture 2 + Lines Edge Z + Lines Offset Limit')].uv = [a_side_verts['flap_edge_vector'].z, limit]
                    if flap_loop.vert is a_side_verts['edge'] or flap_loop.vert is b_side_verts['edge']:
                        flap_loop[bm.loops.layers.uv.get('Object Texture 1 + Lines Edge XY')].uv = [0.5, 0.5]
                        flap_loop[bm.loops.layers.uv.get('Object Texture 2 + Lines Edge Z + Lines Offset Limit')].uv = [0.5, 0.0]
                # print(' ')

                #   Find vertices of flap caps that are unconnected (have a gap due to a convex join), and join them
                if a_side_verts['cap_flap_unconnected'] is True:
                    for cap in unconnected_flap_points:
                        if (cap.outer_vert.co - a_side_verts['edge'].co).magnitude < 0.0001 and (cap.inset_vert.co - a_side_verts['inset'].co).magnitude > 0.0001:
                            new_filler_face_a = bm.faces.new([cap.outer_vert, a_side_verts['inset'], cap.inset_vert])
                            new_filler_face_a.material_index = 1
                            lines_geometry.faces.append(new_filler_face_a)
                            filler_faces.add(new_filler_face_a)

                            #   Add the values stored in the UV layers
                            for loop in new_filler_face_a.loops:
                                if (loop.vert.co - cap.outer_vert.co).magnitude < 0.0001:
                                    filler_loop_outer.add(loop)
                                if (loop.vert.co - a_side_verts['inset'].co).magnitude < 0.0001:
                                    filler_loop_inset_right.add(loop)
                                if (loop.vert.co - cap.inset_vert.co).magnitude < 0.0001:
                                    filler_loop_inset_left.add(loop)
                            break
                    unconnected_flap_points.add(classes.Potential_Cap_Filler_Edge(a_side_verts['edge'], a_side_verts['inset']))

                if b_side_verts['cap_flap_unconnected'] is True:
                    for cap in unconnected_flap_points:
                        if (cap.outer_vert.co - b_side_verts['edge'].co).magnitude < 0.0001 and (cap.inset_vert.co - b_side_verts['inset'].co).magnitude > 0.0001:
                            new_filler_face_b = bm.faces.new([cap.outer_vert, cap.inset_vert, b_side_verts['inset']])
                            new_filler_face_b.material_index = 1
                            lines_geometry.faces.append(new_filler_face_b)
                            filler_faces.add(new_filler_face_b)

                            #   Add the values stored in the UV layers
                            for loop in new_filler_face_b.loops:
                                if (loop.vert.co - cap.outer_vert.co).magnitude < 0.0001:
                                    filler_loop_outer.add(loop)
                                if (loop.vert.co - b_side_verts['inset'].co).magnitude < 0.0001:
                                    filler_loop_inset_left.add(loop)
                                if (loop.vert.co - cap.inset_vert.co).magnitude < 0.0001:
                                    filler_loop_inset_right.add(loop)
                            break
                    unconnected_flap_points.add(classes.Potential_Cap_Filler_Edge(b_side_verts['edge'], b_side_verts['inset']))

                shifting_vector_a = (a_side_verts['TEMP_vec'] * -0.5) + mathutils.Vector([0.5, 0.5, 0.5])
                shifting_vector_b = (b_side_verts['TEMP_vec'] * -0.5) + mathutils.Vector([0.5, 0.5, 0.5])

                #   Assign the UV location for each vertex on the new face's loops
                lines_geometry.verts.append(classes.Shiftable_Vertex(a_side_verts['edge'], classes.Shifting_Vector(mathutils.Vector(([0.5, 0.5, 0.5])), 1.0)))
                a_side_verts_edge_index = len(lines_geometry.verts) - 1
                lines_geometry.verts[-1].uv.append(classes.Face_UV(new_face, [0.015625, 0.015625]))

                lines_geometry.verts.append(classes.Shiftable_Vertex(b_side_verts['edge'], classes.Shifting_Vector(mathutils.Vector(([0.5, 0.5, 0.5])), 1.0)))
                b_side_verts_edge_index = len(lines_geometry.verts) - 1
                lines_geometry.verts[-1].uv.append(classes.Face_UV(new_face, [0.015625, 0.109375]))

                lines_geometry.verts.append(classes.Shiftable_Vertex(a_side_verts['inset'], classes.Shifting_Vector(shifting_vector_a, (1 / a_side_verts['scaling_factor']))))
                lines_geometry.verts[-1].uv.append(classes.Face_UV(new_face, [0.75, 0.015625]))

                lines_geometry.verts.append(classes.Shiftable_Vertex(b_side_verts['inset'], classes.Shifting_Vector(shifting_vector_b, (1 / b_side_verts['scaling_factor']))))
                lines_geometry.verts[-1].uv.append(classes.Face_UV(new_face, [0.75, 0.109375]))

            #   Stop the cycle
            if (counter + 1) >= len(face.loops):
                break

        #   Remove duplicate vertices that are formed when dealing with flaps that have to form around bends
        bmesh.ops.remove_doubles(bm, verts=list(lines_inset_verts), dist=0.0001)

#     #   Copy values stored in UV Maps to the filler faces that join some flaps
#     #   NOTE: This is the part that does not offset, so having overlapping vertices is pointless
#     if config['outline_inset_type'] == 'FLAP':
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
    # [lines_verts_indices.append(shiftable_vertex.vert.index) for shiftable_vertex in lines_geometry.verts if shiftable_vertex.vert.is_valid is True]
    # tile.vertex_groups['Lines'].add(lines_verts_indices, 1, 'ADD')
    
    # outline_verts_indices = []
    # [outline_verts_indices.append(shiftable_vertex.vert.index) for shiftable_vertex in outline_verts if shiftable_vertex.vert.is_valid is True]
    # tile.vertex_groups['Outline'].add(outline_verts_indices, 1, 'ADD')

    #   Lock vertex groups
    helpers.vertex_groups_lock(object, ['Object', 'Lines', 'Outline'])

    #   Push data back into the object's mesh
    helpers.bmesh_to_object(bm, object)

    return lines_geometry


#
#   __main__ Check
#

if __name__ == '__main__':
    print('generate_wireframe.py is not intended to be run as __main__')