# 🎬 ApexSlate

**Professional Camera & Shot Management for Blender 5.0+**

Transform your Blender workflow with cinematic camera controls, intuitive shot management, and powerful batch rendering tools. ApexSlate brings the precision of professional camera rigs and the efficiency of modern shot planning to your 3D projects.

---

## ✨ Features

### 🎥 Professional Camera Rigs
- **Parametric Controls**: Dolly, orbit, tilt, roll, and pan with driver-based animation
- **Real Sensor Presets**: Full Frame, APS-C, Micro 4/3, ARRI Alexa 35, iPhone sensors
- **Lens Library**: From ultra-wide to telephoto, including iPhone 16 Pro camera specs
- **Interactive Focus Picker**: Click-to-focus with real-time depth-of-field preview
- **Macro Mode**: Simulate f/22 aperture for close-up shots

### 🎮 Director Mode
Take control of your camera like never before with **Director Mode** - an intuitive modal interface for real-time camera manipulation:

- **Hotkey-Driven Workflow**: Switch between dolly, orbit, tilt, roll, and pan on the fly
- **Interactive Focus Picking**: Click anywhere in your scene to set focus distance
- **Precision Mode**: Hold Shift for fine-tuned adjustments
- **Customizable Hotkeys**: Configure your own keyboard layout in preferences
- **Visual Feedback**: On-screen HUD shows active mode and camera info

Press **F1** to enter Director Mode and experience camera control like a pro.

### 📊 Shot Management
- **Smart Scan**: Automatically detect shots from keyframe ranges with gap support
- **Timeline Integration**: Camera markers sync automatically with your shot list
- **Frame Range Detection**: Precise shot boundaries based on actual keyframes
- **Custom Naming**: Rename shots and propagate changes across the entire rig hierarchy
- **Isolation Mode**: Focus on individual shots during playback

### 🎨 Composition Tools
- **Camera Lister**: Switch between cameras with one click, auto-hide inactive rigs
- **Composition Guides**: Rule of thirds, center marks, golden ratio overlays
- **Viewport HUD**: Real-time shot name and active camera display
- **Format Presets**: YouTube 16:9, Instagram Story 9:16, Square 1:1, Cinema 2.35:1, 4K, and custom resolutions

### 🚀 Batch Rendering
- **Playblast Queue**: Quick OpenGL previews with metadata burn-in
- **Internal Rendering**: Render all shots with one click
- **Batch Scripts**: Export .bat/.sh files for background rendering
- **Resolution Override**: Set per-shot resolution independent of scene settings
- **Smart Output**: Automatic folder structure based on blend file name

### 🔧 Workflow Enhancements
- **Auto-Update System**: Check for updates directly from GitHub
- **Clean Timeline Markers**: Remove orphaned markers with one click
- **Bug Reporting**: Pre-filled GitHub issue templates with system info
- **Backward Compatibility**: Automatically upgrades old rigs with new features

---

## 📦 Installation

