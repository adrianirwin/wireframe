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

def geometry_create_inset_lines(
        config, context, object
):
    """Create the geometry, UV maps, and vertex colours for the inset lines."""
    if (config['debug'] == True):
        print('geometry_create_inset_lines')

    #   Load the object's mesh datablock into a bmesh
    bm = helpers.object_to_bmesh(object)

    #   Geometry (faces, edges, and verts) from the current
    #   object's mesh.
    object_geometry = helpers.list_geometry(bm)

    #   Newly created geometry (faces and verts) for the inset lines.
    lines_geometry = classes.Lines_Geometry()

    #   Perform tests on the object's geometry to communicate any
    #   deficiencies that need to be addressed.
    if any(edge.smooth == False for edge in object_geometry['edges']) == False:
        bpy.ops.wm.generic_dialog(
            'INVOKE_DEFAULT',
            message='WARNING: Mesh must have edges marked as sharp.'
        )
        return lines_geometry

    #   Filler faces that need to be generated when two inset line
    #   faces do not join due to being created on two edges that meet
    #   at an angle of >180*.
    filler_faces = set()
    filler_loop_inset_left = set()
    filler_loop_inset_right = set()
    filler_loop_outer = set()

    #   Create the inset lines' geometry on a per-face
    #   (not per-tri) basis.
    for face_counter, face in enumerate(object_geometry['faces']):

        #   Track the added inset outline verts that follow the
        #   existing geometry (as opposed to the inset verts).
        #   This is so they may be merged later to remove duplicates.
        unconnected_flap_points = set()
        lines_inset_verts = set()

        #   Set material.
        #   TODO: Move into function that deals specifically with the
        #   object's geometry, not the lines geometry.
        face.material_index = 0

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

                a_side_cap = helpers.create_inset_face_cap(
                    bm,
                    config['outline_inset'],
                    loops['loops']['current'],
                    loops['edges']['current'],
                    loops['verts']['a'],
                    loops['verts']['b'],
                    loops['verts']['prev_sharp'],
                )

                b_side_cap = helpers.create_inset_face_cap(
                    bm,
                    config['outline_inset'],
                    loops['loops']['current'],
                    loops['edges']['current'],
                    loops['verts']['b'],
                    loops['verts']['a'],
                    loops['verts']['next_sharp'],
                )

                #   Store the new vertices.
                lines_inset_verts.add(a_side_cap['vert_inset'])
                lines_inset_verts.add(b_side_cap['vert_inset'])

                #   Create the inset outline face.
                new_face = bm.faces.new([
                    a_side_cap['vert_edge'],
                    b_side_cap['vert_edge'],
                    b_side_cap['vert_inset'],
                    a_side_cap['vert_inset'],
                ])
                new_face.material_index = 1
                lines_geometry.faces.append(new_face)


                #   Find out which edge on the face provides the best
                #   border to limit expansion of this line segment.

                #   Limit the potential growth of the inset face to
                #   so it does not break the silhouette of the object 
                #   TODO: Move the maximum to a config option
                maximum_limit = 10
                limit_a = maximum_limit
                limit_b = maximum_limit


                #   Gather all of the edges of the coplanar faces
                #   attached to this one.
                coplanar_faces_edges = set()
                for edge in face.edges:
                    coplanar_faces_edges.add(edge)
                for object_face in object_geometry['faces']:
                    if (
                        (object_face.normal - face.normal).magnitude < 0.0001
                        and -0.001 < face.normal.dot(object_face.calc_center_median_weighted() - face.calc_center_median_weighted()) < 0.001
                    ):
                        for edge in object_face.edges:
                            coplanar_faces_edges.add(edge)


                #   Check all coplanar edges to find which one the
                #   flap's caps intersect with first as they grow.
                for edge in coplanar_faces_edges:
                    if (
                        edge is not loops['edges']['current']
                        and edge.smooth is False
                    ):

                        #   Compare edges for A cap
                        limit_a = helpers.calculate_inset_face_cap_growth_limit(
                            loops['verts']['a'],
                            loops['edges']['prev'],
                            loops['edges']['prev_sharp'],
                            a_side_cap['vector_to_inset_vert'],
                            edge, edge.verts[0], edge.verts[1],
                            limit_a,
                        )

                        limit_b = helpers.calculate_inset_face_cap_growth_limit(
                            loops['verts']['b'],
                            loops['edges']['next'],
                            loops['edges']['next_sharp'],
                            b_side_cap['vector_to_inset_vert'],
                            edge, edge.verts[0], edge.verts[1],
                            limit_b,
                        )


                #   Store a vector representing the direction along
                #   which that particular line fragment runs.
                #   Also, store the limit of that line fragment's cap
                #   that may expand.
                for loop in new_face.loops:

                    line_direction_vector = classes.Shifting_Vector(0.0)

                    #   The line direction vector is only needed on the
                    #   inset portion of the new face
                    if loop.vert is a_side_cap['vert_inset'] or loop.vert is b_side_cap['vert_inset']:

                        line_direction_vector.vector.x = a_side_cap['edge_vector'].x
                        line_direction_vector.vector.y = a_side_cap['edge_vector'].y
                        line_direction_vector.vector.z = a_side_cap['edge_vector'].z

                        limit = maximum_limit
                        if loop.vert is a_side_cap['vert_inset']:
                            limit = limit_a
                        elif loop.vert is b_side_cap['vert_inset']:
                            limit = limit_b
                        line_direction_vector.factor = (limit / maximum_limit)

                    loop[bm.loops.layers.uv.get('Object Texture 1 + Lines Edge XY')].uv = [
                        line_direction_vector.vector.x, line_direction_vector.vector.y,
                    ]
                    loop[bm.loops.layers.uv.get('Object Texture 2 + Lines Edge Z + Lines Offset Limit')].uv = [
                        line_direction_vector.vector.z, line_direction_vector.factor,
                    ]


                #   Find vertices of flap caps that are unconnected (have a gap due to a convex join), and join them
                #   TODO: Move to helpers.py
                if a_side_cap['inset_face_cap_unconnected'] is True:
                    made_cap_filler = False
                    for cap in unconnected_flap_points:
                        if (cap.edge_vert.co - a_side_cap['vert_edge'].co).magnitude < 0.0001 and (cap.inset_vert.co - a_side_cap['vert_inset'].co).magnitude > 0.0001:
                            new_filler_face_a = bm.faces.new([cap.edge_vert, a_side_cap['vert_inset'], cap.inset_vert])
                            new_filler_face_a.material_index = 1
                            lines_geometry.faces.append(new_filler_face_a)
                            filler_faces.add(new_filler_face_a)

                            #   Add the values stored in the UV layers
                            for loop in new_filler_face_a.loops:
                                if (loop.vert.co - cap.edge_vert.co).magnitude < 0.0001:
                                    filler_loop_outer.add(loop)
                                if (loop.vert.co - a_side_cap['vert_inset'].co).magnitude < 0.0001:
                                    filler_loop_inset_right.add(loop)
                                if (loop.vert.co - cap.inset_vert.co).magnitude < 0.0001:
                                    filler_loop_inset_left.add(loop)

                            unconnected_flap_points.remove(cap)
                            made_cap_filler = True
                            break
                    if made_cap_filler == False:
                        unconnected_flap_points.add(classes.Potential_Cap_Filler_Edge(a_side_cap['vert_edge'], a_side_cap['vert_inset']))

                if b_side_cap['inset_face_cap_unconnected'] is True:
                    made_cap_filler = False
                    for cap in unconnected_flap_points:
                        if (cap.edge_vert.co - b_side_cap['vert_edge'].co).magnitude < 0.0001 and (cap.inset_vert.co - b_side_cap['vert_inset'].co).magnitude > 0.0001:
                            new_filler_face_b = bm.faces.new([cap.edge_vert, cap.inset_vert, b_side_cap['vert_inset']])
                            new_filler_face_b.material_index = 1
                            lines_geometry.faces.append(new_filler_face_b)
                            filler_faces.add(new_filler_face_b)

                            #   Add the values stored in the UV layers
                            for loop in new_filler_face_b.loops:
                                if (loop.vert.co - cap.edge_vert.co).magnitude < 0.0001:
                                    filler_loop_outer.add(loop)
                                if (loop.vert.co - b_side_cap['vert_inset'].co).magnitude < 0.0001:
                                    filler_loop_inset_left.add(loop)
                                if (loop.vert.co - cap.inset_vert.co).magnitude < 0.0001:
                                    filler_loop_inset_right.add(loop)

                            unconnected_flap_points.remove(cap)
                            made_cap_filler = True
                            break
                    if made_cap_filler == False:
                        unconnected_flap_points.add(classes.Potential_Cap_Filler_Edge(b_side_cap['vert_edge'], b_side_cap['vert_inset']))


                #   Store the UV coordinates for each vertex on the
                #   new face. The fractional values (e.g. 7 / 64) are
                #   due to the lines utilizing a texture map that is
                #   64 pixels wide and high, and needing to align
                #   the UV coordinates with a border in the texture.

                #   Line Cap A, Edge Vertex
                lines_geometry.verts.append(
                    classes.Shiftable_Vertex(
                        a_side_cap['vert_edge'],
                        classes.Shifting_Vector()
                    )
                )
                lines_geometry.verts[-1].uv.append(
                    classes.Face_UV(new_face, [(1 / 64), (1 / 64)])
                )

                #   Line Cap B, Edge Vertex
                lines_geometry.verts.append(
                    classes.Shiftable_Vertex(
                        b_side_cap['vert_edge'],
                        classes.Shifting_Vector()
                    )
                )
                lines_geometry.verts[-1].uv.append(
                    classes.Face_UV(new_face, [(1 / 64), (7 / 64)])
                )

                #   Line Cap A, Inset Vertex
                lines_geometry.verts.append(
                    classes.Shiftable_Vertex(
                        a_side_cap['vert_inset'],
                        classes.Shifting_Vector(
                            (1 / a_side_cap['scaling_factor']),
                            helpers.convert_vector_to_colour(a_side_cap['vector_to_inset_vert'])
                        )
                    )
                )
                lines_geometry.verts[-1].uv.append(
                    classes.Face_UV(new_face, [(48 / 64), (1 / 64)])
                )

                #   Line Cap B, Inset Vertex
                lines_geometry.verts.append(
                    classes.Shiftable_Vertex(
                        b_side_cap['vert_inset'],
                        classes.Shifting_Vector(
                            (1 / b_side_cap['scaling_factor']),
                            helpers.convert_vector_to_colour(b_side_cap['vector_to_inset_vert'])
                        )
                    )
                )
                lines_geometry.verts[-1].uv.append(
                    classes.Face_UV(new_face, [(48 / 64), (7 / 64)])
                )


            #   Manually stop the cycle due to the loop being made
            #   twice as long as its natural length.
            if (counter + 1) >= len(face.loops):
                break

        #   Remove duplicate vertices that are formed when dealing with
        #   flaps that have to form around bends.
        bmesh.ops.remove_doubles(bm, verts=list(lines_inset_verts), dist=0.0001)


    #   Assign UV values and vertex colours stored in the new vertices
    #   to the child vertices of the new faces' loops.
    for face in lines_geometry.faces:
        if face.is_valid is True:
            for loop in face.loops:
                for shiftable_vertex in lines_geometry.verts:
                    if shiftable_vertex.vert is loop.vert:
                        loop[bm.loops.layers.color.get('Col')] = shiftable_vertex.colour.vector
                        loop[bm.loops.layers.color.get('Col_ALPHA')] = ([shiftable_vertex.colour.factor] * 3)
                        face_loop_uv = [face_uv.uv for face_uv in shiftable_vertex.uv if face_uv.face is face]
                        if len(face_loop_uv) > 0:
                            loop[bm.loops.layers.uv.get('Lightmap + Lines Texture')].uv = face_loop_uv[0]


    #   Copy values stored in UV Maps to the filler faces. This is the
    #   part that is not shifted by the shader, so having overlapping
    #   vertices is pointless.
    for filler_face in filler_faces:
        for loop in filler_face.loops:
            for reference_loop in loop.vert.link_loops:
                if reference_loop is not loop:
                    loop[bm.loops.layers.uv.get('Object Texture 1 + Lines Edge XY')].uv = reference_loop[bm.loops.layers.uv.get('Object Texture 1 + Lines Edge XY')].uv
                    loop[bm.loops.layers.uv.get('Object Texture 2 + Lines Edge Z + Lines Offset Limit')].uv = reference_loop[bm.loops.layers.uv.get('Object Texture 2 + Lines Edge Z + Lines Offset Limit')].uv

    for loop in filler_loop_outer:
        loop[bm.loops.layers.uv.get('Lightmap + Lines Texture')].uv = [(1 / 64), (4 / 64)]
    for loop in filler_loop_inset_left:
        loop[bm.loops.layers.uv.get('Lightmap + Lines Texture')].uv = [(48 / 64), (7 / 64)]
    for loop in filler_loop_inset_right:
        loop[bm.loops.layers.uv.get('Lightmap + Lines Texture')].uv = [(48 / 64), (1 / 64)]


    #   Push updated mesh data back into the object's mesh
    helpers.bmesh_to_mesh(bm, object)


    #   Assign vertices to vertex groups.
    object.vertex_groups['Lines'].add(helpers.list_shiftable_vertices_indicies(lines_geometry.verts), 1, 'ADD')

    #   TODO: Move into function that deals specifically with the
    #   object's geometry, not the lines geometry.
    # object.vertex_groups['Object'].add(helpers.list_vertices_indicies(object_geometry['verts']), 1, 'ADD')
    

    #   Lock vertex groups
    # helpers.vertex_groups_lock(object, ['Object', 'Lines', 'Outline'])
    helpers.vertex_groups_lock(object, ['Lines'])


    #   Finished metadata updates to the object
    helpers.bmesh_to_object(bm, object)

    return lines_geometry


