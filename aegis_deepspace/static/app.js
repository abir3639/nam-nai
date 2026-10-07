// Aegis-DeepSpace Mission Control & Four-Pillar Client Logic

document.addEventListener("DOMContentLoaded", () => {
  // Navigation elements
  const mainNavBar = document.getElementById("mainNavBar");
  const tabPanes = document.querySelectorAll(".tab-pane");

  // Top header controls
  const commsBadge = document.getElementById("commsBadge");
  const commsStatusText = document.getElementById("commsStatusText");
  const toggleCommsBtn = document.getElementById("toggleCommsBtn");
  const dataFreshness = document.getElementById("dataFreshness");
  const scenarioBtnGroup = document.getElementById("scenarioBtnGroup");

  // Status strip elements (Hero 4-Pillar Overview)
  const stripRadBadge = document.getElementById("stripRadBadge");
  const stripRadSummary = document.getElementById("stripRadSummary");
  const stripVoiceBadge = document.getElementById("stripVoiceBadge");
  const stripVoiceSummary = document.getElementById("stripVoiceSummary");
  const stripTwinBadge = document.getElementById("stripTwinBadge");
  const stripTwinSummary = document.getElementById("stripTwinSummary");
  const stripDecisionBadge = document.getElementById("stripDecisionBadge");
  const stripScoreNum = document.getElementById("stripScoreNum");

  // Pillar 1 Dashboard Elements
  const radRiskBadge = document.getElementById("radRiskBadge");
  const p1DoseRate = document.getElementById("p1DoseRate");
  const p1CumDose = document.getElementById("p1CumDose");
  const p1SpeActive = document.getElementById("p1SpeActive");
  const p1CurrentModule = document.getElementById("p1CurrentModule");
  const p1Shielding = document.getElementById("p1Shielding");
  const p1SafeModule = document.getElementById("p1SafeModule");

  // Pillar 2 Dashboard Elements
  const voiceRiskBadge = document.getElementById("voiceRiskBadge");
  const barCognitive = document.getElementById("barCognitive");
  const valCognitive = document.getElementById("valCognitive");
  const barFatigue = document.getElementById("barFatigue");
  const valFatigue = document.getElementById("valFatigue");
  const barHypoxia = document.getElementById("barHypoxia");
  const valHypoxia = document.getElementById("valHypoxia");
  const valBaselineDev = document.getElementById("valBaselineDev");

  // Pillar 3 Dashboard Elements
  const twinStatusBadge = document.getElementById("twinStatusBadge");
  const p3BoneLoss = document.getElementById("p3BoneLoss");
  const p3MuscleLoss = document.getElementById("p3MuscleLoss");
  const p3DeficitDays = document.getElementById("p3DeficitDays");
  const p3Countermeasure = document.getElementById("p3Countermeasure");

  // Risk Fusion Pipeline Elements
  const fusionFormulaDisplay = document.getElementById("fusionFormulaDisplay");
  const flowResultBadge = document.getElementById("flowResultBadge");
  const flowResultText = document.getElementById("flowResultText");
  const fcBasePoints = document.getElementById("fcBasePoints");
  const fcBaseStatus = document.getElementById("fcBaseStatus");

  const fcP1Card = document.getElementById("fcP1Card");
  const fcP1Points = document.getElementById("fcP1Points");
  const fcP1Status = document.getElementById("fcP1Status");
  const fcP1Detail = document.getElementById("fcP1Detail");

  const fcP2Card = document.getElementById("fcP2Card");
  const fcP2Points = document.getElementById("fcP2Points");
  const fcP2Status = document.getElementById("fcP2Status");
  const fcP2Detail = document.getElementById("fcP2Detail");

  const fcP3Card = document.getElementById("fcP3Card");
  const fcP3Points = document.getElementById("fcP3Points");
  const fcP3Status = document.getElementById("fcP3Status");
  const fcP3Detail = document.getElementById("fcP3Detail");

  const fcSynergyCard = document.getElementById("fcSynergyCard");
  const fcSynergyPoints = document.getElementById("fcSynergyPoints");
  const fcSynergyStatus = document.getElementById("fcSynergyStatus");
  const fcSynergyDetail = document.getElementById("fcSynergyDetail");

  // Pillar 4 Decision Elements
  const heroRiskLevel = document.getElementById("heroRiskLevel");
  const heroRiskScore = document.getElementById("heroRiskScore");
  const decisionMetaTag = document.getElementById("decisionMetaTag");
  const recActionText = document.getElementById("recActionText");
  const altActionText = document.getElementById("altActionText");
  const confidenceVal = document.getElementById("confidenceVal");
  const uncertaintyText = document.getElementById("uncertaintyText");
  const reasoningList = document.getElementById("reasoningList");
  const factorsTableBody = document.getElementById("factorsTableBody");
  const evidenceContainer = document.getElementById("evidenceContainer");

  // Pillar 1 Dedicated Page Elements
  const p1StartSelect = document.getElementById("p1StartSelect");
  const p1TargetSelect = document.getElementById("p1TargetSelect");
  const p1FluxInput = document.getElementById("p1FluxInput");
  const p1RecalculateBtn = document.getElementById("p1RecalculateBtn");
  const p1DonkiBadge = document.getElementById("p1DonkiBadge");
  const p1DonkiEventId = document.getElementById("p1DonkiEventId");
  const p1DonkiFlux = document.getElementById("p1DonkiFlux");
  const p1DonkiSource = document.getElementById("p1DonkiSource");
  const p1DonkiDuration = document.getElementById("p1DonkiDuration");
  const habitatNodesRow = document.getElementById("habitatNodesRow");
  const p1CompartmentTableBody = document.getElementById("p1CompartmentTableBody");
  const p1RouteOrigin = document.getElementById("p1RouteOrigin");
  const p1RouteTarget = document.getElementById("p1RouteTarget");
  const p1TransitDoseVal = document.getElementById("p1TransitDoseVal");
  const p1RouteDisplay = document.getElementById("p1RouteDisplay");
  const p1RouteStepList = document.getElementById("p1RouteStepList");

  // Pillar 4 Dedicated Page Elements
  const p4HeroRiskLevel = document.getElementById("p4HeroRiskLevel");
  const p4HeroRiskScore = document.getElementById("p4HeroRiskScore");
  const p4DecisionMetaTag = document.getElementById("p4DecisionMetaTag");
  const p4ModeVal = document.getElementById("p4ModeVal");
  const p4ConfidenceVal = document.getElementById("p4ConfidenceVal");
  const p4FreshnessVal = document.getElementById("p4FreshnessVal");
  const p4AnomaliesCount = document.getElementById("p4AnomaliesCount");
  const p4RecActionText = document.getElementById("p4RecActionText");
  const p4AltActionText = document.getElementById("p4AltActionText");

  const traceFinalLevelBadge = document.getElementById("traceFinalLevelBadge");
  const traceFormulaPreview = document.getElementById("traceFormulaPreview");
  const traceSignalsContainer = document.getElementById("traceSignalsContainer");
  const traceSynergyContainer = document.getElementById("traceSynergyContainer");
  const traceFinalRiskNum = document.getElementById("traceFinalRiskNum");
  const traceFinalLevelPill = document.getElementById("traceFinalLevelPill");

  // What-If Simulator Elements
  const whatIfDelaySlider = document.getElementById("whatIfDelaySlider");
  const whatIfDelayVal = document.getElementById("whatIfDelayVal");
  const whatIfResetBtn = document.getElementById("whatIfResetBtn");
  const whatIfBaseBadge = document.getElementById("whatIfBaseBadge");
  const whatIfBaseExposure = document.getElementById("whatIfBaseExposure");
  const whatIfBaseScore = document.getElementById("whatIfBaseScore");
  const whatIfBaseAction = document.getElementById("whatIfBaseAction");
  const whatIfDelayTitle = document.getElementById("whatIfDelayTitle");
  const whatIfCounterBadge = document.getElementById("whatIfCounterBadge");
  const whatIfCounterExposure = document.getElementById("whatIfCounterExposure");
  const whatIfCounterScore = document.getElementById("whatIfCounterScore");
  const whatIfCounterAction = document.getElementById("whatIfCounterAction");
  const whatIfCounterCard = document.getElementById("whatIfCounterCard");
  const whatIfImpactBanner = document.getElementById("whatIfImpactBanner");
  const whatIfImpactText = document.getElementById("whatIfImpactText");
  const whatIfDeltaExposureBadge = document.getElementById("whatIfDeltaExposureBadge");
  const whatIfImpactIcon = document.getElementById("whatIfImpactIcon");

  // Dedicated Pages P2 & P3 Elements
  const p2RunInferenceBtn = document.getElementById("p2RunInferenceBtn");
  const p2AudioSelect = document.getElementById("p2AudioSelect");
  const p2TranscriptDisplay = document.getElementById("p2TranscriptDisplay");
  const p2MoodValence = document.getElementById("p2MoodValence");
  const p2MoodSigma = document.getElementById("p2MoodSigma");
  const p2HypoxiaSigma = document.getElementById("p2HypoxiaSigma");
  const p2FatigueAlert = document.getElementById("p2FatigueAlert");
  const p2HypoxiaAlert = document.getElementById("p2HypoxiaAlert");
  const p2StressAlert = document.getElementById("p2StressAlert");

  const pageP2Cognitive = document.getElementById("pageP2Cognitive");
  const pageP2Fatigue = document.getElementById("pageP2Fatigue");
  const pageP2Hypoxia = document.getElementById("pageP2Hypoxia");
  const pageP2ZScore = document.getElementById("pageP2ZScore");
  const pageP2Conf = document.getElementById("pageP2Conf");

  const pageP3Bone = document.getElementById("pageP3Bone");
  const pageP3Muscle = document.getElementById("pageP3Muscle");
  const pageP3Deficit = document.getElementById("pageP3Deficit");
  const pageP3Horizon = document.getElementById("pageP3Horizon");
  const pageP3Schedule = document.getElementById("pageP3Schedule");
  const pageP3Conf = document.getElementById("pageP3Conf");

  // Pillar 3 Interactive Elements
  const p3RunSimBtn = document.getElementById("p3RunSimBtn");
  const p3AstronautSelect = document.getElementById("p3AstronautSelect");
  const p3OutageInput = document.getElementById("p3OutageInput");
  const p3RecoveryInput = document.getElementById("p3RecoveryInput");
  const p3WorkloadInput = document.getElementById("p3WorkloadInput");
  const p3PrescriptionBadge = document.getElementById("p3PrescriptionBadge");
  const p3PrescriptionDeficit = document.getElementById("p3PrescriptionDeficit");
  const p3PrescriptionSurge = document.getElementById("p3PrescriptionSurge");
  const p3SquatAdj = document.getElementById("p3SquatAdj");
  const p3DeadliftAdj = document.getElementById("p3DeadliftAdj");
  const p3NomLossVal = document.getElementById("p3NomLossVal");
  const p3OutLossVal = document.getElementById("p3OutLossVal");
  const p3DeltaLossVal = document.getElementById("p3DeltaLossVal");
  const p3TrajectoryBody = document.getElementById("p3TrajectoryBody");

  // ===================================================================
  // Navigation & Tab Switching
  // ===================================================================
  function switchTab(targetTabId) {
    if (!targetTabId) return;

    // Update nav buttons
    document.querySelectorAll(".nav-tab-btn").forEach(btn => {
      if (btn.dataset.tab === targetTabId) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    // Update all tab panes dynamically
    const allPanes = document.querySelectorAll(".tab-pane");
    allPanes.forEach(pane => {
      if (pane.id === targetTabId) {
        pane.classList.add("active");
      } else {
        pane.classList.remove("active");
      }
    });

    // If switching to Pillar tabs, fetch fresh analysis
    if (targetTabId === "tab-pillar1") {
      fetchPillar1Analysis();
    } else if (targetTabId === "tab-pillar2") {
      fetchPillar2Analysis();
    } else if (targetTabId === "tab-pillar3") {
      fetchPillar3Analysis();
    }
  }

  // Bind main navigation bar
  if (mainNavBar) {
    mainNavBar.addEventListener("click", (e) => {
      const btn = e.target.closest(".nav-tab-btn");
      if (!btn) return;
      e.preventDefault();
      switchTab(btn.dataset.tab);
    });
  }

  // Handle all in-page link buttons with data-switch-tab
  document.addEventListener("click", (e) => {
    const linkBtn = e.target.closest("[data-switch-tab]");
    if (!linkBtn) return;
    e.preventDefault();
    const targetTab = linkBtn.getAttribute("data-switch-tab") || linkBtn.dataset.switchTab;
    if (targetTab) {
      switchTab(targetTab);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  });

  // Scenario Buttons Click Handler
  scenarioBtnGroup.addEventListener("click", (e) => {
    const btn = e.target.closest(".scenario-btn");
    if (!btn) return;

    const scenarioId = btn.dataset.scenario;
    document.querySelectorAll(".scenario-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    loadScenario(scenarioId);
  });

  // Toggle Comms Click Handler
  toggleCommsBtn.addEventListener("click", () => {
    toggleCommsMode();
  });

  // Pillar 1 Recalculate Route Button Handler
  if (p1RecalculateBtn) {
    p1RecalculateBtn.addEventListener("click", () => {
      recalculateP1Route();
    });
  }

  // Pillar 2 Run Neural Inference Button Handler
  if (p2RunInferenceBtn) {
    p2RunInferenceBtn.addEventListener("click", () => {
      runPillar2Inference();
    });
  }

  // Pillar 3 Run Digital Twin Simulation Button Handler
  if (p3RunSimBtn) {
    p3RunSimBtn.addEventListener("click", () => {
      runPillar3Simulation();
    });
  }

  // ===================================================================
  // Data Fetching & Sync
  // ===================================================================
  async function fetchInitialState() {
    try {
      const res = await fetch("/api/state");
      const data = await res.json();
      renderState(data.crew_state, data.decision);
      fetchPillar1Analysis();
      fetchPillar2Analysis();
      fetchPillar3Analysis();
    } catch (err) {
      console.error("Failed to load initial state:", err);
    }
  }

  async function loadScenario(scenarioId) {
    try {
      const res = await fetch(`/api/scenarios/${scenarioId}`, { method: "POST" });
      const data = await res.json();
      renderState(data.crew_state, data.decision);
      
      // Update P1 flux input and start module accordingly
      const isSpe = data.crew_state?.radiation?.spe_active;
      const fluxVal = isSpe ? 250.0 : 5.0;
      if (p1FluxInput) {
        p1FluxInput.value = fluxVal.toFixed(1);
      }
      
      // Extract current module code (e.g., 'Module D', 'Module A', 'Module C')
      const currentModFull = data.crew_state?.radiation?.current_module || "Module D";
      const modPrefixMatch = currentModFull.match(/^(Module [A-D])/);
      const modCode = modPrefixMatch ? modPrefixMatch[1] : "Module D";
      if (p1StartSelect) {
        p1StartSelect.value = modCode;
      }

      // Update P3 confinement days input to match scenario
      if (p3OutageInput && data.crew_state?.astro_twin) {
        p3OutageInput.value = data.crew_state.astro_twin.exercise_deficit_days ?? 0;
      }

      fetchPillar1Analysis(modCode, fluxVal);
      fetchPillar2Analysis(scenarioId);
      fetchPillar3Analysis(scenarioId);
    } catch (err) {
      console.error(`Failed to load scenario ${scenarioId}:`, err);
    }
  }

  async function toggleCommsMode() {
    try {
      const res = await fetch("/api/comms/toggle", { method: "POST" });
      const data = await res.json();
      fetchInitialState();
    } catch (err) {
      console.error("Failed to toggle comms mode:", err);
    }
  }

  async function fetchPillar1Analysis(overrideMod, overrideFlux) {
    try {
      const startMod = overrideMod || (p1StartSelect ? p1StartSelect.value : "Module D");
      const parsedFlux = p1FluxInput ? parseFloat(p1FluxInput.value) : 250.0;
      const fluxVal = overrideFlux !== undefined ? overrideFlux : (isNaN(parsedFlux) ? 250.0 : parsedFlux);
      const res = await fetch(`/api/pillar1/analysis?start_module=${encodeURIComponent(startMod)}&flux_msv=${fluxVal}`);
      const data = await res.json();
      renderPillar1Page(data);
    } catch (err) {
      console.error("Failed to fetch Pillar 1 analysis:", err);
    }
  }

  async function fetchPillar2Analysis(scenarioId) {
    try {
      const activeBtn = document.querySelector(".scenario-btn.active");
      const currentScen = scenarioId || (activeBtn ? activeBtn.dataset.scenario : "normal");
      const res = await fetch(`/api/pillar2/analysis?scenario=${encodeURIComponent(currentScen)}`);
      const data = await res.json();
      renderPillar2Page(data);
    } catch (err) {
      console.error("Failed to fetch Pillar 2 analysis:", err);
    }
  }

  async function runPillar2Inference() {
    try {
      if (p2RunInferenceBtn) {
        p2RunInferenceBtn.textContent = "⏳ RUNNING WHISPER & CNN INFERENCE...";
        p2RunInferenceBtn.disabled = true;
      }
      const res = await fetch("/api/pillar2/process_audio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ audio_path: null })
      });
      const data = await res.json();
      fetchPillar2Analysis();
      fetchInitialState();
    } catch (err) {
      console.error("Failed to run speech inference:", err);
    } finally {
      if (p2RunInferenceBtn) {
        p2RunInferenceBtn.textContent = "🎙️ RUN NEURAL SPEECH INFERENCE";
        p2RunInferenceBtn.disabled = false;
      }
    }
  }

  function renderPillar2Page(data) {
    if (!data) return;
    const tel = data.telemetry || {};
    const anom = data.anomalies || {};
    const zs = anom.z_scores || {};

    if (p2TranscriptDisplay && tel.transcript) {
      p2TranscriptDisplay.textContent = `"${tel.transcript}"`;
    }

    const p2SentimentBadge = document.getElementById("p2SentimentBadge");
    if (p2SentimentBadge && tel.mood_valence !== undefined) {
      const isNeg = tel.mood_valence < 0;
      p2SentimentBadge.textContent = isNeg ? "DISTRESS / ANOMALOUS VALENCE" : "VALENCE NOMINAL";
      p2SentimentBadge.className = `badge ${isNeg ? 'badge-critical' : 'badge-low'}`;
    }

    if (p2MoodValence && tel.mood_valence !== undefined) {
      const isNeg = tel.mood_valence < 0;
      p2MoodValence.innerHTML = `${tel.mood_valence.toFixed(3)} <small>(${isNeg ? 'Negative / Distressed' : 'Positive'})</small>`;
      p2MoodValence.style.color = isNeg ? "var(--accent-red)" : "var(--accent-green)";
    }

    if (p2MoodSigma && zs.mood_sigma !== undefined) {
      p2MoodSigma.textContent = `${zs.mood_sigma > 0 ? '+' : ''}${zs.mood_sigma.toFixed(1)}σ`;
    }

    if (pageP2Cognitive && tel.mood_valence !== undefined && tel.acoustic_fatigue_score !== undefined) {
      const strain = Math.min(1.0, Math.max(0.0, (1.0 - tel.mood_valence) / 2.0 * 0.7 + tel.acoustic_fatigue_score * 0.3));
      pageP2Cognitive.textContent = strain.toFixed(2);
    }

    if (pageP2Fatigue && tel.acoustic_fatigue_score !== undefined) {
      pageP2Fatigue.textContent = tel.acoustic_fatigue_score.toFixed(2);
    }

    if (pageP2Hypoxia && tel.acoustic_hypoxia_score !== undefined) {
      pageP2Hypoxia.textContent = tel.acoustic_hypoxia_score.toFixed(2);
    }

    if (p2HypoxiaSigma && zs.hypoxia_sigma !== undefined) {
      p2HypoxiaSigma.textContent = `+${zs.hypoxia_sigma.toFixed(1)}σ`;
    }

    if (pageP2ZScore && zs.fatigue_sigma !== undefined) {
      pageP2ZScore.textContent = `+${zs.fatigue_sigma.toFixed(1)}σ`;
    }

    if (p2FatigueAlert) {
      p2FatigueAlert.textContent = anom.fatigue_alert ? "ACTIVE" : "NOMINAL";
      p2FatigueAlert.style.color = anom.fatigue_alert ? "var(--accent-red)" : "var(--accent-green)";
    }

    if (p2HypoxiaAlert) {
      p2HypoxiaAlert.textContent = anom.hypoxia_alert ? "ACTIVE" : "NOMINAL";
      p2HypoxiaAlert.style.color = anom.hypoxia_alert ? "var(--accent-amber)" : "var(--accent-green)";
    }

    if (p2StressAlert) {
      p2StressAlert.textContent = anom.isolation_stress_alert ? "ACTIVE" : "NOMINAL";
      p2StressAlert.style.color = anom.isolation_stress_alert ? "var(--accent-red)" : "var(--accent-green)";
    }
  }

  async function recalculateP1Route() {
    try {
      const startMod = p1StartSelect.value;
      const targetMod = p1TargetSelect.value;
      const fluxVal = parseFloat(p1FluxInput.value) || 250.0;

      const res = await fetch("/api/pillar1/calculate_route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_module: startMod,
          target_module: targetMod,
          external_flux_mSv: fluxVal
        })
      });
      const data = await res.json();
      updateP1RouteResults(data);
    } catch (err) {
      console.error("Failed to calculate route:", err);
    }
  }

  // ===================================================================
  // Pillar 3: Astro-Twin Real Hybrid Simulation Engine
  // ===================================================================
  async function fetchPillar3Analysis(scenarioId) {
    try {
      const activeBtn = document.querySelector(".scenario-btn.active");
      const currentScen = scenarioId || (activeBtn ? activeBtn.dataset.scenario : "normal");
      const res = await fetch(`/api/pillar3/analysis?scenario=${encodeURIComponent(currentScen)}`);
      const data = await res.json();
      renderPillar3Page(data);
    } catch (err) {
      console.error("Failed to fetch Pillar 3 analysis:", err);
    }
  }

  async function runPillar3Simulation() {
    try {
      if (p3RunSimBtn) {
        p3RunSimBtn.textContent = "⏳ SIMULATING DIGITAL TWIN...";
        p3RunSimBtn.disabled = true;
      }

      const astronautVal = p3AstronautSelect ? p3AstronautSelect.value : "CDR-MARK-WATNEY";
      const isRipley = astronautVal === "FE-ELLEN-RIPLEY";
      const profile = {
        astronaut_id: astronautVal,
        age: isRipley ? 38 : 42,
        sex: isRipley ? "F" : "M",
        body_mass_kg: isRipley ? 62.0 : 80.5,
        baseline_hip_bmd: isRipley ? 0.960 : 1.050
      };

      const outageDays = p3OutageInput ? parseInt(p3OutageInput.value, 10) : 4;
      const recoveryDays = p3RecoveryInput ? parseInt(p3RecoveryInput.value, 10) : 6;
      const workload = p3WorkloadInput ? parseFloat(p3WorkloadInput.value) : 9000.0;

      const res = await fetch("/api/pillar3/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...profile,
          outage_days: isNaN(outageDays) ? 4 : outageDays,
          outage_start_day: 8,
          recovery_window_days: isNaN(recoveryDays) ? 6 : recoveryDays,
          nominal_volume_kg: isNaN(workload) ? 9000.0 : workload
        })
      });
      const data = await res.json();
      renderPillar3SimulationResult(data);
    } catch (err) {
      console.error("Failed to run Astro-Twin simulation:", err);
    } finally {
      if (p3RunSimBtn) {
        p3RunSimBtn.textContent = "🧬 RUN DIGITAL TWIN SIMULATION";
        p3RunSimBtn.disabled = false;
      }
    }
  }

  function renderPillar3SimulationResult(sim) {
    if (!sim) return;
    const presc = sim.prescription || {};
    const adjustments = presc.specific_exercise_adjustments || {};

    if (p3PrescriptionBadge) {
      p3PrescriptionBadge.textContent = presc.status || "CALCULATED";
      p3PrescriptionBadge.className = `badge ${presc.outage_duration_days > 0 ? 'badge-high' : 'badge-low'}`;
    }

    if (p3PrescriptionDeficit) {
      p3PrescriptionDeficit.innerHTML = `${(presc.total_mechanical_work_deficit_kg || 0).toLocaleString()} kg <small>tonnage</small>`;
    }

    if (p3PrescriptionSurge) {
      p3PrescriptionSurge.textContent = presc.required_daily_volume_surge || "+0.0%";
      p3PrescriptionSurge.style.color = (presc.outage_duration_days > 0) ? "var(--accent-amber)" : "var(--accent-green)";
    }

    if (p3SquatAdj) {
      p3SquatAdj.textContent = adjustments.barbell_squat || "Nominal load";
    }

    if (p3DeadliftAdj) {
      p3DeadliftAdj.textContent = adjustments.deadlift || "Nominal load";
    }

    if (p3NomLossVal) {
      p3NomLossVal.textContent = `-${sim.nominal_loss_pct || 0.45}%`;
    }

    if (p3OutLossVal) {
      p3OutLossVal.textContent = `-${sim.outage_loss_pct || 0.54}%`;
    }

    if (p3DeltaLossVal) {
      p3DeltaLossVal.textContent = `+${sim.delta_loss_pct || 0.09}%`;
    }

    if (p3TrajectoryBody && Array.isArray(sim.days)) {
      const nomTraj = sim.nominal_trajectory || [];
      const outTraj = sim.outage_trajectory || [];
      const outageDays = presc.outage_duration_days || 0;

      let html = "";
      for (let i = 0; i < sim.days.length; i++) {
        const d = sim.days[i];
        const nom = nomTraj[i] !== undefined ? nomTraj[i].toFixed(4) : "-";
        const out = outTraj[i] !== undefined ? outTraj[i].toFixed(4) : "-";
        const diff = (nomTraj[i] !== undefined && outTraj[i] !== undefined)
          ? (outTraj[i] - nomTraj[i]).toFixed(4)
          : "-";
        const inOutage = (outageDays > 0 && d >= 8 && d < 8 + outageDays);

        const statusTag = inOutage
          ? `<span class="badge badge-critical" style="font-size:0.75rem;">CONFINED / OFFLINE</span>`
          : `<span class="badge badge-low" style="font-size:0.75rem;">ARED NOMINAL</span>`;

        html += `
          <tr ${inOutage ? 'style="background: rgba(255, 23, 68, 0.08);"' : ''}>
            <td style="font-family: var(--font-mono); font-weight: 600;">Day ${d}</td>
            <td style="font-family: var(--font-mono);">${nom}</td>
            <td style="font-family: var(--font-mono); ${inOutage ? 'color: var(--accent-red); font-weight:700;' : ''}">${out}</td>
            <td style="font-family: var(--font-mono); color: ${inOutage ? 'var(--accent-amber)' : 'var(--text-muted)'};">${diff}</td>
            <td>${statusTag}</td>
          </tr>
        `;
      }
      p3TrajectoryBody.innerHTML = html;
    }
  }

  function renderPillar3Page(data) {
    if (!data) return;
    if (data.simulation) {
      renderPillar3SimulationResult(data.simulation);
    }
  }

  // ===================================================================
  // Rendering State
  // ===================================================================
  function renderState(state, decision) {
    if (!state || !decision) return;

    // 1. Comms Mode
    const isOffline = state.comms_mode === "OFFLINE";
    if (isOffline) {
      commsBadge.className = "status-indicator offline";
      commsStatusText.textContent = "OFFLINE [20-MIN BLACKOUT ACTIVE]";
    } else {
      commsBadge.className = "status-indicator";
      commsStatusText.textContent = "ONLINE [EARTH LINK ACTIVE]";
    }

    dataFreshness.textContent = `${state.data_freshness_seconds}s`;

    // 2. High-Level 4-Pillar Summary Strip
    const rad = state.radiation;
    const voice = state.voice_vitals;
    const twin = state.astro_twin;

    setSeverityBadge(stripRadBadge, rad.risk_level);
    stripRadSummary.innerHTML = `Flux: <strong>${rad.dose_rate_msv_h.toFixed(2)} mSv/h</strong> | Shelter: <strong>${rad.recommended_safe_module.split(':')[0]}</strong>`;

    const voiceLevel = voice.hypoxia_indicator > 0.35 ? "CRITICAL" : (voice.cognitive_strain_score > 0.5 ? "HIGH" : (voice.cognitive_strain_score > 0.3 ? "MEDIUM" : "NOMINAL"));
    setSeverityBadge(stripVoiceBadge, voiceLevel);
    stripVoiceSummary.innerHTML = `Strain: <strong>${voice.cognitive_strain_score.toFixed(2)}</strong> | Fatigue: <strong>${voice.fatigue_score.toFixed(2)}</strong>`;

    const twinLevel = twin.exercise_deficit_days > 2 ? "HIGH" : (twin.exercise_deficit_days > 0 ? "MEDIUM" : "NOMINAL");
    setSeverityBadge(stripTwinBadge, twinLevel);
    stripTwinSummary.innerHTML = `Bone: <strong>-${twin.projected_bone_loss_pct_mo.toFixed(1)}%/mo</strong> | Deficit: <strong>${twin.exercise_deficit_days}d</strong>`;

    setSeverityBadge(stripDecisionBadge, decision.risk_level);
    stripScoreNum.textContent = decision.risk_score.toFixed(2);

    // 3. Pillar 1: Radiation Safe-Route (Real)
    p1DoseRate.innerHTML = `${rad.dose_rate_msv_h.toFixed(2)} <small>mSv/h</small>`;
    p1CumDose.innerHTML = `${rad.cumulative_dose_msv.toFixed(1)} <small>mSv</small>`;
    p1SpeActive.textContent = rad.spe_active ? "YES (ACTIVE)" : "NO";
    p1CurrentModule.textContent = rad.current_module;
    p1Shielding.textContent = `(${rad.shielding_rating_g_cm2.toFixed(1)} g/cm²)`;
    p1SafeModule.textContent = rad.recommended_safe_module;
    setSeverityBadge(radRiskBadge, rad.risk_level);

    // 4. Pillar 2: Voice Vitals (Simulated)
    valCognitive.textContent = voice.cognitive_strain_score.toFixed(2);
    barCognitive.style.width = `${Math.min(voice.cognitive_strain_score * 100, 100)}%`;
    barCognitive.style.background = getScoreColor(voice.cognitive_strain_score);

    valFatigue.textContent = voice.fatigue_score.toFixed(2);
    barFatigue.style.width = `${Math.min(voice.fatigue_score * 100, 100)}%`;
    barFatigue.style.background = getScoreColor(voice.fatigue_score);

    valHypoxia.textContent = voice.hypoxia_indicator.toFixed(2);
    barHypoxia.style.width = `${Math.min(voice.hypoxia_indicator * 100, 100)}%`;
    barHypoxia.style.background = voice.hypoxia_indicator > 0.35 ? "#ff1744" : "#00e5ff";

    valBaselineDev.textContent = `+${voice.deviation_from_baseline_z.toFixed(1)}σ`;
    setSeverityBadge(voiceRiskBadge, voiceLevel);

    // Populate dedicated P2 page values
    if (pageP2Cognitive) pageP2Cognitive.textContent = voice.cognitive_strain_score.toFixed(2);
    if (pageP2Fatigue) pageP2Fatigue.textContent = voice.fatigue_score.toFixed(2);
    if (pageP2Hypoxia) pageP2Hypoxia.textContent = voice.hypoxia_indicator.toFixed(2);
    if (pageP2ZScore) pageP2ZScore.textContent = `+${voice.deviation_from_baseline_z.toFixed(1)}σ`;
    if (pageP2Conf) pageP2Conf.textContent = `${Math.round(voice.confidence * 100)}%`;

    // 5. Pillar 3: Astro-Twin (Simulated)
    p3BoneLoss.innerHTML = `${twin.projected_bone_loss_pct_mo.toFixed(1)}% <small>/mo</small>`;
    p3MuscleLoss.innerHTML = `${twin.projected_muscle_atrophy_pct.toFixed(1)}%`;
    p3DeficitDays.innerHTML = `${twin.exercise_deficit_days} <small>days</small>`;
    p3Countermeasure.textContent = twin.countermeasure_status === "NOMINAL"
      ? "Adherence nominal; bone mineral density within normal variance."
      : `Warning: Exercise deficit active (${twin.exercise_deficit_days}d). Countermeasure adjustment flagged.`;
    setSeverityBadge(twinStatusBadge, twinLevel);

    // Populate dedicated P3 page values
    if (pageP3Bone) pageP3Bone.innerHTML = `${twin.projected_bone_loss_pct_mo.toFixed(1)}% <small>/mo</small>`;
    if (pageP3Muscle) pageP3Muscle.innerHTML = `${twin.projected_muscle_atrophy_pct.toFixed(1)}%`;
    if (pageP3Deficit) pageP3Deficit.innerHTML = `${twin.exercise_deficit_days} <small>days</small>`;
    if (pageP3Horizon) pageP3Horizon.innerHTML = `${twin.prediction_horizon_days} <small>days</small>`;
    if (pageP3Schedule) pageP3Schedule.textContent = twin.countermeasure_status;
    if (pageP3Conf) pageP3Conf.textContent = `${Math.round(twin.confidence * 100)}%`;

    // 6. Risk Fusion Breakdown (Mathematical Trace)
    const rf = decision.risk_fusion;
    if (rf) {
      fusionFormulaDisplay.textContent = rf.formula;

      fcBasePoints.textContent = `+${rf.baseline_score.toFixed(2)}`;
      fcBaseStatus.textContent = "NOMINAL";

      // P1 Radiation (Real)
      const p1 = rf.p1_radiation;
      fcP1Points.textContent = `+${p1.score_addition.toFixed(2)}`;
      fcP1Status.textContent = p1.status;
      fcP1Detail.textContent = p1.detail;
      setFusionCardStyle(fcP1Card, p1.score_addition, p1.status);

      // P2 Voice Vitals (Simulated)
      const p2 = rf.p2_voice_vitals;
      fcP2Points.textContent = `+${p2.score_addition.toFixed(2)}`;
      fcP2Status.textContent = p2.status;
      fcP2Detail.textContent = p2.detail;
      setFusionCardStyle(fcP2Card, p2.score_addition, p2.status);

      // P3 Astro-Twin (Simulated)
      const p3 = rf.p3_astro_twin;
      fcP3Points.textContent = `+${p3.score_addition.toFixed(2)}`;
      fcP3Status.textContent = p3.status;
      fcP3Detail.textContent = p3.detail;
      setFusionCardStyle(fcP3Card, p3.score_addition, p3.status);

      // Synergy
      fcSynergyPoints.textContent = `+${rf.synergy_score.toFixed(2)}`;
      fcSynergyStatus.textContent = rf.synergy_score > 0 ? "ESCALATED" : "NONE";
      fcSynergyDetail.textContent = rf.synergy_detail || "No multi-signal escalation";
      if (rf.synergy_score > 0) {
        fcSynergyCard.className = "fusion-card synergy-card active";
      } else {
        fcSynergyCard.className = "fusion-card synergy-card";
      }

      flowResultText.textContent = `${decision.risk_level} (${decision.risk_score.toFixed(2)})`;
      setFlowResultStyle(flowResultBadge, decision.risk_level);
    }

    // 7. Pillar 4: Autonomous Decision Object
    heroRiskLevel.textContent = `${decision.risk_level} RISK`;
    heroRiskScore.textContent = decision.risk_score.toFixed(2);
    decisionMetaTag.textContent = `${decision.decision_id} | ${decision.mode} MODE`;
    setHeroRiskStyle(heroRiskLevel, decision.risk_level);

    recActionText.textContent = decision.recommended_action;
    altActionText.textContent = decision.alternative_action || "None required.";
    confidenceVal.textContent = `${Math.round(decision.confidence * 100)}%`;

    if (decision.uncertainty && decision.uncertainty.length > 0) {
      uncertaintyText.innerHTML = `<span style="color: #ffab00;">${decision.uncertainty.join("; ")}</span>`;
    } else {
      uncertaintyText.textContent = "None detected. High SNR across all telemetry channels.";
    }

    // Render Reasons
    reasoningList.innerHTML = "";
    (decision.reasons || []).forEach(reason => {
      const li = document.createElement("li");
      li.textContent = reason;
      reasoningList.appendChild(li);
    });

    // Render Contributing Factors Table
    factorsTableBody.innerHTML = "";
    if (!decision.contributing_factors || decision.contributing_factors.length === 0) {
      factorsTableBody.innerHTML = `<tr><td colspan="4" class="empty-state">No anomalous factors detected. All telemetry within baseline tolerances.</td></tr>`;
    } else {
      decision.contributing_factors.forEach(f => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${f.pillar}</strong></td>
          <td>${f.factor}</td>
          <td><span class="badge ${getBadgeClass(f.severity_contribution)}">${f.severity_contribution}</span></td>
          <td><code>${f.detail}</code></td>
        `;
        factorsTableBody.appendChild(tr);
      });
    }

    // Render Evidence Citations
    evidenceContainer.innerHTML = "";
    (decision.evidence || []).forEach(ev => {
      const card = document.createElement("div");
      card.className = "evidence-card";
      card.innerHTML = `
        <div class="evidence-header">
          <span class="evidence-source">${ev.source}</span>
          <span class="evidence-citation">${ev.citation}</span>
        </div>
        <div class="evidence-title">${ev.title}</div>
        <div class="evidence-excerpt">"${ev.excerpt}"</div>
      `;
      evidenceContainer.appendChild(card);
    });

    // 8. Render Dedicated Pillar 4 Page View & Explain Decision Trace
    renderPillar4Page(state, decision);
  }

  // ===================================================================
  // Dedicated Pillar 4 Page Renderer & Decision Trace
  // ===================================================================
  function renderPillar4Page(state, decision) {
    if (!state || !decision) return;

    // 1. Current Mission Risk on P4 Page
    if (p4HeroRiskLevel) {
      p4HeroRiskLevel.textContent = `${decision.risk_level} RISK`;
      setHeroRiskStyle(p4HeroRiskLevel, decision.risk_level);
    }
    if (p4HeroRiskScore) p4HeroRiskScore.textContent = decision.risk_score.toFixed(2);
    if (p4DecisionMetaTag) p4DecisionMetaTag.textContent = `${decision.decision_id} | ${decision.mode} MODE`;
    if (p4ModeVal) p4ModeVal.textContent = decision.mode;
    if (p4ConfidenceVal) p4ConfidenceVal.textContent = `${Math.round(decision.confidence * 100)}%`;
    if (p4FreshnessVal) p4FreshnessVal.textContent = `${state.data_freshness_seconds}s`;

    const radAnom = state.radiation.spe_active || state.radiation.dose_rate_msv_h >= 0.10;
    const voiceAnom = state.voice_vitals.cognitive_strain_score >= 0.35 || state.voice_vitals.hypoxia_indicator >= 0.30;
    const twinAnom = state.astro_twin.exercise_deficit_days >= 2;
    const activePillars = (radAnom ? 1 : 0) + (voiceAnom ? 1 : 0) + (twinAnom ? 1 : 0);
    if (p4AnomaliesCount) p4AnomaliesCount.textContent = `${activePillars} / 3 Pillars`;

    // 2. Current Recommendation on P4 Page
    if (p4RecActionText) p4RecActionText.textContent = decision.recommended_action;
    if (p4AltActionText) p4AltActionText.textContent = decision.alternative_action || "None required.";

    // 3. Explain Decision (Decision Trace)
    renderDecisionTrace(decision.decision_trace, decision.risk_fusion);

    // 4. Update What-If Simulator Baseline
    updateWhatIfBaseline(state, decision);
  }

  function renderDecisionTrace(trace, riskFusion) {
    if (!trace) return;

    if (traceFinalLevelBadge) {
      traceFinalLevelBadge.textContent = `${trace.final_level} (${trace.final_risk.toFixed(2)})`;
      traceFinalLevelBadge.className = `badge ${getBadgeClass(trace.final_level)}`;
    }

    if (traceFormulaPreview && riskFusion) {
      traceFormulaPreview.textContent = `Formula: ${riskFusion.formula}`;
    }

    if (traceFinalRiskNum) traceFinalRiskNum.textContent = trace.final_risk.toFixed(2);
    if (traceFinalLevelPill) {
      traceFinalLevelPill.textContent = trace.final_level;
      traceFinalLevelPill.className = `badge ${getBadgeClass(trace.final_level)}`;
    }

    // Render Signals
    if (traceSignalsContainer && trace.signals) {
      traceSignalsContainer.innerHTML = "";
      trace.signals.forEach(sig => {
        const card = document.createElement("div");
        const isTriggered = sig.triggered;
        const isCritical = sig.contribution >= 0.35 || sig.explanation.toUpperCase().includes("CRITICAL");
        card.className = `trace-signal-card ${isTriggered ? 'is-triggered' : ''} ${isCritical ? 'critical-trigger' : ''}`;
        card.innerHTML = `
          <div>
            <div class="tsc-header">
              <span class="tsc-source-tag">${sig.source} &bull; ${sig.name}</span>
              <span class="tsc-points-badge ${sig.contribution > 0 ? 'has-points' : ''}">+${sig.contribution.toFixed(2)} pts</span>
            </div>
            <div class="tsc-name">${sig.metric}</div>
            <div class="tsc-body">
              <div class="tsc-row">Observed: <strong>${sig.value}</strong></div>
              <div class="tsc-row">Threshold: <code>${sig.threshold}</code></div>
              <div class="tsc-row" style="color: ${isTriggered ? '#ffd54f' : '#aaa'};">${sig.explanation}</div>
            </div>
          </div>
          <div>
            <span class="tsc-status-tag ${isTriggered ? 'triggered' : 'nominal'}">
              ${isTriggered ? '✓ ' + sig.source + ' Escalation Triggered' : '● Within Baseline Bounds'}
            </span>
          </div>
        `;
        traceSignalsContainer.appendChild(card);
      });
    }

    // Render Synergy Rules
    if (traceSynergyContainer && trace.synergy_rules) {
      traceSynergyContainer.innerHTML = "";
      trace.synergy_rules.forEach(rule => {
        const item = document.createElement("div");
        item.className = `trace-synergy-item ${rule.triggered ? 'active' : ''}`;
        item.innerHTML = `
          <div class="tsi-info">
            <span class="tsi-name">${rule.triggered ? '✓' : '○'} ${rule.name}</span>
            <span class="tsi-exp">${rule.explanation}</span>
          </div>
          <div class="tsi-points">+${rule.contribution.toFixed(2)}</div>
        `;
        traceSynergyContainer.appendChild(item);
      });
    }
  }

  // ===================================================================
  // What-If Counterfactual Simulator
  // ===================================================================
  let currentWhatIfState = null;

  function updateWhatIfBaseline(state, decision) {
    currentWhatIfState = state;
    if (whatIfBaseBadge) setSeverityBadge(whatIfBaseBadge, decision.risk_level);
    if (whatIfBaseExposure) whatIfBaseExposure.innerHTML = `${state.radiation.cumulative_dose_msv.toFixed(2)} <small>mSv</small>`;
    if (whatIfBaseScore) whatIfBaseScore.textContent = decision.risk_score.toFixed(2);
    if (whatIfBaseAction) whatIfBaseAction.textContent = decision.recommended_action;

    // Trigger simulation for current slider position
    const currentDelay = whatIfDelaySlider ? parseFloat(whatIfDelaySlider.value) : 0;
    runWhatIfSimulation(currentDelay);
  }

  async function runWhatIfSimulation(delayMinutes) {
    try {
      const activeBtn = document.querySelector(".scenario-btn.active");
      const currentScenario = activeBtn ? activeBtn.dataset.scenario : "normal";

      const res = await fetch("/api/pillar4/what-if", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          delay_minutes: delayMinutes,
          scenario: currentScenario
        })
      });
      const data = await res.json();
      renderWhatIfResults(data);
    } catch (err) {
      console.error("Failed to execute What-If simulation:", err);
    }
  }

  function renderWhatIfResults(data) {
    if (!data) return;
    const base = data.baseline || {};
    const cf = data.counterfactual || {};
    const impact = data.impact || {};

    const delayMin = data.delay_minutes !== undefined ? data.delay_minutes : 0;
    const projExp = typeof cf.projected_exposure_msv === "number" ? cf.projected_exposure_msv : 0.0;
    const deltaExp = typeof impact.delta_exposure_msv === "number" ? impact.delta_exposure_msv : 0.0;
    const cfScore = typeof cf.risk_score === "number" ? cf.risk_score : 0.10;

    if (whatIfDelayTitle) whatIfDelayTitle.textContent = `WITH ${delayMin} MIN DELAY`;
    if (whatIfCounterBadge) setSeverityBadge(whatIfCounterBadge, cf.risk_level);
    if (whatIfCounterExposure) {
      whatIfCounterExposure.innerHTML = `${projExp.toFixed(2)} <small>mSv</small>`;
      whatIfCounterExposure.style.color = deltaExp > 0.10 ? "var(--accent-red)" : "var(--accent-cyan)";
    }
    if (whatIfCounterScore) whatIfCounterScore.textContent = cfScore.toFixed(2);
    if (whatIfCounterAction) whatIfCounterAction.textContent = cf.recommended_action || "CONTINUE NOMINAL OPERATIONS";

    if (whatIfCounterCard) {
      if (impact.level_escalated || cf.risk_level === "CRITICAL") {
        whatIfCounterCard.className = "whatif-box counterfactual-box escalated";
      } else {
        whatIfCounterCard.className = "whatif-box counterfactual-box";
      }
    }

    if (whatIfDeltaExposureBadge) {
      whatIfDeltaExposureBadge.textContent = `Δ Exposure: +${deltaExp.toFixed(3)} mSv`;
    }

    if (whatIfImpactText) {
      if (impact.level_escalated) {
        whatIfImpactText.innerHTML = `<span style="color: var(--accent-red);">${impact.summary || 'Escalated'} &bull; RISK ESCALATED!</span>`;
      } else if (deltaExp > 0) {
        whatIfImpactText.innerHTML = `${impact.summary || ''} &bull; Stable severity tier`;
      } else {
        whatIfImpactText.textContent = "Immediate action &bull; Zero delay exposure penalty";
      }
    }

    if (whatIfImpactBanner) {
      whatIfImpactBanner.className = impact.level_escalated ? "whatif-impact-banner escalated" : "whatif-impact-banner";
    }

    if (whatIfImpactIcon) {
      whatIfImpactIcon.textContent = impact.level_escalated ? "⚠️" : (deltaExp > 0 ? "⏱️" : "⚖️");
    }
  }

  // Bind What-If Slider & Reset Controls
  if (whatIfDelaySlider) {
    whatIfDelaySlider.addEventListener("input", (e) => {
      const val = parseFloat(e.target.value);
      if (whatIfDelayVal) whatIfDelayVal.textContent = val;
      runWhatIfSimulation(val);
    });
  }

  if (whatIfResetBtn) {
    whatIfResetBtn.addEventListener("click", () => {
      if (whatIfDelaySlider) whatIfDelaySlider.value = 0;
      if (whatIfDelayVal) whatIfDelayVal.textContent = "0";
      runWhatIfSimulation(0);
    });
  }

  // ===================================================================
  // Dedicated Pillar 1 Page Renderer
  // ===================================================================
  function renderPillar1Page(data) {
    if (!data) return;

    // Telemetry Box
    const tel = data.telemetry || {};
    if (p1DonkiBadge) {
      p1DonkiBadge.textContent = tel.active ? "SPE ALERT ACTIVE" : "NOMINAL BACKGROUND";
      p1DonkiBadge.className = `badge ${tel.active ? 'badge-critical' : 'badge-low'}`;
    }
    if (p1DonkiEventId) p1DonkiEventId.textContent = tel.event_id || "NOMINAL";
    if (p1DonkiFlux) p1DonkiFlux.innerHTML = `${data.external_flux_mSv} <small>mSv/hr</small>`;
    if (p1DonkiSource) p1DonkiSource.textContent = tel.source || "NASA DONKI";
    if (p1DonkiDuration) p1DonkiDuration.innerHTML = `${tel.duration_days || 0} <small>days</small>`;

    // Topology Nodes Display
    if (habitatNodesRow && data.topology && data.topology.nodes) {
      habitatNodesRow.innerHTML = "";
      const nodes = data.topology.nodes;
      nodes.forEach((n, idx) => {
        const isCurrent = n.id === data.current_location;
        const isShelter = n.id === data.safest_shelter;
        const compData = (data.compartment_risks || []).find(c => c.module_id === n.id);
        const internalDose = compData ? compData.internal_dose_mSv_h : 0.0;

        const nodeBox = document.createElement("div");
        nodeBox.className = `habitat-node-box ${isShelter ? 'is-safe-haven' : ''} ${isCurrent ? 'is-current' : ''}`;
        nodeBox.innerHTML = `
          <div class="node-mod-id">${n.id} ${isCurrent ? '[CREW HERE]' : ''}</div>
          <div class="node-mod-name">${n.name}</div>
          <div class="node-mod-shield">${Math.round(n.shielding_factor * 100)}% Shielded</div>
          <div class="node-mod-dose">${internalDose.toFixed(1)} mSv/hr</div>
        `;
        habitatNodesRow.appendChild(nodeBox);

        // Add corridor connector between nodes
        if (idx < nodes.length - 1) {
          const conn = document.createElement("div");
          conn.className = "habitat-corridor-connector";
          conn.innerHTML = `<span class="corridor-arrow">&harr;</span><span>Corridor</span>`;
          habitatNodesRow.appendChild(conn);
        }
      });
    }

    // Compartment Table
    if (p1CompartmentTableBody && data.compartment_risks) {
      p1CompartmentTableBody.innerHTML = "";
      data.compartment_risks.forEach(c => {
        const tr = document.createElement("tr");
        const isTarget = c.module_id === data.safest_shelter;
        tr.style.background = isTarget ? "rgba(0, 230, 118, 0.06)" : "";
        tr.innerHTML = `
          <td><strong>${c.module_id}</strong> ${isTarget ? '🟢' : ''}</td>
          <td>${c.name}</td>
          <td>${c.shielding_pct} (${c.shielding_g_cm2} g/cm²)</td>
          <td><strong style="color: ${c.internal_dose_mSv_h > 50 ? '#ff1744' : '#fff'};">${c.internal_dose_mSv_h.toFixed(1)} mSv/hr</strong></td>
          <td><span class="badge ${getBadgeClass(c.hazard_level)}">${c.hazard_level}</span></td>
        `;
        p1CompartmentTableBody.appendChild(tr);
      });
    }

    // Route summary
    if (p1RouteOrigin) p1RouteOrigin.textContent = `${data.current_location || 'Module D'}: ${data.current_location_name || ''}`;
    if (p1RouteTarget) p1RouteTarget.textContent = `${data.safest_shelter || 'Module B'}: ${data.safest_shelter_name || ''}`;
    if (p1TransitDoseVal) {
      const dose = typeof data.transit_dose_mSv === "number" ? data.transit_dose_mSv : 0.0;
      p1TransitDoseVal.innerHTML = `${dose.toFixed(2)} <small>mSv</small>`;
    }

    if (p1RouteDisplay && data.evacuation_route) {
      p1RouteDisplay.innerHTML = data.evacuation_route.map(m => `<strong>[${m}]</strong>`).join(" ➔ ");
    }

    // Step-by-step route list
    if (p1RouteStepList && data.route_steps) {
      renderRouteSteps(data.route_steps, data.safest_shelter);
    }
  }

  function updateP1RouteResults(data) {
    if (!data) return;
    if (p1RouteOrigin) p1RouteOrigin.textContent = data.start_module;
    if (p1RouteTarget) p1RouteTarget.textContent = data.target_module;
    if (p1TransitDoseVal) p1TransitDoseVal.innerHTML = `${data.transit_dose_mSv.toFixed(2)} <small>mSv</small>`;
    if (p1RouteDisplay && data.route) {
      p1RouteDisplay.innerHTML = data.route.map(m => `<strong>[${m}]</strong>`).join(" ➔ ");
    }
    if (p1RouteStepList && data.steps) {
      renderRouteSteps(data.steps, data.target_module);
    }
  }

  function renderRouteSteps(steps, targetModule) {
    p1RouteStepList.innerHTML = "";
    steps.forEach(s => {
      const li = document.createElement("li");
      const isDestination = s.module === targetModule;
      li.className = `route-step-item ${isDestination ? 'target-step' : ''}`;
      li.innerHTML = `
        <span><strong>Step ${s.step}:</strong> ${s.module} (${s.name})</span>
        <span>Transit Time: <strong>${s.transit_time_min || 0} min</strong></span>
        <span>Segment Dose: <strong>${(s.step_dose_mSv || 0).toFixed(2)} mSv</strong></span>
        <span>Cumulative: <strong style="color: var(--accent-cyan);">${(s.accumulated_dose_mSv || 0).toFixed(2)} mSv</strong></span>
      `;
      p1RouteStepList.appendChild(li);
    });
  }

  // ===================================================================
  // Utility Styling Functions
  // ===================================================================
  function setSeverityBadge(badgeEl, level) {
    if (!badgeEl) return;
    badgeEl.textContent = level;
    badgeEl.className = `badge ${getBadgeClass(level)}`;
  }

  function getBadgeClass(level) {
    switch (level?.toUpperCase()) {
      case "CRITICAL":
      case "CRITICAL EXPOSURE":
        return "badge-critical";
      case "HIGH":
      case "HIGH EXPOSURE":
      case "ELEVATED":
        return "badge-high";
      case "MEDIUM":
      case "MODERATE":
      case "MODERATE EXPOSURE":
        return "badge-medium";
      default:
        return "badge-low";
    }
  }

  function setHeroRiskStyle(pillEl, level) {
    pillEl.className = "risk-pill";
    switch (level?.toUpperCase()) {
      case "CRITICAL":
        pillEl.style.background = "rgba(255, 23, 68, 0.25)";
        pillEl.style.color = "#ff1744";
        pillEl.style.borderColor = "#ff1744";
        break;
      case "HIGH":
        pillEl.style.background = "rgba(255, 87, 34, 0.2)";
        pillEl.style.color = "#ff7043";
        pillEl.style.borderColor = "#ff7043";
        break;
      case "MEDIUM":
      case "MODERATE":
        pillEl.style.background = "rgba(255, 171, 0, 0.2)";
        pillEl.style.color = "#ffab00";
        pillEl.style.borderColor = "#ffab00";
        break;
      default:
        pillEl.style.background = "rgba(0, 230, 118, 0.2)";
        pillEl.style.color = "#00e676";
        pillEl.style.borderColor = "#00e676";
        break;
    }
  }

  function getScoreColor(val) {
    if (val > 0.6) return "#ff1744";
    if (val > 0.3) return "#ffab00";
    return "#00e5ff";
  }

  function setFusionCardStyle(cardEl, score, status) {
    if (!cardEl) return;
    const statusUpper = (status || "").toUpperCase();
    if (score >= 0.40 || statusUpper.includes("CRITICAL")) {
      cardEl.className = "fusion-card has-impact critical";
    } else if (score >= 0.25 || statusUpper.includes("HIGH") || statusUpper.includes("SEVERE")) {
      cardEl.className = "fusion-card has-impact high";
    } else if (score > 0 || statusUpper.includes("MODERATE")) {
      cardEl.className = "fusion-card has-impact moderate";
    } else {
      cardEl.className = "fusion-card";
    }
  }

  function setFlowResultStyle(stepEl, level) {
    if (!stepEl) return;
    const levelUpper = (level || "").toUpperCase();
    if (levelUpper === "CRITICAL") {
      stepEl.style.borderColor = "#ff1744";
      stepEl.style.background = "rgba(255, 23, 68, 0.15)";
      stepEl.querySelector(".step-title").style.color = "#ff1744";
    } else if (levelUpper === "HIGH") {
      stepEl.style.borderColor = "#ff7043";
      stepEl.style.background = "rgba(255, 87, 34, 0.15)";
      stepEl.querySelector(".step-title").style.color = "#ff7043";
    } else if (levelUpper === "MEDIUM" || levelUpper === "MODERATE") {
      stepEl.style.borderColor = "#ffab00";
      stepEl.style.background = "rgba(255, 171, 0, 0.15)";
      stepEl.querySelector(".step-title").style.color = "#ffab00";
    } else {
      stepEl.style.borderColor = "#00e676";
      stepEl.style.background = "rgba(0, 230, 118, 0.15)";
      stepEl.querySelector(".step-title").style.color = "#00e676";
    }
  }

  // Initial Boot
  fetchInitialState();
});
