import bpy
import bmesh

from ..helpers import Pitch, Prop

class EnsureVertexPanelData(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.add_vertex_texture_settings"
    bl_label = "Add vertex texture settings"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        dat = context.active_object.data
        if not dat.get("vts_count"):
            dat["vts_count"] = 0
        if not dat.get("vts_start_frame"):
            dat["vts_start_frame"] = 0
        if not dat.get("vts_end_frame"):
            dat["vts_end_frame"] = context.scene.frame_end
        if not dat.get("vts_max_tex_dim"):
            dat["vts_max_tex_dim"] = 4096
        if not dat.get("vts_uv_map"):
            dat["vts_uv_map"] = ""

        n = dat["vts_count"]
        dat[f"vts_tex_name_{n}"] = "position"
        dat[f"vts_red_name_{n}"] = "position.x"
        dat[f"vts_red_min_{n}"] = float(-1.0)
        dat[f"vts_red_max_{n}"] = float(1.0)
        dat[f"vts_green_name_{n}"] = "position.y"
        dat[f"vts_green_min_{n}"] = float(-1.0)
        dat[f"vts_green_max_{n}"] = float(1.0)
        dat[f"vts_blue_name_{n}"] = "position.z"
        dat[f"vts_blue_min_{n}"] = float(-1.0)
        dat[f"vts_blue_max_{n}"] = float(1.0)

        dat["vts_count"] += 1
        return {'FINISHED'}


class GenerateAnimationTexture(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.generate_animation_texture"
    bl_label = "generate animation texture"

    target_object: bpy.props.StringProperty(name="Target Object")

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        o = bpy.data.objects.get(self.target_object)
        dat = o.data
        deps = context.evaluated_depsgraph_get()
        f_count =  dat["vts_end_frame"] - dat["vts_start_frame"]

        if not o or f_count < 1:
            print(f_count)
            return {'CANCELLED'}

        bm = bmesh.new()
        bm.from_object(o, deps)

        v_count = len(bm.verts)
        pitch = Pitch(dat["vts_max_tex_dim"], v_count)
        bm.free()

        for vts in range(dat["vts_count"]):
            print(vts)
            offsets = list()
            red_prop = Prop(dat[f"vts_red_name_{vts}"], dat[f"vts_red_min_{vts}"], dat[f"vts_red_max_{vts}"])
            green_prop = Prop(dat[f"vts_green_name_{vts}"], dat[f"vts_green_min_{vts}"], dat[f"vts_green_max_{vts}"])
            blue_prop = Prop(dat[f"vts_blue_name_{vts}"], dat[f"vts_blue_min_{vts}"], dat[f"vts_blue_max_{vts}"])

            for f in range(dat["vts_start_frame"], dat["vts_end_frame"]):
                context.scene.frame_set(f)
                offset_pixels = [1] * v_count * 4
                deps = context.evaluated_depsgraph_get()
                ibm = bmesh.new()
                ibm.from_object(o, deps)

                red_prop.set_layer(ibm.verts)
                green_prop.set_layer(ibm.verts)
                blue_prop.set_layer(ibm.verts)

                i = 0
                for v in ibm.verts:
                    red = red_prop.get_data(v)
                    green = green_prop.get_data(v)
                    blue = blue_prop.get_data(v)
                    p = i * 4
                    offset_pixels[p:p+3] = (red, green, blue)
                    i += 1
                offsets += offset_pixels
                ibm.free()

            tex_prop = dat[f"vts_tex_name_{vts}"]
            im = bpy.data.images.new(f"{o.name}_{tex_prop}", v_count, f_count, float_buffer=True, is_data=True)
            im.pixels = offsets
        return {'FINISHED'}


class GenerateUVMap(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.generate_animation_uv_map"
    bl_label = "generate animation UV map"

    target_mesh: bpy.props.StringProperty(name="Target Mesh")
    uv_map_name: bpy.props.StringProperty(name="UV Map Name", default="AniMap")

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
        pitch = Pitch(m["vts_max_tex_dim"], count)
        i = 0

        for v in bm.verts:
            for l in v.link_loops:
                l[uv_layer].uv = pitch.pos_from_index(i)
            i += 1

        bm.to_mesh(m)
        bm.free()
        m["vts_uv_map"] = self.uv_map_name
        return {'FINISHED'}

def ops_register():
    bpy.utils.register_class(GenerateUVMap)
    bpy.utils.register_class(GenerateAnimationTexture)
    bpy.utils.register_class(EnsureVertexPanelData)


def ops_unregister():
    bpy.utils.unregister_class(GenerateUVMap)
    bpy.utils.unregister_class(GenerateAnimationTexture)
    bpy.utils.unregister_class(EnsureVertexPanelData)
