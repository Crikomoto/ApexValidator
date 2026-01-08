# 🛡️ Apex Validator

**Scene and Asset Validation for Blender 5.0+ Production Pipelines**

A comprehensive validation and auto-fix tool designed for production pipelines, especially optimized for CAD data import and animation workflows. Built for studios, freelancers, and artists who need clean, production-ready assets with minimal manual fixing.

---

## ✨ Features

### 🔍 **Comprehensive Validation**
Apex Validator scans your scene or collections for critical production issues:

- **🎨 Material Problems**: Broken shaders, missing nodes, disconnected outputs, texture issues
- **📐 Geometry Issues**: Missing UVs, loose vertices, high poly count warnings
- **📏 Transform Issues**: Unapplied scales, non-uniform scales, unapplied rotations
- **🔧 Tools & Effects**: Missing modifier targets, broken boolean/array/shrinkwrap setups
- **🚗 Animation Drivers**: Invalid expressions, circular dependencies, missing targets
- **📦 Mesh Data**: Shape key issues with missing vertex groups
- **🦴 Bones & Weights**: Empty vertex groups, orphaned groups, rigging setup issues
- **♻️ Dependency Loops**: Parent loops, constraint loops, modifier circular dependencies
- **🎯 Shader Compatibility**: Cycles/Eevee compatibility warnings

**CAD-Friendly**: Ignores common CAD data characteristics like N-gons, default mesh names, and mesh instancing that don't affect rendering or animation.

### ⚡ **Smart Auto-Fix**
Automatically repairs issues without manual intervention:

- ✅ **Broken Shaders**: Replaced with red self-illuminating "_BROKEN TO FIX" material for visual feedback
- ✅ **Disconnected Outputs**: Connects Material Output nodes to Principled BSDF
- ✅ **Deprecated Nodes**: Replaces old shader nodes (Diffuse BSDF, Glossy BSDF, etc.)
- ✅ **Invalid Drivers**: Removes broken animation drivers and circular dependencies
- ✅ **Broken Modifiers**: Cleans up missing targets, unbound Surface Deform
- ✅ **Transform Issues**: Applies unapplied scales and rotations
- ✅ **Empty Vertex Groups**: Removes empty and orphaned vertex groups
- ✅ **Missing UVs**: Generates smart UV projection for meshes without UVs

**Intelligent Processing**: Uses batched operations with memory management to handle large scenes (1000+ objects) safely.

See [AUTO_FIX_GUIDE.md](ApexValidator/AUTO_FIX_GUIDE.md) for detailed information on what can be auto-fixed.

### 🎯 **Flexible Scope**
- **Scene Mode**: Validate entire scene
- **Collection Mode**: Validate active collection only
- **Ignore Objects**: Skip objects by name prefix (e.g., `WGT-`, `TEMP-`)

### 📊 **Smart Filtering**
Filter validation results by category:
- Materials
- Geometry
- Transforms
- Tools/Effects (Modifiers)
- Animations (Drivers)
- Mesh Data
- Bones/Weights (Rigging)
- Dependency Loops

### 🎨 **User-Friendly Interface**
- **Clear Language**: Easy to understand for all skill levels
- **Color-Coded Severity**: Red for errors, yellow for warnings
- **One-Click Selection**: Click any object to select and isolate in viewport
- **Full Error Messages**: Complete descriptions visible in results list
- **Progress Tracking**: Real-time progress bar and fix counters during auto-fix
- **Help Tooltips**: Info text explaining each feature

---

## 📦 Installation

### Quick Install
1. Download the latest release or clone this repository
2. In Blender, go to `Edit → Preferences → Add-ons`
3. Click `Install...` and select the `ApexValidator` folder or ZIP file
4. Enable **Apex Validator** in the add-ons list
5. Find the panel in `3D View → Sidebar → Apex` (press **N** to toggle sidebar)

