import bpy
from .processor import SceneProcessor

class APEX_OT_Validate(bpy.types.Operator):
    """Scans for shader issues in Scene or Collection"""
    bl_idname = "apex.validate"
    bl_label = "Validate Shaders"
    bl_options = {'REGISTER', 'UNDO'}

    scope: bpy.props.EnumProperty(
        name="Scope",
        items=[
            ('SCENE', "Full Scene", "Process entire scene"),
            ('COLLECTION', "Active Collection", "Process active collection only")
        ],
        default='SCENE'
    )

    def execute(self, context):
        # Determine scope
        if self.scope == 'SCENE':
            target_objects = context.scene.objects
            scope_name = "Scene"
        else:
            col = context.collection
            target_objects = col.objects
            scope_name = f"Collection '{col.name}'"

        # Get exclusion patterns
        exclusion_patterns = [p.strip() for p in context.scene.apex_exclusions.patterns.split(',') if p.strip()]

        # Execute Core Logic
        processor = SceneProcessor(target_objects, exclusion_patterns)
        reports = processor.scan()

        # Handle Results
        # Clear previous results
        context.scene.apex_validation_results.clear()
        
        if not reports:
            self.report({'INFO'}, f"ApexValidator: {scope_name} is clean.")
        else:
            # Store results in CollectionProperty
            for r in reports:
                item = context.scene.apex_validation_results.add()
                item.object_name = r.object_name
                item.material_name = r.material_name
                item.issue_type = r.issue_type
                item.message = r.message
                item.severity = r.severity
            
            error_count = sum(1 for r in reports if r.severity == 'ERROR')
            warning_count = len(reports) - error_count
                
            self.report({'WARNING'}, f"Found {error_count} errors, {warning_count} warnings in {scope_name}.")

        return {'FINISHED'}


class APEX_OT_FixShaders(bpy.types.Operator):
    """Fixes broken shaders in Scene or Collection"""
    bl_idname = "apex.fix_shaders"
    bl_label = "Fix Broken Shaders"
    bl_options = {'REGISTER', 'UNDO'}

    scope: bpy.props.EnumProperty(
        name="Scope",
        items=[
            ('SCENE', "Full Scene", ""),
            ('COLLECTION', "Active Collection", "")
        ],
        default='SCENE'
    )

    def execute(self, context):
        # Determine scope
        if self.scope == 'SCENE':
            target_objects = context.scene.objects
            scope_name = "Scene"
        else:
            target_objects = context.collection.objects
            scope_name = f"Collection '{context.collection.name}'"

        # Get exclusion patterns
        exclusion_patterns = [p.strip() for p in context.scene.apex_exclusions.patterns.split(',') if p.strip()]

        # Execute Core Logic
        processor = SceneProcessor(target_objects, exclusion_patterns)
        count = processor.fix_broken_shaders()

        self.report({'INFO'}, f"ApexValidator: Fixed {count} materials.")
        
        # Re-scan to update validation results
        context.scene.apex_validation_results.clear()
        reports = processor.scan()
        for r in reports:
            item = context.scene.apex_validation_results.add()
            item.object_name = r.object_name
            item.material_name = r.material_name
            item.issue_type = r.issue_type
            item.message = r.message
            item.severity = r.severity
        
        if len(reports) > 0:
            error_count = sum(1 for r in reports if r.severity == 'ERROR')
            warning_count = len(reports) - error_count
            self.report({'INFO'}, f"Remaining: {error_count} errors, {warning_count} warnings")
        else:
            self.report({'INFO'}, f"{scope_name} is now clean!")
        
        return {'FINISHED'}


