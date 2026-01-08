import bpy
import typing

# ------------------------------------------------------------------------
#   Logic: Driver Validation
# ------------------------------------------------------------------------

class DriverValidator:
    """Validates animation drivers for errors and circular dependencies."""
    
    @staticmethod
    def detect_driver_chain(obj: bpy.types.Object, visited=None, chain=None) -> typing.Optional[typing.List[str]]:
        """Recursively detect driver dependency chains. Returns chain if loop found."""
        # Validate object exists
        if not obj or not hasattr(obj, 'name') or obj.name not in bpy.data.objects:
            return None
        
        if visited is None:
            visited = set()
            chain = []
        
        obj_id = id(obj)
        
        if obj_id in visited:
            # Found a loop
            try:
                loop_start = chain.index(obj.name)
                return chain[loop_start:] + [obj.name]
            except ValueError:
                return None
        
        visited.add(obj_id)
        chain.append(obj.name)
        
        # Check all drivers on this object
        if obj.animation_data and obj.animation_data.drivers:
            for fcurve in obj.animation_data.drivers:
                driver = fcurve.driver
                
                # Check all variables in this driver
                for var in driver.variables:
                    for target in var.targets:
                        if target.id and target.id != obj and hasattr(target.id, 'animation_data'):
                            # Recursively check the target
                            result = DriverValidator.detect_driver_chain(target.id, visited.copy(), chain[:])
                            if result:
                                return result
        
        return None
    
    @staticmethod
    def validate_drivers(obj: bpy.types.Object) -> typing.List[typing.Tuple[str, str, str]]:
        """Check object drivers. Returns list of (issue_type, message, severity)."""
        issues = []
        
        # Validate object still exists
        if not obj or obj.name not in bpy.data.objects:
            return issues
        
        if not obj.animation_data or not hasattr(obj.animation_data, 'drivers'):
            return issues
        
        # Check for driver chains (multi-object circular dependencies)
        driver_chain = DriverValidator.detect_driver_chain(obj)
        if driver_chain:
            chain_str = " → ".join(driver_chain)
            issues.append(("DRIVER_CHAIN", 
                          f"Driver chain loop detected: {chain_str}", 
                          "ERROR"))
        
        # Check drivers
        if obj.animation_data.drivers:
            for fcurve in obj.animation_data.drivers:
                driver = fcurve.driver
                
                # Check if driver is valid
                if not driver.is_valid:
                    issues.append(("INVALID_DRIVER", 
                                  f"Invalid driver on property '{fcurve.data_path}'", 
                                  "ERROR"))
                    continue
                
                # Check for circular dependencies (self-referencing)
                for var in driver.variables:
                    for target in var.targets:
                        if target.id == obj:
                            issues.append(("CIRCULAR_DRIVER", 
                                          f"Circular dependency: Driver on '{fcurve.data_path}' references itself", 
                                          "ERROR"))
                        elif target.id is None:
                            issues.append(("MISSING_DRIVER_TARGET", 
                                          f"Driver on '{fcurve.data_path}' has missing target in variable '{var.name}'", 
                                          "ERROR"))
                
                # Validate scripted expressions
                if driver.type == 'SCRIPTED':
                    if not driver.expression or driver.expression.strip() == "":
                        issues.append(("INVALID_DRIVER", 
                                      f"Empty scripted expression on '{fcurve.data_path}'", 
                                      "ERROR"))
        
        return issues
    
    @staticmethod
    def fix_invalid_drivers(obj: bpy.types.Object) -> int:
        """Removes invalid or circular drivers. Returns count of removed drivers."""
        if not obj.animation_data or not obj.animation_data.drivers:
            return 0
        
        removed_count = 0
        fcurves_to_remove = []
        
        for fcurve in obj.animation_data.drivers:
            driver = fcurve.driver
            should_remove = False
            
            # Remove invalid drivers
            if not driver.is_valid:
                should_remove = True
            
            # Remove scripted drivers with empty expressions
            elif driver.type == 'SCRIPTED' and (not driver.expression or driver.expression.strip() == ""):
                should_remove = True
                print(f"Removing empty scripted driver on {obj.name}.{fcurve.data_path}")
            
            else:
                # Remove circular dependencies and missing targets
                for var in driver.variables:
                    for target in var.targets:
                        if target.id == obj or target.id is None:
                            should_remove = True
                            break
                    if should_remove:
                        break
            
            if should_remove:
                fcurves_to_remove.append(fcurve)
        
        # Remove the problematic drivers
        for fcurve in fcurves_to_remove:
            obj.animation_data.drivers.remove(fcurve)
            removed_count += 1
        
        return removed_count
    
    @staticmethod
    def fix_driver_chains(obj: bpy.types.Object) -> bool:
        """Breaks driver chain loops by removing drivers that cause loops. Returns True if fixed."""
        driver_chain = DriverValidator.detect_driver_chain(obj)
        
        if not driver_chain or not obj.animation_data:
            return False
        
        # Strategy: Remove drivers on THIS object that reference objects in the chain
        # This breaks the loop at this point
        removed_count = 0
        fcurves_to_remove = []
        
        if obj.animation_data.drivers:
            for fcurve in obj.animation_data.drivers:
                driver = fcurve.driver
                
                # Check if this driver references any object in the detected chain
                for var in driver.variables:
                    for target in var.targets:
                        if target.id and hasattr(target.id, 'name'):
                            if target.id.name in driver_chain:
                                fcurves_to_remove.append(fcurve)
                                print(f"Breaking driver chain by removing driver on {obj.name}.{fcurve.data_path}")
                                break
        
        # Remove drivers that create the chain
        for fcurve in fcurves_to_remove:
            obj.animation_data.drivers.remove(fcurve)
            removed_count += 1
        
        return removed_count > 0
