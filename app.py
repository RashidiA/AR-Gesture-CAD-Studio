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
    #2d-canvas {
      position: absolute;
      top: 0;
      left: 0;
      transform: scaleX(-1);
      z-index: 1;
    }
    #3d-canvas {
      position: absolute;
      top: 0;
      left: 0;
      transform: scaleX(-1);
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
  const videoElement = document.getElementById('webcam');
  const canvas2D = document.getElementById('2d-canvas');
  const ctx2D = canvas2D.getContext('2d');
  const canvas3D = document.getElementById('3d-canvas');
  const statusBar = document.getElementById('status-bar');

  let dimensionMode = '2D';
  let currentTool = 'free';
  let isPinching = false;
  let startPinchPoint = null;
  let currentPinchPoint = null;
  let activeDrawnPath = [];

  // Three.js Setup
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1100 / 650, 1, 2000);
  camera.position.set(0, 0, 800);

  const renderer = new THREE.WebGLRenderer({ canvas: canvas3D, alpha: true, antialias: true });
  renderer.setSize(1100, 650);

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(200, 300, 500);
  scene.add(directionalLight);

  const gridHelper = new THREE.GridHelper(800, 20, 0x00b4d8, 0x444444);
  gridHelper.rotation.x = Math.PI / 2;
  scene.add(gridHelper);

  const objects3D = [];

  function animate3D() {
    requestAnimationFrame(animate3D);
    renderer.render(scene, camera);
  }
  animate3D();

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

  function getDistance(p1, p2) {
    return Math.hypot((p1.x - p2.x) * 1100, (p1.y - p2.y) * 650);
  }

  // Precise 2D Pixel to 3D World Coordinate Mapping via Raycasting / Perspective Calculation
  function screenTo3D(pixelX, pixelY, distance = 800) {
    const ndcX = (pixelX / 1100) * 2 - 1;
    const ndcY = -(pixelY / 650) * 2 + 1;
    
    const vector = new THREE.Vector3(ndcX, ndcY, 0.5);
    vector.unproject(camera);
    
    const dir = vector.sub(camera.position).normalize();
    const targetZ = 0;
    const distanceToZ0 = (targetZ - camera.position.z) / dir.z;
    
    return camera.position.clone().add(dir.multiplyScalar(distanceToZ0));
  }

  function create3DSolid(tool, start, end) {
    const dx = Math.abs(end.x - start.x);
    const dy = Math.abs(end.y - start.y);
    
    // Default size if placed with a simple tap/pinch
    const width = dx > 10 ? dx : 80;
    const height = dy > 10 ? dy : 80;
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
      const centerPixelX = (start.x + end.x) / 2;
      const centerPixelY = (start.y + end.y) / 2;
      
      const pos3D = screenTo3D(centerPixelX, centerPixelY);
      mesh.position.copy(pos3D);
      scene.add(mesh);
      objects3D.push(mesh);
    }
  }

  function onResults(results) {
    ctx2D.save();
    ctx2D.clearRect(0, 0, canvas2D.width, canvas2D.height);
    
    ctx2D.drawImage(results.image, 0, 0, canvas2D.width, canvas2D.height);

    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      const landmarks = results.multiHandLandmarks[0];

      const thumbTip = landmarks[4];
      const indexTip = landmarks[8];
      const palmCenter = landmarks[9];

      const canvasCursorX = indexTip.x * 1100;
      const canvasCursorY = indexTip.y * 650;

      const canvasPalmX = palmCenter.x * 1100;
      const canvasPalmY = palmCenter.y * 650;

      // Draw Palm Anchor Marker
      ctx2D.fillStyle = '#ff0055';
      ctx2D.beginPath();
      ctx2D.arc(canvasPalmX, canvasPalmY, 12, 0, 2 * Math.PI);
      ctx2D.fill();

      // Check Pinch
      const pinchDist = getDistance(indexTip, thumbTip);
      const currentlyPinching = pinchDist < 55;

      // Draw Fingertip Tracking Dot
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
          statusBar.innerText = `Gesture Status: Pinching / Dragging (${currentTool.toUpperCase()})`;
        } else {
          currentPinchPoint = { x: canvasCursorX, y: canvasCursorY };
          activeDrawnPath.push(currentPinchPoint);

          // Draw real-time gesture preview box/line
          ctx2D.strokeStyle = '#00ff88';
          ctx2D.lineWidth = 3;
          ctx2D.beginPath();

          if (currentTool === 'free') {
            ctx2D.moveTo(startPinchPoint.x, startPinchPoint.y);
            activeDrawnPath.forEach(pt => ctx2D.lineTo(pt.x, pt.y));
          } else {
            ctx2D.rect(
              startPinchPoint.x, 
              startPinchPoint.y, 
              currentPinchPoint.x - startPinchPoint.x, 
              currentPinchPoint.y - startPinchPoint.y
            );
          }
          ctx2D.stroke();
        }
      } else {
        if (isPinching) {
          isPinching = false;
          statusBar.innerText = "Gesture Status: Created Shape at Release Point";

          if (dimensionMode === '3D') {
            create3DSolid(currentTool, startPinchPoint, currentPinchPoint || startPinchPoint);
          }
        }
      }
    } else {
      statusBar.innerText = "Gesture Status: Looking for hand...";
    }

    ctx2D.restore();
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
