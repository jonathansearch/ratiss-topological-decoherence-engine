(async () => {
  const body = document.body;
  const isComparison = Boolean(body.dataset.baseline);
  const $ = (selector) => document.querySelector(selector);
  const dom = {
    scene: $("#scene"), step: $("#step"), label: $("#step-label"), gate: $("#gate"), psig: $("#psig"), logical: $("#logical"), phase: $("#phase"), twist: $("#twist"), coherence: $("#coherence"), protected: $("#protected"), route: $("#route"), support: $("#support"), activation: $("#activation"), play: $("#play"), reset: $("#reset"), baseline: $("#baseline"), regularized: $("#regularized"),
  };
  const numeric = (value, digits = 3) => Number(value ?? 0).toFixed(digits);
  const radians = (value) => `${numeric(value)} rad`;
  const [design, documents] = await Promise.all([
    fetch("/api/studio/example").then((response) => response.json()),
    isComparison
      ? Promise.all([fetch(body.dataset.baseline).then((response) => response.json()), fetch(body.dataset.regularized).then((response) => response.json())]).then(([baseline, regularized]) => ({ baseline, regularized }))
      : fetch(body.dataset.artifact).then((response) => response.json()).then((single) => ({ single })),
  ]);
  let active = isComparison ? "baseline" : "single";
  let index = 0;
  let playing = true;
  let last = 0;
  let drag = null;

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x061018, 0.045);
  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  const world = new THREE.Group();
  const graphLayer = new THREE.Group();
  const logicalLayer = new THREE.Group();
  const starLayer = new THREE.Group();
  world.add(graphLayer, logicalLayer, starLayer);
  scene.add(world);
  scene.add(new THREE.HemisphereLight(0xc5fbff, 0x07101b, 1.45));
  const keyLight = new THREE.DirectionalLight(0x8fe7ff, 1.55);
  keyLight.position.set(3.4, 4.5, 7.2);
  scene.add(keyLight);
  const phaseLight = new THREE.PointLight(0xb99aff, 1.25, 11);
  phaseLight.position.set(-2.6, 1.6, 3.2);
  scene.add(phaseLight);
  camera.position.set(0, 0.35, 8.7);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  dom.scene.append(renderer.domElement);

  function resize() {
    const bounds = dom.scene.getBoundingClientRect();
    camera.aspect = bounds.width / bounds.height;
    camera.updateProjectionMatrix();
    renderer.setSize(bounds.width, bounds.height, false);
  }
  new ResizeObserver(resize).observe(dom.scene);
  resize();

  function renderDesign() {
    const ns = "http://www.w3.org/2000/svg";
    const designName = $("#design-name");
    const svg = $("#design-schematic");
    const layers = $("#design-layers");
    const frequency = $("#design-frequency");
    const crosstalk = $("#design-crosstalk");
    const count = $("#component-count");
    const status = $("#design-status");
    const consoleNode = $("#design-console");
    if (!svg) return;
    const colors = { qubit: "#4ce0c1", coupler: "#b99aff", resonator: "#79b7ff", feedline: "#f6c665" };
    designName.textContent = design.name;
    count.textContent = `${design.nodes.length} / ${design.edges.length}`;
    status.textContent = "design valide";
    for (const [source, target] of design.edges) {
      const from = design.nodes.find((node) => node.id === source);
      const to = design.nodes.find((node) => node.id === target);
      const line = document.createElementNS(ns, "line");
      line.setAttribute("x1", from.x); line.setAttribute("y1", from.y); line.setAttribute("x2", to.x); line.setAttribute("y2", to.y);
      line.setAttribute("stroke", "#62889b"); line.setAttribute("stroke-width", "1.35"); svg.append(line);
    }
    for (const node of design.nodes) {
      const nodeGroup = document.createElementNS(ns, "g");
      const circle = document.createElementNS(ns, "circle");
      const label = document.createElementNS(ns, "text");
      const frequencyLabel = document.createElementNS(ns, "text");
      circle.setAttribute("cx", node.x); circle.setAttribute("cy", node.y); circle.setAttribute("r", node.kind === "qubit" ? 7 : 5.6);
      circle.setAttribute("fill", colors[node.kind] || "#9fb6c1"); circle.setAttribute("stroke", "#f5ffff"); circle.setAttribute("stroke-opacity", ".65");
      label.setAttribute("x", node.x); label.setAttribute("y", node.y + 1.5); label.setAttribute("text-anchor", "middle"); label.setAttribute("font-size", "3.3"); label.setAttribute("font-weight", "700"); label.setAttribute("fill", "#061018"); label.textContent = node.id;
      frequencyLabel.setAttribute("x", node.x); frequencyLabel.setAttribute("y", node.y + 10); frequencyLabel.setAttribute("text-anchor", "middle"); frequencyLabel.setAttribute("font-size", "2.4"); frequencyLabel.setAttribute("fill", "#c9e1e8"); frequencyLabel.textContent = `${node.frequency} ${node.unit}`;
      nodeGroup.append(circle, label, frequencyLabel); svg.append(nodeGroup);
    }
    const layerByKind = { qubit: "josephson", coupler: "metal", resonator: "resonator", feedline: "control" };
    const layerCounts = {};
    design.nodes.forEach((node) => { const layer = layerByKind[node.kind] || "control"; layerCounts[layer] = (layerCounts[layer] || 0) + 1; });
    layers.innerHTML = Object.entries(layerCounts).map(([name, amount]) => `<div class="mini-row violet"><b>${name}</b> · ${amount} proxy(s)</div>`).join("");
    const qubits = design.nodes.filter((node) => node.kind === "qubit");
    const detuning = Math.abs(qubits[0].frequency - qubits[1].frequency);
    frequency.innerHTML = qubits.map((node, nodeIndex) => `<div class="mini-row"><b>${node.id}</b> · ${node.frequency} GHz<br>voisin ${qubits[1 - nodeIndex].id} · Δ ${detuning.toFixed(3)} GHz · stable</div>`).join("");
    crosstalk.innerHTML = `<div class="mini-row gold"><b>${qubits[0].id} ↔ ${qubits[1].id}</b> · 69/100<br>coupler c0 · Δ ${detuning.toFixed(3)} GHz · overlay nominal</div>`;
    consoleNode.textContent = JSON.stringify({ source: "quantum-circuit-studio/v0.1", name: design.name, logical_scaffold: ["h(q0)", "h(q1)", "cz(q0,q1)"], sidecar: "RATISS TopologicalQubit · twist / phase / coherence", output: "ratiss.topological-decoherence.timeline.v1" }, null, 2);
  }

  function disposeLayer(layer) {
    while (layer.children.length) {
      const child = layer.children.pop();
      child.traverse((object) => {
        object.geometry?.dispose?.();
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        materials.filter(Boolean).forEach((material) => material.dispose?.());
      });
    }
  }

  function current() { return documents[active]; }
  function addLine(parent, points, color, dashed = false, opacity = 0.82) {
    if (points.length < 2) return;
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = dashed
      ? new THREE.LineDashedMaterial({ color, dashSize: 0.13, gapSize: 0.09, transparent: true, opacity })
      : new THREE.LineBasicMaterial({ color, transparent: true, opacity });
    const line = new THREE.Line(geometry, material);
    if (dashed) line.computeLineDistances();
    parent.add(line);
  }

  function ringPoint(angle, twist, scale = 1) {
    const twistFraction = twist / Math.PI;
    const radius = (1.62 + twistFraction * 0.34 * Math.sin(3 * angle)) * scale;
    return new THREE.Vector3(radius * Math.cos(angle), radius * Math.sin(angle), twistFraction * 0.36 * Math.cos(3 * angle));
  }

  function addCorrelationArc(from, to, edge) {
    const correlation = Math.max(0, Number(edge.correlation ?? edge.mutual_information ?? 0));
    const stability = Math.max(0, Math.min(1, Number(edge.stability ?? 1)));
    const midpoint = from.clone().add(to).multiplyScalar(0.5);
    midpoint.y += 0.34 + correlation * 0.95;
    midpoint.z += edge.type === "quantum_candidate" ? 0.42 : 0.14;
    const curve = new THREE.QuadraticBezierCurve3(from, midpoint, to);
    const geometry = new THREE.TubeGeometry(curve, 36, 0.012 + correlation * 0.058, 7, false);
    const color = edge.type === "quantum_candidate" ? 0x4ce0c1 : 0x79b7ff;
    const material = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.22 + correlation * 0.5, transparent: true, opacity: 0.2 + stability * 0.78, roughness: 0.27, metalness: 0.28 });
    graphLayer.add(new THREE.Mesh(geometry, material));
  }

  function addTopologicalQubit(logical) {
    if (!logical || logical.P_sig == null || !Number.isFinite(Number(logical.P_sig))) return;
    const phase = Number(logical.phase || 0);
    const twist = Number(logical.twist || 0);
    const coherence = Math.max(0, Math.min(1, Number(logical.coherence ?? 1)));
    const signature = Math.max(0, Number(logical.P_sig || 0));
    const protectedState = Boolean(logical.protected);
    logicalLayer.rotation.set(0, 0, phase);
    logicalLayer.userData.phase = phase;
    logicalLayer.userData.coherence = coherence;
    const ringColor = protectedState ? 0x4ce0c1 : 0xff687a;
    const ringPoints = Array.from({ length: 97 }, (_, pointIndex) => ringPoint((Math.PI * 2 * pointIndex) / 96, twist));
    const ringCurve = new THREE.CatmullRomCurve3(ringPoints, true, "centripetal");
    const ringGeometry = new THREE.TubeGeometry(ringCurve, 144, 0.034 + Math.min(signature, 1.5) * 0.026, 9, true);
    const ringMaterial = new THREE.MeshStandardMaterial({ color: ringColor, emissive: ringColor, emissiveIntensity: 0.32 + coherence * 0.54, transparent: true, opacity: 0.28 + coherence * 0.7, roughness: 0.21, metalness: 0.34 });
    logicalLayer.add(new THREE.Mesh(ringGeometry, ringMaterial));

    const braidColors = [0xb99aff, 0xfa9cde, 0x79b7ff];
    braidColors.forEach((color, braidIndex) => {
      const braidPoints = Array.from({ length: 121 }, (_, pointIndex) => {
        const t = pointIndex / 120;
        const angle = Math.PI * 2 * t;
        const base = ringPoint(angle, twist);
        const ripple = 0.15 * Math.sin(angle * 3 + braidIndex * (Math.PI * 2 / 3));
        base.x += ripple * Math.cos(angle);
        base.y += ripple * Math.sin(angle);
        base.z += 0.14 * Math.cos(angle * 3 + braidIndex * (Math.PI * 2 / 3));
        return base;
      });
      const braidCurve = new THREE.CatmullRomCurve3(braidPoints, true, "centripetal");
      const braidGeometry = new THREE.TubeGeometry(braidCurve, 156, 0.015, 6, true);
      logicalLayer.add(new THREE.Mesh(braidGeometry, new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.3 + coherence * 0.22, transparent: true, opacity: 0.34 + coherence * 0.4, roughness: 0.32 })));
    });

    const beadCount = 12;
    for (let beadIndex = 0; beadIndex < beadCount; beadIndex += 1) {
      const bead = new THREE.Mesh(new THREE.SphereGeometry(0.055 + signature * 0.014, 14, 10), new THREE.MeshStandardMaterial({ color: 0xe6fffa, emissive: ringColor, emissiveIntensity: 0.62, roughness: 0.18 }));
      bead.position.copy(ringPoint((Math.PI * 2 * beadIndex) / beadCount, twist));
      logicalLayer.add(bead);
    }

    const phaseExtent = Math.max(0.18, Math.min(Math.PI * 2, phase || 0.18));
    const phasePoints = Array.from({ length: 32 }, (_, pointIndex) => {
      const angle = -Math.PI / 2 + phaseExtent * pointIndex / 31;
      return new THREE.Vector3(2.15 * Math.cos(angle), 2.15 * Math.sin(angle), 0.15);
    });
    addLine(logicalLayer, phasePoints, 0xf6c665, false, 0.92);
    const tip = phasePoints.at(-1);
    const arrow = new THREE.Mesh(new THREE.ConeGeometry(0.075, 0.19, 12), new THREE.MeshStandardMaterial({ color: 0xf6c665, emissive: 0xf6c665, emissiveIntensity: 0.7 }));
    arrow.position.copy(tip);
    arrow.rotation.z = Math.PI / 2 + (-Math.PI / 2 + phaseExtent);
    logicalLayer.add(arrow);

    const pulseGeometry = new THREE.SphereGeometry(0.16 + coherence * 0.13, 20, 16);
    const pulseMaterial = new THREE.MeshBasicMaterial({ color: ringColor, transparent: true, opacity: 0.1 + coherence * 0.18, wireframe: true });
    const pulse = new THREE.Mesh(pulseGeometry, pulseMaterial);
    pulse.position.set(0, 0, 0);
    logicalLayer.add(pulse);
  }

  function addGraph(nodes, edges, route) {
    const byId = new Map(nodes.map((node) => [node.id, node]));
    for (const edge of edges || []) {
      const source = byId.get(edge.source);
      const target = byId.get(edge.target);
      if (source && target) addCorrelationArc(new THREE.Vector3(...source.position), new THREE.Vector3(...target.position), edge);
    }
    addLine(graphLayer, (route || []).map((id) => byId.get(id)).filter(Boolean).map((node) => new THREE.Vector3(...node.position)), 0xf2abff, true, 0.96);
    for (const node of nodes) {
      const critical = Number(node.criticality || 0) >= 0.38;
      const support = Math.max(0, Number(node.topology_support || 0));
      const size = 0.13 + support * 0.28;
      const color = critical ? 0xff687a : 0x57d4bf;
      const mesh = new THREE.Mesh(new THREE.IcosahedronGeometry(size, 3), new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: critical ? 0.42 : 0.24 + support * 0.22, roughness: 0.25, metalness: 0.26 }));
      mesh.position.set(...node.position);
      graphLayer.add(mesh);
      const aura = new THREE.Mesh(new THREE.SphereGeometry(size * (critical ? 2.15 : 1.55), 18, 12), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: critical ? 0.09 : 0.045, wireframe: true }));
      aura.position.copy(mesh.position);
      graphLayer.add(aura);
    }
  }

  function addField() {
    const points = [];
    for (let pointIndex = 0; pointIndex < 90; pointIndex += 1) {
      const angle = pointIndex * 2.3999632297;
      const radius = 2.45 + (pointIndex % 9) * 0.06;
      points.push(new THREE.Vector3(Math.cos(angle) * radius, Math.sin(angle) * radius, -1.4 - (pointIndex % 5) * 0.06));
    }
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    starLayer.add(new THREE.Points(geometry, new THREE.PointsMaterial({ color: 0x79b7ff, size: 0.025, transparent: true, opacity: 0.36 })));
  }

  function updateMetrics(step, logical) {
    const scope = step.ttf_smooth_ablation;
    const hasLogicalState = logical?.P_sig != null && Number.isFinite(Number(logical.P_sig));
    dom.label.textContent = `${current().provenance?.mode || "local"} · étape ${step.step} / ${(current().steps || []).length - 1} · ${hasLogicalState ? "qubit topologique logiciel" : "graphe d’inspection"}`;
    dom.gate.textContent = scope ? `${step.gate} · frontière [${(scope.boundary_nodes || []).join(", ")}]` : step.gate;
    dom.psig.textContent = numeric(step.topology?.psig);
    if (dom.logical) dom.logical.textContent = hasLogicalState ? numeric(logical.P_sig) : "—";
    if (dom.phase) dom.phase.textContent = hasLogicalState ? radians(logical.phase) : "non exportée";
    if (dom.twist) dom.twist.textContent = hasLogicalState ? radians(logical.twist) : "non exportée";
    if (dom.coherence) dom.coherence.textContent = hasLogicalState ? numeric(logical.coherence) : "non exportée";
    if (dom.protected) {
      dom.protected.textContent = hasLogicalState ? (logical.protected ? `oui · bit ${logical.logical_bit}` : `non · bit ${logical.logical_bit}`) : "non exporté";
      dom.protected.style.color = logical?.protected ? "#82f4dc" : "#ff99a5";
    }
    if (dom.route) dom.route.textContent = (step.tsp_inspection?.path || []).length ? step.tsp_inspection.path.join(" → ") : "Aucune";
    if (dom.support) dom.support.textContent = numeric((step.qubits || []).reduce((sum, node) => sum + Number(node.topology_support || 0), 0));
    if (dom.activation) dom.activation.textContent = scope?.activation ? numeric(scope.activation.reduce((sum, value) => sum + value, 0) / scope.activation.length) : "—";
  }

  function draw() {
    const document = current();
    const steps = document.steps || [];
    const step = steps[index] || steps[0];
    if (!step) return;
    disposeLayer(graphLayer); disposeLayer(logicalLayer); disposeLayer(starLayer);
    addField();
    addGraph(step.qubits || [], step.edges || [], step.tsp_inspection?.path || []);
    addTopologicalQubit(step.logical_topology);
    updateMetrics(step, step.logical_topology);
    dom.step.max = Math.max(0, steps.length - 1);
    dom.step.value = index;
  }

  function setScenario(name) {
    active = name; index = 0;
    if (dom.baseline) { dom.baseline.classList.toggle("active", name === "baseline"); dom.regularized.classList.toggle("active", name === "regularized"); }
    draw();
  }
  dom.step.addEventListener("input", () => { index = Number(dom.step.value); draw(); });
  dom.play.addEventListener("click", () => { playing = !playing; dom.play.textContent = playing ? "Pause" : "Lire"; });
  dom.reset?.addEventListener("click", () => { camera.position.set(0, 0.35, 8.7); world.rotation.set(0, 0, 0); });
  if (dom.baseline) { dom.baseline.addEventListener("click", () => setScenario("baseline")); dom.regularized.addEventListener("click", () => setScenario("regularized")); }
  dom.scene.addEventListener("pointerdown", (event) => { drag = { x: event.clientX, y: event.clientY }; });
  addEventListener("pointerup", () => { drag = null; });
  addEventListener("pointermove", (event) => { if (!drag) return; world.rotation.y += (event.clientX - drag.x) * 0.008; world.rotation.x += (event.clientY - drag.y) * 0.008; drag = { x: event.clientX, y: event.clientY }; });
  dom.scene.addEventListener("wheel", (event) => { camera.position.z = Math.max(4.3, Math.min(18, camera.position.z + event.deltaY * 0.01)); }, { passive: true });

  function animate(time) {
    requestAnimationFrame(animate);
    if (playing && time - last > 1600) { last = time; index = (index + 1) % Math.max(1, (current().steps || []).length); draw(); }
    if (!drag) { world.rotation.y += 0.00075; logicalLayer.rotation.y += 0.0014 * (logicalLayer.userData.coherence ?? 1); }
    starLayer.rotation.z -= 0.00045;
    renderer.render(scene, camera);
  }
  renderDesign(); draw(); requestAnimationFrame(animate);
})().catch((error) => { document.body.innerHTML = `<pre style="padding:2rem;color:#ff9aa7">Démonstration indisponible : ${error.message}</pre>`; });
