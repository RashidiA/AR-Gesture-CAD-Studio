import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="AR Gesture CAD Studio", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.title("🎨 AR Gesture CAD Studio (2D & 3D)")
st.caption("Edge-Computed Hand Tracking (MediaPipe) + WebGL 3D Parametric CAD Engine (Three.js)")

html_code = r"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>AR Gesture CAD Studio</title>

  <!-- MediaPipe Libraries -->
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
  
  <!-- Three.js Engine for 3D Rendering -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

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
      width: 1100px;
      height: 650px;
      margin: 0 auto;
      border-radius: 16px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
      background: #111827;
    }
    video {
      position: absolute;
      top: 0;
      left: 0;
      width: 1100px;
      height: 650px;
      object-fit: cover;
      transform: scaleX(-1);
      z-index: 1;
    }
    #canvas-container {
      position: absolute;
      top: 0;
      left: 0;
      width: 1100px;
      height: 650px;
      z-index: 2;
      pointer-events: none;
    }
    #2d-canvas {
      position: absolute;
      top: 0;
      left: 0;
      z-index: 2;
    }
    #3d-canvas {
      position: absolute;
      top: 0;
      left: 0;
      z-index: 3;
    }

    #ui-panel {
      position: absolute;
      top: 20px;
      left: 20px;
      z-index: 10;
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 16px;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      width: 240px;
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

    button {
      background: #1f2937;
      color: #9ca3af;
      border: 1px solid #374151;
      padding: 8px 10px;
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
  <div id="canvas-container">
    <canvas id="2d-canvas" width="1100" height="650"></canvas>
    <canvas id="3d-canvas" width="1100" height="650"></canvas>
  </div>

  <div id="ui-panel">
    <div class="ui-group">
      <span class="ui-label">Mode Selection</span>
      <div class="btn-grid">
        <button id="btn-mode-2d" class="active" onclick="switchMode('2D')">2D Canvas</button>
        <button id="btn-mode-3d" onclick="switchMode('3D')">3D Engine</button>
      </div>
    </div>

    <div class="ui-group" id="group-2d-tools">
      <span class="ui-label">2D Sketching</span>
      <div class="btn-grid">
        <button id="btn-free" class="active" onclick="setTool('free')">Freehand</button>
        <button id="btn-rectangle" onclick="setTool('rectangle')">Rectangle</button>
        <button id="btn-circle" onclick="setTool('circle')">Circle</button>
        <button id="btn-triangle" onclick="setTool('triangle')">Triangle</button>
      </div>
    </div>

    <div class="ui-group" id="group-3d-tools" style="display: none;">
      <span class="ui-label">3D Primitives & CAD</span>
      <div class="btn-grid">
        <button id="btn-sphere" onclick="setTool('sphere')">Sphere</button>
        <button id="btn-cube" onclick="setTool('cube')">Cube</button>
        <button id="btn-cone" onclick="setTool('cone')">Cone</button>
        <button id="btn-extrude" onclick="setTool('extrude')">Extrude Z</button>
      </div>
    </div>

    <div class="ui-group">
      <span class="ui-label">Controls</span>
      <button id="btn-clear" onclick="clearCanvas()">Clear All Shapes</button>
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
  const canvas2D = document.getElementById('2d-canvas');
  const ctx2D = canvas2D.getContext('2d');
  const canvas3D = document.getElementById('3d-canvas');
  const statusBarText = document.getElementById('status-text');
  const statusDot = document.getElementById('status-dot');
  const pinchIndicator = document.getElementById('pinch-indicator');

  let activeMode = '2D';
  let currentTool = 'free';
  let isPinching = false;
  let startPinchPoint = null;
  let currentPinchPoint = null;
  let activeDrawnPath = [];

  let smoothedCursor = { x: 0, y: 0 };
  const alpha = 0.35;

  const shapes2D = [];

  // --- Three.js Engine Setup ---
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1100 / 650, 1, 2000);
  camera.position.set(0, 0, 500);

  const renderer = new THREE.WebGLRenderer({ canvas: canvas3D, alpha: true, antialias: true });
  renderer.setClearColor(0x000000, 0); // Transparent background
  renderer.setSize(1100, 650);
  renderer.setPixelRatio(window.devicePixelRatio);

  // Lights
  const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
  scene.add(ambientLight);

  const dirLight1 = new THREE.DirectionalLight(0x00ffff, 2.0);
  dirLight1.position.set(200, 300, 400);
  scene.add(dirLight1);

  const dirLight2 = new THREE.DirectionalLight(0xff00ff, 1.5);
  dirLight2.position.set(-200, -300, 200);
  scene.add(dirLight2);

  const objects3D = [];
  let previewMesh3D = null;

  function animate3D() {
    requestAnimationFrame(animate3D);

    objects3D.forEach(obj => {
      obj.rotation.y += 0.015;
      obj.rotation.x += 0.01;
    });

    if (previewMesh3D) {
      previewMesh3D.rotation.y += 0.02;
    }

    renderer.render(scene, camera);
  }
  animate3D();

  function switchMode(mode) {
    activeMode = mode;
    
    document.getElementById('btn-mode-2d').classList.toggle('active', mode === '2D');
    document.getElementById('btn-mode-3d').classList.toggle('active', mode === '3D');

    const group2D = document.getElementById('group-2d-tools');
    const group3D = document.getElementById('group-3d-tools');

    if (mode === '2D') {
      group2D.style.display = 'flex';
      group3D.style.display = 'none';
      setTool('free');
    } else {
      group2D.style.display = 'none';
      group3D.style.display = 'flex';
      setTool('sphere');
    }
  }

  function setTool(tool) {
    currentTool = tool.toLowerCase();
    
    document.querySelectorAll('#group-2d-tools button, #group-3d-tools button').forEach(btn => {
      btn.classList.remove('active');
    });

    const activeBtn = document.getElementById(`btn-${currentTool}`);
    if (activeBtn) {
      activeBtn.classList.add('active');
    }
  }

  function clearCanvas() {
    ctx2D.clearRect(0, 0, canvas2D.width, canvas2D.height);
    shapes2D.length = 0;

    objects3D.forEach(obj => {
      scene.remove(obj);
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    });
    objects3D.length = 0;

    if (previewMesh3D) {
      scene.remove(previewMesh3D);
      if (previewMesh3D.geometry) previewMesh3D.geometry.dispose();
      if (previewMesh3D.material) previewMesh3D.material.dispose();
      previewMesh3D = null;
    }
  }

  function getDistance(p1, p2) {
    return Math.hypot(p1.x - p2.x, p1.y - p2.y);
  }

  function mapScreenTo3D(screenX, screenY) {
    // Map screen (0..1100, 0..650) to Three.js centered coordinates
    const x = (screenX - 550) * 0.8;
    const y = -(screenY - 325) * 0.8;
    return new THREE.Vector3(x, y, 0);
  }

  function create3DShape(type, size, pos) {
    let geometry;
    const s = Math.max(size, 40);

    if (type === 'sphere') {
      geometry = new THREE.SphereGeometry(s / 1.5, 32, 32);
    } else if (type === 'cube') {
      geometry = new THREE.BoxGeometry(s, s, s);
    } else if (type === 'cone') {
      geometry = new THREE.ConeGeometry(s / 1.5, s * 1.5, 32);
    } else {
      geometry = new THREE.CylinderGeometry(s / 1.5, s / 1.5, s, 32);
    }

    const material = new THREE.MeshPhongMaterial({
      color: 0x00f0ff,
      emissive: 0x003344,
      specular: 0xffffff,
      shininess: 100,
      side: THREE.DoubleSide
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(pos);

    // Add bright wireframe overlay
    const wireGeo = new THREE.WireframeGeometry(geometry);
    const wireMat = new THREE.LineBasicMaterial({ color: 0xffffff });
    const wireframe = new THREE.LineSegments(wireGeo, wireMat);
    mesh.add(wireframe);

    return mesh;
  }

  function update3DPreview(start, end) {
    const size = Math.max(getDistance(start, end), 50);
    const pos = mapScreenTo3D((start.x + end.x) / 2, (start.y + end.y) / 2);

    if (previewMesh3D) {
      scene.remove(previewMesh3D);
    }

    previewMesh3D = create3DShape(currentTool, size, pos);
    scene.add(previewMesh3D);
  }

  function finalize3DSolid() {
    if (previewMesh3D) {
      objects3D.push(previewMesh3D);
      previewMesh3D = null;
    }
  }

  function renderSingle2DShape(shape) {
    if (!shape.start || !shape.end) return;

    ctx2D.strokeStyle = shape.color || '#38bdf8';
    ctx2D.lineWidth = 4;
    ctx2D.lineCap = 'round';
    ctx2D.lineJoin = 'round';
    ctx2D.beginPath();

    if (shape.type === 'free' || shape.type === 'extrude') {
      if (shape.path && shape.path.length > 0) {
        ctx2D.moveTo(shape.path[0].x, shape.path[0].y);
        shape.path.forEach(pt => ctx2D.lineTo(pt.x, pt.y));
      }
    } else if (shape.type === 'rectangle') {
      const w = shape.end.x - shape.start.x;
      const h = shape.end.y - shape.start.y;
      ctx2D.rect(shape.start.x, shape.start.y, w, h);
    } else if (shape.type === 'circle') {
      const r = getDistance(shape.start, shape.end);
      ctx2D.arc(shape.start.x, shape.start.y, r, 0, 2 * Math.PI);
    } else if (shape.type === 'triangle') {
      const topX = (shape.start.x + shape.end.x) / 2;
      ctx2D.moveTo(topX, shape.start.y);
      ctx2D.lineTo(shape.start.x, shape.end.y);
      ctx2D.lineTo(shape.end.x, shape.end.y);
      ctx2D.closePath();
    }
    ctx2D.stroke();
  }

  function onResults(results) {
    ctx2D.clearRect(0, 0, canvas2D.width, canvas2D.height);

    if (activeMode === '2D') {
      shapes2D.forEach(renderSingle2DShape);
    }

    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      statusDot.classList.add('active');
      const landmarks = results.multiHandLandmarks[0];

      const thumbTip = landmarks[4];
      const indexTip = landmarks[8];

      const rawCursorX = (1 - indexTip.x) * 1100;
      const rawCursorY = indexTip.y * 650;
      const rawThumbX = (1 - thumbTip.x) * 1100;
      const rawThumbY = thumbTip.y * 650;

      smoothedCursor.x = alpha * rawCursorX + (1 - alpha) * smoothedCursor.x;
      smoothedCursor.y = alpha * rawCursorY + (1 - alpha) * smoothedCursor.y;

      const pinchDist = getDistance(
        { x: rawCursorX, y: rawCursorY },
        { x: rawThumbX, y: rawThumbY }
      );

      pinchIndicator.innerText = `Pinch Distance: ${Math.round(pinchDist)}px`;
      const currentlyPinching = pinchDist < 45;

      // Draw hand pointer on 2D canvas
      ctx2D.fillStyle = currentlyPinching ? '#10b981' : '#38bdf8';
      ctx2D.shadowColor = currentlyPinching ? '#10b981' : '#38bdf8';
      ctx2D.shadowBlur = 10;
      ctx2D.beginPath();
      ctx2D.arc(smoothedCursor.x, smoothedCursor.y, 8, 0, 2 * Math.PI);
      ctx2D.fill();
      ctx2D.shadowBlur = 0;

      if (currentlyPinching) {
        if (!isPinching) {
          isPinching = true;
          startPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
          currentPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
          activeDrawnPath = [{ x: smoothedCursor.x, y: smoothedCursor.y }];
          statusBarText.innerText = `Drawing [${activeMode} - ${currentTool.toUpperCase()}]`;

          if (activeMode === '3D') {
            update3DPreview(startPinchPoint, currentPinchPoint);
          }
        } else {
          currentPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
          activeDrawnPath.push(currentPinchPoint);

          if (activeMode === '3D') {
            update3DPreview(startPinchPoint, currentPinchPoint);
          } else {
            renderSingle2DShape({
              type: currentTool,
              start: startPinchPoint,
              end: currentPinchPoint,
              path: activeDrawnPath,
              color: '#10b981'
            });
          }
        }
      } else {
        if (isPinching) {
          isPinching = false;
          statusBarText.innerText = `Tracking Active (${activeMode})`;

          if (activeMode === '3D') {
            finalize3DSolid();
          } else {
            shapes2D.push({
              type: currentTool,
              start: { ...startPinchPoint },
              end: { ...currentPinchPoint },
              path: [...activeDrawnPath],
              color: '#38bdf8'
            });
          }
        }
      }
    } else {
      statusDot.classList.remove('active');
      statusBarText.innerText = "Searching for hand...";
      pinchIndicator.innerText = "Pinch Distance: --";
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
    width: 1100,
    height: 650
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

components.html(html_code, height=670, width=1120)