class APEX_OT_AutoFix(bpy.types.Operator):
    """Automatically fixes all fixable issues in Scene or Collection"""
    bl_idname = "apex.auto_fix"
    bl_label = "Auto-Fix All Issues"
    bl_description = "Attempts to automatically fix: broken shaders, invalid drivers, broken modifiers, deprecated nodes, disconnected outputs"
    bl_options = {'REGISTER', 'UNDO'}

    scope: bpy.props.EnumProperty(
        name="Scope",
        items=[
            ('SCENE', "Full Scene", ""),
            ('COLLECTION', "Active Collection", "")
        ],
        default='SCENE'
    )

    def execute(self, context):
        # Validate context before proceeding
        if not context or not context.view_layer:
            self.report({'ERROR'}, "Invalid context - cannot run auto-fix.")
            return {'CANCELLED'}
        
        # Initialize progress tracking
        exclusions = context.scene.apex_exclusions
        exclusions.is_processing = True
        exclusions.progress_percentage = 0.0
        exclusions.progress_message = "Initializing..."
        exclusions.fixes_materials = 0
        exclusions.fixes_drivers = 0
        exclusions.fixes_modifiers = 0
        exclusions.fixes_transforms = 0
        exclusions.fixes_geometry = 0
        exclusions.fixes_rigging = 0
        
        # Force UI update
        context.area.tag_redraw() if context.area else None
        
        try:
            # Ensure we're in OBJECT mode before running auto-fixes (critical for transform operations)
            try:
                if context.view_layer.objects.active and context.view_layer.objects.active.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
            except (RuntimeError, AttributeError) as e:
                self.report({'ERROR'}, f"Cannot switch to OBJECT mode: {e}. Please switch manually.")
                exclusions.is_processing = False
                return {'CANCELLED'}
            
            # Determine scope
            exclusions.progress_message = "Scanning objects..."
            exclusions.progress_percentage = 5.0
            context.area.tag_redraw() if context.area else None
            
            if self.scope == 'SCENE':
                target_objects = list(context.scene.objects)
                scope_name = "Scene"
            else:
                # Use view_layer collection for better reliability
                target_objects = list(context.view_layer.active_layer_collection.collection.objects)
                scope_name = f"Collection '{context.view_layer.active_layer_collection.collection.name}'"

            print(f"\n=== Auto-Fix Running on {scope_name} ===")
            print(f"Total objects in scope: {len(target_objects)}")
            print(f"Object types: {set(obj.type for obj in target_objects)}")

            # Get exclusion patterns
            exclusion_patterns = [p.strip() for p in context.scene.apex_exclusions.patterns.split(',') if p.strip()]

            # Execute all auto-fixes
            exclusions.progress_message = "Running auto-fixes..."
            exclusions.progress_percentage = 10.0
            context.area.tag_redraw() if context.area else None
            
            processor = SceneProcessor(target_objects, exclusion_patterns)
            results = processor.auto_fix_all()
            
            # Update fix counters
            exclusions.fixes_transforms = results['scales_applied'] + results['rotations_applied']
            exclusions.fixes_materials = results['materials_rebuilt'] + results['empty_slots_fixed']
            exclusions.fixes_drivers = results['drivers_fixed'] + results['driver_chains_fixed']
            exclusions.fixes_modifiers = results['modifiers_fixed']
            exclusions.fixes_geometry = results['uvs_generated']
            exclusions.fixes_rigging = results['vertex_groups_cleaned'] + results['weights_normalized']
            
            exclusions.progress_percentage = 80.0
            exclusions.progress_message = "Re-scanning for remaining issues..."
            context.area.tag_redraw() if context.area else None

            # Report summary
            total_fixed = sum(results.values())
            if total_fixed == 0:
                self.report({'INFO'}, f"No fixable issues found in {scope_name}.")
            else:
                summary = []
                if results['scales_applied'] > 0:
                    summary.append(f"{results['scales_applied']} scales")
                if results['rotations_applied'] > 0:
                    summary.append(f"{results['rotations_applied']} rotations")
                if results['vertex_groups_cleaned'] > 0:
                    summary.append(f"{results['vertex_groups_cleaned']} vertex groups")
                if results['weights_normalized'] > 0:
                    summary.append(f"{results['weights_normalized']} weights normalized")
                if results['parent_loops_fixed'] > 0:
                    summary.append(f"{results['parent_loops_fixed']} parent loops")
                if results['driver_chains_fixed'] > 0:
                    summary.append(f"{results['driver_chains_fixed']} driver chains")
                if results['materials_rebuilt'] > 0:
                    summary.append(f"{results['materials_rebuilt']} materials")
                if results['empty_slots_fixed'] > 0:
                    summary.append(f"{results['empty_slots_fixed']} empty slots")
                if results['textures_packed'] > 0:
                    summary.append(f"{results['textures_packed']} textures packed")
                if results['uvs_generated'] > 0:
                    summary.append(f"{results['uvs_generated']} UV maps")
                if results['drivers_fixed'] > 0:
                    summary.append(f"{results['drivers_fixed']} drivers")
                if results['modifiers_fixed'] > 0:
                    summary.append(f"{results['modifiers_fixed']} modifiers")
                if results['deprecated_replaced'] > 0:
                    summary.append(f"{results['deprecated_replaced']} deprecated nodes")
                if results['disconnected_fixed'] > 0:
                    summary.append(f"{results['disconnected_fixed']} disconnected outputs")
                
                self.report({'INFO'}, f"Fixed: {', '.join(summary)}")
            
            # Re-run validation to update results
            exclusions.progress_percentage = 90.0
            exclusions.progress_message = "Updating results..."
            context.area.tag_redraw() if context.area else None
            
            context.scene.apex_validation_results.clear()
            reports = processor.scan()
            
            for r in reports:
                item = context.scene.apex_validation_results.add()
                item.object_name = r.object_name
                item.material_name = r.material_name
                item.issue_type = r.issue_type
                item.message = r.message
                item.severity = r.severity
            
            # Report what remains
            if len(reports) == 0:
                self.report({'INFO'}, f"{scope_name} is now clean!")
            else:
                error_count = sum(1 for r in reports if r.severity == 'ERROR')
                warning_count = len(reports) - error_count
                
                # Show details of what remains
                if error_count > 0:
                    self.report({'WARNING'}, f"Remaining: {error_count} errors, {warning_count} warnings (may need manual fixing)")
                else:
                    self.report({'INFO'}, f"Remaining: {warning_count} warnings (non-critical)")
            
            exclusions.progress_percentage = 100.0
            exclusions.progress_message = "Complete!"
            context.area.tag_redraw() if context.area else None

        finally:
            # Always reset processing flag
            exclusions.is_processing = False
            context.area.tag_redraw() if context.area else None

        return {'FINISHED'}


