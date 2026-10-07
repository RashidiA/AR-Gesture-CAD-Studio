import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AR Gesture CAD Studio", layout="wide")

st.title("🎨 AR Gesture CAD Studio (2D & 3D)")
st.caption("Edge-Computed WebAssembly Tracking (MediaPipe Hands) + WebGL 3D Engine (Three.js)")

html_code = """
<!DOCTYPE html>
<html>
<head>
  <!-- MediaPipe Libraries -->
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
  
  <!-- Three.js Engine for 3D Rendering -->
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
    #2d-canvas {
      position: absolute;
      top: 0;
      left: 0;
      z-index: 1;
    }
    #3d-canvas {
      position: absolute;
      top: 0;
      left: 0;
      z-index: 2;
      pointer-events: none;
    }

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

  <div id="ui-panel">
    <div class="ui-group">
      <span class="ui-label">Select Mode</span>
      <div class="btn-grid">
        <button id="btn-mode-2d" class="active" onclick="switchMode('2D')">2D Mode</button>
        <button id="btn-mode-3d" onclick="switchMode('3D')">3D Mode</button>
      </div>
    </div>

    <div class="ui-group" id="group-2d-tools">
      <span class="ui-label">2D Drawing Tools</span>
      <div class="btn-grid">
        <button id="btn-free" class="active" onclick="setTool('free')">Freehand</button>
        <button id="btn-rectangle" onclick="setTool('rectangle')">Rectangle</button>
        <button id="btn-circle" onclick="setTool('circle')">Circle</button>
        <button id="btn-triangle" onclick="setTool('triangle')">Triangle</button>
      </div>
    </div>

    <div class="ui-group" id="group-3d-tools" style="display: none;">
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
      <button onclick="clearCanvas()" style="background: #e63946; border: none; color: white;">Clear Canvas</button>
    </div>
  </div>

  <div id="status-bar">Gesture Status: Ready</div>
</div>

<script>
  const videoElement = document.getElementById('webcam');
  const canvas2D = document.getElementById('2d-canvas');
  const ctx2D = canvas2D.getContext('2d');
  const canvas3D = document.getElementById('3d-canvas');
  const statusBar = document.getElementById('status-bar');

  let activeMode = '2D';
  let currentTool = 'free';
  let isPinching = false;
  let startPinchPoint = null;
  let currentPinchPoint = null;
  let activeDrawnPath = [];

  const shapes2D = [];

  // Three.js Engine Setup
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1100 / 650, 1, 2000);
  camera.position.set(0, 0, 800);

  const renderer = new THREE.WebGLRenderer({ canvas: canvas3D, alpha: true, antialias: true });
  renderer.setClearColor(0x000000, 0);
  renderer.setSize(1100, 650);

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
  scene.add(ambientLight);

  const mainLight = new THREE.DirectionalLight(0xffffff, 1.5);
  mainLight.position.set(200, 400, 500);
  scene.add(mainLight);

  const objects3D = [];
  let previewMesh3D = null;

  function animate3D() {
    requestAnimationFrame(animate3D);
    if (activeMode === '3D') {
      objects3D.forEach(obj => {
        obj.rotation.y += 0.01;
        obj.rotation.x += 0.005;
      });
      if (previewMesh3D) {
        previewMesh3D.rotation.y += 0.01;
      }
      renderer.render(scene, camera);
    } else {
      renderer.clear();
    }
  }
  animate3D();

  function switchMode(mode) {
    activeMode = mode;
    clearCanvas();

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
    document.querySelectorAll('.btn-grid button').forEach(btn => btn.classList.remove('active'));
    const activeBtn = document.getElementById(`btn-${currentTool}`);
    if (activeBtn) activeBtn.classList.add('active');
  }

  function clearCanvas() {
    ctx2D.clearRect(0, 0, canvas2D.width, canvas2D.height);
    shapes2D.length = 0;

    objects3D.forEach(obj => scene.remove(obj));
    objects3D.length = 0;

    if (previewMesh3D) {
      scene.remove(previewMesh3D);
      previewMesh3D = null;
    }
    renderer.clear();
  }

  function getDistance(p1, p2) {
    return Math.hypot(p1.x - p2.x, p1.y - p2.y);
  }

  function mapScreenTo3DWorld(pixelX, pixelY) {
    const worldX = (pixelX - 550) * 0.95;
    const worldY = -(pixelY - 325) * 0.95;
    return new THREE.Vector3(worldX, worldY, 0);
  }

  function createMeshForTool(tool) {
    let geometry;
    if (tool === 'sphere') {
      geometry = new THREE.SphereGeometry(1, 24, 24);
    } else if (tool === 'cube' || tool === 'extrude') {
      geometry = new THREE.BoxGeometry(2, 2, 2);
    } else if (tool === 'cone') {
      geometry = new THREE.ConeGeometry(1, 2, 24);
    } else {
      geometry = new THREE.SphereGeometry(1, 24, 24);
    }

    const material = new THREE.MeshPhongMaterial({
      color: 0x00ff88,
      emissive: 0x003311,
      specular: 0xffffff,
      shininess: 100,
      side: THREE.DoubleSide
    });

    return new THREE.Mesh(geometry, material);
  }

  function update3DPreview(start, end) {
    const dragDistance = getDistance(start, end);
    const size = Math.max(dragDistance * 0.8, 40);

    if (!previewMesh3D) {
      previewMesh3D = createMeshForTool(currentTool);
      scene.add(previewMesh3D);
    }

    previewMesh3D.scale.set(size, size, size);

    const centerX = (start.x + end.x) / 2;
    const centerY = (start.y + end.y) / 2;
    const pos3D = mapScreenTo3DWorld(centerX, centerY);
    previewMesh3D.position.copy(pos3D);
  }

  function finalize3DSolid() {
    if (previewMesh3D) {
      objects3D.push(previewMesh3D);
      previewMesh3D = null;
    }
  }

  function renderSingle2DShape(shape) {
    if (!shape.start || !shape.end) return;

    ctx2D.strokeStyle = shape.color || '#00ff88';
    ctx2D.lineWidth = 4;
    ctx2D.beginPath();

    if (shape.type === 'free') {
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

    ctx2D.save();
    ctx2D.translate(canvas2D.width, 0);
    ctx2D.scale(-1, 1);
    ctx2D.drawImage(results.image, 0, 0, canvas2D.width, canvas2D.height);
    ctx2D.restore();

    if (activeMode === '2D') {
      shapes2D.forEach(renderSingle2DShape);
    }

    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      const landmarks = results.multiHandLandmarks[0];

      const thumbTip = landmarks[4];
      const indexTip = landmarks[8];
      const palmCenter = landmarks[9];

      const canvasCursorX = (1 - indexTip.x) * 1100;
      const canvasCursorY = indexTip.y * 650;

      const canvasThumbX = (1 - thumbTip.x) * 1100;
      const canvasThumbY = thumbTip.y * 650;

      const canvasPalmX = (1 - palmCenter.x) * 1100;
      const canvasPalmY = palmCenter.y * 650;

      ctx2D.fillStyle = '#ff0055';
      ctx2D.beginPath();
      ctx2D.arc(canvasPalmX, canvasPalmY, 12, 0, 2 * Math.PI);
      ctx2D.fill();

      const pinchDist = getDistance(
        { x: canvasCursorX, y: canvasCursorY },
        { x: canvasThumbX, y: canvasThumbY }
      );
      const currentlyPinching = pinchDist < 50;

      ctx2D.fillStyle = currentlyPinching ? '#00ff88' : '#00b4d8';
      ctx2D.beginPath();
      ctx2D.arc(canvasCursorX, canvasCursorY, 10, 0, 2 * Math.PI);
      ctx2D.fill();

      if (currentlyPinching) {
        if (!isPinching) {
          isPinching = true;
          startPinchPoint = { x: canvasCursorX, y: canvasCursorY };
          currentPinchPoint = { x: canvasCursorX, y: canvasCursorY };
          activeDrawnPath = [{ x: canvasCursorX, y: canvasCursorY }];
          statusBar.innerText = `Gesture Status: Drawing [${activeMode}] (${currentTool.toUpperCase()})`;
        } else {
          currentPinchPoint = { x: canvasCursorX, y: canvasCursorY };

          if (activeMode === '3D') {
            update3DPreview(startPinchPoint, currentPinchPoint);
          } else {
            activeDrawnPath.push(currentPinchPoint);
            renderSingle2DShape({
              type: currentTool,
              start: startPinchPoint,
              end: currentPinchPoint,
              path: activeDrawnPath,
              color: '#00ff88'
            });
          }
        }
      } else {
        if (isPinching) {
          isPinching = false;
          statusBar.innerText = `Gesture Status: Saved [${activeMode}]`;

          if (activeMode === '3D') {
            finalize3DSolid();
          } else {
            shapes2D.push({
              type: currentTool,
              start: { ...startPinchPoint },
              end: { ...currentPinchPoint },
              path: [...activeDrawnPath],
              color: '#00ff88'
            });
          }
        }
      }
    } else {
      statusBar.innerText = "Gesture Status: Searching for hand...";
    }
  }

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
