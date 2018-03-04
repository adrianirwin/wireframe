#
#   Addon Metadata
#

bl_info = {
    "name": "Wireframe Generation Tools",
    "category": "Mesh",
}


#
#   Imports
#

import addon_utils
import bpy
import bmesh
import math
import mathutils
from collections import namedtuple
import itertools
import functools
import os


#
#   Blender UI Panel Layout
#

class WireframeTilePanel(bpy.types.Panel):
    """Panel of Tools for Generating the Wireframe Geometry"""
    bl_label = "Generate Wireframe"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Wireframe"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        #   Debugging Commands
        column_db = layout.column(align=False)
        column_db.label("Create:")
        column_db.operator("wireframe.generate", icon="OBJECT_DATA")
        column_db.separator()


#
#   Blender UI Functions
#

class WireframeGenerate(bpy.types.Operator):
    bl_idname = "wireframe.generate"
    bl_label = "Generate Wireframe Geometry"
    bl_description = "Create metadata and geometry for a single mesh"
 
    def execute(self, context):

        #
        #   Configuration
        #

        config = {
            "debug": False,
        }

        # generate_and_export_tile_group(config, context)

        return{'FINISHED'}


#
#   Extract Data from Blender Mesh
#


#
#   Insert Addon Elements into Blender Mesh
#


#
#   Register Classes with Blender
#

def register():
    bpy.utils.register_class(WireframeTilePanel)
    bpy.utils.register_class(WireframeGenerate)


def unregister():
    bpy.utils.unregister_class(WireframeTilePanel)
    bpy.utils.unregister_class(WireframeGenerate)