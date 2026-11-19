import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(
    page_title="AR Gesture CAD Studio", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.title("🎨 AR Gesture CAD Studio (2D & 3D AR)")
st.caption("Edge-Computed Hand Tracking (MediaPipe) + WebGL Technical CAD Engine (AutoCAD Style)  |  Penjejakan tangan pada peranti (MediaPipe) + enjin CAD teknikal WebGL (gaya AutoCAD)")
st.info("🌐 Language / Bahasa: use the **English / Bahasa Malaysia** buttons at the top of the left panel inside the studio.  |  Gunakan butang **English / Bahasa Malaysia** di bahagian atas panel kiri dalam studio.")

# --- Initialize Session State for persistence ---
if "stl_b64" not in st.session_state:
    st.session_state.stl_b64 = ""
if "img_b64" not in st.session_state:
    st.session_state.img_b64 = ""

# --- File Uploader Sidebar / Top Section ---
col_up1, col_up2 = st.columns(2)

with col_up1:
    uploaded_file = st.file_uploader("📂 Import External 3D Model (.stl)  |  Import model 3D luaran (.stl)", type=["stl"])
    if uploaded_file is not None:
        stl_bytes = uploaded_file.read()
        st.session_state.stl_b64 = base64.b64encode(stl_bytes).decode("utf-8")
        st.success(f"Loaded STL model / Model STL dimuatkan: {uploaded_file.name}")

with col_up2:
    uploaded_image = st.file_uploader("🖼️ Upload 2D Image/Sketch (PNG/JPG) to Convert to 3D  |  Muat naik imej/lakaran 2D (PNG/JPG) untuk ditukar kepada 3D", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        img_bytes = uploaded_image.read()
        st.session_state.img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        st.success(f"Loaded 2D image / Imej 2D dimuatkan '{uploaded_image.name}' for solid 3D extrusion / untuk penyemperitan 3D pepejal!")

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
    #ui-panel { max-height: 610px; overflow-y: auto; scrollbar-width: thin; }
    #hud-canvas { position: absolute; top: 0; left: 0; width: 1280px; height: 720px; z-index: 3; pointer-events: none; }
    #props {
      position: absolute; top: 20px; right: 20px; z-index: 10; width: 250px;
      background: rgba(17, 24, 39, 0.9); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.12); padding: 14px; border-radius: 12px; display: none;
      flex-direction: column; gap: 8px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); font-size: 12px;
    }
    #props .row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
    #props .val { color: #f8fafc; font-weight: 700; font-variant-numeric: tabular-nums; }
    #props .dims { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; }
    #props .dims label { display: flex; flex-direction: column; gap: 2px; font-size: 10px; color: #94a3b8; font-weight: 700; }
    #props input[type=number], #props select, #sec-pos {
      width: 100%; background: #0f172a; color: #e2e8f0; border: 1px solid #334155; border-radius: 6px; padding: 4px 6px; font-size: 12px;
    }
    #props .hint { color: #64748b; font-size: 10px; line-height: 1.3; }
    #sec-pos { padding: 0; accent-color: #facc15; }
    #sec-readout { font-size: 10px; color: #94a3b8; }
    #btn-guide { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 10; padding: 8px 16px; border-radius: 20px; background: rgba(17, 24, 39, 0.9); color: #facc15; border-color: rgba(250, 204, 21, 0.5); }
    #guide {
      position: absolute; inset: 0; z-index: 50; background: rgba(3, 7, 18, 0.88); display: none; align-items: center; justify-content: center;
    }
    #guide .box { width: 1040px; max-height: 690px; overflow-y: auto; background: #111827; border: 1px solid #334155; border-radius: 16px; padding: 20px 24px; }
    #guide h2 { margin: 0 0 4px; font-size: 20px; color: #f8fafc; }
    #guide .sub { color: #94a3b8; font-size: 12px; margin-bottom: 14px; }
    #guide .cards { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
    #guide .gc { background: #0b1220; border: 1px solid #1f2937; border-radius: 12px; padding: 10px; display: flex; flex-direction: column; gap: 6px; transition: all .25s; }
    #guide .gc.done { border-color: #10b981; box-shadow: 0 0 14px rgba(16, 185, 129, .35); }
    #guide .gc.star { border-color: #facc15; }
    #guide .gc svg { width: 100%; height: 86px; background: #020617; border-radius: 8px; }
    #guide .gc b { color: #f8fafc; font-size: 13px; }
    #guide .gc span { color: #94a3b8; font-size: 11px; line-height: 1.35; }
    #guide .gc .tick { color: #475569; font-size: 11px; font-weight: 700; }
    #guide .gc.done .tick { color: #10b981; }
    #guide .tips { margin: 14px 0 0; padding: 10px 12px; background: #0b1220; border-radius: 10px; color: #cbd5e1; font-size: 12px; line-height: 1.5; }
    #guide .foot { display: flex; justify-content: space-between; align-items: center; margin-top: 14px; color: #94a3b8; font-size: 12px; }
    #guide .foot button { background: #0284c7; color: #fff; border-color: #38bdf8; padding: 9px 22px; font-size: 13px; }
  </style>
</head>
<body>

