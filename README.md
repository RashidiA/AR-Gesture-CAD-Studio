# 🎨 AR Gesture CAD Studio (2D & 3D AR)

An edge-computed Augmented Reality (AR) CAD application built with **Streamlit**, **MediaPipe** (real-time hand tracking), and **Three.js** (WebGL 3D rendering engine). This application provides an interactive workspace that supports both 2D parametric sketching and 3D parametric modeling with full gesture-controlled object manipulation, color customization, and external CAD file imports.

---

## 🚀 Key Features

1. **Dual-Mode Workspace**:
   - **2D Canvas Mode**: Interactive 2D sketcher supporting Freehand, Rectangle, Circle, and Triangle tools with real-time pinch drawing.
   - **3D Engine Mode**: WebGL-powered 3D parametric environment rendering live AR camera backgrounds with 3D primitives (Sphere, Cube, Cone, Extrude Z).
2. **Gesture-Controlled Interaction**:
   - **Pinch-to-Draw / Create**: Bring index finger and thumb together to initiate sketching or 3D object extrusion.
   - **Pinch-to-Transform**: Select, move, rotate across three axes ($X, Y, Z$), and resize objects dynamically using natural hand gestures.
3. **Professional AutoCAD / CAD Visual Styling**:
   - Built-in technical edge wireframing (`EdgesGeometry`) that outlines mechanical creases and sharp edges like professional CAD software (AutoCAD / SolidWorks).
   - Balanced PBR lighting and material shading to prevent over-exposure and highlights on complex models.
4. **External STL 3D Model Import**:
   - Upload standard `.stl` CAD files via Streamlit to instantly load, view, reposition, resize, and inspect custom 3D designs in AR space.
5. **8-Color Basic Palette**:
   - Easily customize the color of 2D strokes, 3D primitives, and imported CAD models using a curated 8-color basic palette.

---

## 🛠️ Tech Stack

- **UI & Wrapper**: [Streamlit](https://streamlit.io/) (Python)
- **Computer Vision & Hand Tracking**: [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands) (JavaScript Client-side)
- **3D Graphics & Rendering**: [Three.js](https://threejs.org/) (WebGL)
- **CAD File Parsing**: Three.js `STLLoader`

---

## 📦 Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone [https://github.com/your-username/ar-gesture-cad-studio.git](https://github.com/your-username/ar-gesture-cad-studio.git)
   cd ar-gesture-cad-studio
