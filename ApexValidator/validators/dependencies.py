import bpy
import typing

# ------------------------------------------------------------------------
#   Logic: Circular Dependency Detection
# ------------------------------------------------------------------------

class CircularDependencyValidator:
    """Detects and fixes circular dependency errors."""
    
    @staticmethod
    def detect_parent_loops(obj: bpy.types.Object, visited=None, chain=None) -> typing.Optional[typing.List[str]]:
        """Recursively detect parent loops. Returns chain of object names if loop found."""
        # Validate object exists
        if not obj or not hasattr(obj, 'name') or obj.name not in bpy.data.objects:
            return None
        
        if visited is None:
            visited = set()
            chain = []
        
        if obj.name in visited:
            # Found a loop - return the chain
            loop_start = chain.index(obj.name)
            return chain[loop_start:] + [obj.name]
        
        visited.add(obj.name)
        chain.append(obj.name)
        
        # Check parent
        if obj.parent:
            result = CircularDependencyValidator.detect_parent_loops(obj.parent, visited, chain[:])
            if result:
                return result
        
        return None
    
    @staticmethod
    def validate_dependencies(obj: bpy.types.Object) -> typing.List[typing.Tuple[str, str, str]]:
        """Check for circular dependencies. Returns list of (issue_type, message, severity)."""
        issues = []
        
        # Check parent loops
        parent_loop = CircularDependencyValidator.detect_parent_loops(obj)
        if parent_loop:
            loop_str = " → ".join(parent_loop)
            issues.append(("CIRCULAR_DEPENDENCY", 
                          f"Parent loop detected: {loop_str}", 
                          "ERROR"))
        
        # Check constraint loops
        if obj.constraints:
            for constraint in obj.constraints:
                target = None
                
                # Get constraint target based on type
                if hasattr(constraint, 'target') and constraint.target:
                    target = constraint.target
                
                if target:
                    # Check if target has constraint pointing back to this object
                    for target_constraint in target.constraints:
                        if hasattr(target_constraint, 'target') and target_constraint.target == obj:
                            issues.append(("CIRCULAR_DEPENDENCY", 
                                          f"Constraint loop: '{obj.name}' ↔ '{target.name}'", 
                                          "ERROR"))
        
        return issues
    
    @staticmethod
    def fix_parent_loop(obj: bpy.types.Object) -> bool:
        """Breaks parent loop by clearing object's parent. Returns True if fixed."""
        parent_loop = CircularDependencyValidator.detect_parent_loops(obj)
        if parent_loop:
            # Clear parent (safest option)
            obj.parent = None
            print(f"Broke parent loop for {obj.name}")
            return True
        return False