<div id="studio-container">
  <video id="webcam" playsinline autoplay muted></video>
  <canvas id="webgl-canvas" width="1280" height="720"></canvas>
  <canvas id="sketch-canvas" width="1280" height="720"></canvas>

  <div id="ui-panel">
    <div class="ui-group">
      <span class="ui-label">Language / Bahasa</span>
      <div class="btn-grid">
        <button id="lang-en" class="active" onclick="setLang('en')">English</button>
        <button id="lang-bm" onclick="setLang('bm')">Bahasa Malaysia</button>
      </div>
    </div>

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
      <span class="ui-label">Project & Export</span>
      <div class="btn-grid">
        <button id="btn-save" onclick="saveProject()">Save project</button>
        <button id="btn-load" onclick="document.getElementById('file-load').click()">Load project</button>
      </div>
      <button id="btn-stl" onclick="exportSTL()">Export STL (mm)</button>
      <input type="file" id="file-load" accept=".json,application/json" style="display:none">
    </div>

    <div class="ui-group" id="group-section">
      <span class="ui-label">Section View (cut)</span>
      <button id="btn-section" onclick="toggleSection()">Section: Off</button>
      <div class="btn-grid-3">
        <button id="sec-x" class="active" onclick="setSectionAxis('x')">X</button>
        <button id="sec-y" onclick="setSectionAxis('y')">Y</button>
        <button id="sec-z" onclick="setSectionAxis('z')">Z</button>
      </div>
      <input type="range" id="sec-pos" min="-150" max="150" value="0" step="1" oninput="setSectionPos(this.value)">
      <div class="btn-grid">
        <button id="btn-secflip" onclick="flipSection()">Flip side</button>
        <span id="sec-readout">Cut at 0 mm</span>
      </div>
    </div>

    <div class="ui-group">
      <span class="ui-label">Controls</span>
      <div class="btn-grid">
        <button id="btn-undo" onclick="performUndo()">Undo (1 Step)</button>
        <button id="btn-clear" onclick="clearCanvas()">Clear All</button>
      </div>
    </div>
  </div>

  <canvas id="hud-canvas" width="1280" height="720"></canvas>

  <div id="props">
    <span class="ui-label">Selected object</span>
    <div class="row"><span>Type</span><span class="val" id="p-kind">-</span></div>
    <div class="dims">
      <label>W (X) mm<input type="number" id="dim-x" min="1" step="1"></label>
      <label>H (Y) mm<input type="number" id="dim-y" min="1" step="1"></label>
      <label>D (Z) mm<input type="number" id="dim-z" min="1" step="1"></label>
    </div>
    <div class="row"><span>Material</span><select id="p-mat" style="width:120px"></select></div>
    <div class="row"><span>Volume</span><span class="val" id="p-vol">-</span></div>
    <div class="row"><span>Surface area</span><span class="val" id="p-area">-</span></div>
    <div class="row"><span>Mass</span><span class="val" id="p-mass">-</span></div>
    <div class="hint">Type new W / H / D in mm and press Enter. Volume and mass are for closed solids (approximate for imported STL).</div>
  </div>

  <button id="btn-guide" onclick="showGuide(true)">? Gesture guide</button>

  <div id="guide">
    <div class="box">
      <h2>Hand gesture guide</h2>
      <div class="sub">Stand 40-70 cm from the camera, keep good light on your hands and show your palm. Each card turns green when the app sees you do it.</div>
      <div class="cards">
        <div class="gc" id="g-point">
          <svg viewBox="0 0 120 80"><circle cx="60" cy="40" r="6" fill="#38bdf8"><animate attributeName="cx" values="30;90;30" dur="3s" repeatCount="indefinite"/><animate attributeName="cy" values="55;25;55" dur="3s" repeatCount="indefinite"/></circle><circle cx="60" cy="40" r="12" fill="none" stroke="#38bdf8" opacity=".4"><animate attributeName="cx" values="30;90;30" dur="3s" repeatCount="indefinite"/><animate attributeName="cy" values="55;25;55" dur="3s" repeatCount="indefinite"/></circle></svg>
          <b>1. Point</b><span>Hold up one hand. Your index fingertip is the blue cursor.</span><div class="tick" id="t-point">Not seen yet</div>
        </div>
        <div class="gc" id="g-pinch">
          <svg viewBox="0 0 120 80"><circle r="7" cy="40" fill="#f8fafc"><animate attributeName="cx" values="42;56;42" dur="1.6s" repeatCount="indefinite"/></circle><circle r="7" cy="40" fill="#38bdf8"><animate attributeName="cx" values="78;64;78" dur="1.6s" repeatCount="indefinite"/></circle><text x="60" y="68" fill="#94a3b8" font-size="9" text-anchor="middle">thumb + index touch</text></svg>
          <b>2. Pinch</b><span>Touch thumb and index tip together (distance under 45 px, shown bottom right). Pinch = select, draw or grab. Release = finish.</span><div class="tick" id="t-pinch">Not seen yet</div>
        </div>
        <div class="gc" id="g-drag">
          <svg viewBox="0 0 120 80"><rect x="22" y="25" width="26" height="26" fill="#38bdf8" opacity=".85"><animate attributeName="x" values="22;70;22" dur="2.6s" repeatCount="indefinite"/></rect><circle r="6" cy="38" fill="#10b981"><animate attributeName="cx" values="35;83;35" dur="2.6s" repeatCount="indefinite"/></circle></svg>
          <b>3. Pinch and drag</b><span>Choose Move, Resize, Rot X/Y/Z or Extrude, pinch the object and move your hand.</span><div class="tick" id="t-drag">Not seen yet</div>
        </div>
        <div class="gc star" id="g-scale">
          <svg viewBox="0 0 120 80"><rect x="45" y="25" width="30" height="30" fill="#38bdf8" opacity=".85"><animate attributeName="x" values="45;30;45" dur="2.4s" repeatCount="indefinite"/><animate attributeName="y" values="25;10;25" dur="2.4s" repeatCount="indefinite"/><animate attributeName="width" values="30;60;30" dur="2.4s" repeatCount="indefinite"/><animate attributeName="height" values="30;60;30" dur="2.4s" repeatCount="indefinite"/></rect><circle r="6" cy="40" fill="#10b981"><animate attributeName="cx" values="35;12;35" dur="2.4s" repeatCount="indefinite"/></circle><circle r="6" cy="40" fill="#10b981"><animate attributeName="cx" values="85;108;85" dur="2.4s" repeatCount="indefinite"/></circle></svg>
          <b>4. Two hands: scale</b><span>Pinch the object with BOTH hands (one pinch each). Move the hands apart to enlarge, together to shrink.</span><div class="tick" id="t-scale">Not seen yet</div>
        </div>
        <div class="gc star" id="g-rotate">
          <svg viewBox="0 0 120 80"><g><animateTransform attributeName="transform" type="rotate" values="-30 60 40;30 60 40;-30 60 40" dur="3s" repeatCount="indefinite"/><rect x="45" y="25" width="30" height="30" fill="#38bdf8" opacity=".85"/><line x1="18" y1="40" x2="102" y2="40" stroke="#10b981" stroke-width="2"/><circle cx="18" cy="40" r="6" fill="#10b981"/><circle cx="102" cy="40" r="6" fill="#10b981"/></g></svg>
          <b>5. Two hands: rotate</b><span>Pinch with both hands, then twist them like turning a steering wheel. The object turns with the line between your hands.</span><div class="tick" id="t-rotate">Not seen yet</div>
        </div>
      </div>
      <div class="tips"><b>Two-hand steps:</b> (1) Create or choose a shape. (2) Pinch it once with one hand so it is selected (it turns orange). (3) Pinch with both hands at the same time, a yellow line appears between them. (4) Spread or squeeze to scale, twist to rotate. (5) Release both hands to finish. After two-hand use the app ignores single pinches for a moment, so shapes are not created by accident.<br><b>No webcam?</b> You can still click the buttons, use Section view, type exact sizes and export.</div>
      <div class="foot"><label><input type="checkbox" id="guide-hide"> Do not show this automatically</label><button onclick="showGuide(false)">Start designing</button></div>
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

  var featuresReady = false;   // set true once the engineering tools below are initialised
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

  /* ====================================================================================
     Dual language: English / Bahasa Malaysia (button in the left panel, remembered in the browser)
     ==================================================================================== */
  const BM = {
    'Mode Selection': 'Pilihan Mod', '2D Canvas': 'Kanvas 2D', '3D Engine': 'Enjin 3D', 'Color Palette': 'Palet Warna', '2D Sketching': 'Lakaran 2D',
    'Freehand': 'Tangan bebas', 'Rectangle': 'Segi empat', 'Circle': 'Bulatan', 'Triangle': 'Segi tiga',
    '3D Primitives & Create': 'Bentuk Asas 3D & Cipta', 'Sphere': 'Sfera', 'Cube': 'Kubus', 'Cone': 'Kon', 'Cylinder': 'Silinder', 'Pyramid': 'Piramid',
    'Object Transform & Measure': 'Ubah Objek & Ukur', 'Move': 'Alih', 'Resize': 'Ubah saiz', 'Measure (mm)': 'Ukur (mm)',
    'Rot X': 'Putar X', 'Rot Y': 'Putar Y', 'Rot Z': 'Putar Z', 'Delete Selected': 'Padam yang dipilih',
    'Object Modification & Booleans': 'Ubah Suai Objek & Boolean', 'Extrude Face': 'Tonjol Muka (Extrude)', 'Union': 'Cantum', 'Intersect': 'Persilang', 'Subtract (Difference)': 'Tolak (Beza)',
    'Project & Export': 'Projek & Eksport', 'Save project': 'Simpan projek', 'Load project': 'Buka projek', 'Export STL (mm)': 'Eksport STL (mm)',
    'Section View (cut)': 'Pandangan Keratan', 'Flip side': 'Balikkan sisi', 'Controls': 'Kawalan', 'Undo (1 Step)': 'Buat asal (1 langkah)', 'Clear All': 'Kosongkan semua',
    'Selected object': 'Objek dipilih', 'Type': 'Jenis', 'W (X) mm': 'L (X) mm', 'H (Y) mm': 'T (Y) mm', 'D (Z) mm': 'P (Z) mm', 'Material': 'Bahan',
    'Volume': 'Isi padu', 'Surface area': 'Luas permukaan', 'Mass': 'Jisim',
    'Type new W / H / D in mm and press Enter. Volume and mass are for closed solids (approximate for imported STL).': 'Taip L / T / P baharu dalam mm dan tekan Enter. Isi padu dan jisim adalah untuk pepejal tertutup (anggaran bagi STL yang diimport).',
    '? Gesture guide': '? Panduan gerak isyarat',
    'Hand gesture guide': 'Panduan gerak isyarat tangan',
    'Stand 40-70 cm from the camera, keep good light on your hands and show your palm. Each card turns green when the app sees you do it.': 'Berdiri 40-70 cm dari kamera, pastikan tangan anda mendapat cahaya yang baik dan tunjukkan tapak tangan. Setiap kad bertukar hijau apabila aplikasi nampak anda melakukannya.',
    '1. Point': '1. Tunjuk', 'Hold up one hand. Your index fingertip is the blue cursor.': 'Angkat satu tangan. Hujung jari telunjuk anda ialah kursor biru.',
    '2. Pinch': '2. Cubit', 'Touch thumb and index tip together (distance under 45 px, shown bottom right). Pinch = select, draw or grab. Release = finish.': 'Rapatkan hujung ibu jari dan jari telunjuk (jarak kurang 45 px, ditunjukkan di kanan bawah). Cubit = pilih, lukis atau pegang. Lepas = selesai.',
    'thumb + index touch': 'ibu jari + telunjuk bertemu',
    '3. Pinch and drag': '3. Cubit dan seret', 'Choose Move, Resize, Rot X/Y/Z or Extrude, pinch the object and move your hand.': 'Pilih Alih, Ubah saiz, Putar X/Y/Z atau Tonjol, cubit objek dan gerakkan tangan anda.',
    '4. Two hands: scale': '4. Dua tangan: skala', 'Pinch the object with BOTH hands (one pinch each). Move the hands apart to enlarge, together to shrink.': 'Cubit objek dengan KEDUA-DUA tangan (satu cubitan setiap tangan). Jauhkan tangan untuk membesarkan, dekatkan untuk mengecilkan.',
    '5. Two hands: rotate': '5. Dua tangan: putar', 'Pinch with both hands, then twist them like turning a steering wheel. The object turns with the line between your hands.': 'Cubit dengan kedua-dua tangan, kemudian pusingkan seperti memutar stereng. Objek berputar mengikut garisan antara tangan anda.',
    'Two-hand steps:': 'Langkah dua tangan:',
    '(1) Create or choose a shape. (2) Pinch it once with one hand so it is selected (it turns orange). (3) Pinch with both hands at the same time, a yellow line appears between them. (4) Spread or squeeze to scale, twist to rotate. (5) Release both hands to finish. After two-hand use the app ignores single pinches for a moment, so shapes are not created by accident.': '(1) Cipta atau pilih satu bentuk. (2) Cubit sekali dengan satu tangan supaya ia dipilih (bertukar oren). (3) Cubit dengan kedua-dua tangan serentak, satu garisan kuning muncul di antara tangan. (4) Jauhkan atau dekatkan untuk skala, pusingkan untuk putar. (5) Lepaskan kedua-dua tangan untuk selesai. Selepas guna dua tangan, aplikasi mengabaikan cubitan tunggal seketika supaya bentuk tidak tercipta secara tidak sengaja.',
    'No webcam?': 'Tiada kamera web?', 'You can still click the buttons, use Section view, type exact sizes and export.': 'Anda masih boleh klik butang, guna Pandangan Keratan, taip saiz tepat dan eksport.',
    'Do not show this automatically': 'Jangan papar ini secara automatik', 'Start designing': 'Mula mereka bentuk'
  };
  const KIND_BM = { 'Cube': 'Kubus', 'Sphere': 'Sfera', 'Cone': 'Kon', 'Cylinder': 'Silinder', 'Pyramid': 'Piramid', 'STL import': 'Import STL', 'Sketch solid': 'Pepejal lakaran', 'Boolean union': 'Boolean cantum', 'Boolean intersect': 'Boolean persilang', 'Boolean subtract': 'Boolean tolak', 'Object': 'Objek' };
  const MAT_BM = { 'Steel': 'Keluli', 'Aluminium': 'Aluminium', 'Cast iron': 'Besi tuang', 'Titanium': 'Titanium', 'Copper': 'Kuprum', 'ABS plastic': 'Plastik ABS' };
  const DYN = {
    en: {
      noUndo: 'No previous action to undo', undoOk: 'Undo Successful (1 Step Back)', faceAcq: 'Face Target Acquired (Yellow)', deleted: 'Selected Object Deleted', objSel: 'Object Selected!',
      pinchNone: 'Pinch Distance: --', pinchPx: n => 'Pinch Distance: ' + n + 'px', meas: (d, h, w, r) => 'L:' + d + 'mm | H:' + h + 'mm | W:' + w + 'mm | R:' + r + 'mm',
      lbl_union: 'Union', lbl_intersect: 'Intersect', lbl_subtract: 'Subtract',
      needTwo: l => 'Need at least 2 objects for ' + l, tooDetailed: (l, n) => 'Models too detailed for ' + l + ' in the browser (' + n + ' triangles)', failed: l => l + ' failed (try simpler shapes)',
      noOverlap: 'Intersect: the two objects do not overlap', nothingLeft: l => l + ': nothing left, objects unchanged', boolOk: l => 'Boolean ' + l + ' Successful',
      noSave: 'Nothing to save yet', saved: n => 'Project saved (' + n + ' objects)', loaded: n => 'Project loaded (' + n + ' objects)', loadFail: 'Could not load: not a valid project file',
      noExport: 'Nothing to export yet', stlOk: n => 'STL exported: ' + n + ' triangles (mm)',
      twoNone: 'Two hands: create or select an object first', hudSelect: 'Select an object first', twoMode: t => 'Two-hand mode: ' + t, hudScale: (r, d) => 'Scale x' + r + '   Rotate ' + d + ' deg',
      searching: 'Searching for hand...', active: (m, tl) => 'Active [' + m + ' - ' + tl + ']', tracking: m => 'Tracking Active (' + m + ')',
      twoSeen: 'Two hands seen: pinch with BOTH hands to scale / rotate', camDenied: 'Camera Access Denied/Failed', initCam: 'Initializing Camera...',
      detected: 'Detected', notSeen: 'Not seen yet', secBtn: on => 'Section: ' + (on ? 'On' : 'Off'), secRead: (a, mm, f) => 'Cut ' + a + ' = ' + mm + ' mm' + (f ? ' (flipped)' : '')
    },
    bm: {
      noUndo: 'Tiada tindakan sebelumnya untuk dibuat asal', undoOk: 'Buat asal berjaya (1 langkah ke belakang)', faceAcq: 'Sasaran muka ditemui (Kuning)', deleted: 'Objek yang dipilih telah dipadam', objSel: 'Objek dipilih!',
      pinchNone: 'Jarak Cubitan: --', pinchPx: n => 'Jarak Cubitan: ' + n + 'px', meas: (d, h, w, r) => 'P:' + d + 'mm | T:' + h + 'mm | L:' + w + 'mm | J:' + r + 'mm',
      lbl_union: 'Cantum', lbl_intersect: 'Persilang', lbl_subtract: 'Tolak',
      needTwo: l => 'Perlu sekurang-kurangnya 2 objek untuk ' + l, tooDetailed: (l, n) => 'Model terlalu terperinci untuk ' + l + ' dalam pelayar (' + n + ' segi tiga)', failed: l => l + ' gagal (cuba bentuk yang lebih ringkas)',
      noOverlap: 'Persilang: kedua-dua objek tidak bertindih', nothingLeft: l => l + ': tiada yang tinggal, objek tidak berubah', boolOk: l => 'Boolean ' + l + ' Berjaya',
      noSave: 'Belum ada apa-apa untuk disimpan', saved: n => 'Projek disimpan (' + n + ' objek)', loaded: n => 'Projek dibuka (' + n + ' objek)', loadFail: 'Tidak dapat dibuka: bukan fail projek yang sah',
      noExport: 'Belum ada apa-apa untuk dieksport', stlOk: n => 'STL dieksport: ' + n + ' segi tiga (mm)',
      twoNone: 'Dua tangan: cipta atau pilih objek dahulu', hudSelect: 'Pilih objek dahulu', twoMode: t => 'Mod dua tangan: ' + t, hudScale: (r, d) => 'Skala x' + r + '   Putar ' + d + ' darjah',
      searching: 'Mencari tangan...', active: (m, tl) => 'Aktif [' + m + ' - ' + tl + ']', tracking: m => 'Penjejakan aktif (' + m + ')',
      twoSeen: 'Dua tangan dikesan: cubit dengan KEDUA-DUA tangan untuk skala / putar', camDenied: 'Akses kamera ditolak/gagal', initCam: 'Memulakan kamera...',
      detected: 'Dikesan', notSeen: 'Belum dilihat', secBtn: on => 'Keratan: ' + (on ? 'Hidup' : 'Mati'), secRead: (a, mm, f) => 'Potong ' + a + ' = ' + mm + ' mm' + (f ? ' (dibalikkan)' : '')
    }
  };
  let lang = 'en';
  try { const sv = localStorage.getItem('cadLang'); lang = sv === 'bm' || sv === 'en' ? sv : (/^(ms|id)/i.test(navigator.language || '') ? 'bm' : 'en'); } catch (e) { }
  const T = (k, ...a) => { const v = DYN[lang][k]; return typeof v === 'function' ? v(...a) : v; };
  const kindText = k => lang === 'bm' ? (KIND_BM[k] || k) : (k || 'Object');
  const matText = k => lang === 'bm' ? (MAT_BM[k] || k) : k;
  const DYN_IDS = new Set(['status-text', 'pinch-indicator', 'p-kind', 'p-vol', 'p-area', 'p-mass', 'sec-readout', 'btn-section', 't-point', 't-pinch', 't-drag', 't-scale', 't-rotate']);
  function applyLang() {
    const walker = document.createTreeWalker(document.getElementById('studio-container'), NodeFilter.SHOW_TEXT); const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(n => {
      let p = n.parentNode, skip = false; while (p && p.id !== 'studio-container') { if (p.id && DYN_IDS.has(p.id)) { skip = true; break; } p = p.parentNode; }
      if (skip) return;
      if (n.__en === undefined) n.__en = n.nodeValue;
      const trimmed = n.__en.trim();
      n.nodeValue = (lang === 'bm' && BM[trimmed]) ? n.__en.replace(trimmed, BM[trimmed]) : n.__en;
    });
    document.documentElement.lang = lang === 'bm' ? 'ms' : 'en';
    document.getElementById('lang-en').classList.toggle('active', lang === 'en');
    document.getElementById('lang-bm').classList.toggle('active', lang === 'bm');
    if (/--$/.test(pinchIndicator.innerText)) pinchIndicator.innerText = T('pinchNone');
    if (typeof featuresReady !== 'undefined' && featuresReady) { buildMatOptions(); refreshSection(); refreshTicks(); lastPropsKey = ''; updateProps(); if (selectedObject && currentTool === 'measure') updateMeasurements(selectedObject); }
  }
  function setLang(l) { lang = l; try { localStorage.setItem('cadLang', l); } catch (e) { } applyLang(); }

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
      color: obj.material.color.getHexString(),
      kind: obj.userData.kind, mat: obj.userData.mat
    }));
    historyStack.push(stateSnapshot);
    if (historyStack.length > 25) historyStack.shift();
  }

  function performUndo() {
    if (historyStack.length === 0) {
      statusBarText.innerText = T('noUndo');
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
      mesh.userData.kind = data.kind; mesh.userData.mat = data.mat;
      attachAutoCADEdges(mesh);
      scene.add(mesh);
      objects3D.push(mesh);
    });

    if (objects3D.length > 0) {
      selectedObject = objects3D[objects3D.length - 1];
      setHighlight(selectedObject, true);
      updateMeasurements(selectedObject);
    } else {
      pinchIndicator.innerText = T('pinchNone');
    }
    statusBarText.innerText = T('undoOk');
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

    pinchIndicator.innerText = T('meas', depth, height, width, radius);
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
      statusBarText.innerText = T('faceAcq');
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
    if (featuresReady) { applyClipping(); const t = performance.now(); if (t - lastPropsT > 200) { lastPropsT = t; updateProps(); } cutHelper.visible = sectionOn && activeMode === '3D'; }

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

  // --- Load STL File from Streamlit Session State ---
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
    stlMesh.userData.kind = 'STL import'; stlMesh.userData.mat = 'Steel';
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
      imgMesh.userData.kind = 'Sketch solid'; imgMesh.userData.mat = 'Steel';
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
      statusBarText.innerText = T('deleted');
      pinchIndicator.innerText = T('pinchNone');
    }
  }

  /* ====================================================================================
     Real solid Boolean engine (BSP-tree CSG, after Evan Wallace's csg.js, MIT licence).
     Works on triangles in world space, so it handles any two meshes (primitives, STL, extruded sketches).
     ==================================================================================== */
  const CSG_EPS = 1e-3;
  const V3 = {
    sub: (a, b) => ({ x: a.x - b.x, y: a.y - b.y, z: a.z - b.z }),
    dot: (a, b) => a.x * b.x + a.y * b.y + a.z * b.z,
    cross: (a, b) => ({ x: a.y * b.z - a.z * b.y, y: a.z * b.x - a.x * b.z, z: a.x * b.y - a.y * b.x }),
    len: a => Math.sqrt(V3.dot(a, a)),
    lerp: (a, b, t) => ({ x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t, z: a.z + (b.z - a.z) * t }),
    neg: a => ({ x: -a.x, y: -a.y, z: -a.z })
  };
  function CsgPlane(normal, w) { this.normal = normal; this.w = w; }
  CsgPlane.fromPoints = (a, b, c) => {
    const n = V3.cross(V3.sub(b, a), V3.sub(c, a)), l = V3.len(n);
    if (l < 1e-12) return null;                                   // degenerate triangle
    const u = { x: n.x / l, y: n.y / l, z: n.z / l };
    return new CsgPlane(u, V3.dot(u, a));
  };
  CsgPlane.prototype.flip = function () { this.normal = V3.neg(this.normal); this.w = -this.w; };
  CsgPlane.prototype.splitPolygon = function (poly, coplanarFront, coplanarBack, front, back) {
    const COPLANAR = 0, FRONT = 1, BACK = 2, SPANNING = 3; let polyType = 0; const types = [];
    for (const v of poly.vertices) {
      const t = V3.dot(this.normal, v) - this.w, type = t < -CSG_EPS ? BACK : t > CSG_EPS ? FRONT : COPLANAR;
      polyType |= type; types.push(type);
    }
    if (polyType === COPLANAR) (V3.dot(this.normal, poly.plane.normal) > 0 ? coplanarFront : coplanarBack).push(poly);
    else if (polyType === FRONT) front.push(poly);
    else if (polyType === BACK) back.push(poly);
    else {
      const f = [], b = [];
      for (let i = 0; i < poly.vertices.length; i++) {
        const j = (i + 1) % poly.vertices.length, ti = types[i], tj = types[j], vi = poly.vertices[i], vj = poly.vertices[j];
        if (ti !== BACK) f.push(vi);
        if (ti !== FRONT) b.push(vi);
        if ((ti | tj) === SPANNING) {
          const t = (this.w - V3.dot(this.normal, vi)) / V3.dot(this.normal, V3.sub(vj, vi)), v = V3.lerp(vi, vj, t);
          f.push(v); b.push(v);
        }
      }
      if (f.length >= 3) front.push(new CsgPoly(f, poly.plane));
      if (b.length >= 3) back.push(new CsgPoly(b, poly.plane));
    }
  };
  function CsgPoly(vertices, plane) { this.vertices = vertices; this.plane = plane; }
  CsgPoly.prototype.flip = function () { this.vertices.reverse(); this.plane = new CsgPlane(this.plane.normal, this.plane.w); this.plane.flip(); };
  function CsgNode(polys) { this.plane = null; this.front = null; this.back = null; this.polygons = []; if (polys && polys.length) this.build(polys); }
  CsgNode.prototype.invert = function () {
    const stack = [this];
    while (stack.length) {
      const n = stack.pop();
      n.polygons.forEach(p => p.flip());
      if (n.plane) { n.plane = new CsgPlane(n.plane.normal, n.plane.w); n.plane.flip(); }
      const t = n.front; n.front = n.back; n.back = t;
      if (n.front) stack.push(n.front); if (n.back) stack.push(n.back);
    }
  };
  CsgNode.prototype.clipPolygons = function (polys) {
    if (!this.plane) return polys.slice();
    let front = [], back = [];
    for (const p of polys) this.plane.splitPolygon(p, front, back, front, back);
    front = this.front ? this.front.clipPolygons(front) : front;
    back = this.back ? this.back.clipPolygons(back) : [];
    return front.concat(back);
  };
  CsgNode.prototype.clipTo = function (bsp) {
    const stack = [this];
    while (stack.length) { const n = stack.pop(); n.polygons = bsp.clipPolygons(n.polygons); if (n.front) stack.push(n.front); if (n.back) stack.push(n.back); }
  };
  CsgNode.prototype.allPolygons = function () {
    let out = []; const stack = [this];
    while (stack.length) { const n = stack.pop(); out = out.concat(n.polygons); if (n.front) stack.push(n.front); if (n.back) stack.push(n.back); }
    return out;
  };
  CsgNode.prototype.build = function (polys) {
    const stack = [[this, polys]];
    while (stack.length) {
      const [node, list] = stack.pop(); if (!list.length) continue;
      if (!node.plane) node.plane = list[Math.floor(list.length / 2)].plane;      // middle polygon -> better balanced tree
      const front = [], back = [];
      for (const p of list) node.plane.splitPolygon(p, node.polygons, node.polygons, front, back);
      if (front.length) { if (!node.front) node.front = new CsgNode(); stack.push([node.front, front]); }
      if (back.length) { if (!node.back) node.back = new CsgNode(); stack.push([node.back, back]); }
    }
  };
  /* THREE.Mesh -> world-space triangle polygons */
  function meshToPolys(mesh) {
    mesh.updateMatrixWorld(true);
    let g = mesh.geometry; if (g.index) g = g.toNonIndexed();
    const pos = g.attributes.position, m = mesh.matrixWorld, polys = [], e = m.elements;
    const P = i => { const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i); return { x: e[0] * x + e[4] * y + e[8] * z + e[12], y: e[1] * x + e[5] * y + e[9] * z + e[13], z: e[2] * x + e[6] * y + e[10] * z + e[14] }; };
    for (let i = 0; i + 2 < pos.count; i += 3) {
      const a = P(i), b = P(i + 1), c = P(i + 2), pl = CsgPlane.fromPoints(a, b, c);
      if (pl) polys.push(new CsgPoly([a, b, c], pl));
    }
    if (m.determinant() < 0) polys.forEach(p => p.flip());           // mirrored scale flips the winding
    return polys;
  }
  /* polygons -> centred THREE.BufferGeometry (+ the centre, so the mesh can sit where the solid is) */
  function polysToGeometry(polys) {
    const arr = [];
    for (const p of polys) for (let i = 1; i < p.vertices.length - 1; i++) for (const v of [p.vertices[0], p.vertices[i], p.vertices[i + 1]]) arr.push(v.x, v.y, v.z);
    if (!arr.length) return null;
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(arr, 3));
    g.computeBoundingBox(); const c = new THREE.Vector3(); g.boundingBox.getCenter(c); g.translate(-c.x, -c.y, -c.z); g.computeVertexNormals();
    return { geometry: g, center: c };
  }
  function csgCompute(op, meshA, meshB) {
    const A = new CsgNode(meshToPolys(meshA)), B = new CsgNode(meshToPolys(meshB));
    if (op === 'union') { A.clipTo(B); B.clipTo(A); B.invert(); B.clipTo(A); B.invert(); A.build(B.allPolygons()); return A.allPolygons(); }
    if (op === 'subtract') { A.invert(); A.clipTo(B); B.clipTo(A); B.invert(); B.clipTo(A); B.invert(); A.build(B.allPolygons()); A.invert(); return A.allPolygons(); }
    A.invert(); B.clipTo(A); B.invert(); A.clipTo(B); B.clipTo(A); A.build(B.allPolygons()); A.invert(); return A.allPolygons();   // intersect
  }
  /* choose the two solids: the selected one (A) and the nearest other solid that overlaps it (B) */
  function getActivePair() {
    if (objects3D.length < 2) return null;
    let obj1 = selectedObject;
    if (!obj1 || !objects3D.includes(obj1)) obj1 = objects3D[objects3D.length - 1];
    const b1 = new THREE.Box3().setFromObject(obj1), c1 = b1.getCenter(new THREE.Vector3());
    let obj2 = null, bestD = Infinity;
    for (const o of objects3D) {
      if (o === obj1) continue;
      const b2 = new THREE.Box3().setFromObject(o), d = b2.getCenter(new THREE.Vector3()).distanceTo(c1) - (b1.intersectsBox(b2) ? 1e6 : 0);   // overlapping solids first
      if (d < bestD) { bestD = d; obj2 = o; }
    }
    return obj2 ? { obj1, obj2 } : null;
  }
  function booleanOp(op) {
    const label = T('lbl_' + op);
    const pair = getActivePair();
    if (!pair) { statusBarText.innerText = T('needTwo', label); return; }
    const { obj1, obj2 } = pair;
    const nTri = (obj1.geometry.index ? obj1.geometry.index.count : obj1.geometry.attributes.position.count) / 3 + (obj2.geometry.index ? obj2.geometry.index.count : obj2.geometry.attributes.position.count) / 3;
    if (nTri > 40000) { statusBarText.innerText = T('tooDetailed', label, Math.round(nTri)); return; }
    let polys;
    try { polys = csgCompute(op, obj1, obj2); } catch (e) { console.error(e); statusBarText.innerText = T('failed', label); return; }
    const res = polysToGeometry(polys);
    if (!res) { statusBarText.innerText = op === 'intersect' ? T('noOverlap') : T('nothingLeft', label); return; }
    pushHistory();
    const material = new THREE.MeshStandardMaterial({ color: obj1.material ? obj1.material.color.clone() : new THREE.Color(currentColor), roughness: 0.35, metalness: 0.25, emissive: 0x000000, side: THREE.DoubleSide });
    const resultMesh = new THREE.Mesh(res.geometry, material);
    resultMesh.userData.kind = 'Boolean ' + op; resultMesh.userData.mat = obj1.userData.mat || 'Steel';
    resultMesh.position.copy(res.center);
    [obj1, obj2].forEach(o => { scene.remove(o); const i = objects3D.indexOf(o); if (i > -1) objects3D.splice(i, 1); if (o.geometry) o.geometry.dispose(); });
    attachAutoCADEdges(resultMesh);
    scene.add(resultMesh); objects3D.push(resultMesh);
    if (selectedObject) setHighlight(selectedObject, false);
    selectedObject = resultMesh; setHighlight(selectedObject, true);
    statusBarText.innerText = T('boolOk', label);
    updateMeasurements(selectedObject);
  }
  function performUnion() { booleanOp('union'); }
  function performIntersect() { booleanOp('intersect'); }
  function performSubtract() { booleanOp('subtract'); }

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
      pinchIndicator.innerText = T('pinchNone');
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
      statusBarText.innerText = T('objSel');
      
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
    mesh.userData.kind = type.charAt(0).toUpperCase() + type.slice(1); mesh.userData.mat = 'Steel';
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

  /* ====================================================================================
     Engineering tools: properties (exact size / volume / mass), section view, project save/load, STL export
     1 scene unit = 1.5 mm (same scale as the existing Measure tool).
     ==================================================================================== */
  const MM = 1.5;
  const MATERIALS = { 'Steel': 7.85, 'Aluminium': 2.70, 'Cast iron': 7.20, 'Titanium': 4.51, 'Copper': 8.96, 'ABS plastic': 1.05 };
  const hudCanvas = document.getElementById('hud-canvas'), hudCtx = hudCanvas.getContext('2d');
  renderer.localClippingEnabled = true;

  /* ---- guide ---- */
  const guideState = { point: false, pinch: false, drag: false, scale: false, rotate: false };
  function refreshTicks() { Object.keys(guideState).forEach(k => { const t = document.getElementById('t-' + k); if (t) t.innerText = guideState[k] ? T('detected') : T('notSeen'); }); }
  function buildMatOptions() { const cur = matSel.value || 'Steel'; matSel.innerHTML = ''; Object.keys(MATERIALS).forEach(k => { const o = document.createElement('option'); o.value = k; o.textContent = matText(k) + ' (' + MATERIALS[k] + ' g/cm3)'; matSel.appendChild(o); }); matSel.value = cur; }
  function markGuide(k) {
    if (guideState[k]) return;
    guideState[k] = true;
    const card = document.getElementById('g-' + k), tick = document.getElementById('t-' + k);
    if (card) card.classList.add('done');
    if (tick) tick.innerText = T('detected');
  }
  function showGuide(show) {
    document.getElementById('guide').style.display = show ? 'flex' : 'none';
    if (!show) { try { if (document.getElementById('guide-hide').checked) localStorage.setItem('cadGuideSeen', '1'); } catch (e) { } }
  }
  try { if (!localStorage.getItem('cadGuideSeen')) setTimeout(() => showGuide(true), 600); } catch (e) { setTimeout(() => showGuide(true), 600); }

  /* ---- solid properties ---- */
  function solidStats(mesh) {
    mesh.updateMatrixWorld(true);
    const g = mesh.geometry, pos = g.attributes.position, idx = g.index, e = mesh.matrixWorld.elements, n = idx ? idx.count : pos.count;
    const P = i => { const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i); return [e[0] * x + e[4] * y + e[8] * z + e[12], e[1] * x + e[5] * y + e[9] * z + e[13], e[2] * x + e[6] * y + e[10] * z + e[14]]; };
    let vol = 0, area = 0;
    for (let i = 0; i + 2 < n; i += 3) {
      const a = P(idx ? idx.getX(i) : i), b = P(idx ? idx.getX(i + 1) : i + 1), c = P(idx ? idx.getX(i + 2) : i + 2);
      vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6;
      const ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2], vx = c[0] - a[0], vy = c[1] - a[1], vz = c[2] - a[2];
      area += 0.5 * Math.hypot(uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx);
    }
    return { vol: Math.abs(vol) * MM * MM * MM, area: area * MM * MM };      // mm3, mm2
  }
  const matSel = document.getElementById('p-mat');
  buildMatOptions();
  matSel.onchange = () => { if (selectedObject) { selectedObject.userData.mat = matSel.value; lastPropsKey = ''; updateProps(); } };
  ['x', 'y', 'z'].forEach(ax => {
    const el = document.getElementById('dim-' + ax);
    el.onchange = () => {
      const mm = parseFloat(el.value);
      if (!selectedObject || !(mm > 0)) return;
      const g = selectedObject.geometry; if (!g.boundingBox) g.computeBoundingBox();
      const s = new THREE.Vector3(); g.boundingBox.getSize(s);
      if (s[ax] * MM > 1e-6) { pushHistory(); selectedObject.scale[ax] = mm / (s[ax] * MM); }
      lastPropsKey = ''; updateProps(); updateMeasurements(selectedObject);
    };
  });
  let lastPropsKey = '', lastStats = null, lastPropsT = 0;
  function fmtMass(g) { return g >= 1000 ? (g / 1000).toFixed(3) + ' kg' : g.toFixed(1) + ' g'; }
  function updateProps() {
    const card = document.getElementById('props');
    if (!selectedObject || activeMode !== '3D' || !objects3D.includes(selectedObject)) { card.style.display = 'none'; return; }
    card.style.display = 'flex';
    const o = selectedObject, g = o.geometry; if (!g.boundingBox) g.computeBoundingBox();
    const key = o.uuid + o.scale.toArray().map(v => v.toFixed(3)).join(',') + (o.userData.mat || 'Steel') + g.uuid;
    if (key !== lastPropsKey) { lastPropsKey = key; lastStats = solidStats(o); }
    const s = new THREE.Vector3(); g.boundingBox.getSize(s);
    ['x', 'y', 'z'].forEach(ax => { const el = document.getElementById('dim-' + ax); if (document.activeElement !== el) el.value = (s[ax] * o.scale[ax] * MM).toFixed(1); });
    const mat = o.userData.mat || 'Steel'; if (matSel.value !== mat && document.activeElement !== matSel) matSel.value = mat;
    document.getElementById('p-kind').innerText = kindText(o.userData.kind || 'Object');
    document.getElementById('p-vol').innerText = (lastStats.vol / 1000).toFixed(2) + ' cm3';
    document.getElementById('p-area').innerText = (lastStats.area / 100).toFixed(1) + ' cm2';
    document.getElementById('p-mass').innerText = fmtMass(lastStats.vol / 1000 * MATERIALS[mat]);
  }

  /* ---- section view ---- */
  let sectionOn = false, sectionAxis = 'x', sectionFlipped = false, sectionPos = 0;
  const clipPlane = new THREE.Plane(new THREE.Vector3(1, 0, 0), 0);
  const cutHelper = new THREE.Mesh(new THREE.PlaneGeometry(500, 500), new THREE.MeshBasicMaterial({ color: 0xfacc15, transparent: true, opacity: 0.12, side: THREE.DoubleSide, depthWrite: false }));
  cutHelper.visible = false; scene.add(cutHelper);
  function refreshSection() {
    const n = new THREE.Vector3(); n[sectionAxis] = 1; const s = sectionFlipped ? -1 : 1;
    clipPlane.normal.copy(n).multiplyScalar(s); clipPlane.constant = -sectionPos * s;   // keeps the side where n.p + c >= 0
    cutHelper.position.set(0, 0, 0); cutHelper.position[sectionAxis] = sectionPos;
    cutHelper.rotation.set(0, sectionAxis === 'x' ? Math.PI / 2 : 0, 0); if (sectionAxis === 'y') cutHelper.rotation.x = Math.PI / 2;
    cutHelper.visible = sectionOn && activeMode === '3D';
    document.getElementById('btn-section').innerText = T('secBtn', sectionOn);
    document.getElementById('btn-section').classList.toggle('active', sectionOn);
    document.getElementById('sec-readout').innerText = T('secRead', sectionAxis.toUpperCase(), Math.round(sectionPos * MM), sectionFlipped);
  }
  function toggleSection() { sectionOn = !sectionOn; refreshSection(); }
  function setSectionAxis(a) { sectionAxis = a; ['x', 'y', 'z'].forEach(k => document.getElementById('sec-' + k).classList.toggle('active', k === a)); refreshSection(); }
  function setSectionPos(v) { sectionPos = parseFloat(v); if (!sectionOn) sectionOn = true; refreshSection(); }
  function flipSection() { sectionFlipped = !sectionFlipped; refreshSection(); }
  function applyClipping() {
    const want = sectionOn && activeMode === '3D';
    objects3D.forEach(o => {
      if (o.userData.clipOn === want) return;
      o.userData.clipOn = want;
      const mats = [o.material]; const el = o.getObjectByName('cadEdgeLines'); if (el) mats.push(el.material);
      mats.forEach(m => { m.clippingPlanes = want ? [clipPlane] : null; m.clipShadows = true; m.needsUpdate = true; });
    });
  }
  refreshSection();

  /* ---- save / load project ---- */
  function downloadBlob(blob, name) {
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 800);
  }
  function f32ToB64(arr) {
    const u8 = new Uint8Array(arr.buffer, arr.byteOffset, arr.byteLength); let s = ''; const CH = 0x8000;
    for (let i = 0; i < u8.length; i += CH) s += String.fromCharCode.apply(null, u8.subarray(i, i + CH));
    return btoa(s);
  }
  function b64ToF32(b64) { const bin = atob(b64), u8 = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i); return new Float32Array(u8.buffer); }
  function saveProject() {
    if (!objects3D.length) { statusBarText.innerText = T('noSave'); return; }
    const data = {
      app: 'ARGestureCAD', version: 1,
      objects: objects3D.map(o => {
        let g = o.geometry; if (g.index) g = g.toNonIndexed();
        return { kind: o.userData.kind || 'Object', mat: o.userData.mat || 'Steel', color: '#' + o.material.color.getHexString(),
          pos: o.position.toArray(), rot: [o.rotation.x, o.rotation.y, o.rotation.z], scale: o.scale.toArray(), geom: f32ToB64(new Float32Array(g.attributes.position.array)) };
      })
    };
    downloadBlob(new Blob([JSON.stringify(data)], { type: 'application/json' }), 'cad_project.json');
    statusBarText.innerText = T('saved', objects3D.length);
  }
  function loadProject(file) {
    const rd = new FileReader();
    rd.onload = () => {
      try {
        const data = JSON.parse(rd.result);
        if (data.app !== 'ARGestureCAD' || !Array.isArray(data.objects)) throw new Error('not a project file');
        pushHistory();
        objects3D.forEach(o => { scene.remove(o); if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); });
        objects3D.length = 0; selectedObject = null;
        data.objects.forEach(d => {
          const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(b64ToF32(d.geom), 3)); g.computeVertexNormals();
          const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: d.color, roughness: 0.35, metalness: 0.25, emissive: 0x000000, side: THREE.DoubleSide }));
          m.position.fromArray(d.pos); m.rotation.set(d.rot[0], d.rot[1], d.rot[2]); m.scale.fromArray(d.scale);
          m.userData.kind = d.kind; m.userData.mat = MATERIALS[d.mat] ? d.mat : 'Steel';
          attachAutoCADEdges(m); scene.add(m); objects3D.push(m);
        });
        if (objects3D.length) { selectedObject = objects3D[objects3D.length - 1]; setHighlight(selectedObject, true); updateMeasurements(selectedObject); }
        statusBarText.innerText = T('loaded', objects3D.length);
      } catch (err) { console.error(err); statusBarText.innerText = T('loadFail'); }
    };
    rd.readAsText(file);
  }
  document.getElementById('file-load').onchange = e => { if (e.target.files[0]) loadProject(e.target.files[0]); e.target.value = ''; };

  /* ---- binary STL export (millimetres, Z-up like CAD programs) ---- */
  function exportSTL() {
    if (!objects3D.length) { statusBarText.innerText = T('noExport'); return; }
    const tris = [];
    objects3D.forEach(o => {
      o.updateMatrixWorld(true);
      const g = o.geometry, pos = g.attributes.position, idx = g.index, e = o.matrixWorld.elements, n = idx ? idx.count : pos.count, flip = o.matrixWorld.determinant() < 0;
      const P = i => { const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i), wx = e[0] * x + e[4] * y + e[8] * z + e[12], wy = e[1] * x + e[5] * y + e[9] * z + e[13], wz = e[2] * x + e[6] * y + e[10] * z + e[14]; return [wx * MM, -wz * MM, wy * MM]; };
      for (let i = 0; i + 2 < n; i += 3) {
        let a = P(idx ? idx.getX(i) : i), b = P(idx ? idx.getX(i + 1) : i + 1), c = P(idx ? idx.getX(i + 2) : i + 2);
        if (flip) { const t = b; b = c; c = t; }
        tris.push([a, b, c]);
      }
    });
    const buf = new ArrayBuffer(84 + tris.length * 50), dv = new DataView(buf);
    const hdr = 'AR Gesture CAD Studio'; for (let i = 0; i < hdr.length; i++) dv.setUint8(i, hdr.charCodeAt(i));
    dv.setUint32(80, tris.length, true);
    tris.forEach((t, k) => {
      const o = 84 + k * 50, u = [t[1][0] - t[0][0], t[1][1] - t[0][1], t[1][2] - t[0][2]], v = [t[2][0] - t[0][0], t[2][1] - t[0][1], t[2][2] - t[0][2]];
      let nx = u[1] * v[2] - u[2] * v[1], ny = u[2] * v[0] - u[0] * v[2], nz = u[0] * v[1] - u[1] * v[0]; const l = Math.hypot(nx, ny, nz) || 1; nx /= l; ny /= l; nz /= l;
      [nx, ny, nz, ...t[0], ...t[1], ...t[2]].forEach((val, j) => dv.setFloat32(o + j * 4, val, true));
    });
    downloadBlob(new Blob([buf], { type: 'model/stl' }), 'cad_model.stl');
    statusBarText.innerText = T('stlOk', tris.length);
  }

  featuresReady = true;
  applyLang(); statusBarText.innerText = T('initCam');

  /* ---- two-hand scale / rotate ---- */
  let twoHand = null, pinchLockUntil = 0;
  function pinchInfo(lm) {
    const t = lm[4], i = lm[8], ix = (1 - i.x) * 1280, iy = i.y * 720, tx = (1 - t.x) * 1280, ty = t.y * 720;
    return { ix, iy, tx, ty, dist: Math.hypot(ix - tx, iy - ty), mx: (ix + tx) / 2, my: (iy + ty) / 2 };
  }
  function drawTwoHandHud(a, b, text, ok) {
    hudCtx.lineWidth = 4; hudCtx.strokeStyle = ok ? '#facc15' : '#f97316'; hudCtx.setLineDash(ok ? [] : [10, 8]);
    hudCtx.beginPath(); hudCtx.moveTo(a.x, a.y); hudCtx.lineTo(b.x, b.y); hudCtx.stroke(); hudCtx.setLineDash([]);
    [a, b].forEach(p => { hudCtx.beginPath(); hudCtx.arc(p.x, p.y, 11, 0, Math.PI * 2); hudCtx.fillStyle = '#10b981'; hudCtx.fill(); hudCtx.strokeStyle = '#fff'; hudCtx.lineWidth = 2; hudCtx.stroke(); });
    hudCtx.font = '700 18px system-ui'; hudCtx.textAlign = 'center';
    const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2 - 18, w = hudCtx.measureText(text).width + 20;
    hudCtx.fillStyle = 'rgba(17,24,39,0.9)'; hudCtx.fillRect(mx - w / 2, my - 20, w, 30); hudCtx.fillStyle = ok ? '#facc15' : '#fdba74'; hudCtx.fillText(text, mx, my);
  }
  function handleTwoHand(infos) {
    const a = { x: infos[0].mx, y: infos[0].my }, b = { x: infos[1].mx, y: infos[1].my };
    const d = Math.max(20, getDistance(a, b)), ang = Math.atan2(b.y - a.y, b.x - a.x);
    if (!twoHand) {
      if (isPinching) { isPinching = false; if (previewMesh3D) { scene.remove(previewMesh3D); previewMesh3D = null; } }
      autoSelectUnderCursor((a.x + b.x) / 2, (a.y + b.y) / 2);              // selects the object between the hands (if any)
      if (!selectedObject || !objects3D.includes(selectedObject)) { twoHand = { none: true }; }
      else { pushHistory(); twoHand = { d0: d, ds: d, a0: ang, as: ang, s0: selectedObject.scale.clone(), r0: selectedObject.rotation.z, obj: selectedObject }; }
    }
    if (twoHand.none) { statusBarText.innerText = T('twoNone'); drawTwoHandHud(a, b, T('hudSelect'), false); return; }
    twoHand.ds += 0.4 * (d - twoHand.ds);
    let dA = ang - twoHand.as; while (dA > Math.PI) dA -= 2 * Math.PI; while (dA < -Math.PI) dA += 2 * Math.PI;
    twoHand.as += 0.4 * dA;
    let rel = twoHand.as - twoHand.a0; while (rel > Math.PI) rel -= 2 * Math.PI; while (rel < -Math.PI) rel += 2 * Math.PI;
    const ratio = twoHand.ds / twoHand.d0, o = twoHand.obj;
    o.scale.set(Math.max(0.05, twoHand.s0.x * ratio), Math.max(0.05, twoHand.s0.y * ratio), Math.max(0.05, twoHand.s0.z * ratio));
    o.rotation.z = twoHand.r0 - rel;
    if (Math.abs(ratio - 1) > 0.2) markGuide('scale');
    if (Math.abs(rel) > 0.35) markGuide('rotate');
    const txt = T('hudScale', ratio.toFixed(2), Math.round(-rel * 180 / Math.PI));
    statusBarText.innerText = T('twoMode', txt);
    drawTwoHandHud(a, b, txt, true);
    updateMeasurements(o);
  }

  function onResults(results) {
    const hs = results.multiHandLandmarks || [];
    hudCtx.clearRect(0, 0, 1280, 720);
    if (hs.length === 0) {
      twoHand = null;
      statusDot.classList.remove('active');
      statusBarText.innerText = T('searching');
      if (currentTool !== 'measure') pinchIndicator.innerText = T('pinchNone');
      if (activeMode === '3D') { cursorMesh.position.set(2000, 2000, 0); if (hoveredFaceMarker) hoveredFaceMarker.visible = false; }
      return;
    }
    statusDot.classList.add('active'); markGuide('point');
    const infos = hs.slice(0, 2).map(pinchInfo);

    if (infos.length === 2 && activeMode === '3D' && infos[0].dist < 45 && infos[1].dist < 45) { handleTwoHand(infos); return; }
    if (twoHand) { twoHand = null; pinchLockUntil = performance.now() + 700; }    // ignore single pinches briefly after two-hand use

    let k = 0; if (infos.length === 2 && infos[0].dist >= 45 && infos[1].dist < 45) k = 1;
    const info = infos[k], rawCursorX = info.ix, rawCursorY = info.iy;
    smoothedCursor.x = alpha * rawCursorX + (1 - alpha) * smoothedCursor.x;
    smoothedCursor.y = alpha * rawCursorY + (1 - alpha) * smoothedCursor.y;

    if (activeMode === '3D') {
      const cursor3DPos = mapScreenTo3D(smoothedCursor.x, smoothedCursor.y);
      cursorMesh.position.set(cursor3DPos.x, cursor3DPos.y, 50);
      checkFaceHover(smoothedCursor.x, smoothedCursor.y);
    }
    const pinchDist = info.dist;
    if (currentTool !== 'measure') pinchIndicator.innerText = T('pinchPx', Math.round(pinchDist));
    const currentlyPinching = pinchDist < 45 && (isPinching || performance.now() >= pinchLockUntil);
    if (activeMode === '3D') cursorMat.color.setHex(currentlyPinching ? 0x10b981 : 0x38bdf8);

    if (currentlyPinching) {
      markGuide('pinch');
      if (!isPinching) {
        isPinching = true;
        startPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
        lastPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
        if (activeMode === '3D') autoSelectUnderCursor(smoothedCursor.x, smoothedCursor.y);
        else currentPreviewShape = { tool: currentTool, color: currentColor, start: { x: smoothedCursor.x, y: smoothedCursor.y }, end: { x: smoothedCursor.x, y: smoothedCursor.y }, points: currentTool === 'free' ? [{ x: smoothedCursor.x, y: smoothedCursor.y }] : null };
        statusBarText.innerText = T('active', activeMode, currentTool.toUpperCase());
        updatePreview(startPinchPoint, { x: smoothedCursor.x, y: smoothedCursor.y });
      } else {
        if (activeMode === '3D' && ['move', 'resize', 'extrude', 'rotx', 'roty', 'rotz'].includes(currentTool)) { handleTransform(smoothedCursor, lastPinchPoint); markGuide('drag'); }
        else updatePreview(startPinchPoint, { x: smoothedCursor.x, y: smoothedCursor.y });
        lastPinchPoint = { x: smoothedCursor.x, y: smoothedCursor.y };
      }
    } else {
      if (isPinching) { isPinching = false; statusBarText.innerText = T('tracking', activeMode); finalizeShape(); }
      else if (infos.length === 2 && activeMode === '3D') statusBarText.innerText = T('twoSeen');
    }
  }

  const hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
  });

  hands.setOptions({
    maxNumHands: 2,
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
    statusBarText.innerText = T('tracking', '3D');
  }).catch((err) => {
    statusBarText.innerText = T('camDenied');
    console.error(err);
  });
</script>

</body>
</html>
"""

# Replace placeholders using session state to prevent duplication bugs
html_code = html_code.replace("__STL_BASE64_PLACEHOLDER__", st.session_state.stl_b64)
html_code = html_code.replace("__IMG_BASE64_PLACEHOLDER__", st.session_state.img_b64)
components.html(html_code, height=740, width=1300)
