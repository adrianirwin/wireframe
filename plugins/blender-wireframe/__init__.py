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

    try:
        importlib.reload(create)
    except:
        from . import create

    try:
        importlib.reload(export)
    except:
        from . import export

    try:
        importlib.reload(helpers)
    except:
        from . import helpers

    try:
        importlib.reload(classes)
    except:
        from . import classes

    print('Reloaded files')
else:
    from . import create
    from . import export
    from . import helpers
    from . import classes
    print('Imported files')

import bpy


#
#   Blender UI Panel Layouts
#

class WireframePanelCommands(bpy.types.Panel):
    """Panel of Tools and Options for Generating Wireframe Geometry"""
    bl_label = 'Generate Wireframe'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Wireframe'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout

        #   Creation Commands
        column_cr = layout.column(align=False)
        column_cr.label('Create:')
        column_cr.operator('wireframe.generate', icon='OBJECT_DATA')
        column_cr.separator()

         #   Filenames and Paths
        column_fp = layout.column(align=False)
        column_fp.label("Path & Infixes:")
        column_fp.prop(
            context.user_preferences.addons[__name__].preferences,
            "export_path_root", icon="FILE_FOLDER"
        )
        column_fp.prop(
            context.user_preferences.addons[__name__].preferences,
            "export_infix_object", icon="FILE_TEXT"
        )
        column_fp.prop(
            context.user_preferences.addons[__name__].preferences,
            "export_infix_shell", icon="FILE_TEXT"
        )
        column_fp.separator()


class WireframePanelDebugging(bpy.types.Panel):
    """Panel of Debugging Options for Generating Wireframe Geometry"""
    bl_label = 'Debugging Options'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Wireframe'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout

        #   Debugging Options
        column_db = layout.column(align=False)
        column_db.label("Dimensions:")
        column_db.prop(
            context.user_preferences.addons[__name__].preferences,
            "outline_inset"
        )


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
            'verbose': True,
            'export_path_root': context.user_preferences.addons[__name__].preferences.export_path_root,
            'export_infix_object': context.user_preferences.addons[__name__].preferences.export_infix_object,
            'export_infix_shell': context.user_preferences.addons[__name__].preferences.export_infix_shell,
            'outline_inset': context.user_preferences.addons[__name__].preferences.outline_inset,
        }

        object = context.active_object
        if object.type == 'MESH':

            #   Set up metadata
            create.metadata(config, object, reset=True)

            #   Create (modify, really) geometry for the surface
            create.surface(config, context, object)

            #   Create geometry for the inner portion of the wireframe lines
            create.inset_lines(config, context, object)

            #   Create geometry for the outer portion of the wireframe lines
            create.outline(config, context, object)

            #   Export the selected object
            export.object(config, context, object)

        return {'FINISHED'}


#
#   Set/Delete Default Configuration Values
#

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    #   Filenames and Paths
    export_path_root = bpy.props.StringProperty(name="FBX Export Folder", subtype="DIR_PATH")
    export_infix_object = bpy.props.StringProperty(name="Object Infix", default="Object")
    export_infix_shell = bpy.props.StringProperty(name="Shell Infix", default="Shell")

    #   Dimensions
    outline_inset = bpy.props.FloatProperty(name='Wireframe Inset Geometry Distance', default=0.001, min=0.0001, max=0.5)


#
#   Register Classes with Blender
#

def register():
    bpy.utils.register_class(AddonPreferences)
    bpy.utils.register_class(WireframePanelCommands)
    bpy.utils.register_class(WireframePanelDebugging)
    bpy.utils.register_class(WireframeGenerate)


def unregister():
    bpy.utils.unregister_class(AddonPreferences)
    bpy.utils.unregister_class(WireframePanelCommands)
    bpy.utils.unregister_class(WireframePanelDebugging)
    bpy.utils.unregister_class(WireframeGenerate)

if __name__ == '__main__':
    register()