import bpy
import typing

# ------------------------------------------------------------------------
#   Logic: Transform Validation
# ------------------------------------------------------------------------

class TransformValidator:
    """Validates object transforms for production issues."""
    
    @staticmethod
    def validate_transforms(obj: bpy.types.Object) -> typing.List[typing.Tuple[str, str, str]]:
        """Check transform issues. Returns list of (issue_type, message, severity)."""
        issues = []
        
        # Check for unapplied scale
        scale = obj.scale
        if abs(scale.x - 1.0) > 0.001 or abs(scale.y - 1.0) > 0.001 or abs(scale.z - 1.0) > 0.001:
            issues.append(("TRANSFORM", 
                          f"Unapplied scale: ({scale.x:.3f}, {scale.y:.3f}, {scale.z:.3f})", 
                          "WARNING"))
        
        # Check for non-uniform scale
        if abs(scale.x - scale.y) > 0.001 or abs(scale.x - scale.z) > 0.001:
            issues.append(("TRANSFORM", 
                          f"Non-uniform scale: ({scale.x:.3f}, {scale.y:.3f}, {scale.z:.3f})", 
                          "WARNING"))
        
        # Check for unapplied rotation (only for mesh objects)
        if obj.type == 'MESH':
            rot = obj.rotation_euler
            if abs(rot.x) > 0.001 or abs(rot.y) > 0.001 or abs(rot.z) > 0.001:
                issues.append(("TRANSFORM", 
                              f"Unapplied rotation detected", 
                              "WARNING"))
        
        return issues
    
    @staticmethod
    def fix_unapplied_rotation(obj: bpy.types.Object) -> int:
        """Apply rotation transform to mesh objects. Returns count of objects fixed."""
        # Only apply rotation to mesh objects (safer than all types)
        if obj.type != 'MESH':
            return 0
        
        rot = obj.rotation_euler
        
        # Check if rotation needs fixing
        if abs(rot.x) < 0.001 and abs(rot.y) < 0.001 and abs(rot.z) < 0.001:
            return 0
        
        view_layer = bpy.context.view_layer
        
        # Skip if object is not in current view layer
        if obj.name not in view_layer.objects:
            return 0
        
        # Ensure ALL objects are in OBJECT mode
        if view_layer.objects.active and view_layer.objects.active.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
        
        try:
            # CRITICAL: Force view_layer update
            try:
                view_layer.update()
            except:
                pass
            
            # CRITICAL: Deselect ALL objects safely without using selected_objects
            # (selected_objects can become stale during rapid operations)
            try:
                for o in list(bpy.data.objects):
                    if o and hasattr(o, 'select_set'):
                        try:
                            o.select_set(False)
                        except:
                            pass
            except:
                # If mass deselect fails, try bpy.ops
                try:
                    bpy.ops.object.select_all(action='DESELECT')
                except:
                    pass
            
            # Make data single-user if needed (prevents multi-user errors)
            if hasattr(obj, 'data') and obj.data and obj.data.users > 1:
                obj.data = obj.data.copy()
            
            # Select only target object
            obj.select_set(True)
            view_layer.objects.active = obj
            
            # CRITICAL: Update view_layer after selection change
            try:
                view_layer.update()
            except:
                pass
            
            # Apply rotation using temp_override
            with bpy.context.temp_override(
                view_layer=view_layer,
                selected_objects=[obj],
                active_object=obj,
                object=obj
            ):
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                return 1
        except Exception as e:
            print(f"Warning: Failed to apply rotation to {obj.name}: {e}")
            # CRITICAL: Ensure view_layer is updated even on error
            try:
                bpy.context.view_layer.update()
            except:
                pass
            return 0
    
    @staticmethod
    def fix_unapplied_scale(obj: bpy.types.Object) -> int:
        """Apply scale transform to object and all its instances, then restore instancing. Returns count of objects fixed."""
        scale = obj.scale
        
        # Check if scale needs fixing
        if abs(scale.x - 1.0) < 0.001 and abs(scale.y - 1.0) < 0.001 and abs(scale.z - 1.0) < 0.001:
            return 0
        
        # Only apply scale to mesh, curve, and surface objects
        if obj.type not in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:
            return 0
        
        # Find all instances (objects that share the same data)
        # IMPORTANT: Create list copy to avoid modifying collection during iteration
        instances_to_fix = []
        original_data = obj.data if hasattr(obj, 'data') else None
        
        if original_data:
            all_objects = list(bpy.data.objects)  # Create copy to avoid iteration issues
            for scene_obj in all_objects:
                if scene_obj.type == obj.type and scene_obj.data == original_data:
                    # Check if this instance also has unapplied scale
                    s = scene_obj.scale
                    if abs(s.x - 1.0) > 0.001 or abs(s.y - 1.0) > 0.001 or abs(s.z - 1.0) > 0.001:
                        instances_to_fix.append(scene_obj)
        else:
            # No data block (shouldn't happen, but handle it)
            instances_to_fix = [obj]
        
        if not instances_to_fix:
            return 0
        
        # Get current context view_layer (needed for temp_override)
        view_layer = bpy.context.view_layer
        
        # Track data blocks to clean up later
        temp_data_blocks = []
        successfully_fixed = []
        
        # Apply scale to each instance individually
        for instance in instances_to_fix:
            # CRITICAL: Force view_layer update to prevent context corruption
            try:
                view_layer.update()
            except:
                pass
            
            # Validate instance still exists in Blender's data
            if not instance or not hasattr(instance, 'name'):
                continue
            
            try:
                if instance.name not in bpy.data.objects:
                    continue
            except (RuntimeError, ReferenceError):
                continue
            
            # Skip if object is not in current view layer
            if instance.name not in view_layer.objects:
                print(f"Skipping {instance.name} - not in view layer")
                continue
                
            # Ensure ALL objects are in OBJECT mode (critical to avoid crashes)
            if view_layer.objects.active and view_layer.objects.active.mode != 'OBJECT':
                try:
                    bpy.ops.object.mode_set(mode='OBJECT')
                except:
                    pass
            
            try:
                # CRITICAL: Deselect ALL objects safely without using selected_objects
                # (selected_objects can become stale during rapid operations)
                try:
                    for o in list(bpy.data.objects):
                        if o and hasattr(o, 'select_set'):
                            try:
                                o.select_set(False)
                            except:
                                pass
                except:
                    # If mass deselect fails, try bpy.ops (slower but safer)
                    try:
                        bpy.ops.object.select_all(action='DESELECT')
                    except:
                        pass
                
                # CRITICAL: Make data single-user BEFORE applying transform
                # Blender cannot apply transforms to multi-user data
                if hasattr(instance, 'data') and instance.data and instance.data.users > 1:
                    old_data = instance.data
                    instance.data = instance.data.copy()
                    temp_data_blocks.append(instance.data)
                
                # Select only target object and make it active
                instance.select_set(True)
                view_layer.objects.active = instance
                
                # CRITICAL: Update view_layer again after selection change
                try:
                    view_layer.update()
                except:
                    pass
                
                # Use proper temp_override context with view_layer
                with bpy.context.temp_override(
                    view_layer=view_layer,
                    selected_objects=[instance],
                    active_object=instance,
                    object=instance
                ):
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    successfully_fixed.append(instance)
                    print(f"Successfully applied scale to {instance.name}")
            except Exception as e:
                print(f"Warning: Failed to apply scale to {instance.name}: {e}")
                # CRITICAL: On error, ensure view_layer is updated before continuing
                try:
                    view_layer.update()
                except:
                    pass
                continue
        
        # RESTORE INSTANCING: Re-link all objects to use the same data block
        if len(successfully_fixed) > 1:
            # Use the first object's data as the master
            master_data = successfully_fixed[0].data
            data_to_remove = []
            
            # Link all other objects to the master data
            for instance in successfully_fixed[1:]:
                if instance.data != master_data:
                    old_data = instance.data
                    instance.data = master_data
                    # Mark old data for removal if it has no users
                    if old_data and old_data.users == 0:
                        data_to_remove.append(old_data)
            
            # Clean up orphaned data blocks immediately to free memory
            for data in data_to_remove:
                if not data or data.users > 0:
                    continue
                
                try:
                    # Determine data type and remove from appropriate collection
                    if data.id_data in bpy.data.meshes:
                        bpy.data.meshes.remove(data)
                    elif data.id_data in bpy.data.curves:
                        bpy.data.curves.remove(data)
                    elif data.id_data in bpy.data.metaballs:
                        bpy.data.metaballs.remove(data)
                except (RuntimeError, ReferenceError, KeyError, AttributeError) as e:
                    print(f"Warning: Failed to remove orphaned data block: {e}")
                    continue
            
            # CRITICAL: Force garbage collection after data cleanup
            import gc
            gc.collect()
        
        return len(successfully_fixed)
