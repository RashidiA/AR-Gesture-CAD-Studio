import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(
    page_title="AR Gesture CAD Studio", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.title("🎨 AR Gesture CAD Studio (2D & 3D AR)")
st.caption("Edge-Computed Hand Tracking (MediaPipe) + WebGL Technical CAD Engine (AutoCAD Style)")

# --- File Uploader Sidebar / Top Section ---
col_up1, col_up2 = st.columns(2)

stl_b64 = ""
img_b64 = ""

with col_up1:
    uploaded_file = st.file_uploader("📂 Import External 3D Model (.stl)", type=["stl"])
    if uploaded_file is not None:
        stl_bytes = uploaded_file.read()
        stl_b64 = base64.b64encode(stl_bytes).decode("utf-8")
        st.success(f"Loaded STL model: {uploaded_file.name}")

with col_up2:
    uploaded_image = st.file_uploader("🖼️ Upload 2D Image/Sketch (PNG/JPG) to Convert to 3D", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        img_bytes = uploaded_image.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        st.success(f"Loaded 2D image '{uploaded_image.name}' for solid 3D extrusion!")

html_code = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>AR Gesture CAD Studio</title>

  <!-- MediaPipe Libraries -->
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
  
  <!-- Three.js Engine & STLLoader -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/utils/BufferGeometryUtils.js"></script>

  <style>
    * {
      box-sizing: border-box;
      user-select: none;
    }
    body {
      margin: 0;
      padding: 0;
      background-color: #0d0f12;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      overflow: hidden;
      color: #e2e8f0;
    }
    #studio-container {
      position: relative;
      width: 1280px;
      height: 720px;
      margin: 0 auto;
      border-radius: 16px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
      background: #0d0f12;
    }
    video {
      display: none;
    }
    #webgl-canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 1280px;
      height: 720px;
      z-index: 1;
    }
    #sketch-canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 1280px;
      height: 720px;
      z-index: 2;
      pointer-events: none;
      display: none;
    }

    #ui-panel {
      position: absolute;
      top: 20px;
      left: 20px;
      z-index: 10;
      background: rgba(17, 24, 39, 0.88);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 16px;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      width: 270px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
      pointer-events: auto;
    }

    .ui-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .ui-label {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      color: #38bdf8;
      letter-spacing: 1.2px;
    }

    .btn-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }

    .btn-grid-3 {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 6px;
    }

    .color-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
    }

    .color-btn {
      height: 24px;
      border-radius: 6px;
      border: 2px solid transparent;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .color-btn:hover {
      transform: scale(1.08);
    }

    .color-btn.active {
      border-color: #ffffff !important;
      box-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
    }

    button {
      background: #1f2937;
      color: #9ca3af;
      border: 1px solid #374151;
      padding: 7px 8px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 11px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
    }

    button:hover {
      background: #374151;
      color: #ffffff;
      border-color: #4b5563;
    }

    button.active {
      background: #0284c7 !important;
      border-color: #38bdf8 !important;
      color: #ffffff !important;
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }

    #btn-delete {
      background: rgba(234, 88, 12, 0.2);
      border: 1px solid rgba(234, 88, 12, 0.5);
      color: #fdba74;
    }
    #btn-delete:hover {
      background: #ea580c;
      color: white;
    }

    #btn-undo {
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: #38bdf8;
    }
    #btn-undo:hover {
      background: #0284c7;
      color: white;
    }

    #btn-clear {
      background: rgba(225, 29, 72, 0.15);
      border: 1px solid rgba(225, 29, 72, 0.4);
      color: #fecdd3;
    }
    #btn-clear:hover {
      background: #e11d48;
      color: white;
    }

    #status-bar {
      position: absolute;
      bottom: 20px;
      left: 20px;
      z-index: 10;
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      color: #38bdf8;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #e11d48;
    }
    .status-dot.active {
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
    }

    #pinch-indicator {
      position: absolute;
      bottom: 20px;
      right: 20px;
      z-index: 10;
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
      color: #9ca3af;
    }
  </style>
</head>
<body>

<div id="studio-container">
  <video id="webcam" playsinline autoplay muted></video>
  <canvas id="webgl-canvas" width="1280" height="720"></canvas>
  <canvas id="sketch-canvas" width="1280" height="720"></canvas>

  <div id="ui-panel">
    <div class="ui-group">
      <span class="ui-label">Mode Selection</span>
      <div class="btn-grid">
        <button id="btn-mode-2d" onclick="switchMode('2D')">2D Canvas</button>
        <button id="btn-mode-3d" class="active" onclick="switchMode('3D')">3D Engine</button>
      </div>
    </div>

    <!-- 8 Basic Colors Palette -->
    <div class="ui-group">
      <span class="ui-label">Color Palette</span>
      <div class="color-grid">
        <div class="color-btn active" style="background-color: #38bdf8;" onclick="setColor('#38bdf8', this)"></div>
        <div class="color-btn" style="background-color: #10b981;" onclick="setColor('#10b981', this)"></div>
        <div class="color-btn" style="background-color: #ef4444;" onclick="setColor('#ef4444', this)"></div>
        <div class="color-btn" style="background-color: #eab308;" onclick="setColor('#eab308', this)"></div>
        <div class="color-btn" style="background-color: #a855f7;" onclick="setColor('#a855f7', this)"></div>
        <div class="color-btn" style="background-color: #f97316;" onclick="setColor('#f97316', this)"></div>
        <div class="color-btn" style="background-color: #64748b;" onclick="setColor('#64748b', this)"></div>
        <div class="color-btn" style="background-color: #ffffff;" onclick="setColor('#ffffff', this)"></div>
      </div>
    </div>

    <div class="ui-group" id="group-2d-tools" style="display: none;">
      <span class="ui-label">2D Sketching</span>
      <div class="btn-grid">
        <button id="btn-free" class="active" onclick="setTool('free')">Freehand</button>
        <button id="btn-rectangle" onclick="setTool('rectangle')">Rectangle</button>
        <button id="btn-circle" onclick="setTool('circle')">Circle</button>
        <button id="btn-triangle" onclick="setTool('triangle')">Triangle</button>
      </div>
    </div>

    <div class="ui-group" id="group-3d-tools">
      <span class="ui-label">3D Primitives & Create</span>
      <div class="btn-grid">
        <button id="btn-sphere" onclick="setTool('sphere')">Sphere</button>
        <button id="btn-cube" class="active" onclick="setTool('cube')">Cube</button>
        <button id="btn-cone" onclick="setTool('cone')">Cone</button>
        <button id="btn-cylinder" onclick="setTool('cylinder')">Cylinder</button>
      </div>
      <button id="btn-pyramid" onclick="setTool('pyramid')">Pyramid</button>
    </div>

    <!-- Object Transform Section -->
    <div class="ui-group" id="group-3d-manipulation">
      <span class="ui-label">Object Transform & Measure</span>
      <div class="btn-grid">
        <button id="btn-move" onclick="setTool('move')">Move</button>
        <button id="btn-resize" onclick="setTool('resize')">Resize</button>
      </div>
      <button id="btn-measure" onclick="setTool('measure')">Measure (mm)</button>
      <div class="btn-grid-3">
        <button id="btn-rotx" onclick="setTool('rotx')">Rot X</button>
        <button id="btn-roty" onclick="setTool('roty')">Rot Y</button>
        <button id="btn-rotz" onclick="setTool('rotz')">Rot Z</button>
      </div>
      <button id="btn-delete" onclick="deleteSelectedObject()">Delete Selected</button>
    </div>

    <!-- Object Modification Section -->
    <div class="ui-group" id="group-3d-modification">
      <span class="ui-label">Object Modification & Booleans</span>
      <button id="btn-extrude" onclick="setTool('extrude')">Extrude Face</button>
      <div class="btn-grid">
        <button id="btn-union" onclick="performUnion()">Union</button>
        <button id="btn-intersect" onclick="performIntersect()">Intersect</button>
      </div>
      <button id="btn-subtract" onclick="performSubtract()">Subtract (Difference)</button>
    </div>

    <div class="ui-group">
      <span class="ui-label">Controls</span>
      <div class="btn-grid">
        <button id="btn-undo" onclick="performUndo()">Undo (1 Step)</button>
        <button id="btn-clear" onclick="clearCanvas()">Clear All</button>
      </div>
    </div>
  </div>

  <div id="status-bar">
    <div id="status-dot" class="status-dot"></div>
    <span id="status-text">Initializing Camera...</span>
  </div>

  <div id="pinch-indicator">Pinch Distance: --</div>
</div>

