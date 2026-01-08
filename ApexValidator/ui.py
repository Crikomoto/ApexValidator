import bpy

# PropertyGroup for exclusion patterns and filters
class APEX_ExclusionPatterns(bpy.types.PropertyGroup):
    """Settings for object exclusions and result filtering."""
    patterns: bpy.props.StringProperty(
        name="Exclusion Patterns",
        description="Comma-separated object name prefixes to exclude (e.g., 'WGT-,TEMP-')",
        default="WGT-"
    )
    
    # Progress tracking properties
    is_processing: bpy.props.BoolProperty(
        name="Processing",
        description="Auto-fix is currently running",
        default=False
    )
    progress_message: bpy.props.StringProperty(
        name="Progress",
        description="Current operation status",
        default=""
    )
    progress_percentage: bpy.props.FloatProperty(
        name="Progress",
        description="Progress percentage (0-100)",
        default=0.0,
        min=0.0,
        max=100.0,
        subtype='PERCENTAGE'
    )
    
    # Fix counters (updated during auto-fix)
    fixes_materials: bpy.props.IntProperty(name="Materials Fixed", default=0)
    fixes_drivers: bpy.props.IntProperty(name="Drivers Fixed", default=0)
    fixes_modifiers: bpy.props.IntProperty(name="Modifiers Fixed", default=0)
    fixes_transforms: bpy.props.IntProperty(name="Transforms Fixed", default=0)
    fixes_geometry: bpy.props.IntProperty(name="Geometry Fixed", default=0)
    fixes_rigging: bpy.props.IntProperty(name="Rigging Fixed", default=0)
    
    # Filter controls
    filter_show_all: bpy.props.BoolProperty(
        name="Show All",
        description="Display all issue types",
        default=True
    )
    filter_materials: bpy.props.BoolProperty(
        name="Materials",
        description="Show material issues (shaders, textures, empty slots)",
        default=True
    )
    filter_geometry: bpy.props.BoolProperty(
        name="Geometry",
        description="Show geometry issues (N-gons, missing UVs, poly count)",
        default=True
    )
    filter_transforms: bpy.props.BoolProperty(
        name="Transforms",
        description="Show transform issues (unapplied scales, rotations)",
        default=True
    )
    filter_modifiers: bpy.props.BoolProperty(
        name="Modifiers",
        description="Show modifier issues (broken, unbound, unstable)",
        default=True
    )
    filter_drivers: bpy.props.BoolProperty(
        name="Drivers",
        description="Show driver issues (invalid, circular, missing targets)",
        default=True
    )
    filter_data: bpy.props.BoolProperty(
        name="Object Data",
        description="Show object data issues (multi-user, naming)",
        default=True
    )
    filter_rigging: bpy.props.BoolProperty(
        name="Rigging",
        description="Show rigging issues (vertex groups, armature setup)",
        default=True
    )
    filter_circular: bpy.props.BoolProperty(
        name="Circular Deps",
        description="Show circular dependency errors (parent loops, constraint loops)",
        default=True
    )

# PropertyGroup to store validation results
class APEX_ValidationItem(bpy.types.PropertyGroup):
    object_name: bpy.props.StringProperty(name="Object")
    material_name: bpy.props.StringProperty(name="Material")
    issue_type: bpy.props.StringProperty(name="Type")
    message: bpy.props.StringProperty(name="Message")
    severity: bpy.props.StringProperty(name="Severity")  # 'ERROR' or 'WARNING'

