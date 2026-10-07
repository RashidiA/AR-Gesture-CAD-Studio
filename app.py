import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AR 3D Hand Drawing Studio", layout="wide")

st.title("🎨 AR Gesture CAD Studio (2D & 3D)")
st.caption("Edge-Computed WebAssembly Tracking (MediaPipe Hands) + WebGL 3D Rendering Engine (Three.js)")

html_code = """
<!DOCTYPE html>
<html>
<head>
  <!-- MediaPipe Libraries -->
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
  
  <!-- Three.js Engine for 3D & AR Rendering -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

  <style>
    body {
      margin: 0;
      padding: 0;
      background-color: #121212;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      overflow: hidden;
      color: #ffffff;
    }
    #studio-container {
      position: relative;
      width: 1100px;
      height: 650px;
      margin: 0 auto;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0,0,0,0.6);
      background: #1a1a1a;
    }
    video {
      display: none;
    }
    #canvas-container {
      position: absolute;
      top: 0;
      left: 0;
      width: 1100px;
      height: 650px;
    }
    /* Mirror 2D canvas overlay for video feed and tracking cues */
    #2d-canvas {
      position: absolute;
      top: 0;
      left: 0;
      transform: scaleX(-1);
      z-index: 1;
    }
    /* WebGL Three.js Overlay */
    #3d-canvas {
      position: absolute;
      top: 0;
      left: 0;
      z-index: 2;
      pointer-events: none;
    }

    /* Tinkercad-Style Toolbar UI */
    #ui-panel {
      position: absolute;
      top: 15px;
      left: 15px;
      z-index: 10;
      background: rgba(30, 30, 30, 0.85);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 12px;
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      width: 220px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }

    .ui-group {
      display: flex;
      flex-direction: column;
      gap: 5px;
    }

    .ui-label {
      font-size: 11px;
      font-weight: bold;
      text-transform: uppercase;
      color: #00b4d8;
      letter-spacing: 1px;
    }

    .btn-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }

    button {
      background: #2b2b2b;
      color: #fff;
      border: 1px solid #444;
      padding: 8px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    button:hover {
      background: #00b4d8;
      border-color: #00b4d8;
      color: #000;
    }

    button.active {
      background: #00ff88 !important;
      border-color: #00ff88 !important;
      color: #000 !important;
    }

    /* Status Bar */
    #status-bar {
      position: absolute;
      bottom: 15px;
      left: 15px;
      z-index: 10;
      background: rgba(0, 0, 0, 0.7);
      padding: 8px 15px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: bold;
      color: #00ff88;
    }
  </style>
</head>
<body>

<div id="studio-container">
  <video id="webcam" playsinline></video>
  <div id="canvas-container">
    <canvas id="2d-canvas" width="1100" height="650"></canvas>
    <canvas id="3d-canvas" width="1100" height="650"></canvas>
  </div>

  <!-- Tinkercad-inspired Controls -->
  <div id="ui-panel">
    <div class="ui-group">
      <span class="ui-label">Dimension Mode</span>
      <div class="btn-grid">
        <button id="btn-2d" class="active" onclick="setDimensionMode('2D')">2D Plane</button>
        <button id="btn-3d" onclick="setDimensionMode('3D')">3D Solid</button>
      </div>
    </div>

    <div class="ui-group">
      <span class="ui-label">Drawing Tools</span>
      <div class="btn-grid">
        <button id="btn-free" class="active" onclick="setTool('free')">Freehand</button>
        <button id="btn-rect" onclick="setTool('rectangle')">Rectangle</button>
        <button id="btn-circle" onclick="setTool('circle')">Circle</button>
        <button id="btn-triangle" onclick="setTool('triangle')">Triangle</button>
      </div>
    </div>

    <div class="ui-group" id="3d-tools-group">
      <span class="ui-label">3D Primitives</span>
      <div class="btn-grid">
        <button id="btn-cube" onclick="setTool('cube')">Cube</button>
        <button id="btn-sphere" onclick="setTool('sphere')">Sphere</button>
        <button id="btn-cone" onclick="setTool('cone')">Cone</button>
        <button id="btn-extrude" onclick="setTool('extrude')">Extrude Z</button>
      </div>
    </div>

    <div class="ui-group">
      <span class="ui-label">Canvas Actions</span>
      <button onclick="clearCanvas()" style="background: #e63946; border: none; color: white;">Clear All</button>
    </div>
  </div>

  <div id="status-bar">Gesture Status: Ready (Pinch Index & Thumb to Draw/Place)</div>
</div>

<script>
  // DOM Elements
  const videoElement = document.getElementById('webcam');
  const canvas2D = document.getElementById('2d-canvas');
  const ctx2D = canvas2D.getContext('2d');
  const canvas3D = document.getElementById('3d-canvas');
  const statusBar = document.getElementById('status-bar');

  // Application State
  let dimensionMode = '2D';
  let currentTool = 'free';
  let isPinching = false;
  let startPinchPoint = null;
  let currentPinchPoint = null;
  let activeDrawnPath = [];

  // Three.js 3D Setup
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1100 / 650, 0.1, 1000);
  camera.position.set(0, 0, 500);

  const renderer = new THREE.WebGLRenderer({ canvas: canvas3D, alpha: true, antialias: true });
  renderer.setSize(1100, 650);

  // Add Lights
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambientLight);
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(200, 300, 400);
  scene.add(directionalLight);

  // Grid Helper (Tinkercad Workplane)
  const gridHelper = new THREE.GridHelper(600, 20, 0x00b4d8, 0x444444);
  gridHelper.rotation.x = Math.PI / 2;
  scene.add(gridHelper);

  const objects3D = [];

  function animate3D() {
    requestAnimationFrame(animate3D);
    renderer.render(scene, camera);
  }
  animate3D();

  // Mode & Tool Switching Logic
  function setDimensionMode(mode) {
    dimensionMode = mode;
    document.getElementById('btn-2d').classList.toggle('active', mode === '2D');
    document.getElementById('btn-3d').classList.toggle('active', mode === '3D');
    gridHelper.visible = (mode === '3D');
    
    if (mode === '3D' && ['free', 'rectangle', 'circle', 'triangle'].includes(currentTool)) {
      setTool('cube');
    } else if (mode === '2D' && ['cube', 'sphere', 'cone', 'extrude'].includes(currentTool)) {
      setTool('free');
    }
  }

  function setTool(tool) {
    currentTool = tool;
    document.querySelectorAll('.btn-grid button').forEach(btn => btn.classList.remove('active'));
    
    const activeBtn = document.getElementById(`btn-${tool}`);
    if (activeBtn) activeBtn.classList.add('active');

    if (['cube', 'sphere', 'cone', 'extrude'].includes(tool)) {
      setDimensionMode('3D');
    }
  }

  function clearCanvas() {
    ctx2D.clearRect(0, 0, canvas2D.width, canvas2D.height);
    objects3D.forEach(obj => scene.remove(obj));
    objects3D.length = 0;
  }

  // Hand Tracking Logic (MediaPipe)
  function getDistance(p1, p2) {
    return Math.hypot((p1.x - p2.x) * 1100, (p1.y - p2.y) * 650);
  }

  function screenTo3D(screenX, screenY, zDepth = 0) {
    // Correct horizontal alignment for Three.js coordinates
    const x = screenX - 550;
    const y = -(screenY - 325);
    return new THREE.Vector3(x, y, zDepth);
  }

  function create3DSolid(tool, start, end) {
    const width = Math.abs(end.x - start.x) || 40;
    const height = Math.abs(end.y - start.y) || 40;
    const depth = Math.max(width, height);

    let geometry;
    const material = new THREE.MeshStandardMaterial({ 
      color: 0x00ff88, 
      roughness: 0.3,
      metalness: 0.2
    });

    if (tool === 'cube') {
      geometry = new THREE.BoxGeometry(width, height, depth);
    } else if (tool === 'sphere') {
      geometry = new THREE.SphereGeometry(width / 2, 32, 32);
    } else if (tool === 'cone') {
      geometry = new THREE.ConeGeometry(width / 2, height, 32);
    }

    if (geometry) {
      const mesh = new THREE.Mesh(geometry, material);
      const pos = screenTo3D((start.x + end.x) / 2, (start.y + end.y) / 2, 0);
      mesh.position.copy(pos);
      scene.add(mesh);
      objects3D.push(mesh);
    }
  }

  function extrudeLastShape(depth) {
    if (activeDrawnPath.length < 3) return;

    const shape = new THREE.Shape();
    const firstPos = screenTo3D(activeDrawnPath[0].x, activeDrawnPath[0].y);
    shape.moveTo(firstPos.x, firstPos.y);

    for (let i = 1; i < activeDrawnPath.length; i++) {
      const pos = screenTo3D(activeDrawnPath[i].x, activeDrawnPath[i].y);
      shape.lineTo(pos.x, pos.y);
    }

    const extrudeSettings = { depth: Math.abs(depth) * 2, bevelEnabled: true, bevelThickness: 2, bevelSize: 2 };
    const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    const material = new THREE.MeshStandardMaterial({ color: 0x00b4d8, roughness: 0.2 });
    const mesh = new THREE.Mesh(geometry, material);
    
    scene.add(mesh);
    objects3D.push(mesh);
  }

  function onResults(results) {
    ctx2D.save();
    ctx2D.clearRect(0, 0, canvas2D.width, canvas2D.height);
    
    // Draw Video Feed onto mirrored 2D canvas
    ctx2D.drawImage(results.image, 0, 0, canvas2D.width, canvas2D.height);

    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      const landmarks = results.multiHandLandmarks[0];

      const thumbTip = landmarks[4];
      const indexTip = landmarks[8];
      const palmCenter = landmarks[9];

      // Native coordinates matching mirrored canvas
      const canvasCursorX = indexTip.x * 1100;
      const canvasCursorY = indexTip.y * 650;

      const canvasPalmX = palmCenter.x * 1100;
      const canvasPalmY = palmCenter.y * 650;

      // Screen-mapped coordinates (Un-mirrored) for 3D calculations
      const screenCursorX = (1 - indexTip.x) * 1100;
      const screenCursorY = indexTip.y * 650;

      // Draw Red Palm Anchor Marker
      ctx2D.fillStyle = '#ff0055';
      ctx2D.beginPath();
      ctx2D.arc(canvasPalmX, canvasPalmY, 12, 0, 2 * Math.PI);
      ctx2D.fill();

      // Measure Pinch (Index + Thumb)
      const pinchDist = getDistance(indexTip, thumbTip);
      const currentlyPinching = pinchDist < 55;

      // Draw Index Fingertip Cursor (Green when pinching, Blue when open)
      ctx2D.fillStyle = currentlyPinching ? '#00ff88' : '#00b4d8';
      ctx2D.beginPath();
      ctx2D.arc(canvasCursorX, canvasCursorY, 10, 0, 2 * Math.PI);
      ctx2D.fill();

      // Gesture State Transitions
      if (currentlyPinching) {
        if (!isPinching) {
          // Pinch Started
          isPinching = true;
          startPinchPoint = { x: screenCursorX, y: screenCursorY, canvasX: canvasCursorX, canvasY: canvasCursorY };
          activeDrawnPath = [{ x: screenCursorX, y: screenCursorY }];
          statusBar.innerText = `Gesture Status: Drawing (${currentTool.toUpperCase()})`;
        } else {
          // Continuous Pinch Drag
          currentPinchPoint = { x: screenCursorX, y: screenCursorY, canvasX: canvasCursorX, canvasY: canvasCursorY };
          activeDrawnPath.push(currentPinchPoint);

          // Real-time 2D Preview Drawing
          if (dimensionMode === '2D' || currentTool === 'free') {
            ctx2D.strokeStyle = '#00ff88';
            ctx2D.lineWidth = 4;
            ctx2D.beginPath();
            ctx2D.moveTo(startPinchPoint.canvasX, startPinchPoint.canvasY);

            if (currentTool === 'free') {
              activeDrawnPath.forEach(pt => ctx2D.lineTo(pt.canvasX || pt.x, pt.canvasY || pt.y));
            } else if (currentTool === 'rectangle') {
              ctx2D.strokeRect(startPinchPoint.canvasX, startPinchPoint.canvasY, currentPinchPoint.canvasX - startPinchPoint.canvasX, currentPinchPoint.canvasY - startPinchPoint.canvasY);
            } else if (currentTool === 'circle') {
              const radius = Math.hypot(currentPinchPoint.canvasX - startPinchPoint.canvasX, currentPinchPoint.canvasY - startPinchPoint.canvasY);
              ctx2D.arc(startPinchPoint.canvasX, startPinchPoint.canvasY, radius, 0, 2 * Math.PI);
            }
            ctx2D.stroke();
          }
        }
      } else {
        if (isPinching) {
          // Pinch Released: Finalize Shape Creation
          isPinching = false;
          statusBar.innerText = "Gesture Status: Pinch Released (Shape Created)";

          if (dimensionMode === '3D') {
            if (['cube', 'sphere', 'cone'].includes(currentTool)) {
              create3DSolid(currentTool, startPinchPoint, currentPinchPoint || startPinchPoint);
            } else if (currentTool === 'extrude') {
              const depth = Math.hypot(currentPinchPoint.x - startPinchPoint.x, currentPinchPoint.y - startPinchPoint.y);
              extrudeLastShape(depth);
            }
          }
        }
      }
    } else {
      statusBar.innerText = "Gesture Status: Looking for hand...";
    }

    ctx2D.restore();
  }

  // Camera & MediaPipe Initialization
  const hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
  });

  hands.setOptions({
    maxNumHands: 1,
    modelComplexity: 1,
    minDetectionConfidence: 0.6,
    minTrackingConfidence: 0.6
  });

  hands.onResults(onResults);

  const cameraMedia = new Camera(videoElement, {
    onFrame: async () => {
      await hands.send({ image: videoElement });
    },
    width: 1100,
    height: 650
  });

  cameraMedia.start();
</script>

</body>
</html>
"""

components.html(html_code, height=670, width=1120)
