import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const form = document.getElementById("convertForm");
const fileInput = document.getElementById("csvFile");
const csvText = document.getElementById("csvText");
const loadSampleButton = document.getElementById("loadSampleButton");
const statusMessage = document.getElementById("statusMessage");
const resultJson = document.getElementById("resultJson");
const validationLogs = document.getElementById("validationLogs");
const materialGroups = document.getElementById("materialGroups");
const summarySource = document.getElementById("summarySource");
const summaryRows = document.getElementById("summaryRows");
const summaryCabinets = document.getElementById("summaryCabinets");
const summaryPlanks = document.getElementById("summaryPlanks");
const viewerRoot = document.getElementById("viewer");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf7f1e7);

const camera = new THREE.PerspectiveCamera(50, 1, 1, 20000);
camera.position.set(2600, 2200, 3000);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio || 1);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
viewerRoot.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(800, 500, 600);

const ambientLight = new THREE.AmbientLight(0xffffff, 1.4);
scene.add(ambientLight);

const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
keyLight.position.set(2500, 3200, 2600);
keyLight.castShadow = true;
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xfff2df, 0.65);
fillLight.position.set(-1800, 1200, 900);
scene.add(fillLight);

const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(12000, 12000),
  new THREE.ShadowMaterial({ color: 0x000000, opacity: 0.08 }),
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -1;
floor.receiveShadow = true;
scene.add(floor);

const grid = new THREE.GridHelper(12000, 24, 0xc8baa2, 0xdccfb8);
grid.position.y = 0;
scene.add(grid);

const modelGroup = new THREE.Group();
scene.add(modelGroup);

const colors = {
  wall: 0x6d7686,
  cabinet: 0xcf8a44,
  plank: 0x3d866b,
};

function setStatus(message, type) {
  statusMessage.textContent = message;
  statusMessage.className = `status ${type}`;
}

function clearStatus() {
  statusMessage.textContent = "";
  statusMessage.className = "status hidden";
}

function resizeRenderer() {
  const width = viewerRoot.clientWidth;
  const height = viewerRoot.clientHeight;
  renderer.setSize(width, height, false);
  camera.aspect = width / Math.max(height, 1);
  camera.updateProjectionMatrix();
}

function clearModel() {
  while (modelGroup.children.length > 0) {
    const child = modelGroup.children[0];
    modelGroup.remove(child);
    if (child.geometry) {
      child.geometry.dispose();
    }
    if (Array.isArray(child.material)) {
      child.material.forEach((material) => material.dispose());
    } else if (child.material) {
      child.material.dispose();
    }
  }
}

function createLabelSprite(text) {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 128;
  const context = canvas.getContext("2d");
  context.fillStyle = "rgba(255, 250, 242, 0.95)";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.strokeStyle = "rgba(31, 37, 49, 0.2)";
  context.strokeRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#1f2531";
  context.font = "28px Segoe UI";
  context.fillText(text, 22, 74);

  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(420, 105, 1);
  return sprite;
}

