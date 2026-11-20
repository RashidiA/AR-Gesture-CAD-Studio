# 🎨 AR Gesture CAD Studio (2D & 3D AR)

A browser-based, gesture-controlled Augmented Reality (AR) CAD and 3D modelling studio built with **Python**, **Streamlit**, **MediaPipe**, **Three.js** and **WebGL**. Use your webcam and hand gestures, or just a mouse or touch screen, to create, edit, measure and export 3D parts. Everything runs in your browser; no video leaves your device.

**Live app:** https://ar-gesture-cad-studio-yovhcowlmh6mesydbs7wtj.streamlit.app/

---

## 🚀 Key Features

### Modelling
* **Primitives**: sphere, cube, cone, cylinder and pyramid, created by pinch gesture or by double-clicking the viewport.
* **Real Boolean operations (CSG)**: **Union**, **Intersect** and **Subtract** on solid meshes (BSP-tree based), so combined objects are genuinely merged, overlapped or cut.
* **Transform tools**: Move, Resize, Extrude (face targeting), Rotate X/Y/Z.
* **STL import**: binary and ASCII `.stl`, auto-scaled and centred.
* **2D-to-3D extrusion**: upload a PNG/JPG sketch or silhouette and extrude it into a solid.
* **2D sketch canvas**: line, rectangle, circle, freehand drawing.

### Engineering tools
* **Exact dimensions**: type length / height / width in mm and press Enter.
* **Volume, surface area and mass** for the selected solid, with material choice (steel, aluminium, cast iron, titanium, copper, ABS plastic). Values are estimates for closed solids.
* **Section view**: clipping plane along X, Y or Z with an adjustable position, to inspect the inside of a part.
* **Measure tool** with live millimetre readout.
* **Export STL** for 3D printing, and **Save / Open project** (`.json`).

### Professional workspace
* **Icon toolbar** with tooltips, plus collapsible panel groups.
* **Mouse and touch navigation** (works without a webcam): drag to orbit, right-drag or Shift-drag to pan, scroll or pinch to zoom, click to select, drag with the Move tool.
* **View cube** and standard views (front / right / top), reset view.
* **Full undo / redo** (40 steps) and duplicate.
* **Auto-save and restore**: work is saved in your browser every few seconds; a banner offers to restore after a reload.
* **Grid floor** and optional **soft shadows** (off by default for performance).
* **AutoCAD-style look**: dark UI, edge outlines, face-hover marker for extrusion.

### Gestures
* **One-hand pinch** (thumb + index): select, create, drag, resize or rotate depending on the active tool.
* **Two-hand pinch**: spread to scale, twist to rotate the selected object.
* **Gesture guide** (press `H` or the `?` button) ticks off each gesture as you perform it.
* Camera-relative mapping, so gestures follow the current view.

### Dual language
* Full **English / Bahasa Malaysia** interface, switchable at any time.

---

## ⌨️ Keyboard Shortcuts

| Key | Action | Key | Action |
|---|---|---|---|
| `Ctrl+Z` | Undo | `G` | Toggle grid |
| `Ctrl+Y` / `Ctrl+Shift+Z` | Redo | `F` / `Home` | Reset view |
| `Ctrl+S` | Save project | `1` / `2` / `3` | Front / right / top view |
| `Ctrl+D` | Duplicate | `H` | Gesture guide |
| `Delete` | Delete selected | `K` | Shortcut list |
| `Esc` | Close dialogs | | |

---

## 🛠️ Technology Stack

* **UI**: Streamlit (`1.x`), HTML5, CSS3 (glassmorphic dark theme) embedded via `components.html`
* **3D engine**: Three.js `r128`, WebGLRenderer, STLLoader, custom BSP-tree CSG
* **Computer vision**: MediaPipe Hands and Camera Utils (on-device, in the browser)
* **Python**: Streamlit app shell, Base64 handling of uploaded STL and images

---

## 📋 Installation & Running Locally

1. Download `app.py` (and `requirements.txt` if you have one) into a folder.
2. Install and run:
   ```bash
   pip install streamlit
   streamlit run app.py
   ```
3. Open the local URL, allow camera access, and start modelling. A webcam is optional: mouse and touch work on their own.

> Camera access requires HTTPS or `localhost`.

---

## 💡 Tips

* Good lighting and a plain background give the best hand tracking.
* If the app feels slow, leave **Shadows** off and use a desktop browser such as Chrome or Edge. The "AI: N fps" readout in the Controls group shows hand-tracking speed.
* Press **Discard** on the restore banner to start with a clean scene.
* Booleans work best on closed, overlapping solids.

---

## 🔒 Privacy

Camera frames are processed locally in your browser and are never uploaded. Auto-save data stays in your browser's local storage.

---

## 👤 Author

Developed by **Rashidi Asari** as an interactive automotive and engineering teaching tool.
