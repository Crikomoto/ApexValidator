import bpy
import typing

# ------------------------------------------------------------------------
#   Logic: Data Validation
# ------------------------------------------------------------------------

class DataValidator:
    """Validates object data for production issues."""
    
    @staticmethod
    def validate_object_data(obj: bpy.types.Object) -> typing.List[typing.Tuple[str, str, str]]:
        """Check object data issues. Returns list of (issue_type, message, severity)."""
        issues = []
        
        # Check for mesh data with multiple users (potential instancing issue)
        if obj.type == 'MESH' and obj.data.users > 1:
            issues.append(("DATA", 
                          f"Mesh data '{obj.data.name}' has {obj.data.users} users (linked duplicates)", 
                          "WARNING"))
        
        # NOTE: Default mesh names (Mesh.001, etc.) are ignored - common in CAD data and not critical
        
        # Check for shape keys issues
        if obj.type == 'MESH' and obj.data.shape_keys:
            sk = obj.data.shape_keys
            # Check for broken shape key references
            for key_block in sk.key_blocks:
                if key_block.vertex_group and key_block.vertex_group not in obj.vertex_groups:
                    issues.append(("DATA", 
                                  f"Shape key '{key_block.name}' references missing vertex group '{key_block.vertex_group}'", 
                                  "ERROR"))
        
        return issues
    
    @staticmethod
    def fix_default_mesh_names(obj: bpy.types.Object) -> bool:
        """Renames mesh data from default names like 'Mesh.001' to match object name. Returns True if renamed."""
        if obj.type != 'MESH' or not obj.data:
            return False
        
        # Check if mesh has default name pattern
        if obj.data.name.startswith("Mesh.") or obj.data.name == "Mesh":
            # Create clean name from object name
            new_name = f"{obj.name}_mesh"
            obj.data.name = new_name
            return True
        
        return False