### Manual Install
1. Clone this repository or download as ZIP
2. Copy the `ApexValidator` folder to your Blender addons directory:
   - **Windows**: `%APPDATA%\Blender Foundation\Blender\5.0\scripts\addons\`
   - **macOS**: `~/Library/Application Support/Blender/5.0/scripts/addons/`
   - **Linux**: `~/.config/blender/5.0/scripts/addons/`
3. Restart Blender and enable the addon

---

## 🎯 Quick Start

### Basic Workflow
1. Open the **Apex Validator** panel in the 3D View sidebar (press **N**)
2. *(Optional)* Set object name prefixes to ignore (e.g., `WGT-,TEMP-`)
3. Select check scope: **Scene** or **Collection**
4. Click **Find Problems** to scan for issues
5. Review results - click any object name to select/isolate it in the viewport
6. Click **Fix Automatically** to repair fixable issues
7. Use filters to show/hide specific issue types

### Understanding Results
- **🔴 ERROR**: Critical issues that affect rendering, rigging, or animation
- **🟡 WARNING**: Non-critical issues that may need review
- **Click object names** to select and isolate them in the viewport (click again to un-isolate)
- **Full messages** are displayed - no truncation
- **Visual Feedback**: Broken shaders are replaced with bright red self-illuminating material

### Ignore Objects
Exclude objects from validation by name prefix:
1. Enter comma-separated patterns in the "Ignore Objects" field (e.g., `WGT-,TEMP-,_IGNORE`)
2. Any object starting with these prefixes will be skipped during validation
3. Default pattern `WGT-` excludes rig widget objects

---

## 📋 Validation Categories

### 🎨 Material Problems
- **Broken Shaders**: Materials with no nodes or missing output nodes (AUTO-FIXED with red marker material)
- **Disconnected Outputs**: Material Output not connected to surface shader
- **Deprecated Nodes**: Old shader nodes that should be Principled BSDF
- **Missing Textures**: Image texture nodes pointing to missing files
- **Empty Material Slots**: Mesh objects with empty material slots
- **Shader Compatibility**: Cycles-only or Eevee-only nodes

### 📐 Geometry Issues
- **Missing UVs**: Meshes without UV maps (AUTO-FIXED with Smart UV Project)
- **Loose Vertices**: Vertices not connected to any edges
- **Zero-Face Meshes**: Meshes with vertices but no faces
- **High Poly Count**: Meshes exceeding performance thresholds

**Note**: N-gons are NOT flagged - they're normal for CAD data and don't cause rendering issues.

### 📏 Transform Issues
- **Unapplied Scale**: Non-uniform scale transforms not applied (AUTO-FIXED)
- **Unapplied Rotation**: Rotation transforms not applied to mesh data (AUTO-FIXED)
- **Non-Uniform Scale**: Different scale values on X/Y/Z axes

### 🔧 Tools & Effects (Modifiers)
- **Missing Targets**: Boolean, Shrinkwrap, Array modifiers with no target object (AUTO-REMOVED)
- **Unbound Surface Deform**: Critical crash risk - modifier not bound to target (AUTO-REMOVED)
- **Missing Armature**: Armature modifier with no armature object assigned
- **Broken Data Transfer**: Data Transfer modifier with no source object

### 🚗 Animation Drivers
- **Invalid Expressions**: Corrupted or broken driver expressions (AUTO-REMOVED)
- **Circular Dependencies**: Drivers referencing their own object (AUTO-FIXED)
- **Missing Targets**: Driver variables pointing to deleted objects
- **Invalid Variables**: Driver variables with corrupt data

### 🦴 Bones & Weights (Rigging)
- **Empty Vertex Groups**: Vertex groups with no vertices assigned (AUTO-REMOVED)
- **Zero-Weight Groups**: Vertex groups where all weights are 0
- **Orphaned Groups**: Vertex groups that don't match any bones in armature (AUTO-REMOVED)
- **Missing Armature Modifier**: Rigged mesh without armature modifier

### 📦 Mesh Data
- **Shape Key Issues**: Shape keys referencing missing vertex groups

**Note**: Multi-user mesh data and default names (Mesh.001) are NOT flagged - they're normal for CAD workflows and don't affect animation.

### ♻️ Dependency Loops
- **Parent Loops**: Objects parented in a circular chain
- **Constraint Loops**: Constraint dependencies forming cycles
- **Modifier Loops**: Modifier target chains creating circular references

---

## 🛠️ Auto-Fix Capabilities

Apex Validator can automatically fix many common issues:

### ✅ Automatically Fixed
- **Broken Shaders**: Replaced with red self-illuminating "_BROKEN TO FIX" material for visual identification
- **Disconnected Material Outputs**: Reconnected to Principled BSDF
- **Deprecated Shader Nodes**: Replaced with modern equivalents
- **Invalid Drivers**: Removed completely
- **Circular Driver Dependencies**: Dependencies broken to resolve loops
- **Broken Modifiers**: Removed (missing targets, unbound Surface Deform)
- **Unapplied Transforms**: Applied to mesh data (batched processing for large scenes)
- **Empty Vertex Groups**: Removed automatically
- **Orphaned Vertex Groups**: Removed if not matching any armature bones
- **Missing UVs**: Smart UV projection generated

### ⚠️ Requires Manual Fix
- **Missing Texture Files**: You need to locate and relink the files
- **Empty Material Slots**: Decide what material to assign
- **Shader Compatibility Warnings**: Depends on your target render engine
- **Geometry Issues**: Artistic decisions (loose vertices may be intentional)

### 🔧 Performance & Safety Features
- **Batched Processing**: Handles 1000+ objects safely with 15-object batches
- **Memory Management**: Automatic garbage collection between batches
- **Crash Prevention**: Validates objects before accessing properties
- **Progress Tracking**: Real-time progress bar and fix counters
- **Stabilization Delays**: Prevents access violations during rapid operations

See [AUTO_FIX_GUIDE.md](AUTO_FIX_GUIDE.md) for complete details on what can and cannot be auto-fixed.

---

## 🎨 Use Cases

### 🏭 CAD Data Import Workflows
- **Import Cleanup**: Validate CAD imports (STEP, IGES, FBX) before animation
- **Ignore Non-Issues**: N-gons, default names, and mesh instancing are automatically ignored
- **Focus on Real Problems**: Only flags issues that affect rendering and rigging

### 🎬 Animation Production
- **Pre-Animation Checks**: Ensure rigs are clean before animators start work
- **Transform Validation**: Catch unapplied transforms that cause deformation issues
- **Broken Shader Detection**: Visual red material highlights problems immediately

### 🏭 Studio Pipelines
- **Quality Control**: Validate freelance submissions or team assets
- **Asset Library Maintenance**: Keep library clean and production-ready
- **Final Scene Cleanup**: Pre-flight checks before client delivery or rendering

### 🎓 Education & Training
- **Teaching Best Practices**: Show students proper asset creation workflows
- **Project Grading**: Automated validation of student submissions
- **Learning Material Setup**: Understand what makes clean production assets
- Validate topology before export to game engines
- Ensure proper UV mapping on all assets
- Check transform applications for clean FBX/glTF export

---

## 💡 Best Practices

### 1. **Set Up Ignore Patterns First**
Configure name prefixes for rig widgets (`WGT-`), temporary objects (`TEMP-`), and helper objects to reduce noise in results.

### 2. **Find Problems First, Then Fix**
Review the validation results before clicking "Fix Automatically" - understand what will be changed.

### 3. **Use Collection Mode for Focused Work**
When working on specific assets, validate just that collection for faster feedback and targeted fixes.

### 4. **Visual Feedback for Broken Shaders**
Look for bright red glowing objects - these had broken shaders and need manual material setup.

### 5. **Filter Results by Category**
Use category filters to focus on specific types of issues. Fix critical errors (red) before warnings (yellow).

### 6. **Large Scene Handling**
For scenes with 500+ objects, auto-fix uses batched processing. Expect progress updates in the console.

### 7. **Click to Isolate Objects**
Click object names in results to select and isolate them in the viewport - click again to un-isolate and see the full scene.

### 8. **CAD Data Friendly**
The validator ignores common CAD characteristics (N-gons, default names, instancing) that don't affect production work.

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/NewValidator`)
3. Commit your changes (`git commit -m 'Add vertex color validator'`)
4. Push to the branch (`git push origin feature/NewValidator`)
5. Open a Pull Request

