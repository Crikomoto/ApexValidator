import bpy
import typing

# ------------------------------------------------------------------------
#   Logic: Geometry Validation
# ------------------------------------------------------------------------

class GeometryValidator:
    """Validates mesh geometry for production/pipeline issues."""
    
    @staticmethod
    def validate_geometry(obj: bpy.types.Object) -> typing.List[typing.Tuple[str, str, str]]:
        """Check geometry issues. Returns list of (issue_type, message, severity)."""
        issues = []
        
        if not obj or obj.type != 'MESH':
            return issues
        
        if not hasattr(obj, 'data') or not obj.data:
            issues.append(("GEOMETRY", "Mesh object has no data.", "ERROR"))
            return issues
        
        mesh = obj.data
        
        # Check for zero-face mesh
        if len(mesh.polygons) == 0 and len(mesh.vertices) > 0:
            issues.append(("GEOMETRY", 
                          f"Mesh has {len(mesh.vertices)} vertices but no faces", 
                          "WARNING"))
        
        # Check for loose vertices
        if len(mesh.edges) == 0 and len(mesh.vertices) > 0:
            issues.append(("GEOMETRY", 
                          f"Mesh has {len(mesh.vertices)} loose vertices (no edges)", 
                          "WARNING"))
        
        # NOTE: N-gons are NOT checked - they're normal for CAD data and don't cause issues
        
        # Check for missing UVs
        if len(mesh.uv_layers) == 0 and len(mesh.polygons) > 0:
            issues.append(("GEOMETRY", 
                          f"Mesh has no UV maps", 
                          "ERROR"))
        
        # Check poly count (high-poly warning)
        poly_count = len(mesh.polygons)
        if poly_count > 100000:
            issues.append(("GEOMETRY", 
                          f"Very high poly count: {poly_count:,} faces (may cause performance issues)", 
                          "WARNING"))
        elif poly_count > 50000:
            issues.append(("GEOMETRY", 
                          f"High poly count: {poly_count:,} faces", 
                          "WARNING"))
        
        return issues
    
    @staticmethod
    def fix_missing_uvs(obj: bpy.types.Object) -> bool:
        """Generates UV map for meshes that have none. Returns True if UV created."""
        if not obj or obj.type != 'MESH':
            return False
        
        if not hasattr(obj, 'data') or not obj.data:
            return False
        
        mesh = obj.data
        
        # Check if mesh has UV layers and polygons attributes
        if not hasattr(mesh, 'uv_layers') or not hasattr(mesh, 'polygons'):
            return False
        
        # Check if mesh has no UV maps and has faces
        if len(mesh.uv_layers) == 0 and len(mesh.polygons) > 0:
            view_layer = bpy.context.view_layer
            
            # Skip if object is not in current view layer
            if obj.name not in view_layer.objects:
                return False
            
            # Ensure object is in OBJECT mode
            if view_layer.objects.active and view_layer.objects.active.mode != 'OBJECT':
                try:
                    bpy.ops.object.mode_set(mode='OBJECT')
                except:
                    pass
            
            try:
                # Create UV map using Smart UV Project (conservative settings)
                with bpy.context.temp_override(
                    view_layer=view_layer,
                    selected_objects=[obj],
                    active_object=obj,
                    object=obj
                ):
                    # Add UV map first
                    mesh.uv_layers.new(name="UVMap")
                    
                    # Switch to edit mode and unwrap
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                    return True
            except Exception as e:
                print(f"Warning: Failed to generate UVs for {obj.name}: {e}")
                return False
        
        return False
