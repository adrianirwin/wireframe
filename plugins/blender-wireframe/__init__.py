#   TODO: Docstring for the module, functions, and classes

#
#   Blender Add-on Metadata
#

bl_info = {
    'name': 'Wireframe Generation Tools',
    'category': 'Mesh',
}

#
#   Imports
#

if 'bpy' in locals():
    import importlib
    importlib.reload(generate_wireframe)
    importlib.reload(helpers)
    importlib.reload(classes)
    print('Reloaded files')
else:
    from . import generate_wireframe
    from . import helpers
    from . import classes
    print('Imported files')

import bpy


#
#   Blender UI Panel Layout
#

class WireframeTilePanel(bpy.types.Panel):
    """Panel of Tools for Generating the Wireframe Geometry"""
    bl_label = 'Generate Wireframe'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Wireframe'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        #   Debugging Commands
        column_db = layout.column(align=False)
        column_db.label('Create:')
        column_db.operator('wireframe.generate', icon='OBJECT_DATA')
        column_db.separator()


#
#   Blender UI Functions
#

class WireframeGenerate(bpy.types.Operator):
    bl_idname = 'wireframe.generate'
    bl_label = 'Generate Wireframe'
    bl_description = 'Create wireframe metadata and geometry for a single mesh'
 
    def execute(self, context):

        #
        #   Configuration
        #

        config = {
            'debug': True,
            'outline_inset': context.scene.outline_inset,
        }

        object = context.active_object
        if object.type == 'MESH':

            #   Reset metadata
            generate_wireframe.metadata_reset(config, object)
            generate_wireframe.metadata_create(config, object)

            #   Load the object's mesh datablock into a bmesh
            bm = helpers.object_to_bmesh(object)

            #   Create geometry for the inner portion of the wireframe
            lines_geometry = generate_wireframe.geometry_create_inset(
                config, context, bm, object)

        return {'FINISHED'}


#
#   Set/Delete Default Configuration Values
#

def SetDefaultWireframeGenerationParameters():
    bpy.types.Scene.outline_inset = bpy.props.FloatProperty(name='Wireframe Inset Geometry Distance', default=0.1, min=0.001, max=0.5)


def DeleteDefaultWireframeGenerationParameters():
    del bpy.types.Scene.outline_inset


#
#   Register Classes with Blender
#

def register():
    SetDefaultWireframeGenerationParameters()
    bpy.utils.register_class(WireframeTilePanel)
    bpy.utils.register_class(WireframeGenerate)


def unregister():
    DeleteDefaultWireframeGenerationParameters()
    bpy.utils.unregister_class(WireframeTilePanel)
    bpy.utils.unregister_class(WireframeGenerate)

if __name__ == '__main__':
    register()