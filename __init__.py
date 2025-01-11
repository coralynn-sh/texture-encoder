from .ops import ops_register, ops_unregister
from .UI import ui_register, ui_unregister

def register():
    ops_register()
    ui_register()

def unregister():
    ops_unregister()
    ui_unregister()