# UIList for displaying validation results
class APEX_UL_ValidationList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            # Severity icon
            if item.severity == 'ERROR':
                row.label(text="", icon='CANCEL')
            else:
                row.label(text="", icon='ERROR')  # WARNING
            
            # Issue type icon
            type_icon = 'DOT'
            if item.issue_type == 'BROKEN_SHADER':
                type_icon = 'SHADING_RENDERED'
            elif item.issue_type == 'TEXTURE':
                type_icon = 'TEXTURE'
            elif item.issue_type == 'INVALID_DRIVER' or item.issue_type == 'CIRCULAR_DRIVER' or item.issue_type == 'MISSING_DRIVER_TARGET':
                type_icon = 'DRIVER'
            elif item.issue_type == 'BROKEN_MODIFIER' or item.issue_type == 'UNBOUND_MODIFIER' or item.issue_type == 'UNSTABLE_MODIFIER':
                type_icon = 'MODIFIER'
            elif item.issue_type == 'GEOMETRY':
                type_icon = 'MESH_DATA'
            elif item.issue_type == 'SHADER_COMPAT':
                type_icon = 'NODE_MATERIAL'
            elif item.issue_type == 'EMPTY_SLOT':
                type_icon = 'MATERIAL'
            elif item.issue_type == 'TRANSFORM':
                type_icon = 'ORIENTATION_GLOBAL'
            elif item.issue_type == 'DATA':
                type_icon = 'OUTLINER_DATA_MESH'
            
            row.label(text="", icon=type_icon)
            
            # Object name (clickable to select)
            if item.object_name in context.scene.objects:
                op = row.operator("apex.select_object", text=item.object_name, emboss=False)
                op.object_name = item.object_name
            else:
                row.label(text=item.object_name)
            
            # Material name (if applicable)
            if item.material_name != "N/A":
                sub = row.row()
                sub.scale_x = 0.8
                sub.label(text=item.material_name, icon='MATERIAL')
            
            # Issue type badge
            sub = row.row()
            sub.scale_x = 0.6
            sub.label(text=f"[{item.issue_type}]")
            
            # Message (truncated)
            msg = item.message[:35] + "..." if len(item.message) > 35 else item.message
            row.label(text=msg)
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='ERROR')

