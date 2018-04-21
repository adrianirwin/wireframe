#   TODO: Docstring for the module, functions, and classes

#
#   create.py
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
else:
    pass

import bpy
import os.path


#
#   FBX Exporters
#

def object(
        config, context, object
):
    """Export the selected object as a FBX file."""
    if (config['verbose'] == True):
        print(__name__ + '.object')

    #   Build file path
    dir_path = config['export_path_root']

    #   Check for a relative path ('//../../foo')
    #   TODO: This may be windows specific, need to test on mac and *nix
    if dir_path[:2] == '//':
        dir_path = os.path.dirname(bpy.data.filepath) + os.path.abspath(config['export_path_root'])[1:]

    object_export_path = os.path.join(dir_path, (config['export_infix_object'] + ".fbx"))

    #   Operate on only a single selection
    if len(context.selected_objects) == 1:

        #   Export the visible object mesh
        bpy.ops.export_scene.fbx(
            filepath=object_export_path, check_existing=True,
            axis_forward='-Z', axis_up='Y',
            filter_glob="*.fbx", version='BIN7400',
            use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=False,
            object_types={'MESH'}, use_mesh_modifiers=True, mesh_smooth_type='EDGE', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=False,
            primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False,
            bake_anim=False, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0,
            use_anim=True, use_anim_action_all=True, use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0,
            path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True
        )

    # if False:
    #     #   Make sure this is operating on a group
    #     if len(context.selected_objects) > 0:
    #         bpy.ops.object.select_grouped(extend=False, type='GROUP')
    #         if len(context.selected_objects) > 0:
    #             tiles = context.selected_objects

    #             #   Generate metadata and mesh geometry for each tile
    #             for tile in tiles:
    #                 if tile.type == 'MESH':
    #                     remove_generated_tile_geometry(context, tile)
    #                     generate_tile_geometry(config, context, tile)

    #             #   Duplicate and merge into the merged tiles mesh
    #             bpy.ops.object.duplicate()
    #             bpy.ops.object.join()
    #             merged_tiles = context.selected_objects[0]

    #             #   Optimize the shell
    #             remove_merged_interior_faces(config, context, merged_tiles)
    #             triangulate_merged_tile_surface(config, context, merged_tiles)

    #             #   Restore the original tiles
    #             merged_tiles.select = False
    #             for tile in tiles:
    #                 if tile.type == 'MESH':
    #                     bpy.context.scene.objects.active = tile
    #                     tile.select = True
    #                     remove_generated_tile_geometry(context, tile)
    #                     tile.select = False

    #             #   Select the tiles
    #             for tile in tiles:
    #                 if tile.type == 'MESH':
    #                     tile.select = True

    #             #   Duplicate and merge into the tiles shell mesh
    #             bpy.ops.object.duplicate()
    #             bpy.ops.object.join()
    #             tiles_shell = context.selected_objects[0]

    #             #   Optimize the shell
    #             remove_shell_interior_faces(config, context, tiles_shell)
    #             decimate_tile_surface(config, context, tiles_shell)

    #             #   Set the origin of the merged and tiles shell meshes to their bottom center
    #             saved_cursor_location = bpy.context.scene.cursor_location.copy()

    #             #   Select and center the tiles shell mesh
    #             bpy.context.scene.objects.active = tiles_shell
    #             tiles_shell.select = True
    #             bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    #             shell_origin = mathutils.Vector([tiles_shell.location.x, tiles_shell.location.y, (tiles_shell.location.z - (tiles_shell.dimensions.z / 2))])
    #             bpy.context.scene.cursor_location = shell_origin
    #             bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    #             tiles_shell.location = mathutils.Vector([0.0, 0.0, 0.0])

    #             #   Optimize the tiles shell mesh (remove interior faces and decimate the remaining faces)
    #             # bpy.ops.mesh.select_interior_faces()
    #             # bpy.ops.mesh.delete(type='FACE')

    #             #   Smooth the output mesh to prevent extra vertices from being created. Use the normal property of the UE4 material inputs to force flat shading
    #             #   NOTE/TODO: This probably won't work on mobile
    #             # bpy.ops.mesh.faces_shade_smooth()



    #             #   Remove the tiles shell mesh
    #             bpy.ops.object.delete()

    #             #   Select and center the merged tiles mesh
    #             bpy.context.scene.objects.active = merged_tiles
    #             merged_tiles.select = True
    #             bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    #             bpy.context.scene.cursor_location = shell_origin
    #             bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    #             merged_tiles.location = mathutils.Vector([0.0, 0.0, 0.0])

    #             #   Create UV coordinates for an optimized lightmap for the visible tile geometry
    #             uv_coordinates_for_tile_lightmap(config, context, merged_tiles, (1 / 512), 3)

    #             #   Create UV coordinates for textures
    #             uv_coordinates_for_texture_mapping(config, context, merged_tiles, (1 / 256), 3)

    #             #   Export the merged tiles mesh
    #             if config['export_to_file'] is True:
    #                 bpy.ops.export_scene.fbx(
    #                     filepath=merged_tiles_export_path, check_existing=True,
    #                     axis_forward='-Z', axis_up='Y',
    #                     filter_glob="*.fbx", version='BIN7400',
    #                     use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=False,
    #                     object_types={'MESH'}, use_mesh_modifiers=True, mesh_smooth_type='EDGE', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=False,
    #                     primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False,
    #                     bake_anim=False, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0,
    #                     use_anim=True, use_anim_action_all=True, use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0,
    #                     path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True
    #                 )

    #                 #   Remove the merged tiles mesh
    #                 bpy.ops.object.delete()

    #             #   Reset the 3d cursor
    #             bpy.context.scene.cursor_location = saved_cursor_location


#
#   __main__ Check
#

if __name__ == '__main__':
    print(__name__ + ' is not intended to be run as __main__')