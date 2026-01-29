const dropArea = document.getElementById('drop-area');
const fileElem = document.getElementById('fileElem');
const solveBtn = document.getElementById('solveBtn');
const routeMap = document.getElementById('routeMap');
const totalCostEl = document.getElementById('totalCost');
const vehCountEl = document.getElementById('vehCount');

let currentFile = null;

// File Handling
fileElem.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    if (files.length > 0) {
        currentFile = files[0];
        document.querySelector('label[for="fileElem"]').innerText = currentFile.name;
    }
}

// Solve
solveBtn.addEventListener('click', async () => {
    if (!currentFile) return alert('Veuillez uploader un fichier .dat');

    solveBtn.innerText = 'Optimisation en cours...';
    solveBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', currentFile);

    try {
        const response = await fetch('/solve', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (response.ok) {
            renderSolution(data);
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

const V_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function renderSolution(data) {
    totalCostEl.innerText = data.cost.toFixed(2);
    vehCountEl.innerText = data.routes.length;

    // Clear map
    routeMap.innerHTML = '';

    // Calculate bounds to scale 0-100 coordinates
    // Assuming coordinates are already roughly in a reasonable range or 0-100

    data.routes.forEach((route, vIdx) => {
        const color = V_COLORS[vIdx % V_COLORS.length];

        // Draw path
        let d = `M ${route[0].x} ${100 - route[0].y}`;
        for (let i = 1; i < route.length; i++) {
            d += ` L ${route[i].x} ${100 - route[i].y}`;
        }

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', d);
        path.setAttribute('stroke', color);
        path.setAttribute('class', 'v-route');
        path.style.strokeOpacity = 0.7;
        routeMap.appendChild(path);

        // Draw nodes
        route.forEach(node => {
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', node.x);
            circle.setAttribute('cy', 100 - node.y);
            circle.setAttribute('r', node.type === 'start' || node.type === 'end' ? 1.2 : 0.8);

            let fill = '#fff';
            if (node.type === 'pickup') fill = '#f59e0b'; // Depot
            if (node.type === 'delivery') fill = '#ef4444'; // Station
            if (node.type === 'start') fill = color;

            circle.setAttribute('fill', fill);
            circle.setAttribute('class', 'node');

            const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
            title.textContent = `${node.type} ID:${node.id} Prod:P${node.product_type + 1}`;
            circle.appendChild(title);

            routeMap.appendChild(circle);
        });
    });
}
