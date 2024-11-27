import importlib
if "bpy" in locals():    
    importlib.reload(function)
else:

    from . import (function)    
import bpy


from bpy.types import (
        Operator,
        Panel,
        AddonPreferences,
        )
from bpy.props import (
        StringProperty,
        BoolProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        CollectionProperty,
        BoolVectorProperty,
        PointerProperty,
        EnumProperty,
        )
import os
import shutil
import tempfile
import subprocess

class InstantMeshesRemesh(Operator):
    """Remesh by using the Instant Meshes program"""
    bl_idname = "object.instant_meshes_remesh"
    bl_label = "Instant Meshes Remesh"
    bl_options = {'REGISTER', 'UNDO'}

    exported = False
    deterministic: BoolProperty(name="Deterministic (slower)", description="Prefer (slower) deterministic algorithms", default=False)
    dominant: BoolProperty(name="Dominant", description="Generate a tri/quad dominant mesh instead of a pure tri/quad mesh", default=False)
    intrinsic: BoolProperty(name="Intrinsic", description="Intrinsic mode (extrinsic is the default)", default=False)
    boundaries: BoolProperty(name="Boundaries", description="Align to boundaries (only applies when the mesh is not closed)", default=False)
    crease: IntProperty(name="Crease Degree", description="Dihedral angle threshold for creases", default=0, min=0, max=100)
    verts: IntProperty(name="Vertex Count", description="Desired vertex count of the output mesh", default=2000, min=10, max=50000)
    smooth: IntProperty(name="Smooth iterations", description="Number of smoothing & ray tracing reprojection steps (default: 2)", default=2, min=0, max=10)
    remeshIt: BoolProperty(name="Start Remeshing", description="Activating it will start Remesh", default=False)
    openUI: BoolProperty(name="Open in InstantMeshes", description="Opens the selected object in Instant Meshes and imports the result when you are done.", default=False)

    loc = None
    rot = None
    scl = None
    meshname = None

    def execute(self, context):
        exe = context.preferences.addons[__package__].preferences.filepath
        orig = os.path.join(tempfile.gettempdir(), 'original.obj')
        output = os.path.join(tempfile.gettempdir(), 'out.obj')

        if self.remeshIt:

            if not self.exported:
                try:
                    os.remove(orig)
                except:
                    pass
                self.meshname = bpy.context.active_object.name
                mesh = bpy.context.active_object
                # self.loc = mesh.matrix_world.to_translation()
                # self.rot = mesh.matrix_world.to_euler('XYZ')
                # self.scl = mesh.matrix_world.to_scale()
                # bpy.ops.object.location_clear()
                # bpy.ops.object.rotation_clear()
                # bpy.ops.object.scale_clear()

                bpy.ops.wm.obj_export(filepath=orig,
                                         check_existing=False,
                                         forward_axis='NEGATIVE_Z', up_axis='Y',
                                         export_selected_objects=True,
                                         apply_modifiers=True,
                                         # use_mesh_modifiers_render=False,
                                         export_triangulated_mesh=True,
                                         export_smooth_groups=False,
                                         smooth_group_bitflags=False,
                                         export_normals=True,
                                         export_uv=True, )

                self.exported = True
                # mesh.location = self.loc
                # mesh.rotation_euler = self.rot
                # mesh.scale = self.scl

            mesh = bpy.data.objects[self.meshname]
            mesh.hide_viewport = False
            options = ['-c', str(self.crease),
                       '-v', str(self.verts),
                       '-S', str(self.smooth),
                       '-o', output]
            if self.deterministic:
                options.append('-d')
            if self.dominant:
                options.append('-D')
            if self.intrinsic:
                options.append('-i')
            if self.boundaries:
                options.append('-b')

            cmd = [exe] + options + [orig]

            print (cmd)

            if self.openUI:
                os.chdir(os.path.dirname(orig))
                shutil.copy2(orig, output)
                subprocess.run([exe, output])
                self.openUI = False
            else:
                subprocess.run(cmd)

            bpy.ops.wm.obj_import(filepath=output,
                                     use_split_objects=False,
                                     # use_smooth_groups =False,
                                     # use_image_search=False,
                                     forward_axis='NEGATIVE_Z', up_axis='Y')
            imported_mesh = bpy.context.selected_objects[0]
            # imported_mesh.location = self.loc
            # imported_mesh.rotation_euler = self.rot
            # imported_mesh.scale = self.scl
            print(mesh, mesh.name)
            imported_mesh.name = mesh.name + '_remesh'
            for i in mesh.data.materials:
                print('setting mat: ' + i.name)
                imported_mesh.data.materials.append(i)
            for edge in imported_mesh.data.edges:
                edge.use_edge_sharp = False
            for other_obj in bpy.data.objects:
                other_obj.select_set(state=False)
            imported_mesh.select_set(state=True)
            # imported_mesh.active_material.use_nodes = False
            # imported_mesh.data.use_auto_smooth = False

            bpy.ops.object.shade_flat()
            bpy.ops.mesh.customdata_custom_splitnormals_clear()

            mesh.select_set(state=True)
            bpy.context.view_layer.objects.active = mesh
            bpy.ops.object.data_transfer(use_reverse_transfer=False,
                                         use_freeze=False, data_type='UV', use_create=True, vert_mapping='NEAREST',
                                         edge_mapping='NEAREST', loop_mapping='NEAREST_POLYNOR', poly_mapping='NEAREST',
                                         use_auto_transform=False, use_object_transform=True, use_max_distance=False,
                                         max_distance=1.0, ray_radius=0.0, islands_precision=0.1, layers_select_src='ACTIVE',
                                         layers_select_dst='ACTIVE', mix_mode='REPLACE', mix_factor=1.0)
            mesh.select_set(state=False)
            #mesh.hide_viewport = True
            #mesh.hide_render = True
            mesh.hide_set(True)
            imported_mesh.select_set(state=False)
            os.remove(output)
            bpy.context.space_data.overlay.show_wireframes = True

            return {'FINISHED'}
        else:
            return {'FINISHED'}