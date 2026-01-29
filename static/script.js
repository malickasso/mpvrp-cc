const dropArea = document.getElementById('drop-area');
const fileElem = document.getElementById('fileElem');
const solveBtn = document.getElementById('solveBtn');
const totalCostEl = document.getElementById('totalCost');
const vehCountEl = document.getElementById('vehCount');

let currentFile = null;
let scene, camera, renderer, controls;
let objects = [];

// Initialize Three.js
function init3D() {
    const container = document.getElementById('map-3d');
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);

    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(50, 60, 100);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(50, 100, 50);
    scene.add(directionalLight);

    // Grid Floor
    const grid = new THREE.GridHelper(200, 20, 0x475569, 0x1e293b);
    grid.position.y = -0.1;
    scene.add(grid);

    animate();
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

window.addEventListener('resize', () => {
    const container = document.getElementById('map-3d');
    if (!container) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});

// File Handling
fileElem.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        currentFile = e.target.files[0];
        document.querySelector('label[for="fileElem"]').innerText = currentFile.name;
    }
});

// Solve
solveBtn.addEventListener('click', async () => {
    if (!currentFile) return alert('Veuillez uploader un fichier .dat');

    solveBtn.innerText = 'Calcul en cours...';
    solveBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', currentFile);

    try {
        const response = await fetch('/solve', { method: 'POST', body: formData });
        const data = await response.json();

        if (response.ok) {
            render3DSolution(data);
            showDownloadLink(data.dat_url);
        } else {
            alert(data.message || 'Erreur lors du traitement');
        }
    } catch (err) {
        console.error(err);
        alert('Erreur serveur');
    } finally {
        solveBtn.innerText = "Lancer l'Optimisation";
        solveBtn.disabled = false;
    }
});

function showDownloadLink(url) {
    let dlBtn = document.getElementById('dl-btn');
    if (!dlBtn) {
        dlBtn = document.createElement('a');
        dlBtn.id = 'dl-btn';
        dlBtn.className = 'btn-primary';
        dlBtn.style.textAlign = 'center';
        dlBtn.style.marginTop = '1rem';
        dlBtn.style.textDecoration = 'none';
        dlBtn.style.display = 'block';
        document.querySelector('.stats').appendChild(dlBtn);
    }
    dlBtn.href = url;
    dlBtn.innerText = 'Télécharger la Solution (.dat)';
}

const V_COLORS = [0x6366f1, 0x10b981, 0xf59e0b, 0xef4444, 0x8b5cf6, 0xec4899];

function clearScene() {
    objects.forEach(obj => scene.remove(obj));
    objects = [];
}

function createDetailedTruck(color) {
    const truckGroup = new THREE.Group();
    // Chassis
    const chassis = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.4, 4), new THREE.MeshPhongMaterial({ color: 0x222222 }));
    chassis.position.y = 0.4;
    truckGroup.add(chassis);
    // Cabin
    const cabin = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.4, 1.4), new THREE.MeshPhongMaterial({ color: color }));
    cabin.position.set(0, 1.2, 1.3);
    truckGroup.add(cabin);
    // Tank
    const tank = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.7, 2.6, 16), new THREE.MeshPhongMaterial({ color: 0x999999, shininess: 80 }));
    tank.rotateX(Math.PI / 2);
    tank.position.set(0, 1.3, -0.6);
    truckGroup.add(tank);
    // Wheels
    const wGeo = new THREE.CylinderGeometry(0.4, 0.4, 0.3, 12);
    wGeo.rotateZ(Math.PI / 2);
    const wMat = new THREE.MeshPhongMaterial({ color: 0x111111 });
    [[-0.8, 0.4, 1.4], [0.8, 0.4, 1.4], [-0.8, 0.4, -0.6], [0.8, 0.4, -0.6], [-0.8, 0.4, -1.5], [0.8, 0.4, -1.5]].forEach(p => {
        const w = new THREE.Mesh(wGeo, wMat);
        w.position.set(...p);
        truckGroup.add(w);
    });
    return truckGroup;
}