function addBox({ type, entityName, dimensions, position }, parentPosition = { x: 0, y: 0, z: 0 }) {
  const geometry = new THREE.BoxGeometry(dimensions.width, dimensions.height, dimensions.depth);
  const material = new THREE.MeshStandardMaterial({
    color: colors[type],
    roughness: 0.48,
    metalness: 0.04,
    transparent: type === "wall",
    opacity: type === "wall" ? 0.82 : 1,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  const worldX = parentPosition.x + position.x + dimensions.width / 2;
  const worldY = parentPosition.y + position.z + dimensions.height / 2;
  const worldZ = parentPosition.z + position.y + dimensions.depth / 2;
  mesh.position.set(worldX, worldY, worldZ);

  const edgeLines = new THREE.LineSegments(
    new THREE.EdgesGeometry(geometry),
    new THREE.LineBasicMaterial({ color: 0x1d2433, transparent: true, opacity: 0.34 }),
  );
  mesh.add(edgeLines);

  const label = createLabelSprite(entityName);
  label.position.set(0, dimensions.height / 2 + 120, 0);
  mesh.add(label);

  modelGroup.add(mesh);

  return {
    x: parentPosition.x + position.x,
    y: parentPosition.y + position.z,
    z: parentPosition.z + position.y,
  };
}

function fitCameraToModel() {
  const box = new THREE.Box3().setFromObject(modelGroup);
  if (box.isEmpty()) {
    controls.target.set(800, 500, 600);
    camera.position.set(2600, 2200, 3000);
    return;
  }

  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDimension = Math.max(size.x, size.y, size.z, 1);
  const distance = maxDimension * 1.8;

  controls.target.copy(center);
  camera.position.set(center.x + distance, center.y + distance * 0.8, center.z + distance);
  camera.near = Math.max(1, distance / 200);
  camera.far = distance * 10;
  camera.updateProjectionMatrix();
}

function renderModel(payload) {
  clearModel();

  const { model } = payload;
  if (!model || !model.wall) {
    return;
  }

  addBox(model.wall);

  model.cabinets.forEach((entry) => {
    const cabinetBase = addBox(entry.cabinet, model.wall.position);
    entry.planks.forEach((plank) => {
      addBox(plank, cabinetBase);
    });
  });

  fitCameraToModel();
}

function renderSummary(payload) {
  summarySource.textContent = payload.sourceName;
  summaryRows.textContent = String(payload.rowCount);
  summaryCabinets.textContent = String(payload.model.metadata.cabinetCount);
  summaryPlanks.textContent = String(payload.model.metadata.plankCount);
  resultJson.textContent = payload.modelJson;

  validationLogs.innerHTML = "";
  const logs = payload.model.metadata.validationLogs;
  if (!logs.length) {
    validationLogs.className = "log-list empty-list";
    validationLogs.innerHTML = "<li>No validation issues found.</li>";
  } else {
    validationLogs.className = "log-list";
    logs.forEach((log) => {
      const item = document.createElement("li");
      item.textContent = `${String(log.level).toUpperCase()}${log.row ? ` row ${log.row}` : ""}: ${log.message}`;
      validationLogs.appendChild(item);
    });
  }

  materialGroups.innerHTML = "";
  const groups = payload.model.metadata.materialGroups;
  const materialNames = Object.keys(groups);
  if (!materialNames.length) {
    materialGroups.className = "log-list empty-list";
    materialGroups.innerHTML = "<li>No grouped materials available.</li>";
  } else {
    materialGroups.className = "log-list";
    materialNames.forEach((material) => {
      const item = document.createElement("li");
      item.textContent = `${material}: ${groups[material].length} item(s)`;
      materialGroups.appendChild(item);
    });
  }
}

async function submitConversion(formData) {
  clearStatus();
  setStatus("Generating the 3D model from your CSV...", "success");

  const response = await fetch("/api/convert", {
    method: "POST",
    body: formData,
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Conversion failed.");
  }

  renderSummary(payload);
  renderModel(payload);
  setStatus("3D model generated successfully.", "success");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData();
  if (fileInput.files[0]) {
    formData.append("csv_file", fileInput.files[0]);
  }
  if (csvText.value.trim()) {
    formData.append("csv_text", csvText.value.trim());
  }

  try {
    await submitConversion(formData);
  } catch (error) {
    setStatus(error.message, "error");
  }
});

loadSampleButton.addEventListener("click", () => {
  csvText.value = window.__SAMPLE_CSV__;
  fileInput.value = "";
});

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

window.addEventListener("resize", resizeRenderer);
resizeRenderer();
animate();

if (window.__INITIAL_RESULT__) {
  renderSummary(window.__INITIAL_RESULT__);
  renderModel(window.__INITIAL_RESULT__);
  setStatus("Loaded the latest generated model.", "success");
}
