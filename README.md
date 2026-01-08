# 🛡️ Apex Validator

**Scene and Asset Validation for Blender 5.0+ Production Pipelines**

A comprehensive validation and auto-fix tool for detecting and resolving common production issues in Blender scenes. Built for studios, freelancers, and artists who need clean, production-ready assets.

---

## ✨ Features

### 🔍 **Comprehensive Validation**
Apex Validator scans your scene or collections for 9 categories of issues:

- **🎨 Materials & Shaders**: Broken shaders, missing nodes, disconnected outputs, deprecated nodes, texture issues
- **📐 Geometry**: N-gons, missing UVs, loose vertices, zero-face meshes, high poly count warnings
- **📏 Transforms**: Unapplied scales, non-uniform scales, unapplied rotations
- **🔧 Modifiers**: Missing targets, unbound Surface Deform, broken boolean/array/shrinkwrap setups
- **🚗 Drivers**: Invalid expressions, circular dependencies, missing targets
- **📦 Object Data**: Multi-user data blocks, naming conflicts
- **🦴 Rigging**: Empty vertex groups, orphaned vertex groups, zero-weight groups, armature issues
- **♻️ Circular Dependencies**: Parent loops, constraint loops, modifier dependencies
- **🎯 PBR Compatibility**: Cycles/Eevee shader compatibility warnings

### ⚡ **Smart Auto-Fix**
Automatically repairs common issues without manual intervention:

- ✅ Resets broken shaders to clean Principled BSDF setup
- ✅ Connects disconnected Material Output nodes
- ✅ Replaces deprecated shader nodes (Diffuse BSDF, Glossy BSDF, etc.)
- ✅ Removes invalid drivers and circular dependencies
- ✅ Cleans up broken modifiers (missing targets, unbound Surface Deform)
- ✅ Applies unapplied transforms
- ✅ Removes empty vertex groups
- ✅ Fixes multi-user data blocks

See [AUTO_FIX_GUIDE.md](ApexValidator/AUTO_FIX_GUIDE.md) for detailed information on what can be auto-fixed.

### 🎯 **Flexible Scope**
- **Scene Mode**: Validate entire scene
- **Collection Mode**: Validate active collection only
- **Exclusion Patterns**: Skip objects by name prefix (e.g., `WGT-`, `TEMP-`)

### 📊 **Smart Filtering**
Filter validation results by category:
- Materials & Shaders
- Geometry Issues
- Transform Issues
- Modifier Problems
- Driver Errors
- Object Data
- Rigging Issues
- Circular Dependencies

### 🎨 **Intuitive UI**
- Color-coded severity levels (ERROR vs WARNING)
- One-click object selection from results
- Progress tracking during auto-fix operations
- Real-time fix counters by category
- Clean, organized panel layout

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
2. Select scope: **Scene** or **Collection**
3. Click **Validate** to scan for issues
4. Review results in the validation list
5. Click **Auto-Fix All** to automatically repair fixable issues
6. Use filters to focus on specific issue types

### Understanding Results
- **🔴 ERROR**: Critical issues that should be fixed
- **🟡 WARNING**: Non-critical issues that may need attention
- Click any item to select the object in the scene
- Use category filters to focus on specific issue types

### Exclusion Patterns
Exclude objects from validation by name prefix:
1. Enter comma-separated patterns (e.g., `WGT-,TEMP-,_IGNORE`)
2. Any object starting with these prefixes will be skipped
3. Default pattern `WGT-` excludes widget objects

---

## 📋 Validation Categories

### 🎨 Material & Shader Issues
- **Broken Shaders**: Materials with no nodes or missing output nodes
- **Disconnected Outputs**: Material Output not connected to surface shader
- **Deprecated Nodes**: Old Diffuse BSDF, Glossy BSDF nodes that should be Principled
- **Missing Textures**: Image texture nodes pointing to missing files
- **Empty Material Slots**: Mesh objects with empty material slots
- **Shader Compatibility**: Cycles-only or Eevee-only nodes causing render issues

### 📐 Geometry Problems
- **N-gons**: Faces with more than 4 vertices
- **Missing UVs**: Meshes without UV maps
- **Loose Vertices**: Vertices not connected to any edges
- **Zero-Face Meshes**: Meshes with vertices but no faces
- **High Poly Count**: Meshes exceeding reasonable polygon limits

