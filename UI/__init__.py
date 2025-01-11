import bpy

class VertexTexturePanel(bpy.types.Panel):
    """Vertex Texture Panel"""
    bl_label = "Vertex Texture Panel"
    bl_idname = "OBJECT_PT_vertex_texture_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        layout = self.layout

        dat = context.object.data
        vts_count = dat.get("vts_count")
        if not vts_count:
            row = layout.row()
            row.operator("object.add_vertex_texture_settings")
        else:
            op = layout.operator("object.generate_animation_texture")
            op.target_object = context.active_object.name
            row = layout.row()
            row.prop(dat, '["vts_start_frame"]', text="Start frame")
            row.prop(dat, '["vts_end_frame"]', text="End frame")
            row = layout.row()
            row.prop(dat, '["vts_uv_map"]', text="UV Map")
            op = row.operator("object.generate_animation_uv_map")
            op.target_mesh = dat.name
            for i in range(vts_count):
                layout.separator()
                layout.prop(dat, f"[\"vts_tex_name_{i}\"]", text="Texture Name")
                row = layout.row()
                row.prop(dat, f"[\"vts_red_name_{i}\"]", text="red")
                row.prop(dat, f"[\"vts_red_min_{i}\"]", text="min")
                row.prop(dat, f"[\"vts_red_max_{i}\"]", text="max")
                row = layout.row()
                row.prop(dat, f"[\"vts_green_name_{i}\"]", text="green")
                row.prop(dat, f"[\"vts_green_min_{i}\"]", text="min")
                row.prop(dat, f"[\"vts_green_max_{i}\"]", text="max")
                row = layout.row()
                row.prop(dat, f"[\"vts_blue_name_{i}\"]", text="blue")
                row.prop(dat, f"[\"vts_blue_min_{i}\"]", text="min")
                row.prop(dat, f"[\"vts_blue_max_{i}\"]", text="max")

            row = layout.row()
            row.operator("object.add_vertex_texture_settings")


def ui_register():
    bpy.utils.register_class(VertexTexturePanel)

def ui_unregister():
    bpy.utils.unregister_class(VertexTexturePanel)