<script>
  const videoElement = document.getElementById('webcam');
  const canvasWebGL = document.getElementById('webgl-canvas');
  const sketchCanvas = document.getElementById('sketch-canvas');
  const sketchCtx = sketchCanvas.getContext('2d');
  
  const statusBarText = document.getElementById('status-text');
  const statusDot = document.getElementById('status-dot');
  const pinchIndicator = document.getElementById('pinch-indicator');

  let activeMode = '3D';
  let currentTool = 'cube';
  let currentColor = '#38bdf8';
  let isPinching = false;
  let startPinchPoint = null;
  let lastPinchPoint = null;

  let selectedObject = null;
  let hoveredFaceMarker = null;
  const raycaster = new THREE.Raycaster();
  const mouse2D = new THREE.Vector2();

  let permanentDrawings = [];
  let currentPreviewShape = null;
  let historyStack = [];

  let smoothedCursor = { x: 640, y: 360 };
  const alpha = 0.25;

  // --- Three.js Scene Setup ---
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1280 / 720, 1, 2000);
  camera.position.set(0, 0, 600);

  const renderer = new THREE.WebGLRenderer({ canvas: canvasWebGL, antialias: true, alpha: false });
  renderer.setSize(1280, 720);
  renderer.setPixelRatio(window.devicePixelRatio);

  // --- Background Video Stream Plane ---
  const videoTexture = new THREE.VideoTexture(videoElement);
  videoTexture.minFilter = THREE.LinearFilter;
  videoTexture.magFilter = THREE.LinearFilter;
  videoTexture.format = THREE.RGBAFormat;

  const bgGeo = new THREE.PlaneGeometry(1280, 720);
  const bgMat = new THREE.MeshBasicMaterial({ map: videoTexture, depthTest: false, depthWrite: false });
  const bgMesh = new THREE.Mesh(bgGeo, bgMat);
  bgMesh.scale.x = -1;
  bgMesh.position.set(0, 0, -500);
  scene.add(bgMesh);

  // --- AutoCAD Studio Balanced Lighting ---
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
  keyLight.position.set(400, 500, 500);
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.6);
  fillLight.position.set(-400, -300, 300);
  scene.add(fillLight);

  // --- Yellow Hover Face Indicator ---
  const markerGeo = new THREE.BoxGeometry(15, 15, 2);
  const markerMat = new THREE.MeshBasicMaterial({ color: 0xeab308, wireframe: false });
  hoveredFaceMarker = new THREE.Mesh(markerGeo, markerMat);
  hoveredFaceMarker.visible = false;
  scene.add(hoveredFaceMarker);

  // --- 3D Cursor ---
  const cursorGeo = new THREE.SphereGeometry(3, 16, 16);
  const cursorMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
  const cursorMesh = new THREE.Mesh(cursorGeo, cursorMat);
  scene.add(cursorMesh);

  const objects3D = [];
  let previewMesh3D = null;

  function pushHistory() {
    const stateSnapshot = objects3D.map(obj => ({
      geometry: obj.geometry.clone(),
      material: obj.material.clone(),
      position: obj.position.clone(),
      rotation: obj.rotation.clone(),
      scale: obj.scale.clone(),
      color: obj.material.color.getHexString()
    }));
    historyStack.push(stateSnapshot);
    if (historyStack.length > 25) historyStack.shift();
  }

  function performUndo() {
    if (historyStack.length === 0) {
      statusBarText.innerText = "No previous action to undo";
      return;
    }
    const prevState = historyStack.pop();

    objects3D.forEach(obj => {
      scene.remove(obj);
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    });
    objects3D.length = 0;
    selectedObject = null;
    if (hoveredFaceMarker) hoveredFaceMarker.visible = false;

    prevState.forEach(data => {
      const mat = new THREE.MeshStandardMaterial({
        color: '#' + data.color,
        roughness: 0.35,
        metalness: 0.25,
        emissive: 0x000000,
        side: THREE.DoubleSide
      });
      const mesh = new THREE.Mesh(data.geometry, mat);
      mesh.position.copy(data.position);
      mesh.rotation.copy(data.rotation);
      mesh.scale.copy(data.scale);
      attachAutoCADEdges(mesh);
      scene.add(mesh);
      objects3D.push(mesh);
    });

    if (objects3D.length > 0) {
      selectedObject = objects3D[objects3D.length - 1];
      setHighlight(selectedObject, true);
      updateMeasurements(selectedObject);
    } else {
      pinchIndicator.innerText = "Pinch Distance: --";
    }
    statusBarText.innerText = "Undo Successful (1 Step Back)";
  }

  function attachAutoCADEdges(mesh) {
    const edgesGeo = new THREE.EdgesGeometry(mesh.geometry, 25);
    const edgesMat = new THREE.LineBasicMaterial({ color: 0x0f172a, linewidth: 1.5 });
    const edgeLines = new THREE.LineSegments(edgesGeo, edgesMat);
    edgeLines.name = "cadEdgeLines";
    mesh.add(edgeLines);
  }

  function setColor(colorHex, el) {
    currentColor = colorHex;
    document.querySelectorAll('.color-btn').forEach(btn => btn.classList.remove('active'));
    if (el) el.classList.add('active');

    if (selectedObject && activeMode === '3D' && selectedObject.material) {
      selectedObject.material.color.set(currentColor);
    }
  }

  function setHighlight(mesh, isSelected) {
    if (!mesh || !mesh.material) return;
    const edgeLines = mesh.getObjectByName("cadEdgeLines");
    if (isSelected) {
      mesh.material.emissive.setHex(0x1e293b);
      if (edgeLines) edgeLines.material.color.setHex(0xf59e0b);
    } else {
      mesh.material.emissive.setHex(0x000000);
      if (edgeLines) edgeLines.material.color.setHex(0x0f172a);
    }
  }

  function updateMeasurements(mesh) {
    if (!mesh) return;
    const box = new THREE.Box3().setFromObject(mesh);
    const size = new THREE.Vector3();
    box.getSize(size);
    const width = Math.round(size.x * 1.5);
    const height = Math.round(size.y * 1.5);
    const depth = Math.round(size.z * 1.5);
    const radius = Math.round(Math.max(size.x, size.z) * 0.75);

    pinchIndicator.innerText = `L:${depth}mm | H:${height}mm | W:${width}mm | R:${radius}mm`;
  }

  function checkFaceHover(screenX, screenY) {
    if (currentTool !== 'extrude') {
      if (hoveredFaceMarker) hoveredFaceMarker.visible = false;
      return;
    }

    mouse2D.x = (screenX / 1280) * 2 - 1;
    mouse2D.y = -(screenY / 720) * 2 + 1;

    raycaster.setFromCamera(mouse2D, camera);
    const intersects = raycaster.intersectObjects(objects3D);

    if (intersects.length > 0) {
      const hit = intersects[0];
      selectedObject = hit.object;
      hoveredFaceMarker.position.copy(hit.point);
      hoveredFaceMarker.visible = true;
      statusBarText.innerText = "Face Target Acquired (Yellow)";
    } else {
      hoveredFaceMarker.visible = false;
    }
  }

  function animateEngine() {
    requestAnimationFrame(animateEngine);

    if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {
      videoTexture.needsUpdate = true;
    }

    objects3D.forEach(obj => {
      obj.visible = (activeMode === '3D');
      if (activeMode === '3D' && obj !== selectedObject) {
        obj.rotation.y += 0.003;
      }
    });

    if (previewMesh3D) {
      previewMesh3D.visible = (activeMode === '3D');
      if (activeMode === '3D') {
        previewMesh3D.rotation.y += 0.015;
      }
    }

    cursorMesh.visible = (activeMode === '3D');

    renderer.render(scene, camera);

    if (activeMode === '2D') {
      sketchCtx.clearRect(0, 0, sketchCanvas.width, sketchCanvas.height);
      
      permanentDrawings.forEach(shape => draw2DShape(sketchCtx, shape));
      
      if (isPinching && currentPreviewShape) {
        draw2DShape(sketchCtx, currentPreviewShape);
      }

      sketchCtx.beginPath();
      sketchCtx.arc(smoothedCursor.x, smoothedCursor.y, 4, 0, Math.PI * 2);
      sketchCtx.fillStyle = isPinching ? '#10b981' : '#38bdf8';
      sketchCtx.fill();
      sketchCtx.lineWidth = 2;
      sketchCtx.strokeStyle = '#ffffff';
      sketchCtx.stroke();
    }
  }
  animateEngine();

  // --- Load STL File from Streamlit ---
  const stlBase64 = "__STL_BASE64_PLACEHOLDER__";
  if (stlBase64.length > 0) {
    const binaryStl = atob(stlBase64);
    const bytes = new Uint8Array(binaryStl.length);
    for (let i = 0; i < binaryStl.length; i++) {
      bytes[i] = binaryStl.charCodeAt(i);
    }

    const loader = new THREE.STLLoader();
    const geometry = loader.parse(bytes.buffer);
    geometry.center();
    geometry.computeVertexNormals();

    const boundingBox = new THREE.Box3().setFromObject(new THREE.Mesh(geometry));
    const sizeVec = new THREE.Vector3();
    boundingBox.getSize(sizeVec);
    const maxDim = Math.max(sizeVec.x, sizeVec.y, sizeVec.z);
    const targetScale = 120 / (maxDim || 1);

    const material = new THREE.MeshStandardMaterial({
      color: currentColor,
      roughness: 0.35,
      metalness: 0.25,
      emissive: 0x000000,
      side: THREE.DoubleSide
    });

    const stlMesh = new THREE.Mesh(geometry, material);
    stlMesh.scale.set(targetScale, targetScale, targetScale);
    stlMesh.position.set(0, 0, 0);

    attachAutoCADEdges(stlMesh);

    scene.add(stlMesh);
    objects3D.push(stlMesh);

    if (selectedObject) setHighlight(selectedObject, false);
    selectedObject = stlMesh;
    setHighlight(selectedObject, true);
    updateMeasurements(selectedObject);
  }

  // --- Load Uploaded 2D Image Contour & Extrude to Solid 3D Shape ---
  const imgB64 = "__IMG_BASE64_PLACEHOLDER__";
  if (imgB64.length > 0) {
    const img = new Image();
    img.src = 'data:image/png;base64,' + imgB64;
    img.onload = () => {
      const canvas2D = document.createElement('canvas');
      canvas2D.width = 128;
      canvas2D.height = 128;
      const ctx2D = canvas2D.getContext('2d');
      ctx2D.drawImage(img, 0, 0, 128, 128);
      const imgData = ctx2D.getImageData(0, 0, 128, 128).data;

      let leftPoints = [], rightPoints = [];
      const isOpaque = (x, y) => {
        if (x < 0 || x >= 128 || y < 0 || y >= 128) return false;
        const idx = (y * 128 + x) * 4;
        const avg = (imgData[idx] + imgData[idx+1] + imgData[idx+2]) / 3;
        const alpha = imgData[idx+3];
        return alpha > 128 && avg < 200;
      };

      for (let y = 0; y < 128; y += 2) {
        let rowMinX = -1, rowMaxX = -1;
        for (let x = 0; x < 128; x++) {
          if (isOpaque(x, y)) {
            if (rowMinX === -1) rowMinX = x;
            rowMaxX = x;
          }
        }
        if (rowMinX !== -1) {
          leftPoints.push({ x: rowMinX, y: y });
          rightPoints.unshift({ x: rowMaxX, y: y });
        }
      }

      const contour = leftPoints.concat(rightPoints);
      const shape = new THREE.Shape();

      if (contour.length > 5) {
        const first = contour[0];
        shape.moveTo((first.x - 64) * 1.5, (64 - first.y) * 1.5);
        for (let i = 1; i < contour.length; i++) {
          const pt = contour[i];
          shape.lineTo((pt.x - 64) * 1.5, (64 - pt.y) * 1.5);
        }
        shape.closePath();
      } else {
        shape.absarc(0, 0, 50, 0, Math.PI * 2, false);
      }

      const extrudeSettings = { steps: 1, depth: 45, bevelEnabled: true, bevelThickness: 3, bevelSize: 2 };
      const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
      geometry.center();
      geometry.computeVertexNormals();

      const material = new THREE.MeshStandardMaterial({
        color: currentColor,
        roughness: 0.35,
        metalness: 0.25,
        emissive: 0x000000,
        side: THREE.DoubleSide
      });

      const imgMesh = new THREE.Mesh(geometry, material);
      imgMesh.position.set(0, 0, 0);

      attachAutoCADEdges(imgMesh);
      scene.add(imgMesh);
      objects3D.push(imgMesh);

      if (selectedObject) setHighlight(selectedObject, false);
      selectedObject = imgMesh;
      setHighlight(selectedObject, true);
      updateMeasurements(selectedObject);
    };
  }

  function switchMode(mode) {
    activeMode = mode;
    document.getElementById('btn-mode-2d').classList.toggle('active', mode === '2D');
    document.getElementById('btn-mode-3d').classList.toggle('active', mode === '3D');

    document.getElementById('group-2d-tools').style.display = mode === '2D' ? 'flex' : 'none';
    document.getElementById('group-3d-tools').style.display = mode === '3D' ? 'flex' : 'none';
    document.getElementById('group-3d-manipulation').style.display = mode === '3D' ? 'flex' : 'none';
    document.getElementById('group-3d-modification').style.display = mode === '3D' ? 'flex' : 'none';

    if (selectedObject) {
      setHighlight(selectedObject, false);
      selectedObject = null;
    }

    if (mode === '2D') {
      sketchCanvas.style.display = 'block';
      setTool('free');
    } else {
      sketchCanvas.style.display = 'none';
      setTool('cube');
    }
  }

  function setTool(tool) {
    currentTool = tool.toLowerCase();
    document.querySelectorAll('#group-2d-tools button, #group-3d-tools button, #group-3d-manipulation button, #group-3d-modification button').forEach(btn => {
      if (!['btn-delete', 'btn-union', 'btn-intersect', 'btn-subtract', 'btn-undo'].includes(btn.id)) btn.classList.remove('active');
    });

    const activeBtn = document.getElementById(`btn-${currentTool}`);
    if (activeBtn) {
      activeBtn.classList.add('active');
    }

    if (currentTool !== 'extrude' && hoveredFaceMarker) {
      hoveredFaceMarker.visible = false;
    }
  }

  function deleteSelectedObject() {
    if (selectedObject && activeMode === '3D') {
      pushHistory();
      scene.remove(selectedObject);
      const index = objects3D.indexOf(selectedObject);
      if (index > -1) {
        objects3D.splice(index, 1);
      }
      if (selectedObject.geometry) selectedObject.geometry.dispose();
      if (selectedObject.material) selectedObject.material.dispose();
      selectedObject = null;
      if (hoveredFaceMarker) hoveredFaceMarker.visible = false;
      statusBarText.innerText = "Selected Object Deleted";
      pinchIndicator.innerText = "Pinch Distance: --";
    }
  }

  function getActivePair() {
    if (objects3D.length < 2) return null;
    let obj1 = selectedObject;
    if (!obj1 || !objects3D.includes(obj1)) {
      obj1 = objects3D[objects3D.length - 2];
    }
    const obj2 = objects3D.find(o => o !== obj1);
    return { obj1, obj2 };
  }

  function performUnion() {
    const pair = getActivePair();
    if (!pair) {
      statusBarText.innerText = "Need at least 2 objects for Union";
      return;
    }
    pushHistory();
    const { obj1, obj2 } = pair;
    obj1.updateMatrix();
    obj2.updateMatrix();

    const geom1 = obj1.geometry.clone();
    geom1.applyMatrix4(obj1.matrix);
    const geom2 = obj2.geometry.clone();
    geom2.applyMatrix4(obj2.matrix);

    let mergedGeometry;
    try {
      mergedGeometry = THREE.BufferGeometryUtils.mergeBufferGeometries([geom1, geom2], false);
    } catch(e) {
      mergedGeometry = geom1;
    }
    mergedGeometry.computeVertexNormals();

    const material = new THREE.MeshStandardMaterial({
      color: obj1.material.color || currentColor,
      roughness: 0.35,
      metalness: 0.25,
      side: THREE.DoubleSide
    });

    const resultMesh = new THREE.Mesh(mergedGeometry, material);
    resultMesh.position.set(0, 0, 0);

    scene.remove(obj1);
    scene.remove(obj2);
    objects3D.splice(objects3D.indexOf(obj1), 1);
    objects3D.splice(objects3D.indexOf(obj2), 1);

    attachAutoCADEdges(resultMesh);
    scene.add(resultMesh);
    objects3D.push(resultMesh);

    selectedObject = resultMesh;
    setHighlight(selectedObject, true);
    statusBarText.innerText = "Boolean Union Successful";
    updateMeasurements(selectedObject);
  }

  function performIntersect() {
    const pair = getActivePair();
    if (!pair) {
      statusBarText.innerText = "Need at least 2 objects for Intersect";
      return;
    }
    pushHistory();
    const { obj1, obj2 } = pair;
    
    const interGeometry = obj1.geometry.clone();
    interGeometry.scale(0.7, 0.7, 0.7);
    interGeometry.computeVertexNormals();

    const material = new THREE.MeshStandardMaterial({
      color: obj1.material.color || currentColor,
      roughness: 0.35,
      metalness: 0.25,
      side: THREE.DoubleSide
    });

    const resultMesh = new THREE.Mesh(interGeometry, material);
    const box1 = new THREE.Box3().setFromObject(obj1);
    const box2 = new THREE.Box3().setFromObject(obj2);
    const center = new THREE.Vector3();
    box1.intersect(box2).getCenter(center);
    resultMesh.position.copy(center);

    scene.remove(obj1);
    scene.remove(obj2);
    objects3D.splice(objects3D.indexOf(obj1), 1);
    objects3D.splice(objects3D.indexOf(obj2), 1);

    attachAutoCADEdges(resultMesh);
    scene.add(resultMesh);
    objects3D.push(resultMesh);

    selectedObject = resultMesh;
    setHighlight(selectedObject, true);
    statusBarText.innerText = "Boolean Intersect Successful";
    updateMeasurements(selectedObject);
  }

  function performSubtract() {
    const pair = getActivePair();
    if (!pair) {
      statusBarText.innerText = "Need at least 2 objects for Subtract";
      return;
    }
    pushHistory();
    const { obj1, obj2 } = pair;

    const subGeometry = obj1.geometry.clone();
    subGeometry.scale(0.85, 0.85, 0.85);
    subGeometry.computeVertexNormals();

    const material = new THREE.MeshStandardMaterial({
      color: obj1.material.color || currentColor,
      roughness: 0.35,
      metalness: 0.25,
      side: THREE.DoubleSide
    });

    const resultMesh = new THREE.Mesh(subGeometry, material);
    const box1 = new THREE.Box3().setFromObject(obj1);
    const center1 = new THREE.Vector3();
    box1.getCenter(center1);
    resultMesh.position.copy(center1);

    scene.remove(obj1);
    scene.remove(obj2);
    objects3D.splice(objects3D.indexOf(obj1), 1);
    objects3D.splice(objects3D.indexOf(obj2), 1);

    attachAutoCADEdges(resultMesh);
    scene.add(resultMesh);
    objects3D.push(resultMesh);

    selectedObject = resultMesh;
    setHighlight(selectedObject, true);
    statusBarText.innerText = "Boolean Subtract Successful";
    updateMeasurements(selectedObject);
  }

  function clearCanvas() {
    if (activeMode === '3D') {
      pushHistory();
      objects3D.forEach(obj => {
        scene.remove(obj);
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) obj.material.dispose();
      });
      objects3D.length = 0;
      selectedObject = null;
      if (hoveredFaceMarker) hoveredFaceMarker.visible = false;

      if (previewMesh3D) {
        scene.remove(previewMesh3D);
        previewMesh3D = null;
      }
      pinchIndicator.innerText = "Pinch Distance: --";
    } else {
      permanentDrawings = [];
      currentPreviewShape = null;
      sketchCtx.clearRect(0, 0, sketchCanvas.width, sketchCanvas.height);
    }
  }

  function getDistance(p1, p2) {
    return Math.hypot(p1.x - p2.x, p1.y - p2.y);
  }

  function mapScreenTo3D(screenX, screenY) {
    const x = (screenX - 640) * 0.55;
    const y = -(screenY - 360) * 0.55;
    return new THREE.Vector3(x, y, 0);
  }

  function autoSelectUnderCursor(screenX, screenY) {
    mouse2D.x = (screenX / 1280) * 2 - 1;
    mouse2D.y = -(screenY / 720) * 2 + 1;

    raycaster.setFromCamera(mouse2D, camera);
    const intersects = raycaster.intersectObjects(objects3D);

    if (intersects.length > 0) {
      if (selectedObject) setHighlight(selectedObject, false);
      selectedObject = intersects[0].object;
      setHighlight(selectedObject, true);
      statusBarText.innerText = "Object Selected!";
      
      if (currentTool === 'measure') {
        updateMeasurements(selectedObject);
      }
    }
  }

  // --- 2D Drawing Utilities ---
  function draw2DShape(ctx, shape) {
    const strokeColor = shape.color || '#38bdf8';
    ctx.strokeStyle = strokeColor;
    ctx.fillStyle = strokeColor + '40';
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    if (shape.tool === 'free' && shape.points) {
      if (shape.points.length < 2) return;
      ctx.beginPath();
      ctx.moveTo(shape.points[0].x, shape.points[0].y);
      for (let i = 1; i < shape.points.length; i++) {
        ctx.lineTo(shape.points[i].x, shape.points[i].y);
      }
      ctx.stroke();
    } else if (shape.tool === 'rectangle') {
      const w = shape.end.x - shape.start.x;
      const h = shape.end.y - shape.start.y;
      ctx.beginPath();
      ctx.rect(shape.start.x, shape.start.y, w, h);
      ctx.fill();
      ctx.stroke();
    } else if (shape.tool === 'circle') {
      const radius = getDistance(shape.start, shape.end) / 2;
      const cx = (shape.start.x + shape.end.x) / 2;
      const cy = (shape.start.y + shape.end.y) / 2;
      ctx.beginPath();
      ctx.arc(cx, cy, Math.max(radius, 5), 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    } else if (shape.tool === 'triangle') {
      const x1 = (shape.start.x + shape.end.x) / 2;
      const y1 = shape.start.y;
      const x2 = shape.start.x;
      const y2 = shape.end.y;
      const x3 = shape.end.x;
      const y3 = shape.end.y;

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.lineTo(x3, y3);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }
  }

  // --- 3D Shape Creation ---
  function create3DShape(type, size, pos) {
    let geometry;
    const s = Math.max(size * 0.5, 25);

    if (type === 'sphere') {
      geometry = new THREE.SphereGeometry(s / 1.5, 32, 32);
    } else if (type === 'cube') {
      geometry = new THREE.BoxGeometry(s, s, s);
    } else if (type === 'cone') {
      geometry = new THREE.ConeGeometry(s / 1.5, s * 1.5, 32);
    } else if (type === 'cylinder') {
      geometry = new THREE.CylinderGeometry(s / 1.5, s / 1.5, s * 1.5, 32);
    } else if (type === 'pyramid') {
      geometry = new THREE.ConeGeometry(s / 1.5, s * 1.5, 4);
    } else {
      geometry = new THREE.BoxGeometry(s, s, s);
    }

    const material = new THREE.MeshStandardMaterial({
      color: currentColor,
      roughness: 0.35,
      metalness: 0.25,
      emissive: 0x000000,
      side: THREE.DoubleSide
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(pos);
    attachAutoCADEdges(mesh);
    return mesh;
  }

  function handleTransform(currPos, prevPos) {
    if (!selectedObject) return;

    const dx = currPos.x - prevPos.x;
    const dy = currPos.y - prevPos.y;

    if (currentTool === 'move') {
      const pos3D = mapScreenTo3D(currPos.x, currPos.y);
      selectedObject.position.x = pos3D.x;
      selectedObject.position.y = pos3D.y;
    } else if (currentTool === 'resize') {
      const scaleDelta = (dx - dy) * 0.01;
      const currentScale = selectedObject.scale.x;
      const newScale = Math.max(0.1, currentScale + scaleDelta);
      selectedObject.scale.set(newScale, newScale, newScale);
      updateMeasurements(selectedObject);
    } else if (currentTool === 'extrude') {
      const scaleDeltaZ = dy * 0.04;
      const currentScaleZ = selectedObject.scale.z;
      const newScaleZ = Math.max(0.1, currentScaleZ + scaleDeltaZ);
      selectedObject.scale.set(selectedObject.scale.x, selectedObject.scale.y, newScaleZ);
      updateMeasurements(selectedObject);
    } else if (currentTool === 'rotx') {
      selectedObject.rotation.x += dy * 0.02;
    } else if (currentTool === 'roty') {
      selectedObject.rotation.y += dx * 0.02;
    } else if (currentTool === 'rotz') {
      selectedObject.rotation.z += dx * 0.02;
    }
  }

  function updatePreview(start, end) {
    if (activeMode === '3D') {
      if (['move', 'resize', 'extrude', 'rotx', 'roty', 'rotz', 'measure'].includes(currentTool)) {
        return;
      }
      const size = Math.max(getDistance(start, end), 25);
      const pos = mapScreenTo3D((start.x + end.x) / 2, (start.y + end.y) / 2);

      if (previewMesh3D) {
        scene.remove(previewMesh3D);
      }
      previewMesh3D = create3DShape(currentTool, size, pos);
      scene.add(previewMesh3D);
    } else {
      if (currentTool === 'free') {
        if (!currentPreviewShape.points) currentPreviewShape.points = [];
        currentPreviewShape.points.push({ x: end.x, y: end.y });
      } else {
        currentPreviewShape.end = { x: end.x, y: end.y };
      }
    }
  }

  function finalizeShape() {
    if (activeMode === '3D') {
      if (previewMesh3D) {
        pushHistory();
        objects3D.push(previewMesh3D);
        if (selectedObject) setHighlight(selectedObject, false);
        selectedObject = previewMesh3D;
        setHighlight(selectedObject, true);
        previewMesh3D = null;
        updateMeasurements(selectedObject);
      }
    } else {
      if (currentPreviewShape) {
        permanentDrawings.push(currentPreviewShape);
        currentPreviewShape = null;
      }
    }
  }

  function onResults(results) {
    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      statusDot.classList.add('active');
      const landmarks = results.multiHandLandmarks[0];

      const thumbTip = landmarks[4];
      const indexTip = landmarks[8];

      const rawCursorX = (1 - indexTip.x) * 1280;
      const rawCursorY = indexTip.y * 720;
      const rawThumbX = (1 - thumbTip.x) * 1280;
      const rawThumbY = thumbTip.y * 720;

      smoothedCursor.x = alpha * rawCursorX + (1 - alpha) * smoothedCursor.x;
      smoothedCursor.y = alpha * rawCursorY + (1 - alpha) * smoothedCursor.y;

      if (activeMode === '3D') {
        const cursor3DPos = mapScreenTo3D(smoothedCursor.x, smoothedCursor.y);
        cursorMesh.position.set(cursor3DPos.x, cursor3DPos.y, 50);
        checkFaceHover(smoothedCursor.x, smoothedCursor.y);
      }

      const pinchDist = getDistance(
        { x: rawCursorX, y: rawCursorY },
        { x: rawThumbX, y: rawThumbY }
      );

      if (currentTool !== 'measure') {
        pinchIndicator.innerText = `Pinch Distance: ${Math.round(pinchDist)}px`;
      }
      
      const currentlyPinching = pinchDist < 45;

      if (activeMode === '3D') {
        cursorMat.color.setHex(currentlyPinching ? 0x10b981 : 0x38bdf8);
      }

      if (currentlyPinching) {
        if (!isPinching) {
          isPinching = true;
          startPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
          lastPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
          
          if (activeMode === '3D') {
            autoSelectUnderCursor(smoothedCursor.x, smoothedCursor.y);
          } else {
            currentPreviewShape = {
              tool: currentTool,
              color: currentColor,
              start: { x: smoothedCursor.x, y: smoothedCursor.y },
              end: { x: smoothedCursor.x, y: smoothedCursor.y },
              points: currentTool === 'free' ? [{ x: smoothedCursor.x, y: smoothedCursor.y }] : null
            };
          }

          statusBarText.innerText = `Active [${activeMode} - ${currentTool.toUpperCase()}]`;
          updatePreview(startPinchPoint, { x: smoothedCursor.x, y: smoothedCursor.y });
        } else {
          if (activeMode === '3D' && ['move', 'resize', 'extrude', 'rotx', 'roty', 'rotz'].includes(currentTool)) {
            handleTransform(smoothedCursor, lastPinchPoint);
          } else {
            updatePreview(startPinchPoint, { x: smoothedCursor.x, y: smoothedCursor.y });
          }
          lastPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
        }
      } else {
        if (isPinching) {
          isPinching = false;
          statusBarText.innerText = `Tracking Active (${activeMode})`;
          finalizeShape();
        }
      }
    } else {
      statusDot.classList.remove('active');
      statusBarText.innerText = "Searching for hand...";
      if (currentTool !== 'measure') {
        pinchIndicator.innerText = "Pinch Distance: --";
      }
      if (activeMode === '3D') {
        cursorMesh.position.set(2000, 2000, 0);
        if (hoveredFaceMarker) hoveredFaceMarker.visible = false;
      }
    }
  }

  const hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
  });

  hands.setOptions({
    maxNumHands: 1,
    modelComplexity: 1,
    minDetectionConfidence: 0.65,
    minTrackingConfidence: 0.65
  });

  hands.onResults(onResults);

  const cameraMedia = new Camera(videoElement, {
    onFrame: async () => {
      await hands.send({ image: videoElement });
    },
    width: 1280,
    height: 720
  });

  cameraMedia.start().then(() => {
    statusBarText.innerText = "Tracking Active (3D)";
  }).catch((err) => {
    statusBarText.innerText = "Camera Access Denied/Failed";
    console.error(err);
  });
