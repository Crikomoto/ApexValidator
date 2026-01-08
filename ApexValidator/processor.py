import bpy
import typing
from .models import ValidationReport
from .validators.materials import MaterialValidator
from .validators.drivers import DriverValidator
from .validators.modifiers import ModifierValidator
from .validators.geometry import GeometryValidator
from .validators.transforms import TransformValidator
from .validators.rigging import RiggingValidator
from .validators.dependencies import CircularDependencyValidator
from .validators.data import DataValidator

# ------------------------------------------------------------------------
#   Logic: Scene Processor
# ------------------------------------------------------------------------

class SceneProcessor:
    """
    Iterates over a provided set of objects to apply validation or fixes.
    """
    
    def __init__(self, objects: typing.Iterable[bpy.types.Object], exclusion_patterns: typing.List[str] = None):
        self.objects = objects
        self.reports: typing.List[ValidationReport] = []
        self.exclusion_patterns = exclusion_patterns or []
    
    def is_excluded(self, obj_name: str) -> bool:
        """Check if object name matches any exclusion pattern."""
        for pattern in self.exclusion_patterns:
            if pattern and obj_name.startswith(pattern.strip()):
                return True
        return False

    def scan(self) -> typing.List[ValidationReport]:
        self.reports.clear()
        
        for obj in self.objects:
            # Skip excluded objects
            if self.is_excluded(obj.name):
                continue
            
            # Validate Transforms (all object types)
            transform_issues = TransformValidator.validate_transforms(obj)
            for issue_type, message, severity in transform_issues:
                self.reports.append(ValidationReport(
                    object_name=obj.name,
                    material_name="N/A",
                    issue_type=issue_type,
                    message=message,
                    severity=severity
                ))
            
            # Validate Object Data (all object types)
            data_issues = DataValidator.validate_object_data(obj)
            for issue_type, message, severity in data_issues:
                self.reports.append(ValidationReport(
                    object_name=obj.name,
                    material_name="N/A",
                    issue_type=issue_type,
                    message=message,
                    severity=severity
                ))
            
            # Validate Drivers (all object types)
            driver_issues = DriverValidator.validate_drivers(obj)
            for issue_type, message, severity in driver_issues:
                self.reports.append(ValidationReport(
                    object_name=obj.name,
                    material_name="N/A",
                    issue_type=issue_type,
                    message=message,
                    severity=severity
                ))
            
            # Validate Modifiers (all object types)
            modifier_issues = ModifierValidator.validate_modifiers(obj)
            for issue_type, message, severity in modifier_issues:
                self.reports.append(ValidationReport(
                    object_name=obj.name,
                    material_name="N/A",
                    issue_type=issue_type,
                    message=message,
                    severity=severity
                ))
            
            # Validate Geometry (mesh objects only)
            geometry_issues = GeometryValidator.validate_geometry(obj)
            for issue_type, message, severity in geometry_issues:
                self.reports.append(ValidationReport(
                    object_name=obj.name,
                    material_name="N/A",
                    issue_type=issue_type,
                    message=message,
                    severity=severity
                ))
            
            # Validate Rigging (mesh objects only)
            rigging_issues = RiggingValidator.validate_vertex_groups(obj)
            for issue_type, message, severity in rigging_issues:
                self.reports.append(ValidationReport(
                    object_name=obj.name,
                    material_name="N/A",
                    issue_type=issue_type,
                    message=message,
                    severity=severity
                ))
            
            # Validate Circular Dependencies (all object types)
            circular_issues = CircularDependencyValidator.validate_dependencies(obj)
            for issue_type, message, severity in circular_issues:
                self.reports.append(ValidationReport(
                    object_name=obj.name,
                    material_name="N/A",
                    issue_type=issue_type,
                    message=message,
                    severity=severity
                ))
            
            # Validate Materials
            if obj.type not in {'MESH', 'CURVE', 'SURFACE'}:
                continue
                
            if not obj.material_slots:
                continue

            for slot in obj.material_slots:
                if not slot.material:
                    self.reports.append(ValidationReport(
                        object_name=obj.name,
                        material_name="None",
                        issue_type="EMPTY_SLOT",
                        message="Empty material slot found.",
                        severity="WARNING"
                    ))
                    continue

                mat = slot.material
                
                # Check if shader is broken
                is_broken, msg, severity = MaterialValidator.is_material_broken(mat)
                if is_broken:
                    self.reports.append(ValidationReport(
                        object_name=obj.name,
                        material_name=mat.name,
                        issue_type="BROKEN_SHADER",
                        message=msg,
                        severity=severity
                    ))
                
                # Check textures
                texture_issues = MaterialValidator.validate_textures(mat)
                for message, severity in texture_issues:
                    self.reports.append(ValidationReport(
                        object_name=obj.name,
                        material_name=mat.name,
                        issue_type="TEXTURE",
                        message=message,
                        severity=severity
                    ))
                
                # Check shader compatibility
                compat_issues = MaterialValidator.check_shader_compatibility(mat)
                for message, severity in compat_issues:
                    self.reports.append(ValidationReport(
                        object_name=obj.name,
                        material_name=mat.name,
                        issue_type="SHADER_COMPAT",
                        message=message,
                        severity=severity
                    ))
        
        return self.reports

    def fix_broken_shaders(self) -> int:
        """Fixes unique materials used by the objects in scope."""
        materials_to_fix = set()
        
        try:
            objects_list = list(self.objects)  # Create safe copy
        except (RuntimeError, ReferenceError):
            return 0
        
        for obj in objects_list:
            if not obj or obj.type not in {'MESH', 'CURVE', 'SURFACE'}:
                continue
            
            if not hasattr(obj, 'material_slots'):
                continue
            
            try:
                for slot in obj.material_slots:
                    if slot and slot.material:
                        # Validate material still exists
                        mat = slot.material
                        if mat.name in bpy.data.materials:
                            is_broken, _, _ = MaterialValidator.is_material_broken(mat)
                            if is_broken:
                                materials_to_fix.add(mat)
            except (RuntimeError, ReferenceError):
                continue

        count = 0
        for mat in materials_to_fix:
            try:
                if mat and mat.name in bpy.data.materials:
                    MaterialValidator.fix_material(mat)
                    count += 1
            except (RuntimeError, ReferenceError, AttributeError) as e:
                print(f"Warning: Failed to fix material {mat.name if mat else 'Unknown'}: {e}")
                continue
            
        return count
    
    def auto_fix_all(self) -> typing.Dict[str, int]:
        """
        Attempts to automatically fix all fixable issues.
        Returns dict with counts of fixes by category.
        
        IMPORTANT: Transform operations are batched to prevent context corruption
        when processing large numbers of objects (200+).
        """
        # Counters
        materials_rebuilt = 0
        disconnected_fixed = 0
        deprecated_replaced = 0
        drivers_fixed = 0
        driver_chains_fixed = 0
        modifiers_fixed = 0
        empty_slots_fixed = 0
        scales_applied = 0
        rotations_applied = 0
        textures_packed = 0
        uvs_generated = 0
        vertex_groups_cleaned = 0
        weights_normalized = 0
        parent_loops_fixed = 0
        
        # Collect unique materials
        materials_processed = set()
        materials_fully_fixed = set()  # Track materials that were completely rebuilt
        objects_processed = set()  # Track objects already processed to avoid duplicate fixes
        
        # PHASE 1: Transform fixes (must be done separately to avoid iteration issues)
        # CRITICAL: Batch processing to prevent context corruption with large object counts
        print("=== Phase 1: Transform Fixes ===")
        
        BATCH_SIZE = 15  # Reduced from 25 - prevents access violations with transform operations
        transform_objects = []
        
        # Collect objects that need transform fixes
        for obj in list(self.objects):
            if not obj or not hasattr(obj, 'name'):
                continue
            
            try:
                if obj.name not in bpy.data.objects:
                    continue
            except (RuntimeError, ReferenceError):
                continue
            
            if self.is_excluded(obj.name):
                continue
            
            transform_objects.append(obj)
        
        print(f"Found {len(transform_objects)} objects to process for transforms")
        
        # SAFETY: Warn if processing a very large number of objects
        if len(transform_objects) > 500:
            print(f"WARNING: Processing {len(transform_objects)} objects may take several minutes")
            print(f"         and consume significant memory. Consider processing in smaller batches.")
        
        # Process in batches
        for batch_start in range(0, len(transform_objects), BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, len(transform_objects))
            batch = transform_objects[batch_start:batch_end]
            
            batch_num = batch_start//BATCH_SIZE + 1
            total_batches = (len(transform_objects) + BATCH_SIZE - 1) // BATCH_SIZE
            print(f"Processing transform batch {batch_num}/{total_batches} ({len(batch)} objects)...")
            
            # CRITICAL: Force view_layer update before batch
            try:
                bpy.context.view_layer.update()
            except:
                pass
            
            # CRITICAL: Force Python garbage collection between batches
            # This prevents memory buildup from data copies
            import gc
            gc.collect()
            
            for obj in batch:
                # Validate object still exists
                if not obj or not hasattr(obj, 'name'):
                    continue
                
                try:
                    if obj.name not in bpy.data.objects:
                        continue
                except (RuntimeError, ReferenceError):
                    continue
                
                # Fix unapplied scales (only process once per instance group)
                if obj not in objects_processed:
                    try:
                        fixed_count = TransformValidator.fix_unapplied_scale(obj)
                        if fixed_count > 0:
                            scales_applied += fixed_count
                            # Mark all instances as processed to avoid double-counting
                            if hasattr(obj, 'data') and obj.data:
                                # Create list copy to avoid collection modification during iteration
                                all_objects = list(bpy.data.objects)
                                for scene_obj in all_objects:
                                    if scene_obj.type == obj.type and scene_obj.data == obj.data:
                                        objects_processed.add(scene_obj)
                    except Exception as e:
                        print(f"Error fixing scale for {obj.name}: {e}")
                        continue
                
                # Fix unapplied rotations (mesh objects only, conservative)
                # CRITICAL: Validate object before accessing
                try:
                    if not obj or obj.name not in bpy.data.objects:
                        continue
                    # Test object accessibility
                    _ = obj.type
                    if TransformValidator.fix_unapplied_rotation(obj):
                        rotations_applied += 1
                except (RuntimeError, ReferenceError, AttributeError) as e:
                    print(f"Error: Object {obj.name if obj else 'Unknown'} became invalid: {e}")
                    continue
                except Exception as e:
                    print(f"Error fixing rotation for {obj.name if obj else 'Unknown'}: {e}")
                    continue
            
            # CRITICAL: Cleanup and sync after each batch
            try:
                # Force view_layer update
                bpy.context.view_layer.update()
                
                # Force depsgraph update to ensure all changes are processed
                bpy.context.evaluated_depsgraph_get().update()
            except:
                pass
            
            # CRITICAL: Force Python garbage collection again after batch
            # This clears temporary data copies and frees memory
            import gc
            gc.collect()
            
            # SAFETY: Small delay to let Blender stabilize internal state
            # Prevents access violations from rapid operations
            import time
            time.sleep(0.05)  # 50ms delay
            
            print(f"Batch {batch_num}/{total_batches} complete. Total: Scales={scales_applied}, Rotations={rotations_applied}")
        
        print(f"=== Phase 1 Complete: {scales_applied} scales, {rotations_applied} rotations ===")
        
        # PHASE 2: Object-level fixes (drivers, modifiers, materials)
        print("=== Phase 2: Object-Level Fixes ===")
        for obj in self.objects:
            # Validate object still exists
            if not obj or not hasattr(obj, 'name'):
                continue
            
            try:
                if obj.name not in bpy.data.objects:
                    continue
            except (RuntimeError, ReferenceError):
                continue
            
            # Skip excluded objects
            if self.is_excluded(obj.name):
                continue
            
            try:
                # Fix empty material slots first
                empty_slots_fixed += MaterialValidator.fix_empty_slots(obj)
            except Exception as e:
                print(f"Error fixing empty slots for {obj.name}: {e}")
            
            try:
                # Fix drivers
                drivers_fixed += DriverValidator.fix_invalid_drivers(obj)
            except Exception as e:
                print(f"Error fixing drivers for {obj.name}: {e}")
            
            try:
                # Fix driver chains (circular dependencies across multiple objects)
                if DriverValidator.fix_driver_chains(obj):
                    driver_chains_fixed += 1
            except Exception as e:
                print(f"Error fixing driver chains for {obj.name}: {e}")
            
            try:
                # Fix modifiers
                modifiers_fixed += ModifierValidator.fix_broken_modifiers(obj)
            except Exception as e:
                print(f"Error fixing modifiers for {obj.name}: {e}")
            
            try:
                # Generate missing UVs (mesh objects only)
                if GeometryValidator.fix_missing_uvs(obj):
                    uvs_generated += 1
            except Exception as e:
                print(f"Error generating UVs for {obj.name}: {e}")
            
            # NOTE: Mesh renaming disabled - CAD data often has default names intentionally
            
            try:
                # Fix circular dependencies (parent loops)
                if CircularDependencyValidator.fix_parent_loop(obj):
                    parent_loops_fixed += 1
            except Exception as e:
                print(f"Error fixing circular dependencies for {obj.name}: {e}")
            
            try:
                # Fix rigging issues (mesh objects only)
                rigging_results = RiggingValidator.fix_vertex_groups(obj)
                if rigging_results['empty_removed'] > 0 or rigging_results['orphaned_removed'] > 0:
                    vertex_groups_cleaned += rigging_results['empty_removed'] + rigging_results['orphaned_removed']
                if rigging_results['normalized'] > 0:
                    weights_normalized += 1
            except Exception as e:
                print(f"Error fixing rigging for {obj.name}: {e}")
            
            # Fix materials
            if obj.type not in {'MESH', 'CURVE', 'SURFACE'}:
                continue
            
            if not hasattr(obj, 'material_slots'):
                continue
            
            try:
                material_slots = list(obj.material_slots)  # Create safe copy
            except (RuntimeError, ReferenceError):
                continue
            
            for slot_idx, slot in enumerate(material_slots):
                # Validate slot exists
                if not slot:
                    continue
                
                if not slot.material:
                    continue
                    
                mat = slot.material
                
                # Validate material still exists in blend data
                try:
                    if mat.name not in bpy.data.materials:
                        continue
                except (RuntimeError, ReferenceError):
                    continue
                
                # Skip if already the marker material
                if mat.name == "_BROKEN TO FIX":
                    continue
                
                # Skip if already processed
                if mat in materials_processed:
                    continue
                    
                materials_processed.add(mat)
                
                try:
                    # Check if material is broken
                    is_broken, msg, severity = MaterialValidator.is_material_broken(mat)
                    
                    # Replace broken shaders (ERROR severity) with red marker material
                    if is_broken and severity == 'ERROR':
                        if MaterialValidator.mark_broken_material(obj, slot_idx):
                            materials_rebuilt += 1
                    
                    # Fix only minor issues (WARNINGS)
                    elif is_broken and severity == 'WARNING':
                        if MaterialValidator.fix_disconnected_output(mat):
                            disconnected_fixed += 1
                    
                    # Replace deprecated nodes (safe operation)
                    replaced_count = MaterialValidator.replace_deprecated_nodes(mat)
                    deprecated_replaced += replaced_count
                    
                    # Pack external textures (always safe, makes file self-contained)
                    packed_count = MaterialValidator.pack_external_textures(mat)
                    textures_packed += packed_count
                except Exception as e:
                    print(f"Error fixing material {mat.name}: {e}")
                    continue
        
        print(f"=== Auto-Fix Complete: {materials_rebuilt} materials, {scales_applied} scales, {vertex_groups_cleaned} vertex groups, {driver_chains_fixed} driver chains ===")
        
        return {
            'materials_rebuilt': materials_rebuilt,
            'disconnected_fixed': disconnected_fixed,
            'deprecated_replaced': deprecated_replaced,
            'drivers_fixed': drivers_fixed,
            'driver_chains_fixed': driver_chains_fixed,
            'modifiers_fixed': modifiers_fixed,
            'empty_slots_fixed': empty_slots_fixed,
            'scales_applied': scales_applied,
            'rotations_applied': rotations_applied,
            'textures_packed': textures_packed,
            'uvs_generated': uvs_generated,
            'vertex_groups_cleaned': vertex_groups_cleaned,
            'weights_normalized': weights_normalized,
            'parent_loops_fixed': parent_loops_fixed
        }