function createDetailedBuilding(node, color) {
    const group = new THREE.Group();
    group.position.set(node.x, 0, node.y);
    if (node.type === 'depot') {
        [[-1.5, 0, 0], [1.5, 0, 0], [0, 0, 1.5]].forEach(p => {
            const t = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 5, 16), new THREE.MeshPhongMaterial({ color: 0xf59e0b }));
            t.position.set(p[0], 2.5, p[2]);
            group.add(t);
        });
    } else if (node.type === 'station') {
        const base = new THREE.Mesh(new THREE.BoxGeometry(4, 0.2, 4), new THREE.MeshPhongMaterial({ color: 0x333333 }));
        group.add(base);
        const roof = new THREE.Mesh(new THREE.BoxGeometry(4.5, 0.2, 4.5), new THREE.MeshPhongMaterial({ color: 0xef4444 }));
        roof.position.y = 4;
        group.add(roof);
        [[-1.8, 2, 1.8], [1.8, 2, 1.8], [-1.8, 2, -1.8], [1.8, 2, -1.8]].forEach(p => {
            const pil = new THREE.Mesh(new THREE.BoxGeometry(0.2, 4, 0.2), new THREE.MeshPhongMaterial({ color: 0x777777 }));
            pil.position.set(...p);
            group.add(pil);
        });
        const pump = new THREE.Mesh(new THREE.BoxGeometry(0.6, 1.2, 0.4), new THREE.MeshPhongMaterial({ color: 0xef4444 }));
        pump.position.y = 0.6;
        group.add(pump);
    } else {
        const garage = new THREE.Mesh(new THREE.BoxGeometry(4, 3, 4), new THREE.MeshPhongMaterial({ color: color, transparent: true, opacity: 0.6 }));
        garage.position.y = 1.5;
        group.add(garage);
    }
    scene.add(group);
    objects.push(group);
}

// Helper for 3D Labels (CSS2D replacement using CanvasTexture)
function createTextLabel(text, color = 'white') {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(0, 0, 256, 64);
    ctx.font = 'Bold 30px Arial';
    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    ctx.fillText(text, 128, 45);

    const texture = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMat);
    sprite.scale.set(6, 1.5, 1);
    return sprite;
}

function render3DSolution(data) {
    totalCostEl.innerText = (data.total_distance + data.total_transition_cost).toFixed(2);
    vehCountEl.innerText = data.routes.length;
    clearScene();

    data.routes.forEach((routeData, vIdx) => {
        const color = V_COLORS[vIdx % V_COLORS.length];
        const route = routeData.nodes;
        const prods = routeData.prods;

        // 1. Create Buildings with Names and Demands
        route.forEach((node, i) => {
            createDetailedBuilding(node, color);
            if (node.type === 'station' || node.type === 'depot') {
                const label = createTextLabel(`${node.idx}: ${node.demand || 0}L`, node.type === 'depot' ? '#f59e0b' : '#ef4444');
                label.position.set(node.x, 8, node.y);
                scene.add(label);
                objects.push(label);
            }
        });

        const curvePoints = route.map(n => new THREE.Vector3(n.x, 0.2, n.y));
        const curve = new THREE.CatmullRomCurve3(curvePoints);
        const tube = new THREE.Mesh(
            new THREE.TubeGeometry(curve, 100, 0.1, 8, false),
            new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.2 })
        );
        scene.add(tube);
        objects.push(tube);

        const truck = createDetailedTruck(color);
        const truckLabel = createTextLabel('V' + (vIdx + 1), '#' + color.toString(16).padStart(6, '0'));
        truckLabel.position.y = 4;
        truck.add(truckLabel);

        scene.add(truck);
        objects.push(truck);

        let start = Date.now();
        const duration = 10000; // 10 seconds per route

        function animateTruck() {
            let elapsed = Date.now() - start;
            let progress = elapsed / duration;

            if (progress >= 1) {
                // Stop at the end (Home Garage)
                const finalPos = curve.getPointAt(1);
                truck.position.copy(finalPos);
                truckLabel.textContent = "DONE";
                return;
            }

            const pos = curve.getPointAt(progress);
            const nextPos = curve.getPointAt(Math.min(progress + 0.01, 1));
            truck.position.copy(pos);
            truck.lookAt(nextPos);

            // Dynamic Truck Label
            const nodeIdx = Math.floor(progress * (route.length - 1));
            const current = prods[nodeIdx] || prods[prods.length - 1];
            // We can't update text easily on CanvasTexture once created, 
            // but we can show the truck is active

            requestAnimationFrame(animateTruck);
        }
        animateTruck();
    });

    camera.position.set(50, 100, 150);
    controls.target.set(50, 0, 50);
}


init3D();