def geometry_modify_object(
        config, context, object
):
    """Create UV maps and vertex colours for the object itself."""
    if (config['debug'] == True):
        print('geometry_modify_object')

    #   Load the object's mesh datablock into a bmesh
    bm = helpers.object_to_bmesh(object)

    #   Geometry (faces, edges, and verts) from the current
    #   object's mesh.
    object_geometry = helpers.list_geometry(bm)

    for vert_counter, vert in enumerate(object_geometry['verts']):
        #   Conver the vertex to a Shiftable_Vertex
        object_geometry['verts'][vert_counter] = classes.Shiftable_Vertex(
            vert,
            classes.Shifting_Vector(
                1.0,
                helpers.convert_vector_to_colour(vert.normal)
            )
        )

    #   Assign vertex colours
    for face in object_geometry['faces']:
        for loop in face.loops:
            for shiftable_vertex in object_geometry['verts']:
                if shiftable_vertex.vert is loop.vert:
                    loop[bm.loops.layers.color.get('Col')] = shiftable_vertex.colour.vector
                    loop[bm.loops.layers.color.get('Col_ALPHA')] = ([shiftable_vertex.colour.factor] * 3)

    #   Push updated mesh data back into the object's mesh
    helpers.bmesh_to_mesh(bm, object)

    #   TODO: Move into function that deals specifically with the
    #   object's geometry, not the lines geometry.
    object.vertex_groups['Object'].add(helpers.list_shiftable_vertices_indicies(object_geometry['verts']), 1, 'ADD')

    #   Lock vertex groups
    helpers.vertex_groups_lock(object, ['Object'])

    #   Finished metadata updates to the object
    helpers.bmesh_to_object(bm, object)


#
#   __main__ Check
#

if __name__ == '__main__':
    print('generate_wireframe.py is not intended to be run as __main__')