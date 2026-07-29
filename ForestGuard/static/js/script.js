document.addEventListener("DOMContentLoaded", () => {
    console.log("🌲 ForestGuard: Nivel 3 (Multi-Nodo / Sala de Control) Activado");

    // --- 1. Navegación entre Pestañas ---
    const navLinks = document.querySelectorAll(".nav-link");
    const sections = document.querySelectorAll(".tab-content");

    navLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const targetTab = link.getAttribute("data-tab");

            navLinks.forEach(l => l.classList.remove("active"));
            link.classList.add("active");

            sections.forEach(sec => {
                if (sec.id === targetTab) {
                    sec.classList.remove("hidden");
                } else {
                    sec.classList.add("hidden");
                }
            });
        });
    });

    // --- 2. Base de Datos Local de los 3 Nodos ---
    const nodesData = {
        node1: {
            id: "ESP32-FG-01",
            location: "Sector Valparaíso - Reserva Peñuelas",
            temp: 24.5,
            hum: 55,
            smoke: false
        },
        node2: {
            id: "ESP32-FG-02",
            location: "Sector Biobío - Parque Nahuelbuta",
            temp: 19.0,
            hum: 68,
            smoke: false
        },
        node3: {
            id: "ESP32-FG-03",
            location: "Sector Araucanía - Reserva Conguillío",
            temp: 21.0,
            hum: 60,
            smoke: false
        }
    };

    let activeNodeId = "node1"; // Nodo seleccionado por defecto

    // Elementos del DOM
    const nodeBtns = document.querySelectorAll(".node-btn");
    const activeNodeTitle = document.getElementById("active-node-title");
    const activeNodeLocation = document.getElementById("active-node-location");

    const tempSlider = document.getElementById("temp-slider");
    const tempValue = document.getElementById("temp-value");
    const tempBar = document.getElementById("temp-bar");
    const cardTemp = document.getElementById("card-temp");

    const humSlider = document.getElementById("hum-slider");
    const humValue = document.getElementById("hum-value");
    const humBar = document.getElementById("hum-bar");
    const cardHum = document.getElementById("card-hum");

    const smokeToggle = document.getElementById("smoke-toggle");
    const smokeValue = document.getElementById("smoke-value");
    const smokeBar = document.getElementById("smoke-bar");
    const cardSmoke = document.getElementById("card-smoke");

    const globalStatus = document.getElementById("global-status");
    const liveAlertBanner = document.getElementById("live-alert-banner");
    const alertStep = document.querySelector(".alert-step");
    const btnAutoSim = document.getElementById("btn-auto-sim");

    let autoSimInterval = null;

    // --- 3. Función para Renderizar el Nodo Seleccionado ---
    function renderCurrentNode() {
        const currentNode = nodesData[activeNodeId];

        // Titulares
        if (activeNodeTitle) activeNodeTitle.innerText = `Nodo Activo: ${currentNode.id}`;
        if (activeNodeLocation) activeNodeLocation.innerText = currentNode.location;

        // Cargar valores a los sliders
        if (tempSlider) tempSlider.value = currentNode.temp;
        if (humSlider) humSlider.value = currentNode.hum;
        if (smokeToggle) smokeToggle.checked = currentNode.smoke;

        actualizarMetricasUI();
    }

    // --- 4. Evaluación Dinámica y Estado del Sistema ---
    function actualizarMetricasUI() {
        const currentNode = nodesData[activeNodeId];

        // Guardar valores desde los controles al nodo activo
        if (tempSlider) currentNode.temp = parseFloat(tempSlider.value);
        if (humSlider) currentNode.hum = parseInt(humSlider.value);
        if (smokeToggle) currentNode.smoke = smokeToggle.checked;

        const temp = currentNode.temp;
        const hum = currentNode.hum;
        const hayHumo = currentNode.smoke;

        // 1. Temperatura
        tempValue.innerText = `${temp.toFixed(1)} °C`;
        const tempPercent = Math.min(Math.max(((temp - 15) / (50 - 15)) * 100, 0), 100);
        tempBar.style.width = `${tempPercent}%`;

        if (temp > 40) {
            cardTemp.className = "metric-card card-danger";
            tempBar.style.backgroundColor = "#dc2626";
        } else if (temp > 30) {
            cardTemp.className = "metric-card card-warning";
            tempBar.style.backgroundColor = "#f97316";
        } else {
            cardTemp.className = "metric-card";
            tempBar.style.backgroundColor = "#16a34a";
        }

        // 2. Humedad
        humValue.innerText = `${hum} %`;
        humBar.style.width = `${hum}%`;

        if (hum < 20) {
            cardHum.className = "metric-card card-danger";
            humBar.style.backgroundColor = "#dc2626";
        } else if (hum < 35) {
            cardHum.className = "metric-card card-warning";
            humBar.style.backgroundColor = "#f97316";
        } else {
            cardHum.className = "metric-card";
            humBar.style.backgroundColor = "#2563eb";
        }

        // 3. Humo
        smokeValue.innerText = hayHumo ? "DETECTADO" : "NORMAL";
        smokeBar.style.width = hayHumo ? "100%" : "5%";
        smokeBar.style.backgroundColor = hayHumo ? "#dc2626" : "#64748b";
        cardSmoke.className = hayHumo ? "metric-card card-danger" : "metric-card";

        // --- Actualizar Indicadores de Todos los Nodos en la Red ---
        let hayPeligroGlobal = false;

        Object.keys(nodesData).forEach(key => {
            const node = nodesData[key];
            const esPeligro = node.temp > 40 || node.hum < 20 || node.smoke;
            const btn = document.getElementById(`node-btn-${key}`);
            
            if (btn) {
                const dot = btn.querySelector(".node-status-dot");
                if (esPeligro) {
                    dot.className = "node-status-dot red";
                    btn.classList.add("node-alert");
                    hayPeligroGlobal = true;
                } else {
                    dot.className = "node-status-dot green";
                    btn.classList.remove("node-alert");
                }
            }
        });

        // Alerta en Header y Banners
        if (hayPeligroGlobal) {
            if (globalStatus) {
                globalStatus.className = "status-badge status-danger";
                globalStatus.innerText = "🚨 ALERTA CRÍTICA EN RED";
            }
            if (liveAlertBanner) liveAlertBanner.classList.remove("hidden");
            if (alertStep) alertStep.classList.add("active-danger");
        } else {
            if (globalStatus) {
                globalStatus.className = "status-badge status-ok";
                globalStatus.innerText = "🟡 NODOS EN LÍNEA";
            }
            if (liveAlertBanner) liveAlertBanner.classList.add("hidden");
            if (alertStep) alertStep.classList.remove("active-danger");
        }
    }

    // --- 5. Cambio de Nodo por Clic del Usuario ---
    nodeBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            nodeBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            activeNodeId = btn.getAttribute("data-node");
            renderCurrentNode();
        });
    });

    // --- Eventos en Controles ---
    if (tempSlider) tempSlider.addEventListener("input", actualizarMetricasUI);
    if (humSlider) humSlider.addEventListener("input", actualizarMetricasUI);
    if (smokeToggle) smokeToggle.addEventListener("change", actualizarMetricasUI);

    // --- Fluctuación Automática en Tiempo Real ---
    if (btnAutoSim) {
        btnAutoSim.addEventListener("click", () => {
            if (autoSimInterval) {
                clearInterval(autoSimInterval);
                autoSimInterval = null;
                btnAutoSim.innerText = "Iniciar Fluctuación Automática 🔄";
                btnAutoSim.style.backgroundColor = "";
            } else {
                btnAutoSim.innerText = "Detener Simulación ⏸️";
                btnAutoSim.style.backgroundColor = "#dc2626";

                autoSimInterval = setInterval(() => {
                    const node = nodesData[activeNodeId];
                    node.temp = parseFloat((Math.random() * (45 - 18) + 18).toFixed(1));
                    node.hum = Math.floor(Math.random() * (70 - 15) + 15);
                    if (Math.random() < 0.2) node.smoke = !node.smoke;
                    
                    renderCurrentNode();
                }, 2000);
            }
        });
    }

    // Inicializar primer nodo
    renderCurrentNode();
});