### Quick Install
1. Download the latest release from [Releases](https://github.com/Crikomoto/ApexSlate/releases)
2. In Blender, go to `Edit → Preferences → Add-ons`
3. Click `Install...` and select the downloaded `.zip` file
4. Enable **ApexSlate** in the add-ons list
5. Find the panel in `3D View → Sidebar → ApexSlate` (press **N** to toggle sidebar)

### Manual Install
1. Clone this repository or download as ZIP
2. Copy the `apex_slate` folder to your Blender addons directory:
   - **Windows**: `%APPDATA%/Blender Foundation/Blender/5.0/scripts/addons/`
   - **macOS**: `~/Library/Application Support/Blender/5.0/scripts/addons/`
   - **Linux**: `~/.config/blender/5.0/scripts/addons/`
3. Restart Blender and enable the addon

---

## 🎯 Quick Start

### Create Your First Camera Rig
1. Place your 3D cursor where you want the camera
2. Open the **ApexSlate** panel in the sidebar
3. Click **Create Camera Rig**
4. A professional camera rig appears with full parametric controls

### Enter Director Mode
1. Select any camera rig
2. Press **F1** (or click **DIRECTOR MODE**)
3. Use number keys to switch between modes:
   - **1** - Dolly (Distance)
   - **2** - Orbit
   - **3** - Tilt (Elevation)
   - **4** - Roll
   - **5** - Pan (Move)
   - **6** - Interactive Focus
   - **7** - Free Rotate
   - **8** - Snap to Object
4. Move your mouse to adjust, click to confirm, ESC to exit

### Manage Shots
1. Animate your camera rigs with keyframes
2. Click **Smart Scan** in the Render Queue panel
3. All shots are automatically detected and added to the timeline
4. Click any shot in the list to switch cameras
5. Use **Playblast** for quick previews or **Render All Shots** for final output

---

## 🎨 Use Cases

- **Product Visualization**: Multi-angle turntable shots with precise camera placement
- **Architectural Walkthroughs**: Smooth camera paths with professional controls
- **Character Animation**: Multiple camera angles for dialogue and action sequences
- **Motion Graphics**: Quick shot sequencing with automated batch rendering
- **Showreels**: Manage dozens of shots in a single blend file

---

## 🛠️ Advanced Features

### Custom Hotkeys
Configure Director Mode hotkeys in **Edit → Preferences → Add-ons → ApexSlate**. Each action (dolly, orbit, tilt, roll, pan, focus, rotate, snap) can be mapped to any key.

### Focus System
- Focus target is visible in viewport for intuitive placement
- All focus keyframes stored on master controller for centralized animation
- Driver-based system links focus empty to custom properties
- Real-time depsgraph updates ensure smooth interaction

### Rig Visibility Management
When switching cameras in the Camera Lister, only the active camera, master control, and focus empty remain visible. All helper objects (MCH chain) are automatically hidden for a clean viewport.

### Automatic Renaming
Rename a camera in the Camera Lister, and ApexSlate automatically propagates the change to:
- Master control (`Shot_01_CTRL` → `NewName_CTRL`)
- All child elements (MCH objects, camera, focus target)
- Associated timeline markers
- Take list entries

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features or improvements:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🐛 Bug Reports

Found a bug? Use the built-in bug reporter:
1. Go to **Edit → Preferences → Add-ons → ApexSlate**
2. Scroll to **Bug Reports & Feature Requests**
3. Click **Report Bug on GitHub**
4. Fill in the pre-populated template and submit

Or manually open an issue on [GitHub Issues](https://github.com/Crikomoto/ApexSlate/issues).

---

## 📄 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Cristian Koch R.**

- GitHub: [@Crikomoto](https://github.com/Crikomoto)

---

## 🌟 Support

If ApexSlate improves your workflow, consider:
- ⭐ Starring this repository
- 🐦 Sharing it with other Blender artists
- 💬 Providing feedback and feature requests

---

## 📚 Version History

### v1.7.5 - Current Release
- Enhanced camera lister with automatic visibility management
- Automatic rig renaming with hierarchy propagation
- Timeline marker cleanup system
- Smart scan with precise keyframe detection and gap support
- Bug report integration with GitHub
- Focus picker improvements and error fixes
- Cross-platform hotkey support verified

### v1.5.0
- Focus picker visibility enhancements
- Centralized keyframe management
- Director mode improvements
- Custom hotkey system
- Auto-update infrastructure

---

## 🎓 Tips & Tricks

- **Shift in Director Mode**: Hold Shift for precision movements at 10% speed
- **Quick Focus**: Press 6 in Director Mode, click anywhere, done!
- **Timeline Markers**: Camera markers auto-sync - use Clean Markers to remove orphans
- **Batch Rendering**: Save your .blend file first to set proper output paths
- **Viewport Performance**: Hidden rigs don't render - switch cameras freely without lag
- **Keyframe Workflow**: ApexSlate respects your keyframes - gaps between shots are preserved

---

**Made with ❤️ for the Blender Community**