class APEX_PT_MainPanel(bpy.types.Panel):
    bl_label = "Apex Validator"
    bl_idname = "APEX_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Apex'

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        
        # Quick Actions - Most common workflow at the top
        box_quick = layout.box()
        box_quick.label(text="Quick Actions", icon='PLAY')
        
        # Single row with scope selector and main buttons
        row = box_quick.row(align=True)
        row.label(text="Scope:")
        row.prop(context.scene, "apex_quick_scope", text="", icon='NONE')
        
        # Main action buttons
        row = box_quick.row(align=True)
        row.scale_y = 1.5
        
        op_scan = row.operator("apex.validate", text="Scan", icon='ZOOM_IN')
        op_scan.scope = context.scene.apex_quick_scope
        
        op_autofix = row.operator("apex.auto_fix", text="Auto-Fix", icon='TOOL_SETTINGS')
        op_autofix.scope = context.scene.apex_quick_scope
        
        # Progress indicator (shown when processing)
        exclusions = context.scene.apex_exclusions
        if exclusions.is_processing:
            layout.separator()
            progress_box = layout.box()
            progress_box.label(text="Processing...", icon='TIME')
            
            # Progress bar
            progress_box.prop(exclusions, "progress_percentage", text="", slider=True)
            
            # Status message
            if exclusions.progress_message:
                progress_box.label(text=exclusions.progress_message, icon='INFO')
            
            # Live fix counters
            if (exclusions.fixes_materials + exclusions.fixes_drivers + 
                exclusions.fixes_modifiers + exclusions.fixes_transforms + 
                exclusions.fixes_geometry + exclusions.fixes_rigging) > 0:
                
                counter_grid = progress_box.grid_flow(row_major=True, columns=3, align=True)
                if exclusions.fixes_materials > 0:
                    counter_grid.label(text=f"Materials: {exclusions.fixes_materials}", icon='MATERIAL')
                if exclusions.fixes_transforms > 0:
                    counter_grid.label(text=f"Transforms: {exclusions.fixes_transforms}", icon='ORIENTATION_GLOBAL')
                if exclusions.fixes_drivers > 0:
                    counter_grid.label(text=f"Drivers: {exclusions.fixes_drivers}", icon='DRIVER')
                if exclusions.fixes_modifiers > 0:
                    counter_grid.label(text=f"Modifiers: {exclusions.fixes_modifiers}", icon='MODIFIER')
                if exclusions.fixes_geometry > 0:
                    counter_grid.label(text=f"Geometry: {exclusions.fixes_geometry}", icon='MESH_DATA')
                if exclusions.fixes_rigging > 0:
                    counter_grid.label(text=f"Rigging: {exclusions.fixes_rigging}", icon='ARMATURE_DATA')
        
        layout.separator()
        
        # Section: Exclusion Patterns
        box_exclusions = layout.box()
        box_exclusions.label(text="Exclusion Patterns", icon='FILTER')
        row = box_exclusions.row()
        row.prop(context.scene.apex_exclusions, "patterns", text="")
        box_exclusions.label(text="Comma-separated prefixes (e.g., 'WGT-,TEMP-')", icon='INFO')

        # Section: Result Filters
        if len(context.scene.apex_validation_results) > 0:
            layout.separator()
            box_filters = layout.box()
            filter_header = box_filters.row()
            filter_header.label(text="Filter Results", icon='FILTER')
            
            # Show All toggle
            filter_header.prop(context.scene.apex_exclusions, "filter_show_all", text="Show All", toggle=True)
            
            # Individual filter checkboxes (disabled when Show All is active)
            if not context.scene.apex_exclusions.filter_show_all:
                grid = box_filters.grid_flow(row_major=True, columns=2, align=True)
                grid.prop(context.scene.apex_exclusions, "filter_materials", text="Materials", icon='MATERIAL')
                grid.prop(context.scene.apex_exclusions, "filter_geometry", text="Geometry", icon='MESH_DATA')
                grid.prop(context.scene.apex_exclusions, "filter_transforms", text="Transforms", icon='ORIENTATION_GLOBAL')
                grid.prop(context.scene.apex_exclusions, "filter_modifiers", text="Modifiers", icon='MODIFIER')
                grid.prop(context.scene.apex_exclusions, "filter_drivers", text="Drivers", icon='DRIVER')
                grid.prop(context.scene.apex_exclusions, "filter_rigging", text="Rigging", icon='ARMATURE_DATA')
                grid.prop(context.scene.apex_exclusions, "filter_circular", text="Circular", icon='CON_TRACKTO')
                grid.prop(context.scene.apex_exclusions, "filter_data", text="Data", icon='OUTLINER_DATA_MESH')

        # Validation Results Panel - Categorized by Type and Severity
        if len(context.scene.apex_validation_results) > 0:
            layout.separator()
            
            # Overall summary header
            total_issues = len(context.scene.apex_validation_results)
            error_count = sum(1 for item in context.scene.apex_validation_results if item.severity == 'ERROR')
            warning_count = total_issues - error_count
            
            summary_box = layout.box()
            summary_row = summary_box.row()
            summary_row.label(text=f"Found {total_issues} Issue(s):", icon='INFO')
            if error_count > 0:
                summary_row.label(text=f"{error_count} Errors", icon='CANCEL')
            if warning_count > 0:
                summary_row.label(text=f"{warning_count} Warnings", icon='ERROR')
            summary_box.operator("apex.clear_results", text="Clear All", icon='X')
            
            # Categorize issues by type
            categories = {}
            for item in context.scene.apex_validation_results:
                if item.issue_type not in categories:
                    categories[item.issue_type] = {'errors': [], 'warnings': []}
                
                if item.severity == 'ERROR':
                    categories[item.issue_type]['errors'].append(item)
                else:
                    categories[item.issue_type]['warnings'].append(item)
            
            # Display by category with filtering
            category_names = {
                'BROKEN_SHADER': ('Broken Shaders', 'SHADING_RENDERED'),
                'TEXTURE': ('Textures', 'TEXTURE'),
                'GEOMETRY': ('Geometry', 'MESH_DATA'),
                'TRANSFORM': ('Transforms', 'ORIENTATION_GLOBAL'),
                'DATA': ('Object Data', 'OUTLINER_DATA_MESH'),
                'INVALID_DRIVER': ('Invalid Drivers', 'DRIVER'),
                'CIRCULAR_DRIVER': ('Circular Drivers', 'DRIVER'),
                'DRIVER_CHAIN': ('Driver Chain Loops', 'DRIVER'),
                'MISSING_DRIVER_TARGET': ('Missing Driver Targets', 'DRIVER'),
                'BROKEN_MODIFIER': ('Broken Modifiers', 'MODIFIER'),
                'UNBOUND_MODIFIER': ('Unbound Modifiers', 'MODIFIER'),
                'UNSTABLE_MODIFIER': ('Unstable Modifiers', 'MODIFIER'),
                'SHADER_COMPAT': ('Shader Compatibility', 'NODE_MATERIAL'),
                'EMPTY_SLOT': ('Empty Material Slots', 'MATERIAL'),
                'RIGGING': ('Rigging Issues', 'ARMATURE_DATA'),
                'CIRCULAR_DEPENDENCY': ('Circular Dependencies', 'CON_TRACKTO'),
            }
            
            # Category to filter mapping
            category_filter_map = {
                'BROKEN_SHADER': 'filter_materials',
                'TEXTURE': 'filter_materials',
                'SHADER_COMPAT': 'filter_materials',
                'EMPTY_SLOT': 'filter_materials',
                'GEOMETRY': 'filter_geometry',
                'TRANSFORM': 'filter_transforms',
                'DATA': 'filter_data',
                'INVALID_DRIVER': 'filter_drivers',
                'CIRCULAR_DRIVER': 'filter_drivers',
                'DRIVER_CHAIN': 'filter_drivers',
                'MISSING_DRIVER_TARGET': 'filter_drivers',
                'BROKEN_MODIFIER': 'filter_modifiers',
                'UNBOUND_MODIFIER': 'filter_modifiers',
                'UNSTABLE_MODIFIER': 'filter_modifiers',
                'RIGGING': 'filter_rigging',
                'CIRCULAR_DEPENDENCY': 'filter_circular',
            }
            
            filters = context.scene.apex_exclusions
            
            for issue_type in sorted(categories.keys()):
                # Apply filtering
                if not filters.filter_show_all:
                    filter_prop = category_filter_map.get(issue_type)
                    if filter_prop and not getattr(filters, filter_prop, True):
                        continue  # Skip this category if filtered out
                
                errors = categories[issue_type]['errors']
                warnings = categories[issue_type]['warnings']
                
                if not errors and not warnings:
                    continue
                
                cat_name, cat_icon = category_names.get(issue_type, (issue_type, 'DOT'))
                
                cat_box = layout.box()
                header = cat_box.row()
                header.label(text=cat_name, icon=cat_icon)
                if errors:
                    header.label(text=f"{len(errors)} Errors", icon='CANCEL')
                if warnings:
                    header.label(text=f"{len(warnings)} Warnings", icon='ERROR')
                
                # Show errors first
                if errors:
                    for item in errors:
                        row = cat_box.row()
                        row.alert = True  # Red highlight for errors
                        
                        # Clickable object name
                        if item.object_name in context.scene.objects:
                            op = row.operator("apex.select_object", text=item.object_name, emboss=False, icon='CANCEL')
                            op.object_name = item.object_name
                        else:
                            row.label(text=item.object_name, icon='CANCEL')
                        
                        # Message (truncated)
                        msg = item.message[:40] + "..." if len(item.message) > 40 else item.message
                        row.label(text=msg)
                
                # Then warnings
                if warnings:
                    for item in warnings:
                        row = cat_box.row()
                        
                        # Clickable object name
                        if item.object_name in context.scene.objects:
                            op = row.operator("apex.select_object", text=item.object_name, emboss=False, icon='ERROR')
                            op.object_name = item.object_name
                        else:
                            row.label(text=item.object_name, icon='ERROR')
                        
                        # Message (truncated)
                        msg = item.message[:40] + "..." if len(item.message) > 40 else item.message
                        row.label(text=msg)