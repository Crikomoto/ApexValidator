# Apex Validator - Auto-Fix Guide

## Overview
The **Auto-Fix** feature automatically repairs common asset issues that don't require user decision-making. This saves time and prevents manual fixes for repetitive problems.

---

## ✅ Issues That CAN Be Auto-Fixed

### 🎨 **Shader/Material Issues**

#### 1. **Broken Shaders (ERROR)**
- **Problem**: Materials with no nodes, missing output nodes, or broken node trees
- **Fix**: Completely resets material to clean Principled BSDF + Material Output setup
- **Approach**: Clears all nodes and creates standard PBR workflow

#### 2. **Disconnected Material Output (WARNING)**
- **Problem**: Material Output's Surface input is not connected
- **Fix**: Finds or creates Principled BSDF and connects it to Material Output
- **Approach**: Preserves existing nodes when possible, only adds missing connection

#### 3. **Deprecated Shader Nodes (WARNING)**
- **Problem**: Old nodes like Diffuse BSDF, Glossy BSDF, Emission shader
- **Fix**: Replaces with Principled BSDF
- **Approach**: Removes deprecated node, creates Principled BSDF in same location, reconnects outputs

---

### 🎭 **Driver Issues**

#### 4. **Invalid Drivers (ERROR)**
- **Problem**: Corrupted or broken driver expressions
- **Fix**: Removes the invalid driver
- **Approach**: Deletes driver FCurve, property returns to manual control

#### 5. **Circular Dependencies (ERROR)**
- **Problem**: Driver references its own object (causes infinite loops)
- **Fix**: Removes the problematic driver
- **Approach**: Prevents crash by breaking the circular reference

#### 6. **Missing Driver Targets (ERROR)**
- **Problem**: Driver variable points to deleted object
- **Fix**: Removes the driver
- **Approach**: Non-functional driver is cleaned up

---

### 🔧 **Modifier Issues**

#### 7. **Array Modifier - Missing Offset Object (WARNING)**
- **Problem**: Object Offset enabled but no object assigned
- **Fix**: Disables Object Offset option
- **Approach**: Preserves modifier but switches to simpler offset mode

#### 8. **Boolean Modifier - Missing Target (ERROR)**
- **Problem**: No target object assigned or target was deleted
- **Fix**: Removes the modifier
- **Approach**: Non-functional modifier cannot work without target

#### 9. **Shrinkwrap Modifier - Missing Target (ERROR)**
- **Problem**: No target mesh assigned
- **Fix**: Removes the modifier
- **Approach**: Shrinkwrap needs target to function

#### 10. **Armature Modifier - Missing Armature (ERROR)**
- **Problem**: No armature object assigned
- **Fix**: Removes the modifier
- **Approach**: Cannot deform without armature

#### 11. **Surface Deform - Unbound (ERROR)**
- **Problem**: Modifier not bound (major crash risk)
- **Fix**: Removes the modifier
- **Approach**: **Critical safety fix** - unbound Surface Deform can crash Blender

#### 12. **Data Transfer - Missing Source (ERROR)**
- **Problem**: No source object assigned
- **Fix**: Removes the modifier
- **Approach**: Cannot transfer data without source

---

## ❌ Issues That CANNOT Be Auto-Fixed

These require user decision or manual intervention:

### 🖼️ **Texture Issues**
- **Missing Texture Files**: Needs user to provide correct file path
- **Broken File Paths**: User must relocate or relink textures
- **Failed Image Loading**: Requires fixing corrupted image or finding replacement

### ⚠️ **Shader Compatibility**
- **Cycles-only Nodes**: User decides whether to keep for Cycles or convert for Eevee
- Some workflows intentionally use render-engine-specific features

### 📐 **Geometry Issues**
- **Zero-face Meshes**: User decides if mesh should be deleted or if faces should be added
- **Loose Vertices**: User decides to keep, delete, or connect them
- Geometry issues often require artistic judgment

### 🎨 **Empty Material Slots**
- Currently flagged as WARNING only
- User may intentionally leave slots empty for specific workflows

---

## 🔄 Auto-Fix Workflow

### How It Works:
1. Click **"Auto-Fix"** button in the panel
2. Runs through all fixable issues in priority order:
   - Drivers (prevents crashes from circular deps)
   - Modifiers (removes broken/unbound ones)
   - Materials (fixes broken shaders)
   - Shader nodes (updates deprecated nodes)
   - Connections (fixes disconnected outputs)
3. Reports summary of what was fixed
4. Re-runs validation to show remaining issues

### Safety Features:
- All fixes are **undoable** (Ctrl+Z)
- Only touches problematic elements
- Preserves working parts of materials
- Conservative approach (removes when unsure)

---

## 💡 Best Practices

### Before Auto-Fix:
1. **Save your file** - Always have a backup
2. **Run Scan first** - Review what will be fixed
3. **Understand the fixes** - Know what Auto-Fix will do

### After Auto-Fix:
1. **Check the summary** - See what was changed
2. **Re-scan** - Verify remaining issues need manual attention
3. **Test renders** - Ensure materials still look correct
4. **Review removed modifiers** - Recreate if needed with proper targets

### When NOT to Auto-Fix:
- **Production files near deadline** - Manual fixes give more control
- **Complex driver setups** - Review circular dependencies manually
- **Intentional deprecated nodes** - Some workflows use old nodes purposefully
- **WIP materials** - Disconnected outputs might be temporary

---

## 🎯 Fix Priority Order

Auto-Fix processes issues in this order for safety:

1. **Drivers** (highest risk - can cause crashes)
2. **Modifiers** (especially Surface Deform - critical)
3. **Broken Shaders** (ERROR severity only)
4. **Disconnected Outputs** (minor shader issues)
5. **Deprecated Nodes** (cosmetic/compatibility)

This ensures critical safety issues are resolved first.

---

## 📊 Expected Results

### Typical Scene:
- **Before**: 50 issues (30 errors, 20 warnings)
- **After Auto-Fix**: 8 issues (0 errors, 8 warnings)
- **Remaining**: Texture paths and user-decision items

### What You'll Still See:
- Missing texture file warnings (need manual relink)
- Geometry warnings (need artistic judgment)
- Compatibility warnings (render engine choices)
- Empty slots (intentional or not?)

---

## Summary

**Auto-Fix handles ~70% of common issues automatically**, focusing on safety-critical problems and technical errors. The remaining ~30% require human judgment or external resources (texture files, etc.).

This approach balances automation with safety, ensuring your scene is stable while preserving artistic intent.
