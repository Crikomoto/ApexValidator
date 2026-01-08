import bpy

# PropertyGroup for exclusion patterns and filters
class APEX_ExclusionPatterns(bpy.types.PropertyGroup):
    """Settings for object exclusions and result filtering."""
    patterns: bpy.props.StringProperty(
        name="Ignore by Name Prefix",
        description="Comma-separated name prefixes to skip (e.g., 'WGT-,TEMP-')",
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
        description="Show geometry issues (missing UVs, poly count)",
        default=True
    )
    filter_transforms: bpy.props.BoolProperty(
        name="Transforms",
        description="Show transform issues (unapplied scales, rotations)",
        default=True
    )
    filter_modifiers: bpy.props.BoolProperty(
        name="Tools & Effects",
        description="Show modifier issues (tools that change object shape/behavior)",
        default=True
    )
    filter_drivers: bpy.props.BoolProperty(
        name="Animations",
        description="Show animation driver issues (automated property changes)",
        default=True
    )
    filter_data: bpy.props.BoolProperty(
        name="Mesh Data",
        description="Show mesh data issues",
        default=True
    )
    filter_rigging: bpy.props.BoolProperty(
        name="Bones & Weights",
        description="Show rigging issues (armature, vertex groups, skinning)",
        default=True
    )
    filter_circular: bpy.props.BoolProperty(
        name="Dependency Loops",
        description="Show circular dependency errors (infinite reference loops)",
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
            
            # Object name (clickable to select) - compact
            obj_col = row.column()
            obj_col.scale_x = 0.5
            if item.object_name in context.scene.objects:
                op = obj_col.operator("apex.select_object", text=item.object_name, emboss=False)
                op.object_name = item.object_name
            else:
                obj_col.label(text=item.object_name)
            
            # Material name (if applicable) - very compact
            if item.material_name != "N/A":
                mat_col = row.column()
                mat_col.scale_x = 0.4
                mat_col.label(text=item.material_name, icon='MATERIAL')
            
            # Issue type badge - tiny
            type_col = row.column()
            type_col.scale_x = 0.25
            type_col.label(text=f"{item.issue_type}")
            
            # Message - use split layout to force it to take remaining space without truncation
            split = row.split(factor=0.9, align=True)
            split.label(text=item.message)
            
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
        
        # Section: Ignore Objects - Moved to top for easy access
        box_exclusions = layout.box()
        header = box_exclusions.row()
        header.label(text="Ignore Objects", icon='FILTER')
        header.label(text="", icon='QUESTION')  # Tooltip indicator
        row = box_exclusions.row()
        row.prop(context.scene.apex_exclusions, "patterns", text="")
        info_row = box_exclusions.row()
        info_row.label(text="Skip objects with these name prefixes (e.g., 'WGT-,TEMP-')", icon='INFO')
        info_row.scale_y = 0.7
        
        layout.separator()
        
        # Check & Fix - Most common workflow
        box_quick = layout.box()
        quick_header = box_quick.row()
        quick_header.label(text="Check & Fix", icon='TOOL_SETTINGS')
        
        # Single row with scope selector and main buttons
        row = box_quick.row(align=True)
        row.label(text="Check:")
        scope_prop = row.row()
        scope_prop.prop(context.scene, "apex_quick_scope", text="", icon='NONE')
        scope_prop.label(text="", icon='BLANK1')  # Spacing
        
        # Main action buttons with tooltips
        row = box_quick.row(align=True)
        row.scale_y = 1.5
        
        scan_row = row.row()
        op_scan = scan_row.operator("apex.validate", text="Find Problems", icon='VIEWZOOM')
        op_scan.scope = context.scene.apex_quick_scope
        
        fix_row = row.row()
        op_autofix = fix_row.operator("apex.auto_fix", text="Fix Automatically", icon='SHADERFX')
        op_autofix.scope = context.scene.apex_quick_scope
        
        # Help text
        help_row = box_quick.row()
        help_row.scale_y = 0.6
        help_row.label(text="Find all issues, then fix them automatically where possible", icon='INFO')
        
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

        # Section: Result Filters
        if len(context.scene.apex_validation_results) > 0:
            layout.separator()
            box_filters = layout.box()
            filter_header = box_filters.row()
            filter_header.label(text="Filter Results", icon='FILTER')
            
            # Show All toggle with tooltip
            toggle_row = filter_header.row()
            toggle_row.prop(context.scene.apex_exclusions, "filter_show_all", text="Show All", toggle=True)
            
            # Help text for filters
            help_row = box_filters.row()
            help_row.scale_y = 0.6
            help_row.label(text="Toggle 'Show All' off to filter specific issue types", icon='INFO')
            
            # Individual filter checkboxes (disabled when Show All is active)
            if not context.scene.apex_exclusions.filter_show_all:
                grid = box_filters.grid_flow(row_major=True, columns=2, align=True)
                grid.prop(context.scene.apex_exclusions, "filter_materials", text="Materials", icon='MATERIAL')
                grid.prop(context.scene.apex_exclusions, "filter_geometry", text="Geometry", icon='MESH_DATA')
                grid.prop(context.scene.apex_exclusions, "filter_transforms", text="Transforms", icon='ORIENTATION_GLOBAL')
                grid.prop(context.scene.apex_exclusions, "filter_modifiers", text="Tools/Effects", icon='MODIFIER')
                grid.prop(context.scene.apex_exclusions, "filter_drivers", text="Animations", icon='DRIVER')
                grid.prop(context.scene.apex_exclusions, "filter_rigging", text="Bones/Weights", icon='ARMATURE_DATA')
                grid.prop(context.scene.apex_exclusions, "filter_circular", text="Loops", icon='CON_TRACKTO')
                grid.prop(context.scene.apex_exclusions, "filter_data", text="Mesh Data", icon='OUTLINER_DATA_MESH')

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
            summary_box.operator("apex.clear_results", text="Clear Results", icon='X')
            
            # Add help text
            help_row = summary_box.row()
            help_row.scale_y = 0.6
            help_row.label(text="Click objects to select/isolate | Red=Error, Yellow=Warning", icon='INFO')
            
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