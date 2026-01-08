import bpy
import typing

# ------------------------------------------------------------------------
#   Logic: Modifier Validation
# ------------------------------------------------------------------------

class ModifierValidator:
    """Validates modifiers for common issues."""
    
    @staticmethod
    def validate_modifiers(obj: bpy.types.Object) -> typing.List[typing.Tuple[str, str, str]]:
        """Check modifiers. Returns list of (issue_type, message, severity)."""
        issues = []
        
        for mod in obj.modifiers:
            # Check Array modifier
            if mod.type == 'ARRAY':
                if mod.use_object_offset and not mod.offset_object:
                    issues.append(("BROKEN_MODIFIER", 
                                  f"Array modifier '{mod.name}' has Object Offset enabled but no object set", 
                                  "WARNING"))
            
            # Check Boolean modifier
            elif mod.type == 'BOOLEAN':
                if not mod.object:
                    issues.append(("BROKEN_MODIFIER", 
                                  f"Boolean modifier '{mod.name}' has no target object", 
                                  "ERROR"))
                elif mod.object.name not in bpy.data.objects:
                    issues.append(("BROKEN_MODIFIER", 
                                  f"Boolean modifier '{mod.name}' target object is missing", 
                                  "ERROR"))
            
            # Check Shrinkwrap modifier
            elif mod.type == 'SHRINKWRAP':
                if not mod.target:
                    issues.append(("BROKEN_MODIFIER", 
                                  f"Shrinkwrap modifier '{mod.name}' has no target", 
                                  "ERROR"))
            
            # Check Armature modifier
            elif mod.type == 'ARMATURE':
                if not mod.object:
                    issues.append(("BROKEN_MODIFIER", 
                                  f"Armature modifier '{mod.name}' has no armature object", 
                                  "ERROR"))
            
            # Check Surface Deform modifier (critical - can crash)
            elif mod.type == 'SURFACE_DEFORM':
                if not mod.is_bound:
                    issues.append(("UNBOUND_MODIFIER", 
                                  f"Surface Deform modifier '{mod.name}' is not bound - bind it or remove it to prevent crashes", 
                                  "ERROR"))
                elif mod.target and mod.target.mode != 'OBJECT':
                    issues.append(("UNSTABLE_MODIFIER", 
                                  f"Surface Deform target '{mod.target.name}' is in Edit Mode - this is unstable", 
                                  "ERROR"))
            
            # Check Data Transfer modifier
            elif mod.type == 'DATA_TRANSFER':
                if not mod.object:
                    issues.append(("BROKEN_MODIFIER", 
                                  f"Data Transfer modifier '{mod.name}' has no source object", 
                                  "ERROR"))
        
        return issues
    
    @staticmethod
    def fix_broken_modifiers(obj: bpy.types.Object) -> int:
        """Removes or fixes broken modifiers. Returns count of fixed/removed modifiers."""
        fixed_count = 0
        modifiers_to_remove = []
        
        for mod in obj.modifiers:
            should_remove = False
            
            # Array modifier - disable object offset if no object
            if mod.type == 'ARRAY':
                if mod.use_object_offset and not mod.offset_object:
                    mod.use_object_offset = False
                    fixed_count += 1
            
            # Boolean modifier - remove if no target
            elif mod.type == 'BOOLEAN':
                if not mod.object or mod.object.name not in bpy.data.objects:
                    should_remove = True
            
            # Shrinkwrap modifier - remove if no target
            elif mod.type == 'SHRINKWRAP':
                if not mod.target:
                    should_remove = True
            
            # Armature modifier - remove if no armature
            elif mod.type == 'ARMATURE':
                if not mod.object:
                    should_remove = True
            
            # Surface Deform - remove if unbound (safer than leaving it)
            elif mod.type == 'SURFACE_DEFORM':
                if not mod.is_bound:
                    should_remove = True
            
            # Data Transfer - remove if no source
            elif mod.type == 'DATA_TRANSFER':
                if not mod.object:
                    should_remove = True
            
            if should_remove:
                modifiers_to_remove.append(mod)
        
        # Remove problematic modifiers
        for mod in modifiers_to_remove:
            try:
                if mod and mod.name in obj.modifiers:
                    obj.modifiers.remove(mod)
                    fixed_count += 1
            except (RuntimeError, ReferenceError, ValueError) as e:
                print(f"Warning: Failed to remove modifier {mod.name if mod else 'Unknown'}: {e}")
                continue
        
        return fixed_count
