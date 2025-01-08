import bpy
import bmesh

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


class GenerateVATMap(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.generate_vat_map"
    bl_label = "generate vat map"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        m = context.active_object.data
        bm = bmesh.new()
        bm.from_mesh(m)

        uv_layer = bm.loops.layers.uv.new("VATMap")
        count = len(bm.verts)
        i = 0

        for v in bm.verts:
            for l in v.link_loops:
                uv = l[uv_layer].uv
                uv[1] = 0.0
                uv[0] = i/count + (0.5/count)
            i += 1

        bm.to_mesh(m)
        bm.free()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(GenerateVATMap)
    bpy.utils.register_class(GenerateVAT)


def unregister():
    bpy.utils.unregister_class(GenerateVATMap)
    bpy.utils.unregister_class(GenerateVAT)