class APEX_OT_SelectObject(bpy.types.Operator):
    """Click to select and isolate object. Click again to un-isolate. Professional toggling system"""
    bl_idname = "apex.select_object"
    bl_label = "Select Object"
    bl_options = {'REGISTER', 'UNDO'}
    
    object_name: bpy.props.StringProperty()
    
    def execute(self, context):
        # Validate context
        if not context or not context.scene or not context.view_layer:
            self.report({'ERROR'}, "Invalid context.")
            return {'CANCELLED'}
        
        if not self.object_name:
            self.report({'ERROR'}, "No object name provided.")
            return {'CANCELLED'}
        
        # Check if object exists in scene
        if self.object_name not in context.scene.objects:
            self.report({'ERROR'}, f"Object '{self.object_name}' not found in scene.")
            return {'CANCELLED'}
        
        # Get view layer object
        try:
            view_layer_obj = context.view_layer.objects.get(self.object_name)
        except (RuntimeError, AttributeError) as e:
            self.report({'ERROR'}, f"Cannot access view layer: {e}")
            return {'CANCELLED'}
        
        if view_layer_obj is None:
            self.report({'ERROR'}, f"Object '{self.object_name}' is not in the current View Layer.")
            return {'CANCELLED'}
        
        # CRITICAL: Create safe list copies to prevent iterator invalidation
        try:
            view_layer_objects = list(context.view_layer.objects)
        except (RuntimeError, ReferenceError):
            self.report({'ERROR'}, "Cannot access view layer objects.")
            return {'CANCELLED'}
        
        # Determine current state
        try:
            is_currently_active = (context.view_layer.objects.active == view_layer_obj)
            is_currently_selected = view_layer_obj.select_get()
        except (RuntimeError, ReferenceError):
            self.report({'ERROR'}, "Object state is invalid.")
            return {'CANCELLED'}
        
        # Count hidden objects (excluding the target) - use safe list
        hidden_count = 0
        for obj in view_layer_objects:
            if not obj or not hasattr(obj, 'hide_get'):
                continue
            try:
                if obj != view_layer_obj and obj.hide_get():
                    hidden_count += 1
            except (RuntimeError, ReferenceError):
                continue
        
        is_isolated = hidden_count > 0
        
        # Decision logic
        if is_currently_active and is_currently_selected and is_isolated:
            # State: Same object clicked while isolated → UN-ISOLATE
            # Show all objects, keep selection
            for other_obj in view_layer_objects:
                if not other_obj or not hasattr(other_obj, 'hide_set'):
                    continue
                try:
                    other_obj.hide_set(False)
                except (RuntimeError, ReferenceError):
                    continue
            
            self.report({'INFO'}, f"Un-isolated: {self.object_name}")
        
        else:
            # State: New object OR not isolated → SELECT & ISOLATE
            # Deselect everything first - use safe list
            for other_obj in view_layer_objects:
                if not other_obj or not hasattr(other_obj, 'select_set'):
                    continue
                try:
                    other_obj.select_set(False)
                except (RuntimeError, ReferenceError):
                    continue
            
            # Select and activate target
            try:
                view_layer_obj.select_set(True)
                context.view_layer.objects.active = view_layer_obj
            except (RuntimeError, ReferenceError) as e:
                self.report({'ERROR'}, f"Cannot select object: {str(e)}")
                return {'CANCELLED'}
            
            # Isolate: hide everything except target - use safe list
            for other_obj in view_layer_objects:
                if not other_obj or not hasattr(other_obj, 'hide_set'):
                    continue
                try:
                    if other_obj != view_layer_obj:
                        other_obj.hide_set(True)
                    else:
                        # Ensure target is visible
                        other_obj.hide_set(False)
                except (RuntimeError, ReferenceError):
                    continue
            
            # Frame the isolated object in all 3D viewports for better focus
            # CRITICAL: Validate screen and areas before accessing
            if context.screen and hasattr(context.screen, 'areas'):
                for area in context.screen.areas:
                    if not area or area.type != 'VIEW_3D':
                        continue
                    
                    for region in area.regions:
                        if not region or region.type != 'WINDOW':
                            continue
                        
                        try:
                            with context.temp_override(area=area, region=region, 
                                                      active_object=view_layer_obj,
                                                      selected_objects=[view_layer_obj]):
                                bpy.ops.view3d.view_selected()
                        except (RuntimeError, ReferenceError, AttributeError):
                            pass
                        break
            
            self.report({'INFO'}, f"Isolated: {self.object_name}")
        
        return {'FINISHED'}


class APEX_OT_ClearResults(bpy.types.Operator):
    """Clear validation results"""
    bl_idname = "apex.clear_results"
    bl_label = "Clear Results"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.scene.apex_validation_results.clear()
        self.report({'INFO'}, "Results cleared.")
        return {'FINISHED'}