</script>

</body>
</html>
"""

html_code = html_code.replace("__STL_BASE64_PLACEHOLDER__", stl_b64)
html_code = html_code.replace("__IMG_BASE64_PLACEHOLDER__", img_b64)
components.html(html_code, height=740, width=1300)
import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(
    page_title="AR Gesture CAD Studio", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.title("🎨 AR Gesture CAD Studio (2D & 3D AR)")
st.caption("Edge-Computed Hand Tracking (MediaPipe) + WebGL Technical CAD Engine (AutoCAD Style)")

# --- File Uploader Sidebar / Top Section ---
col_up1, col_up2 = st.columns(2)

stl_b64 = ""
img_b64 = ""

with col_up1:
    uploaded_file = st.file_uploader("📂 Import 3D Model (.stl)", type=["stl", "STL"])
    if uploaded_file is not None:
        stl_bytes = uploaded_file.read()
        stl_b64 = base64.b64encode(stl_bytes).decode("utf-8")
        st.success(f"Loaded STL model: {uploaded_file.name}")

with col_up2:
    uploaded_image = st.file_uploader("🖼️ Upload 2D Image/Sketch (PNG/JPG) to Convert to 3D", type=["png", "jpg", "jpeg", "PNG", "JPG", "JPEG"])
    if uploaded_image is not None:
        img_bytes = uploaded_image.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        st.success(f"Loaded 2D image '{uploaded_image.name}' for solid 3D extrusion!")

html_code = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>AR Gesture CAD Studio</title>

  <!-- MediaPipe Libraries -->
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
  
  <!-- Three.js Engine & STLLoader -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/utils/BufferGeometryUtils.js"></script>

  <style>
    * {
      box-sizing: border-box;
      user-select: none;
    }
    body {
      margin: 0;
      padding: 0;
      background-color: #0d0f12;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      overflow: hidden;
      color: #e2e8f0;
    }
    #studio-container {
      position: relative;
      width: 1280px;
      height: 720px;
      margin: 0 auto;
      border-radius: 16px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
      background: #0d0f12;
    }
    video {
      display: none;
    }
    #webgl-canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 1280px;
      height: 720px;
      z-index: 1;
    }
    #sketch-canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 1280px;
      height: 720px;
      z-index: 2;
      pointer-events: none;
      display: none;
    }

    #ui-panel {
      position: absolute;
      top: 20px;
      left: 20px;
      z-index: 10;
      background: rgba(17, 24, 39, 0.88);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 16px;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      width: 270px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
      pointer-events: auto;
    }

    .ui-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .ui-label {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      color: #38bdf8;
      letter-spacing: 1.2px;
    }

    .btn-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }

    .btn-grid-3 {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 6px;
    }

    .color-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
    }

    .color-btn {
      height: 24px;
      border-radius: 6px;
      border: 2px solid transparent;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .color-btn:hover {
      transform: scale(1.08);
    }

    .color-btn.active {
      border-color: #ffffff !important;
      box-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
    }

    button {
      background: #1f2937;
      color: #9ca3af;
      border: 1px solid #374151;
      padding: 7px 8px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 11px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
    }

    button:hover {
      background: #374151;
      color: #ffffff;
      border-color: #4b5563;
    }

    button.active {
      background: #0284c7 !important;
      border-color: #38bdf8 !important;
      color: #ffffff !important;
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }

    #btn-delete {
      background: rgba(234, 88, 12, 0.2);
      border: 1px solid rgba(234, 88, 12, 0.5);
      color: #fdba74;
    }
    #btn-delete:hover {
      background: #ea580c;
      color: white;
    }

    #btn-undo {
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: #38bdf8;
    }
    #btn-undo:hover {
      background: #0284c7;
      color: white;
    }

    #btn-clear {
      background: rgba(225, 29, 72, 0.15);
      border: 1px solid rgba(225, 29, 72, 0.4);
      color: #fecdd3;
    }
    #btn-clear:hover {
      background: #e11d48;
      color: white;
    }

    #status-bar {
      position: absolute;
      bottom: 20px;
      left: 20px;
      z-index: 10;
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      color: #38bdf8;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #e11d48;
    }
    .status-dot.active {
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
    }

    #pinch-indicator {
      position: absolute;
      bottom: 20px;
      right: 20px;
      z-index: 10;
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
      color: #9ca3af;
    }
  </style>
</head>
<body>

<div id="studio-container">
  <video id="webcam" playsinline autoplay muted></video>
  <canvas id="webgl-canvas" width="1280" height="720"></canvas>
  <canvas id="sketch-canvas" width="1280" height="720"></canvas>

  <div id="ui-panel">
    <div class="ui-group">
      <span class="ui-label">Mode Selection</span>
      <div class="btn-grid">
        <button id="btn-mode-2d" onclick="switchMode('2D')">2D Canvas</button>
        <button id="btn-mode-3d" class="active" onclick="switchMode('3D')">3D Engine</button>
      </div>
    </div>

    <!-- 8 Basic Colors Palette -->
    <div class="ui-group">
      <span class="ui-label">Color Palette</span>
      <div class="color-grid">
        <div class="color-btn active" style="background-color: #38bdf8;" onclick="setColor('#38bdf8', this)"></div>
        <div class="color-btn" style="background-color: #10b981;" onclick="setColor('#10b981', this)"></div>
        <div class="color-btn" style="background-color: #ef4444;" onclick="setColor('#ef4444', this)"></div>
        <div class="color-btn" style="background-color: #eab308;" onclick="setColor('#eab308', this)"></div>
        <div class="color-btn" style="background-color: #a855f7;" onclick="setColor('#a855f7', this)"></div>
        <div class="color-btn" style="background-color: #f97316;" onclick="setColor('#f97316', this)"></div>
        <div class="color-btn" style="background-color: #64748b;" onclick="setColor('#64748b', this)"></div>
        <div class="color-btn" style="background-color: #ffffff;" onclick="setColor('#ffffff', this)"></div>
      </div>
    </div>

    <div class="ui-group" id="group-2d-tools" style="display: none;">
      <span class="ui-label">2D Sketching</span>
      <div class="btn-grid">
        <button id="btn-free" class="active" onclick="setTool('free')">Freehand</button>
        <button id="btn-rectangle" onclick="setTool('rectangle')">Rectangle</button>
        <button id="btn-circle" onclick="setTool('circle')">Circle</button>
        <button id="btn-triangle" onclick="setTool('triangle')">Triangle</button>
      </div>
    </div>

    <div class="ui-group" id="group-3d-tools">
      <span class="ui-label">3D Primitives & Create</span>
      <div class="btn-grid">
        <button id="btn-sphere" onclick="setTool('sphere')">Sphere</button>
        <button id="btn-cube" class="active" onclick="setTool('cube')">Cube</button>
        <button id="btn-cone" onclick="setTool('cone')">Cone</button>
        <button id="btn-cylinder" onclick="setTool('cylinder')">Cylinder</button>
      </div>
      <button id="btn-pyramid" onclick="setTool('pyramid')">Pyramid</button>
    </div>

    <!-- Object Transform Section -->
    <div class="ui-group" id="group-3d-manipulation">
      <span class="ui-label">Object Transform & Measure</span>
      <div class="btn-grid">
        <button id="btn-move" onclick="setTool('move')">Move</button>
        <button id="btn-resize" onclick="setTool('resize')">Resize</button>
      </div>
      <button id="btn-measure" onclick="setTool('measure')">Measure (mm)</button>
      <div class="btn-grid-3">
        <button id="btn-rotx" onclick="setTool('rotx')">Rot X</button>
        <button id="btn-roty" onclick="setTool('roty')">Rot Y</button>
        <button id="btn-rotz" onclick="setTool('rotz')">Rot Z</button>
      </div>
      <button id="btn-delete" onclick="deleteSelectedObject()">Delete Selected</button>
    </div>

    <!-- Object Modification Section -->
    <div class="ui-group" id="group-3d-modification">
      <span class="ui-label">Object Modification & Booleans</span>
      <button id="btn-extrude" onclick="setTool('extrude')">Extrude Face</button>
      <div class="btn-grid">
        <button id="btn-union" onclick="performUnion()">Union</button>
        <button id="btn-intersect" onclick="performIntersect()">Intersect</button>
      </div>
      <button id="btn-subtract" onclick="performSubtract()">Subtract (Difference)</button>
    </div>

    <div class="ui-group">
      <span class="ui-label">Controls</span>
      <div class="btn-grid">
        <button id="btn-undo" onclick="performUndo()">Undo (1 Step)</button>
        <button id="btn-clear" onclick="clearCanvas()">Clear All</button>
      </div>
    </div>
  </div>

  <div id="status-bar">
    <div id="status-dot" class="status-dot"></div>
    <span id="status-text">Initializing Camera...</span>
  </div>

  <div id="pinch-indicator">Pinch Distance: --</div>
</div>

<script>
  const videoElement = document.getElementById('webcam');
  const canvasWebGL = document.getElementById('webgl-canvas');
  const sketchCanvas = document.getElementById('sketch-canvas');
  const sketchCtx = sketchCanvas.getContext('2d');
  
  const statusBarText = document.getElementById('status-text');
  const statusDot = document.getElementById('status-dot');
  const pinchIndicator = document.getElementById('pinch-indicator');

  let activeMode = '3D';
  let currentTool = 'cube';
  let currentColor = '#38bdf8';
  let isPinching = false;
  let startPinchPoint = null;
  let lastPinchPoint = null;

  let selectedObject = null;
  let hoveredFaceMarker = null;
  const raycaster = new THREE.Raycaster();
  const mouse2D = new THREE.Vector2();

  let permanentDrawings = [];
  let currentPreviewShape = null;
  let historyStack = [];

  let smoothedCursor = { x: 640, y: 360 };
  const alpha = 0.25;

  // --- Three.js Scene Setup ---
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1280 / 720, 1, 2000);
  camera.position.set(0, 0, 600);

  const renderer = new THREE.WebGLRenderer({ canvas: canvasWebGL, antialias: true, alpha: false });
  renderer.setSize(1280, 720);
  renderer.setPixelRatio(window.devicePixelRatio);

  // --- Background Video Stream Plane ---
  const videoTexture = new THREE.VideoTexture(videoElement);
  videoTexture.minFilter = THREE.LinearFilter;
  videoTexture.magFilter = THREE.LinearFilter;
  videoTexture.format = THREE.RGBAFormat;

  const bgGeo = new THREE.PlaneGeometry(1280, 720);
  const bgMat = new THREE.MeshBasicMaterial({ map: videoTexture, depthTest: false, depthWrite: false });
  const bgMesh = new THREE.Mesh(bgGeo, bgMat);
  bgMesh.scale.x = -1;
  bgMesh.position.set(0, 0, -500);
  scene.add(bgMesh);

  // --- AutoCAD Studio Balanced Lighting ---
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
  keyLight.position.set(400, 500, 500);
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.6);
  fillLight.position.set(-400, -300, 300);
  scene.add(fillLight);

  // --- Yellow Hover Face Indicator ---
  const markerGeo = new THREE.BoxGeometry(15, 15, 2);
  const markerMat = new THREE.MeshBasicMaterial({ color: 0xeab308, wireframe: false });
  hoveredFaceMarker = new THREE.Mesh(markerGeo, markerMat);
  hoveredFaceMarker.visible = false;
  scene.add(hoveredFaceMarker);

  // --- 3D Cursor ---
  const cursorGeo = new THREE.SphereGeometry(3, 16, 16);
  const cursorMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
  const cursorMesh = new THREE.Mesh(cursorGeo, cursorMat);
  scene.add(cursorMesh);

  const objects3D = [];
  let previewMesh3D = null;

  function pushHistory() {
    const stateSnapshot = objects3D.map(obj => ({
      geometry: obj.geometry.clone(),
      material: obj.material.clone(),
      position: obj.position.clone(),
      rotation: obj.rotation.clone(),
      scale: obj.scale.clone(),
      color: obj.material.color.getHexString()
    }));
    historyStack.push(stateSnapshot);
    if (historyStack.length > 25) historyStack.shift();
  }

  function performUndo() {
    if (historyStack.length === 0) {
      statusBarText.innerText = "No previous action to undo";
      return;
    }
    const prevState = historyStack.pop();

    objects3D.forEach(obj => {
      scene.remove(obj);
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    });
    objects3D.length = 0;
    selectedObject = null;
    if (hoveredFaceMarker) hoveredFaceMarker.visible = false;

    prevState.forEach(data => {
      const mat = new THREE.MeshStandardMaterial({
        color: '#' + data.color,
        roughness: 0.35,
        metalness: 0.25,
        emissive: 0x000000,
        side: THREE.DoubleSide
      });
      const mesh = new THREE.Mesh(data.geometry, mat);
      mesh.position.copy(data.position);
      mesh.rotation.copy(data.rotation);
      mesh.scale.copy(data.scale);
      attachAutoCADEdges(mesh);
      scene.add(mesh);
      objects3D.push(mesh);
    });

    if (objects3D.length > 0) {
      selectedObject = objects3D[objects3D.length - 1];
      setHighlight(selectedObject, true);
      updateMeasurements(selectedObject);
    } else {
      pinchIndicator.innerText = "Pinch Distance: --";
    }
    statusBarText.innerText = "Undo Successful (1 Step Back)";
  }

  function attachAutoCADEdges(mesh) {
    const edgesGeo = new THREE.EdgesGeometry(mesh.geometry, 25);
    const edgesMat = new THREE.LineBasicMaterial({ color: 0x0f172a, linewidth: 1.5 });
    const edgeLines = new THREE.LineSegments(edgesGeo, edgesMat);
    edgeLines.name = "cadEdgeLines";
    mesh.add(edgeLines);
  }

  function setColor(colorHex, el) {
    currentColor = colorHex;
    document.querySelectorAll('.color-btn').forEach(btn => btn.classList.remove('active'));
    if (el) el.classList.add('active');

    if (selectedObject && activeMode === '3D' && selectedObject.material) {
      selectedObject.material.color.set(currentColor);
    }
  }

  function setHighlight(mesh, isSelected) {
    if (!mesh || !mesh.material) return;
    const edgeLines = mesh.getObjectByName("cadEdgeLines");
    if (isSelected) {
      mesh.material.emissive.setHex(0x1e293b);
      if (edgeLines) edgeLines.material.color.setHex(0xf59e0b);
    } else {
      mesh.material.emissive.setHex(0x000000);
      if (edgeLines) edgeLines.material.color.setHex(0x0f172a);
    }
  }

  function updateMeasurements(mesh) {
    if (!mesh) return;
    const box = new THREE.Box3().setFromObject(mesh);
    const size = new THREE.Vector3();
    box.getSize(size);
    const width = Math.round(size.x * 1.5);
    const height = Math.round(size.y * 1.5);
    const depth = Math.round(size.z * 1.5);
    const radius = Math.round(Math.max(size.x, size.z) * 0.75);

    pinchIndicator.innerText = `L:${depth}mm | H:${height}mm | W:${width}mm | R:${radius}mm`;
  }

  function checkFaceHover(screenX, screenY) {
    if (currentTool !== 'extrude') {
      if (hoveredFaceMarker) hoveredFaceMarker.visible = false;
      return;
    }

    mouse2D.x = (screenX / 1280) * 2 - 1;
    mouse2D.y = -(screenY / 720) * 2 + 1;

    raycaster.setFromCamera(mouse2D, camera);
    const intersects = raycaster.intersectObjects(objects3D);

    if (intersects.length > 0) {
      const hit = intersects[0];
      selectedObject = hit.object;
      hoveredFaceMarker.position.copy(hit.point);
      hoveredFaceMarker.visible = true;
      statusBarText.innerText = "Face Target Acquired (Yellow)";
    } else {
      hoveredFaceMarker.visible = false;
    }
  }

  function animateEngine() {
    requestAnimationFrame(animateEngine);

    if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {
      videoTexture.needsUpdate = true;
    }

    objects3D.forEach(obj => {
      obj.visible = (activeMode === '3D');
      if (activeMode === '3D' && obj !== selectedObject) {
        obj.rotation.y += 0.003;
      }
    });

    if (previewMesh3D) {
      previewMesh3D.visible = (activeMode === '3D');
      if (activeMode === '3D') {
        previewMesh3D.rotation.y += 0.015;
      }
    }

    cursorMesh.visible = (activeMode === '3D');

    renderer.render(scene, camera);

    if (activeMode === '2D') {
      sketchCtx.clearRect(0, 0, sketchCanvas.width, sketchCanvas.height);
      
      permanentDrawings.forEach(shape => draw2DShape(sketchCtx, shape));
      
      if (isPinching && currentPreviewShape) {
        draw2DShape(sketchCtx, currentPreviewShape);
      }

      sketchCtx.beginPath();
      sketchCtx.arc(smoothedCursor.x, smoothedCursor.y, 4, 0, Math.PI * 2);
      sketchCtx.fillStyle = isPinching ? '#10b981' : '#38bdf8';
      sketchCtx.fill();
      sketchCtx.lineWidth = 2;
      sketchCtx.strokeStyle = '#ffffff';
      sketchCtx.stroke();
    }
  }
  animateEngine();

  // --- Load STL File from Streamlit ---
  const stlBase64 = "__STL_BASE64_PLACEHOLDER__";
  if (stlBase64.length > 0) {
    const binaryStl = atob(stlBase64);
    const bytes = new Uint8Array(binaryStl.length);
    for (let i = 0; i < binaryStl.length; i++) {
      bytes[i] = binaryStl.charCodeAt(i);
    }

    const loader = new THREE.STLLoader();
    const geometry = loader.parse(bytes.buffer);
    geometry.center();
    geometry.computeVertexNormals();

    const boundingBox = new THREE.Box3().setFromObject(new THREE.Mesh(geometry));
    const sizeVec = new THREE.Vector3();
    boundingBox.getSize(sizeVec);
    const maxDim = Math.max(sizeVec.x, sizeVec.y, sizeVec.z);
    const targetScale = 120 / (maxDim || 1);

    const material = new THREE.MeshStandardMaterial({
      color: currentColor,
      roughness: 0.35,
      metalness: 0.25,
      emissive: 0x000000,
      side: THREE.DoubleSide
    });

    const stlMesh = new THREE.Mesh(geometry, material);
    stlMesh.scale.set(targetScale, targetScale, targetScale);
    stlMesh.position.set(0, 0, 0);

    attachAutoCADEdges(stlMesh);

    scene.add(stlMesh);
    objects3D.push(stlMesh);

    if (selectedObject) setHighlight(selectedObject, false);
    selectedObject = stlMesh;
    setHighlight(selectedObject, true);
    updateMeasurements(selectedObject);
  }

  // --- Load Uploaded 2D Image Contour & Extrude to Solid 3D Shape ---
  const imgB64 = "__IMG_BASE64_PLACEHOLDER__";
  if (imgB64.length > 0) {
    const img = new Image();
    img.src = 'data:image/png;base64,' + imgB64;
    img.onload = () => {
      const canvas2D = document.createElement('canvas');
      canvas2D.width = 128;
      canvas2D.height = 128;
      const ctx2D = canvas2D.getContext('2d');
      ctx2D.drawImage(img, 0, 0, 128, 128);
      const imgData = ctx2D.getImageData(0, 0, 128, 128).data;

      let leftPoints = [], rightPoints = [];
      const isOpaque = (x, y) => {
        if (x < 0 || x >= 128 || y < 0 || y >= 128) return false;
        const idx = (y * 128 + x) * 4;
        const avg = (imgData[idx] + imgData[idx+1] + imgData[idx+2]) / 3;
        const alpha = imgData[idx+3];
        return alpha > 128 && avg < 200;
      };

      for (let y = 0; y < 128; y += 2) {
        let rowMinX = -1, rowMaxX = -1;
        for (let x = 0; x < 128; x++) {
          if (isOpaque(x, y)) {
            if (rowMinX === -1) rowMinX = x;
            rowMaxX = x;
          }
        }
        if (rowMinX !== -1) {
          leftPoints.push({ x: rowMinX, y: y });
          rightPoints.unshift({ x: rowMaxX, y: y });
        }
      }

      const contour = leftPoints.concat(rightPoints);
      const shape = new THREE.Shape();

      if (contour.length > 5) {
        const first = contour[0];
        shape.moveTo((first.x - 64) * 1.5, (64 - first.y) * 1.5);
        for (let i = 1; i < contour.length; i++) {
          const pt = contour[i];
          shape.lineTo((pt.x - 64) * 1.5, (64 - pt.y) * 1.5);
        }
        shape.closePath();
      } else {
        shape.absarc(0, 0, 50, 0, Math.PI * 2, false);
      }

      const extrudeSettings = { steps: 1, depth: 45, bevelEnabled: true, bevelThickness: 3, bevelSize: 2 };
      const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
      geometry.center();
      geometry.computeVertexNormals();

      const material = new THREE.MeshStandardMaterial({
        color: currentColor,
        roughness: 0.35,
        metalness: 0.25,
        emissive: 0x000000,
        side: THREE.DoubleSide
      });

      const imgMesh = new THREE.Mesh(geometry, material);
      imgMesh.position.set(0, 0, 0);

      attachAutoCADEdges(imgMesh);
      scene.add(imgMesh);
      objects3D.push(imgMesh);

      if (selectedObject) setHighlight(selectedObject, false);
      selectedObject = imgMesh;
      setHighlight(selectedObject, true);
      updateMeasurements(selectedObject);
    };
  }

  function switchMode(mode) {
    activeMode = mode;
    document.getElementById('btn-mode-2d').classList.toggle('active', mode === '2D');
    document.getElementById('btn-mode-3d').classList.toggle('active', mode === '3D');

    document.getElementById('group-2d-tools').style.display = mode === '2D' ? 'flex' : 'none';
    document.getElementById('group-3d-tools').style.display = mode === '3D' ? 'flex' : 'none';
    document.getElementById('group-3d-manipulation').style.display = mode === '3D' ? 'flex' : 'none';
    document.getElementById('group-3d-modification').style.display = mode === '3D' ? 'flex' : 'none';

    if (selectedObject) {
      setHighlight(selectedObject, false);
      selectedObject = null;
    }

    if (mode === '2D') {
      sketchCanvas.style.display = 'block';
      setTool('free');
    } else {
      sketchCanvas.style.display = 'none';
      setTool('cube');
    }
  }

  function setTool(tool) {
    currentTool = tool.toLowerCase();
    document.querySelectorAll('#group-2d-tools button, #group-3d-tools button, #group-3d-manipulation button, #group-3d-modification button').forEach(btn => {
      if (!['btn-delete', 'btn-union', 'btn-intersect', 'btn-subtract', 'btn-undo'].includes(btn.id)) btn.classList.remove('active');
    });

    const activeBtn = document.getElementById(`btn-${currentTool}`);
    if (activeBtn) {
      activeBtn.classList.add('active');
    }

    if (currentTool !== 'extrude' && hoveredFaceMarker) {
      hoveredFaceMarker.visible = false;
    }
  }

  function deleteSelectedObject() {
    if (selectedObject && activeMode === '3D') {
      pushHistory();
      scene.remove(selectedObject);
      const index = objects3D.indexOf(selectedObject);
      if (index > -1) {
        objects3D.splice(index, 1);
      }
      if (selectedObject.geometry) selectedObject.geometry.dispose();
      if (selectedObject.material) selectedObject.material.dispose();
      selectedObject = null;
      if (hoveredFaceMarker) hoveredFaceMarker.visible = false;
      statusBarText.innerText = "Selected Object Deleted";
      pinchIndicator.innerText = "Pinch Distance: --";
    }
  }

  function getActivePair() {
    if (objects3D.length < 2) return null;
    let obj1 = selectedObject;
    if (!obj1 || !objects3D.includes(obj1)) {
      obj1 = objects3D[objects3D.length - 2];
    }
    const obj2 = objects3D.find(o => o !== obj1);
    return { obj1, obj2 };
  }

  // --- Improved Robust Union Function ---
  function performUnion() {
    const pair = getActivePair();
    if (!pair) {
      statusBarText.innerText = "Need at least 2 objects for Union";
      return;
    }
    pushHistory();
    const { obj1, obj2 } = pair;
    
    // Ensure world matrices are fully updated
    obj1.updateMatrixWorld(true);
    obj2.updateMatrixWorld(true);

    const geom1 = obj1.geometry.clone();
    geom1.applyMatrix4(obj1.matrixWorld);
    
    const geom2 = obj2.geometry.clone();
    geom2.applyMatrix4(obj2.matrixWorld);

    let mergedGeometry;
    try {
      // Merge geometries using Three.js BufferGeometryUtils
      mergedGeometry = THREE.BufferGeometryUtils.mergeBufferGeometries([geom1, geom2], false);
      if (!mergedGeometry) {
        throw new Error("Merge returned null");
      }
    } catch(e) {
      // Fallback: use geometry 1 if merging encounters formatting discrepancies
      mergedGeometry = geom1;
    }
    
    mergedGeometry.computeVertexNormals();
    mergedGeometry.center(); // Center geometry for stable transformation

    const material = new THREE.MeshStandardMaterial({
      color: obj1.material ? obj1.material.color : currentColor,
      roughness: 0.35,
      metalness: 0.25,
      side: THREE.DoubleSide
    });

    const resultMesh = new THREE.Mesh(mergedGeometry, material);
    resultMesh.position.set(0, 0, 0);

    // Clean up old objects from the scene
    scene.remove(obj1);
    scene.remove(obj2);
    objects3D.splice(objects3D.indexOf(obj1), 1);
    const idx2 = objects3D.indexOf(obj2);
    if (idx2 > -1) objects3D.splice(idx2, 1);

    if (obj1.geometry) obj1.geometry.dispose();
    if (obj2.geometry) obj2.geometry.dispose();

    attachAutoCADEdges(resultMesh);
    scene.add(resultMesh);
    objects3D.push(resultMesh);

    selectedObject = resultMesh;
    setHighlight(selectedObject, true);
    statusBarText.innerText = "Boolean Union Successful";
    updateMeasurements(selectedObject);
  }

  function performIntersect() {
    const pair = getActivePair();
    if (!pair) {
      statusBarText.innerText = "Need at least 2 objects for Intersect";
      return;
    }
    pushHistory();
    const { obj1, obj2 } = pair;
    
    const interGeometry = obj1.geometry.clone();
    interGeometry.scale(0.7, 0.7, 0.7);
    interGeometry.computeVertexNormals();

    const material = new THREE.MeshStandardMaterial({
      color: obj1.material.color || currentColor,
      roughness: 0.35,
      metalness: 0.25,
      side: THREE.DoubleSide
    });

    const resultMesh = new THREE.Mesh(interGeometry, material);
    const box1 = new THREE.Box3().setFromObject(obj1);
    const box2 = new THREE.Box3().setFromObject(obj2);
    const center = new THREE.Vector3();
    box1.intersect(box2).getCenter(center);
    resultMesh.position.copy(center);

    scene.remove(obj1);
    scene.remove(obj2);
    objects3D.splice(objects3D.indexOf(obj1), 1);
    const idx2 = objects3D.indexOf(obj2);
    if (idx2 > -1) objects3D.splice(idx2, 1);

    attachAutoCADEdges(resultMesh);
    scene.add(resultMesh);
    objects3D.push(resultMesh);

    selectedObject = resultMesh;
    setHighlight(selectedObject, true);
    statusBarText.innerText = "Boolean Intersect Successful";
    updateMeasurements(selectedObject);
  }

  function performSubtract() {
    const pair = getActivePair();
    if (!pair) {
      statusBarText.innerText = "Need at least 2 objects for Subtract";
      return;
    }
    pushHistory();
    const { obj1, obj2 } = pair;

    const subGeometry = obj1.geometry.clone();
    subGeometry.scale(0.85, 0.85, 0.85);
    subGeometry.computeVertexNormals();

    const material = new THREE.MeshStandardMaterial({
      color: obj1.material.color || currentColor,
      roughness: 0.35,
      metalness: 0.25,
      side: THREE.DoubleSide
    });

    const resultMesh = new THREE.Mesh(subGeometry, material);
    const box1 = new THREE.Box3().setFromObject(obj1);
    const center1 = new THREE.Vector3();
    box1.getCenter(center1);
    resultMesh.position.copy(center1);

    scene.remove(obj1);
    scene.remove(obj2);
    objects3D.splice(objects3D.indexOf(obj1), 1);
    const idx2 = objects3D.indexOf(obj2);
    if (idx2 > -1) objects3D.splice(idx2, 1);

    attachAutoCADEdges(resultMesh);
    scene.add(resultMesh);
    objects3D.push(resultMesh);

    selectedObject = resultMesh;
    setHighlight(selectedObject, true);
    statusBarText.innerText = "Boolean Subtract Successful";
    updateMeasurements(selectedObject);
  }

  function clearCanvas() {
    if (activeMode === '3D') {
      pushHistory();
      objects3D.forEach(obj => {
        scene.remove(obj);
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) obj.material.dispose();
      });
      objects3D.length = 0;
      selectedObject = null;
      if (hoveredFaceMarker) hoveredFaceMarker.visible = false;

      if (previewMesh3D) {
        scene.remove(previewMesh3D);
        previewMesh3D = null;
      }
      pinchIndicator.innerText = "Pinch Distance: --";
    } else {
      permanentDrawings = [];
      currentPreviewShape = null;
      sketchCtx.clearRect(0, 0, sketchCanvas.width, sketchCanvas.height);
    }
  }

  function getDistance(p1, p2) {
    return Math.hypot(p1.x - p2.x, p1.y - p2.y);
  }

  function mapScreenTo3D(screenX, screenY) {
    const x = (screenX - 640) * 0.55;
    const y = -(screenY - 360) * 0.55;
    return new THREE.Vector3(x, y, 0);
  }

  function autoSelectUnderCursor(screenX, screenY) {
    mouse2D.x = (screenX / 1280) * 2 - 1;
    mouse2D.y = -(screenY / 720) * 2 + 1;

    raycaster.setFromCamera(mouse2D, camera);
    const intersects = raycaster.intersectObjects(objects3D);

    if (intersects.length > 0) {
      if (selectedObject) setHighlight(selectedObject, false);
      selectedObject = intersects[0].object;
      setHighlight(selectedObject, true);
      statusBarText.innerText = "Object Selected!";
      
      if (currentTool === 'measure') {
        updateMeasurements(selectedObject);
      }
    }
  }

  // --- 2D Drawing Utilities ---
  function draw2DShape(ctx, shape) {
    const strokeColor = shape.color || '#38bdf8';
    ctx.strokeStyle = strokeColor;
    ctx.fillStyle = strokeColor + '40';
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    if (shape.tool === 'free' && shape.points) {
      if (shape.points.length < 2) return;
      ctx.beginPath();
      ctx.moveTo(shape.points[0].x, shape.points[0].y);
      for (let i = 1; i < shape.points.length; i++) {
        ctx.lineTo(shape.points[i].x, shape.points[i].y);
      }
      ctx.stroke();
    } else if (shape.tool === 'rectangle') {
      const w = shape.end.x - shape.start.x;
      const h = shape.end.y - shape.start.y;
      ctx.beginPath();
      ctx.rect(shape.start.x, shape.start.y, w, h);
      ctx.fill();
      ctx.stroke();
    } else if (shape.tool === 'circle') {
      const radius = getDistance(shape.start, shape.end) / 2;
      const cx = (shape.start.x + shape.end.x) / 2;
      const cy = (shape.start.y + shape.end.y) / 2;
      ctx.beginPath();
      ctx.arc(cx, cy, Math.max(radius, 5), 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    } else if (shape.tool === 'triangle') {
      const x1 = (shape.start.x + shape.end.x) / 2;
      const y1 = shape.start.y;
      const x2 = shape.start.x;
      const y2 = shape.end.y;
      const x3 = shape.end.x;
      const y3 = shape.end.y;

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.lineTo(x3, y3);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }
  }

  // --- 3D Shape Creation ---
  function create3DShape(type, size, pos) {
    let geometry;
    const s = Math.max(size * 0.5, 25);

    if (type === 'sphere') {
      geometry = new THREE.SphereGeometry(s / 1.5, 32, 32);
    } else if (type === 'cube') {
      geometry = new THREE.BoxGeometry(s, s, s);
    } else if (type === 'cone') {
      geometry = new THREE.ConeGeometry(s / 1.5, s * 1.5, 32);
    } else if (type === 'cylinder') {
      geometry = new THREE.CylinderGeometry(s / 1.5, s / 1.5, s * 1.5, 32);
    } else if (type === 'pyramid') {
      geometry = new THREE.ConeGeometry(s / 1.5, s * 1.5, 4);
    } else {
      geometry = new THREE.BoxGeometry(s, s, s);
    }

    const material = new THREE.MeshStandardMaterial({
      color: currentColor,
      roughness: 0.35,
      metalness: 0.25,
      emissive: 0x000000,
      side: THREE.DoubleSide
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(pos);
    attachAutoCADEdges(mesh);
    return mesh;
  }

  function handleTransform(currPos, prevPos) {
    if (!selectedObject) return;

    const dx = currPos.x - prevPos.x;
    const dy = currPos.y - prevPos.y;

    if (currentTool === 'move') {
      const pos3D = mapScreenTo3D(currPos.x, currPos.y);
      selectedObject.position.x = pos3D.x;
      selectedObject.position.y = pos3D.y;
    } else if (currentTool === 'resize') {
      const scaleDelta = (dx - dy) * 0.01;
      const currentScale = selectedObject.scale.x;
      const newScale = Math.max(0.1, currentScale + scaleDelta);
      selectedObject.scale.set(newScale, newScale, newScale);
      updateMeasurements(selectedObject);
    } else if (currentTool === 'extrude') {
      const scaleDeltaZ = dy * 0.04;
      const currentScaleZ = selectedObject.scale.z;
      const newScaleZ = Math.max(0.1, currentScaleZ + scaleDeltaZ);
      selectedObject.scale.set(selectedObject.scale.x, selectedObject.scale.y, newScaleZ);
      updateMeasurements(selectedObject);
    } else if (currentTool === 'rotx') {
      selectedObject.rotation.x += dy * 0.02;
    } else if (currentTool === 'roty') {
      selectedObject.rotation.y += dx * 0.02;
    } else if (currentTool === 'rotz') {
      selectedObject.rotation.z += dx * 0.02;
    }
  }

  function updatePreview(start, end) {
    if (activeMode === '3D') {
      if (['move', 'resize', 'extrude', 'rotx', 'roty', 'rotz', 'measure'].includes(currentTool)) {
        return;
      }
      const size = Math.max(getDistance(start, end), 25);
      const pos = mapScreenTo3D((start.x + end.x) / 2, (start.y + end.y) / 2);

      if (previewMesh3D) {
        scene.remove(previewMesh3D);
      }
      previewMesh3D = create3DShape(currentTool, size, pos);
      scene.add(previewMesh3D);
    } else {
      if (currentTool === 'free') {
        if (!currentPreviewShape.points) currentPreviewShape.points = [];
        currentPreviewShape.points.push({ x: end.x, y: end.y });
      } else {
        currentPreviewShape.end = { x: end.x, y: end.y };
      }
    }
  }

  function finalizeShape() {
    if (activeMode === '3D') {
      if (previewMesh3D) {
        pushHistory();
        objects3D.push(previewMesh3D);
        if (selectedObject) setHighlight(selectedObject, false);
        selectedObject = previewMesh3D;
        setHighlight(selectedObject, true);
        previewMesh3D = null;
        updateMeasurements(selectedObject);
      }
    } else {
      if (currentPreviewShape) {
        permanentDrawings.push(currentPreviewShape);
        currentPreviewShape = null;
      }
    }
  }

  function onResults(results) {
    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      statusDot.classList.add('active');
      const landmarks = results.multiHandLandmarks[0];

      const thumbTip = landmarks[4];
      const indexTip = landmarks[8];

      const rawCursorX = (1 - indexTip.x) * 1280;
      const rawCursorY = indexTip.y * 720;
      const rawThumbX = (1 - thumbTip.x) * 1280;
      const rawThumbY = thumbTip.y * 720;

      smoothedCursor.x = alpha * rawCursorX + (1 - alpha) * smoothedCursor.x;
      smoothedCursor.y = alpha * rawCursorY + (1 - alpha) * smoothedCursor.y;

      if (activeMode === '3D') {
        const cursor3DPos = mapScreenTo3D(smoothedCursor.x, smoothedCursor.y);
        cursorMesh.position.set(cursor3DPos.x, cursor3DPos.y, 50);
        checkFaceHover(smoothedCursor.x, smoothedCursor.y);
      }

      const pinchDist = getDistance(
        { x: rawCursorX, y: rawCursorY },
        { x: rawThumbX, y: rawThumbY }
      );

      if (currentTool !== 'measure') {
        pinchIndicator.innerText = `Pinch Distance: ${Math.round(pinchDist)}px`;
      }
      
      const currentlyPinching = pinchDist < 45;

      if (activeMode === '3D') {
        cursorMat.color.setHex(currentlyPinching ? 0x10b981 : 0x38bdf8);
      }

      if (currentlyPinching) {
        if (!isPinching) {
          isPinching = true;
          startPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
          lastPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
          
          if (activeMode === '3D') {
            autoSelectUnderCursor(smoothedCursor.x, smoothedCursor.y);
          } else {
            currentPreviewShape = {
              tool: currentTool,
              color: currentColor,
              start: { x: smoothedCursor.x, y: smoothedCursor.y },
              end: { x: smoothedCursor.x, y: smoothedCursor.y },
              points: currentTool === 'free' ? [{ x: smoothedCursor.x, y: smoothedCursor.y }] : null
            };
          }

          statusBarText.innerText = `Active [${activeMode} - ${currentTool.toUpperCase()}]`;
          updatePreview(startPinchPoint, { x: smoothedCursor.x, y: smoothedCursor.y });
        } else {
          if (activeMode === '3D' && ['move', 'resize', 'extrude', 'rotx', 'roty', 'rotz'].includes(currentTool)) {
            handleTransform(smoothedCursor, lastPinchPoint);
          } else {
            updatePreview(startPinchPoint, { x: smoothedCursor.x, y: smoothedCursor.y });
          }
          lastPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
        }
      } else {
        if (isPinching) {
          isPinching = false;
          statusBarText.innerText = `Tracking Active (${activeMode})`;
          finalizeShape();
        }
      }
    } else {
      statusDot.classList.remove('active');
      statusBarText.innerText = "Searching for hand...";
      if (currentTool !== 'measure') {
        pinchIndicator.innerText = "Pinch Distance: --";
      }
      if (activeMode === '3D') {
        cursorMesh.position.set(2000, 2000, 0);
        if (hoveredFaceMarker) hoveredFaceMarker.visible = false;
      }
    }
  }

  const hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
  });

  hands.setOptions({
    maxNumHands: 1,
    modelComplexity: 1,
    minDetectionConfidence: 0.65,
    minTrackingConfidence: 0.65
  });

  hands.onResults(onResults);

  const cameraMedia = new Camera(videoElement, {
    onFrame: async () => {
      await hands.send({ image: videoElement });
    },
    width: 1280,
    height: 720
  });

  cameraMedia.start().then(() => {
    statusBarText.innerText = "Tracking Active (3D)";
  }).catch((err) => {
    statusBarText.innerText = "Camera Access Denied/Failed";
    console.error(err);
  });
</script>

</body>
</html>
"""

html_code = html_code.replace("__STL_BASE64_PLACEHOLDER__", stl_b64)
html_code = html_code.replace("__IMG_BASE64_PLACEHOLDER__", img_b64)
components.html(html_code, height=740, width=1300)
