import bpy
import typing
import os

# ------------------------------------------------------------------------
#   Logic: Material Validation
# ------------------------------------------------------------------------

class MaterialValidator:
    """
    Static analyzer for Material Node Trees.
    Validates PBR compliance for Cycles/Eevee in Blender 5.0.
    """
    
    @staticmethod
    def is_material_broken(mat: bpy.types.Material) -> typing.Tuple[bool, str, str]:
        """Checks if a material is missing nodes, links, or output. Returns (is_broken, message, severity)."""
        if not mat:
            return False, "", ""  # Empty slot handled elsewhere
        
        # Validate material still exists in blend data
        if mat.name not in bpy.data.materials:
            return True, "Material has been deleted.", "ERROR"
            
        if not mat.use_nodes:
            return True, "Material does not use Nodes (Legacy).", "ERROR"
        
        tree = mat.node_tree
        if not tree or not hasattr(tree, 'nodes'):
            return True, "Node tree is None or invalid.", "ERROR"
            
        # Check for Output Node
        try:
            output_node = next((n for n in tree.nodes if n.type == 'OUTPUT_MATERIAL'), None)
        except (RuntimeError, ReferenceError):
            return True, "Cannot access node tree (may be deleted).", "ERROR"
            
        if not output_node:
            return True, "Missing Material Output node.", "ERROR"
            
        # Check if Output is connected
        if 'Surface' in output_node.inputs and not output_node.inputs['Surface'].is_linked:
            return True, "Material Output surface is disconnected.", "WARNING"

        return False, "", ""

    @staticmethod
    def fix_material(mat: bpy.types.Material):
        """Resets the material to a clean Principled BSDF setup."""
        mat.use_nodes = True
        tree = mat.node_tree
        tree.nodes.clear()
        
        output = tree.nodes.new('ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        principled = tree.nodes.new('ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)
        
        tree.links.new(principled.outputs[0], output.inputs[0])
    
    @staticmethod
    def get_or_create_broken_marker_material() -> bpy.types.Material:
        """Creates or returns the _BROKEN TO FIX marker material (red, self-illuminating)."""
        marker_name = "_BROKEN TO FIX"
        
        # Check if material already exists
        if marker_name in bpy.data.materials:
            return bpy.data.materials[marker_name]
        
        # Create new marker material
        mat = bpy.data.materials.new(name=marker_name)
        mat.use_nodes = True
        tree = mat.node_tree
        tree.nodes.clear()
        
        # Create output node
        output = tree.nodes.new('ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        # Create emission shader (self-illuminating red)
        emission = tree.nodes.new('ShaderNodeEmission')
        emission.location = (0, 0)
        emission.inputs['Color'].default_value = (1.0, 0.0, 0.0, 1.0)  # Bright red
        emission.inputs['Strength'].default_value = 2.0  # Strong emission for visibility
        
        # Connect emission to output
        tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        return mat
    
    @staticmethod
    def mark_broken_material(obj: bpy.types.Object, slot_index: int) -> bool:
        """Replaces broken material with _BROKEN TO FIX marker. Returns True if replaced."""
        if not obj or not hasattr(obj, 'material_slots'):
            return False
        
        if slot_index < 0 or slot_index >= len(obj.material_slots):
            return False
        
        try:
            marker_mat = MaterialValidator.get_or_create_broken_marker_material()
            obj.material_slots[slot_index].material = marker_mat
            return True
        except (RuntimeError, ReferenceError, IndexError):
            return False
    
    @staticmethod
    def fix_empty_slots(obj: bpy.types.Object) -> int:
        """Removes empty material slots. Returns count of deleted slots."""
        if not obj or not hasattr(obj, 'material_slots') or not obj.material_slots:
            return 0
        
        if not hasattr(obj, 'data') or not obj.data or not hasattr(obj.data, 'materials'):
            return 0
        
        try:
            # Count empty slots before removal
            fixed_count = sum(1 for slot in obj.material_slots if not slot.material)
            
            if fixed_count == 0:
                return 0
            
            # Rebuild materials list without empty slots
            valid_materials = [slot.material for slot in obj.material_slots if slot.material]
            
            # Clear all materials
            obj.data.materials.clear()
            
            # Re-add only valid materials
            for mat in valid_materials:
                if mat and mat.name in bpy.data.materials:
                    obj.data.materials.append(mat)
            
            return fixed_count
        except (RuntimeError, ReferenceError, AttributeError) as e:
            print(f"Warning: Failed to fix empty slots for {obj.name}: {e}")
            return 0
    
    @staticmethod
    def fix_disconnected_output(mat: bpy.types.Material) -> bool:
        """Connects Material Output to a Principled BSDF if disconnected. Returns True if fixed."""
        if not mat or not mat.use_nodes:
            return False
        
        tree = mat.node_tree
        output_node = next((n for n in tree.nodes if n.type == 'OUTPUT_MATERIAL'), None)
        
        if output_node and not output_node.inputs['Surface'].is_linked:
            # Try to find existing Principled BSDF
            principled = next((n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            
            if not principled:
                # Create new Principled BSDF
                principled = tree.nodes.new('ShaderNodeBsdfPrincipled')
                principled.location = (output_node.location[0] - 300, output_node.location[1])
            
            tree.links.new(principled.outputs[0], output_node.inputs['Surface'])
            return True
        
        return False
    
    @staticmethod
    def replace_deprecated_nodes(mat: bpy.types.Material) -> int:
        """Replaces deprecated shader nodes with Principled BSDF. Returns count of replaced nodes."""
        if not mat or not mat.use_nodes:
            return 0
        
        tree = mat.node_tree
        deprecated_map = {
            'BSDF_DIFFUSE': 'diffuse',
            'BSDF_GLOSSY': 'specular',
            'EMISSION': 'emission',
        }
        
        replaced_count = 0
        
        for node in list(tree.nodes):  # Use list() to avoid modification during iteration
            if node.type in deprecated_map:
                # Get node position and connected outputs
                node_loc = node.location
                output_links = [(link.to_socket, link.to_node) for link in node.outputs[0].links]
                
                # Create Principled BSDF replacement
                principled = tree.nodes.new('ShaderNodeBsdfPrincipled')
                principled.location = node_loc
                
                # Reconnect outputs
                for to_socket, to_node in output_links:
                    tree.links.new(principled.outputs[0], to_socket)
                
                # Remove old node
                tree.nodes.remove(node)
                replaced_count += 1
        
        return replaced_count

    @staticmethod
    def validate_textures(mat: bpy.types.Material) -> typing.List[typing.Tuple[str, str]]:
        """Check for missing or broken texture nodes. Returns list of (message, severity)."""
        issues = []
        
        if not mat or not mat.use_nodes or not mat.node_tree:
            return issues
        
        try:
            nodes = list(mat.node_tree.nodes)  # Create copy to avoid iteration issues
        except (RuntimeError, ReferenceError):
            return issues  # Node tree deleted or invalid
        
        for node in nodes:
            # Check Image Texture nodes
            if node.type == 'TEX_IMAGE':
                try:
                    if not node.image or node.image.name not in bpy.data.images:
                        issues.append(("Image Texture node has no image assigned.", "WARNING"))
                        continue
                except (RuntimeError, ReferenceError, AttributeError):
                    issues.append(("Image Texture node references deleted image.", "ERROR"))
                    continue
                
                try:
                    if node.image.source == 'FILE':
                        # Skip packed images - they're stored in the blend file
                        if node.image.packed_file:
                            continue
                        
                        # Check if file exists
                        if not node.image.filepath:
                            issues.append((f"Image '{node.image.name}' has no filepath.", "ERROR"))
                        else:
                            filepath = bpy.path.abspath(node.image.filepath)
                            if not os.path.exists(filepath):
                                issues.append((f"Missing texture file: {node.image.name} ({node.image.filepath})", "ERROR"))
                            elif node.image.has_data is False:
                                issues.append((f"Image '{node.image.name}' failed to load.", "ERROR"))
                            else:
                                # Check texture size (large textures can cause issues)
                                try:
                                    width, height = node.image.size[:]
                                except (RuntimeError, IndexError, AttributeError):
                                    continue  # Image size unavailable
                                
                                if width > 0 and height > 0:
                                    # Warn about very large textures
                                    if width > 8192 or height > 8192:
                                        issues.append((f"Very large texture: {node.image.name} ({width}x{height})", "WARNING"))
                                    
                                    # Warn about non-power-of-2 textures
                                    def is_power_of_2(n):
                                        return n > 0 and (n & (n - 1)) == 0
                                    
                                    if not is_power_of_2(width) or not is_power_of_2(height):
                                        issues.append((f"Non-power-of-2 texture: {node.image.name} ({width}x{height})", "WARNING"))
                except (RuntimeError, ReferenceError, AttributeError) as e:
                    issues.append((f"Error checking image texture: {str(e)}", "WARNING"))
                except (RuntimeError, ReferenceError, AttributeError) as e:
                    issues.append((f"Error checking image texture: {str(e)}", "WARNING"))
            
            # Check Environment Texture nodes
            elif node.type == 'TEX_ENVIRONMENT':
                if not node.image:
                    issues.append(("Environment Texture node has no image assigned.", "WARNING"))
                elif node.image.source == 'FILE':
                    # Skip packed images
                    if node.image.packed_file:
                        continue
                    
                    filepath = bpy.path.abspath(node.image.filepath)
                    if not os.path.exists(filepath):
                        issues.append((f"Missing environment texture: {node.image.name}", "ERROR"))
        
        return issues
    
    @staticmethod
    def check_shader_compatibility(mat: bpy.types.Material) -> typing.List[typing.Tuple[str, str]]:
        """Check for shader nodes that may cause compatibility issues."""
        issues = []
        
        if not mat or not mat.use_nodes:
            return issues
        
        cycles_only_nodes = {
            'BSDF_HAIR', 'BSDF_HAIR_PRINCIPLED', 'SUBSURFACE_SCATTERING',
            'BSDF_ANISOTROPIC', 'BSDF_SHEEN', 'BSDF_TOON'
        }
        
        deprecated_nodes = {
            'BSDF_DIFFUSE': 'Use Principled BSDF instead',
            'BSDF_GLOSSY': 'Use Principled BSDF instead',
            'EMISSION': 'Use Principled BSDF emission',
        }
        
        for node in mat.node_tree.nodes:
            # Check for Cycles-only nodes
            if node.type in cycles_only_nodes:
                issues.append((f"Node '{node.name}' ({node.type}) is Cycles-only, may not render in Eevee.", "WARNING"))
            
            # Check for deprecated nodes
            if node.type in deprecated_nodes:
                reason = deprecated_nodes[node.type]
                issues.append((f"Deprecated node '{node.name}' ({node.type}). {reason}", "WARNING"))
        
        return issues
    
    @staticmethod
    def pack_external_textures(mat: bpy.types.Material) -> int:
        """Packs external texture files into the .blend file. Returns count of textures packed."""
        if not mat or not mat.use_nodes:
            return 0
        
        packed_count = 0
        
        for node in mat.node_tree.nodes:
            # Check Image Texture nodes
            if node.type == 'TEX_IMAGE' and node.image:
                img = node.image
                
                # Only pack images from file source that aren't already packed
                if img.source == 'FILE' and not img.packed_file:
                    # Check if file path exists
                    if img.filepath:
                        filepath = bpy.path.abspath(img.filepath)
                        if os.path.exists(filepath):
                            try:
                                img.pack()
                                packed_count += 1
                            except Exception as e:
                                print(f"Warning: Failed to pack texture {img.name}: {e}")
            
            # Check Environment Texture nodes
            elif node.type == 'TEX_ENVIRONMENT' and node.image:
                img = node.image
                
                if img.source == 'FILE' and not img.packed_file:
                    if img.filepath:
                        filepath = bpy.path.abspath(img.filepath)
                        if os.path.exists(filepath):
                            try:
                                img.pack()
                                packed_count += 1
                            except Exception as e:
                                print(f"Warning: Failed to pack texture {img.name}: {e}")
        
        return packed_count
