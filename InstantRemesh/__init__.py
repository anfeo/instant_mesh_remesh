import importlib
bl_info = {
    "name": "Instant Meshes Remesh",
    "author": "knekke, cgvirus, anfeo",
    "category": "Object",
    "blender": (4, 1, 0),
}

if "bpy" in locals():
    importlib.reload(operator)
    importlib.reload(function)

else:
    from . import (operator,function,)
import shutil
import tempfile
import subprocess
import os
import bpy


class InstantMeshesRemeshPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__

    filepath: bpy.props.StringProperty(
        name="Instant Meshes Executable",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="""Please specify the path to 'Instant Meshes.exe'
            Get it from https://github.com/wjakob/instant-meshes""")
        layout.prop(self, "filepath")



##############################################


def menu_func(self, context):

    self.layout.operator(operator.InstantMeshesRemesh.bl_idname)


classes = (
    operator.InstantMeshesRemesh,

    InstantMeshesRemeshPrefs,
)


def register():
    # add operator
    from bpy.utils import register_class
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.VIEW3D_MT_object.append(menu_func)
    try:
        os.remove(os.path.join(tempfile.gettempdir(), 'original.obj'))
        os.remove(os.path.join(tempfile.gettempdir(), 'out.obj'))
    except:
        pass


def unregister():
    from bpy.utils import unregister_class
    bpy.types.VIEW3D_MT_object.remove(menu_func)

    # remove operator and preferences
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()