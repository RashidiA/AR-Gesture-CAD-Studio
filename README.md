# 🎨 AR Gesture CAD Studio (2D & 3D AR)

An edge-computed, gesture-controlled Augmented Reality (AR) CAD and 3D modeling web application built with **Python**, **Streamlit**, **MediaPipe**, **Three.js**, and **WebGL**. 

Designed with an AutoCAD-style professional dark interface, this studio allows engineers and designers to interact with 3D space, manipulate primitives, import external `.stl` models, extrude 2D sketches, and perform robust CAD boolean operations using real-time hand tracking.

---

## 🚀 Key Features

* **AI Hand Gesture Tracking**: Powered by MediaPipe Hands via your webcam. Control cursors, select objects, and execute commands using natural pinch gestures.
* **External 3D Model Import (`.stl`)**: Seamlessly import binary and ASCII STL models into the AR viewport with automatic scaling and centering.
* **2D-to-3D Image Extrusion**: Upload 2D PNG/JPG sketches or silhouettes to automatically trace contours and extrude them into solid 3D shapes.
* **Boolean Operations**: 
  * **Union**: Merge two selected 3D meshes into a single unified geometry with recalculated vertex normals and boundaries.
  * **Intersection**: Calculate overlapping geometric regions.
  * **Subtract (Difference)**: Cut or subtract one shape from another.
* **AutoCAD-Style Technical Viewport**: Features dynamic face hovering (yellow marker targeting for face extrusions), automatic edge outlines (`EdgesGeometry`), and live dimensional measurements in millimeters.
* **History & Undo System**: Step backward through your modifications or clear the canvas instantly.

---

## 🛠️ Technology Stack

* **Frontend Framework / UI**: Streamlit (`v1.x`), HTML5, CSS3 (Glassmorphic dark UI)
* **3D Graphics Engine**: Three.js (`r128`), WebGLRenderer, STLLoader, BufferGeometryUtils
* **Computer Vision / AI**: MediaPipe Hands & Camera Utils (Edge-computed in browser)
* **Data Processing**: Python, Base64 encoding, Pandas

---

## 📋 Installation & Running Locally

1. **Clone or Download** the project files into your local directory.
2. **Install Dependencies**:
   Make sure you have Python installed, then run:
   ```bash
   pip install streamlit