### 📏 Transform Issues
- **Unapplied Scale**: Non-uniform scale transforms not applied
- **Unapplied Rotation**: Rotation transforms not applied to mesh data
- **Non-Uniform Scale**: Different scale values on X/Y/Z axes

### 🔧 Modifier Problems
- **Missing Targets**: Boolean, Shrinkwrap, Array modifiers with no target object
- **Unbound Surface Deform**: Critical crash risk - modifier not bound to target
- **Missing Armature**: Armature modifier with no armature object assigned
- **Broken Data Transfer**: Data Transfer modifier with no source object

### 🚗 Driver Issues
- **Invalid Expressions**: Corrupted or broken driver expressions
- **Circular Dependencies**: Drivers referencing their own object
- **Missing Targets**: Driver variables pointing to deleted objects
- **Invalid Variables**: Driver variables with corrupt data

### 🦴 Rigging Issues
- **Empty Vertex Groups**: Vertex groups with no vertices assigned
- **Zero-Weight Groups**: Vertex groups where all weights are 0
- **Orphaned Groups**: Vertex groups that don't match any bones in armature
- **Missing Armature Modifier**: Rigged mesh without armature modifier

### 📦 Object Data Issues
- **Multi-User Data**: Multiple objects sharing the same mesh/curve data
- **Naming Conflicts**: Data blocks with confusing or non-standard names

### ♻️ Circular Dependencies
- **Parent Loops**: Objects parented in a circular chain
- **Constraint Loops**: Constraint dependencies forming cycles
- **Modifier Loops**: Modifier target chains creating circular references

---

## 🛠️ Auto-Fix Capabilities

Apex Validator can automatically fix many common issues:

### ✅ Automatically Fixed
- Broken shader node trees (resets to Principled BSDF)
- Disconnected Material Output nodes
- Deprecated shader nodes (replaced with Principled BSDF)
- Invalid drivers (removed)
- Circular driver dependencies (broken)
- Broken modifiers with missing targets (removed)
- Unbound Surface Deform modifiers (removed - prevents crashes)
- Unapplied transforms (applied to mesh data)
- Empty vertex groups (removed)
- Multi-user mesh data (made single-user)

### ⚠️ Requires Manual Fix
- Missing texture files (you need to locate/relink)
- Geometry issues (N-gons, missing UVs - artistic decisions)
- Empty material slots (you decide what material to assign)
- Shader compatibility warnings (depends on your render engine)

See [AUTO_FIX_GUIDE.md](ApexValidator/AUTO_FIX_GUIDE.md) for complete details on what can and cannot be auto-fixed.

---

## 🎨 Use Cases

### 🏭 Production Pipelines
- Pre-flight checks before sending assets to rendering
- Team collaboration - ensure everyone follows naming conventions
- Asset library maintenance - keep library clean and validated

### 🎬 Studio Workflows
- Quality control for freelance submissions
- Asset validation before rigging or animation
- Final scene cleanup before client delivery

### 🎓 Education
- Teaching proper asset creation workflows
- Student project validation and grading
- Learning material best practices

### 🎮 Game Asset Preparation
- Validate topology before export to game engines
- Ensure proper UV mapping on all assets
- Check transform applications for clean FBX/glTF export

---

## 💡 Best Practices

### 1. **Validate Early, Validate Often**
Run validation during modeling, not just at the end. Catching issues early saves time.

### 2. **Use Collection Mode for Iterative Work**
When working on specific assets, validate just that collection to get faster feedback.

### 3. **Set Up Exclusion Patterns**
Configure patterns for rig widgets (`WGT-`), temporary objects (`TEMP-`), and helper objects to reduce noise.

### 4. **Review Before Auto-Fix**
Check the validation results first. Auto-fix is powerful but might remove things you want to keep.

### 5. **Filter by Category**
Use category filters to focus on specific types of issues. Fix materials first, then geometry, then modifiers.

### 6. **Understand Severity Levels**
- **ERROR** (red): Must be fixed for production
- **WARNING** (yellow): Should be reviewed, may be intentional

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

### v1.2.0 - Current Release
- Complete validation system with 9 categories
- Smart auto-fix for common issues
- Category-based filtering system
- Progress tracking for auto-fix operations
- Exclusion pattern support
- Scene and Collection scope modes
- One-click object selection from results
- Real-time fix counters by category

---

## 🙏 Acknowledgments

Built for the Blender community to help maintain clean, production-ready assets.

---

**Made with ❤️ for the Blender Community**
