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
            'outline_inset': context.user_preferences.addons[__name__].preferences.outline_inset,
        }

        object = context.active_object
        if object.type == 'MESH':

            #   Reset metadata
            generate_wireframe.metadata_reset(config, object)
            generate_wireframe.metadata_create(config, object)

            #   Create geometry for the inner portion of the wireframe
            generate_wireframe.geometry_modify_object(
                config, context, object)

            #   Create geometry for the inner portion of the wireframe
            lines_geometry = generate_wireframe.geometry_create_inset_lines(
                config, context, object)

        return {'FINISHED'}


#
#   Set/Delete Default Configuration Values
#

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    outline_inset = bpy.props.FloatProperty(name='Wireframe Inset Geometry Distance', default=0.001, min=0.0001, max=0.5)


#
#   Register Classes with Blender
#

def register():
    bpy.utils.register_class(AddonPreferences)
    bpy.utils.register_class(WireframeTilePanel)
    bpy.utils.register_class(WireframeGenerate)


def unregister():
    bpy.utils.unregister_class(AddonPreferences)
    bpy.utils.unregister_class(WireframeTilePanel)
    bpy.utils.unregister_class(WireframeGenerate)

if __name__ == '__main__':
    register()