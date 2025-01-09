import bpy
import bmesh

from .helpers import Pitch

class GenerateVAT(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.generate_vat"
    bl_label = "generate vat"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        m = context.active_object
        deps = context.evaluated_depsgraph_get()

        bm = bmesh.new()
        bm.from_object(m, deps)

        v_count = len(bm.verts)
        f_count = context.scene.frame_end
        bm.free()

        offsets = list()

        for f in range(f_count):
            context.scene.frame_set(f + 1)
            offset_pixels = [1] * v_count * 4
            deps = context.evaluated_depsgraph_get()
            ibm = bmesh.new()
            ibm.from_object(m, deps)
            offset_layer = ibm.verts.layers.float['offset']
            i = 0
            for v in ibm.verts:
                offset = v[offset_layer]
                p = i * 4
                offset_pixels[p:p+3] = (offset, offset, offset)
                i += 1
            offsets += offset_pixels
            ibm.free()

        im = bpy.data.images.new(f"{m.name}_vat", v_count, f_count, float_buffer=True, is_data=True)
        im.pixels = offsets
        return {'FINISHED'}


class GenerateUVMap(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.generate_animation_uv_map"
    bl_label = "generate animation UV map"

    target_mesh: bpy.props.StringProperty(name="Target Mesh")
    uv_map_name: bpy.props.StringProperty(name="UV Map Name", default="AniMap")
    max_texture_dimension: bpy.props.IntProperty(name="Max texture dimension", default=4096)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        m = bpy.data.meshes.get(self.target_mesh)
        if not m:
            return {'CANCELLED'}

        bm = bmesh.new()
        bm.from_mesh(m)

        uv_layer = bm.loops.layers.uv.get(self.uv_map_name)
        if not uv_layer:
            uv_layer = bm.loops.layers.uv.new(self.uv_map_name)

        count = len(bm.verts)
        pitch = Pitch(self.max_texture_dimension, count)
        i = 0

        for v in bm.verts:
            for l in v.link_loops:
                l[uv_layer].uv = pitch.pos_from_index(i)
            i += 1

        bm.to_mesh(m)
        bm.free()
        return {'FINISHED'}

def ops_register():
    bpy.utils.register_class(GenerateUVMap)
    bpy.utils.register_class(GenerateVAT)


def ops_unregister():
    bpy.utils.unregister_class(GenerateUVMap)
    bpy.utils.unregister_class(GenerateVAT)
