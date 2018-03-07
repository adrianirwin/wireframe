#
#   Blender Add-on Metadata
#

bl_info = {
    "name": "Wireframe Generation Tools",
    "category": "Mesh",
}

#
#   Imports
#

if "bpy" in locals():
    import imp
    imp.reload(generate_wireframe)
    print("Reloaded files")
else:
    from . import generate_wireframe
    print("Imported files")

import bpy


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
    bl_label = "Generate Wireframe"
    bl_description = "Create wireframe metadata and geometry for a single mesh"
 
    def execute(self, context):

        #
        #   Configuration
        #

        config = {
            "debug": True,
        }

        object = context.active_object
        if object.type == 'MESH':
            generate_wireframe.reset_metadata(config, object)
            generate_wireframe.create_metadata(config, object)

        return {'FINISHED'}


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

if __name__ == "__main__":
    register()