### Adding New Validators
New validators should be added to `ApexValidator/validators/` and follow the pattern:
```python
class MyValidator:
    @staticmethod
    def validate_my_check(obj) -> List[Tuple[str, str, str]]:
        """Returns list of (issue_type, message, severity)."""
        issues = []
        # ... validation logic
        return issues
```

---

## 📄 License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Apex Dev**

---

## 📚 Version History

### v2.0.0 - Current Release
**Major UI/UX Overhaul & CAD Workflow Optimization**

#### New Features
- 🎨 **Visual Broken Shader Feedback**: Replaced with red self-illuminating "_BROKEN TO FIX" material
- 👆 **Click-to-Isolate**: Click objects in results to select/isolate, click again to un-isolate
- 📝 **Full Error Messages**: Complete descriptions displayed without truncation
- 🎯 **User-Friendly Language**: Renamed categories for clarity (e.g., "Tools/Effects" instead of "Modifiers")
- 💡 **Help Tooltips**: Info text throughout the interface explaining features
- 🔧 **Force Visibility**: Clicking objects now forces them to be visible in viewport

#### CAD Workflow Optimizations
- ✅ Ignores N-gons (normal for CAD data, don't affect rendering)
- ✅ Ignores default mesh names (Mesh.001, etc. - common in CAD imports)
- ✅ Ignores mesh instancing (multiple users - not a problem for animation)
- 🎯 Focuses only on issues that affect rendering, rigging, and animation

#### Performance & Stability
- ⚡ Reduced batch size (25→15) for safer transform operations
- 🛡️ Enhanced crash prevention with object validation before operations
- 🔄 Added stabilization delays between batches (prevents access violations)
- 💾 Improved memory management with garbage collection
- 📊 Better error handling for large scenes (1000+ objects)

#### UI Improvements
- 🎨 "Ignore Objects" section moved to top for easy access
- 🎯 "Find Problems" and "Fix Automatically" buttons with clearer labels
- 📂 Renamed filters: "Tools/Effects", "Animations", "Bones/Weights", "Loops"
- 🎨 Category names more accessible: "Material Problems", "Animation Problems", etc.
- 📏 Compact UI with better space allocation for error messages

### v1.2.0 - Previous Release
- Complete validation system with 9 categories
- Smart auto-fix for common issues
- Category-based filtering system
- Progress tracking for auto-fix operations
- Exclusion pattern support
- Scene and Collection scope modes

---

## 🙏 Acknowledgments

Built for the Blender community to help maintain clean, production-ready assets.

---

**Made with ❤️ for the Blender Community**
