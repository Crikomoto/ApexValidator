bl_info = {
    "name": "Apex Validator",
    "author": "Apex Dev",
    "version": (1, 2, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Apex",
    "description": "Scene and Collection validator for production",
    "category": "Development",
}

import bpy
from . import ops, ui

# List of classes to register from modules
classes = (
    ui.APEX_ExclusionPatterns,
    ui.APEX_ValidationItem,
    ui.APEX_UL_ValidationList,
    ops.APEX_OT_Validate,
    ops.APEX_OT_FixShaders,
    ops.APEX_OT_AutoFix,
    ops.APEX_OT_SelectObject,
    ops.APEX_OT_ClearResults,
    ui.APEX_PT_MainPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register quick scope selector
    bpy.types.Scene.apex_quick_scope = bpy.props.EnumProperty(
        name="Scope",
        items=[
            ('SCENE', "Scene", "Validate entire scene"),
            ('COLLECTION', "Collection", "Validate active collection only")
        ],
        default='SCENE'
    )
    
    # Register exclusion patterns
    bpy.types.Scene.apex_exclusions = bpy.props.PointerProperty(type=ui.APEX_ExclusionPatterns)
    
    # Register CollectionProperty to store validation results
    bpy.types.Scene.apex_validation_results = bpy.props.CollectionProperty(type=ui.APEX_ValidationItem)
    bpy.types.Scene.apex_validation_index = bpy.props.IntProperty(default=0)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.apex_validation_results
    del bpy.types.Scene.apex_validation_index
    del bpy.types.Scene.apex_exclusions
    del bpy.types.Scene.apex_quick_scope

if __name__ == "__main__":
    register()