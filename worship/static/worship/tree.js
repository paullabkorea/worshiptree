import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const container = document.getElementById('tree-container');
if (container) {
  init();
}

async function init() {
  const width = container.clientWidth;
  const height = container.clientHeight || 500;

  // Scene
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87CEEB);
  scene.fog = new THREE.Fog(0x87CEEB, 40, 80);

  // Camera — pulled back to see large tree
  const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 200);
  camera.position.set(0, 10, 22);

  // Renderer
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.shadowMap.enabled = true;
  container.appendChild(renderer.domElement);

  // Controls
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 8, 0);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI / 2;

  // Lights
  scene.add(new THREE.AmbientLight(0xffffff, 0.7));
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
  dirLight.position.set(8, 20, 10);
  dirLight.castShadow = true;
  scene.add(dirLight);
  // Warm highlight from opposite side
  const fillLight = new THREE.DirectionalLight(0xfff0dd, 0.3);
  fillLight.position.set(-5, 8, -5);
  scene.add(fillLight);

  // Ground
  const groundGeo = new THREE.PlaneGeometry(60, 60);
  const groundMat = new THREE.MeshLambertMaterial({ color: 0x7CCD7C });
  const ground = new THREE.Mesh(groundGeo, groundMat);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  // ---- Big trunk ----
  const trunkGeo = new THREE.CylinderGeometry(0.6, 1.0, 8, 12);
  const trunkMat = new THREE.MeshLambertMaterial({ color: 0x8B4513 });
  const trunk = new THREE.Mesh(trunkGeo, trunkMat);
  trunk.position.y = 4;
  trunk.castShadow = true;
  scene.add(trunk);

  // ---- Thick branches ----
  const branchMat = new THREE.MeshLambertMaterial({ color: 0x6B3410 });
  const branches = [
    { pos: [0, 7, 0],   rot: [0, 0, 0.4],    len: 5 },
    { pos: [0, 6, 0],   rot: [0, 1.2, -0.45], len: 4.5 },
    { pos: [0, 5, 0],   rot: [0, 2.5, 0.4],   len: 4 },
    { pos: [0, 7.5, 0], rot: [0, 3.8, -0.35], len: 4.5 },
    { pos: [0, 5.5, 0], rot: [0, 5.0, 0.3],   len: 3.8 },
    { pos: [0, 8, 0],   rot: [0, 0.6, -0.25], len: 3.5 },
    { pos: [0, 6.5, 0], rot: [0, 4.2, 0.5],   len: 4 },
    { pos: [0, 7.8, 0], rot: [0, 2.0, 0.15],  len: 3 },
  ];
  branches.forEach(b => {
    const geo = new THREE.CylinderGeometry(0.08, 0.2, b.len, 8);
    geo.translate(0, b.len / 2, 0);
    const mesh = new THREE.Mesh(geo, branchMat);
    mesh.position.set(...b.pos);
    mesh.rotation.set(...b.rot);
    mesh.castShadow = true;
    scene.add(mesh);
  });

  // ---- Large canopy (many leaf clusters) ----
  const leafMat = new THREE.MeshLambertMaterial({ color: 0x228B22, transparent: true, opacity: 0.82 });
  const leafPositions = [
    // center top
    [0, 13, 0, 3.0],
    [0, 11, 0, 3.5],
    // ring around
    [2.5, 12, 1, 2.5],
    [-2.5, 12, -1, 2.5],
    [1, 11, -2.5, 2.5],
    [-1, 11, 2.5, 2.5],
    // lower ring
    [3.5, 10, 0, 2.2],
    [-3.5, 10, 0, 2.2],
    [0, 10, 3.5, 2.2],
    [0, 10, -3.5, 2.2],
    [2.5, 9.5, 2.5, 2.0],
    [-2.5, 9.5, -2.5, 2.0],
    [2.5, 9.5, -2.5, 2.0],
    [-2.5, 9.5, 2.5, 2.0],
    // fill gaps
    [1.5, 13.5, -1, 2.0],
    [-1.5, 13.5, 1, 2.0],
  ];
  leafPositions.forEach(([x, y, z, r]) => {
    const geo = new THREE.SphereGeometry(r, 10, 10);
    const mesh = new THREE.Mesh(geo, leafMat);
    mesh.position.set(x, y, z);
    scene.add(mesh);
  });

  // ---- Canopy surface function ----
  // The canopy is roughly an ellipsoid: center (0, 11, 0), radii ~6 horizontal, ~4 vertical
  const canopyCenter = new THREE.Vector3(0, 11, 0);
  const canopyRx = 5.8;  // horizontal radius
  const canopyRy = 3.8;  // vertical radius (top-bottom)

  function getCanopySurfacePoint(theta, phi) {
    // Spherical coords mapped onto ellipsoid surface + small outward push
    const outward = -0.15; // slightly inward so fruits touch the leaves
    const rx = canopyRx + outward;
    const ry = canopyRy + outward;
    const x = rx * Math.sin(phi) * Math.cos(theta);
    const z = rx * Math.sin(phi) * Math.sin(theta);
    const y = ry * Math.cos(phi);
    return new THREE.Vector3(
      canopyCenter.x + x,
      canopyCenter.y + y,
      canopyCenter.z + z,
    );
  }

  // ---- Fetch fruit data & create apples on canopy surface ----
  try {
    const res = await fetch('/api/tree-data/');
    const data = await res.json();
    const fruits = data.fruits || [];

    fruits.forEach((fruit, i) => {
      const apple = createApple();

      // Distribute on outer surface using Fibonacci sphere (golden angle)
      const golden = 2.399963;
      const theta = i * golden;
      // phi from ~30deg to ~140deg so fruits stay on visible part (not very top/bottom)
      const t = (i + 0.5) / Math.max(fruits.length, 1);
      const phi = 0.5 + t * 2.1; // range ~0.5 to ~2.6 radians

      const pos = getCanopySurfacePoint(theta, phi);
      apple.position.copy(pos);
      scene.add(apple);
    });
  } catch (e) {
    // No fruits to show
  }

  // ---- Apple mesh builder ----
  function createApple() {
    const group = new THREE.Group();

    // Apple body — red sphere
    const bodyGeo = new THREE.SphereGeometry(0.35, 14, 14);
    const bodyMat = new THREE.MeshPhongMaterial({
      color: 0xCC0000,
      shininess: 100,
      specular: 0x660000,
    });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.castShadow = true;
    group.add(body);

    // Slight indent on top
    body.scale.set(1, 0.9, 1);

    // Stem — small brown cylinder
    const stemGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.2, 6);
    const stemMat = new THREE.MeshLambertMaterial({ color: 0x5C3317 });
    const stem = new THREE.Mesh(stemGeo, stemMat);
    stem.position.y = 0.35;
    group.add(stem);

    // Tiny leaf on stem
    const leafGeo = new THREE.SphereGeometry(0.08, 6, 4);
    leafGeo.scale(1, 0.4, 1);
    const leafM = new THREE.MeshLambertMaterial({ color: 0x32CD32 });
    const leaf = new THREE.Mesh(leafGeo, leafM);
    leaf.position.set(0.06, 0.38, 0);
    leaf.rotation.z = -0.5;
    group.add(leaf);

    return group;
  }

  // Animation loop
  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  // Resize handler
  window.addEventListener('resize', () => {
    const w = container.clientWidth;
    const h = container.clientHeight || 500;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });
}
