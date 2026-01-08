import bpy
import typing

# ------------------------------------------------------------------------
#   Logic: Rigging Validation
# ------------------------------------------------------------------------

class RiggingValidator:
    """Validates rigging setup for common issues."""
    
    @staticmethod
    def validate_vertex_groups(obj: bpy.types.Object) -> typing.List[typing.Tuple[str, str, str]]:
        """Check vertex group issues. Returns list of (issue_type, message, severity)."""
        issues = []
        
        if not obj or obj.type != 'MESH' or not obj.vertex_groups:
            return issues
        
        if not hasattr(obj, 'data') or not obj.data:
            return issues
        
        mesh = obj.data
        
        # Check each vertex group
        for vgroup in obj.vertex_groups:
            # Count vertices in this group
            vertex_count = 0
            total_weight = 0.0
            
            for vert in mesh.vertices:
                for g in vert.groups:
                    if g.group == vgroup.index:
                        vertex_count += 1
                        total_weight += g.weight
                        break
            
            # Empty vertex group (no vertices assigned)
            if vertex_count == 0:
                issues.append(("RIGGING", 
                              f"Vertex group '{vgroup.name}' is empty (no vertices assigned)", 
                              "WARNING"))
            
            # Zero-weight vertex group (all weights are 0)
            elif total_weight == 0.0:
                issues.append(("RIGGING", 
                              f"Vertex group '{vgroup.name}' has zero total weight", 
                              "WARNING"))
        
        # Check for orphaned vertex groups (groups that don't match any bone)
        armature_mod = next((mod for mod in obj.modifiers if mod.type == 'ARMATURE' and mod.object), None)
        
        if armature_mod and armature_mod.object.type == 'ARMATURE':
            armature = armature_mod.object
            bone_names = set(bone.name for bone in armature.data.bones)
            
            for vgroup in obj.vertex_groups:
                if vgroup.name not in bone_names:
                    issues.append(("RIGGING", 
                                  f"Orphaned vertex group '{vgroup.name}' (no matching bone in armature)", 
                                  "WARNING"))
        
        return issues
    
    @staticmethod
    def fix_vertex_groups(obj: bpy.types.Object) -> typing.Dict[str, int]:
        """Clean up vertex groups. Returns dict with counts."""
        if obj.type != 'MESH' or not obj.vertex_groups:
            return {'empty_removed': 0, 'orphaned_removed': 0, 'normalized': 0}
        
        mesh = obj.data
        empty_groups = []
        orphaned_groups = []
        
        # Find armature if present
        armature_mod = next((mod for mod in obj.modifiers if mod.type == 'ARMATURE' and mod.object), None)
        bone_names = set()
        
        if armature_mod and armature_mod.object.type == 'ARMATURE':
            bone_names = set(bone.name for bone in armature_mod.object.data.bones)
        
        # Check each vertex group
        for vgroup in obj.vertex_groups:
            # Count vertices in this group
            vertex_count = 0
            total_weight = 0.0
            
            for vert in mesh.vertices:
                for g in vert.groups:
                    if g.group == vgroup.index:
                        vertex_count += 1
                        total_weight += g.weight
                        break
            
            # Mark empty groups
            if vertex_count == 0 or total_weight == 0.0:
                empty_groups.append(vgroup)
            
            # Mark orphaned groups (if armature exists)
            elif bone_names and vgroup.name not in bone_names:
                orphaned_groups.append(vgroup)
        
        # Remove empty groups
        for vgroup in empty_groups:
            obj.vertex_groups.remove(vgroup)
        
        # Remove orphaned groups  
        for vgroup in orphaned_groups:
            obj.vertex_groups.remove(vgroup)
        
        # Normalize weights (ensure all weights sum to 1.0)
        normalized_count = 0
        if obj.vertex_groups:
            try:
                view_layer = bpy.context.view_layer
                if obj.name in view_layer.objects:
                    # Ensure object mode
                    if view_layer.objects.active and view_layer.objects.active.mode != 'OBJECT':
                        bpy.ops.object.mode_set(mode='OBJECT')
                    
                    # Normalize all vertex weights
                    with bpy.context.temp_override(
                        view_layer=view_layer,
                        selected_objects=[obj],
                        active_object=obj,
                        object=obj
                    ):
                        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                        bpy.ops.object.vertex_group_normalize_all()
                        bpy.ops.object.mode_set(mode='OBJECT')
                        normalized_count = 1
            except Exception as e:
                print(f"Warning: Failed to normalize weights for {obj.name}: {e}")
        
        return {
            'empty_removed': len(empty_groups),
            'orphaned_removed': len(orphaned_groups),
            'normalized': normalized_count
        }
