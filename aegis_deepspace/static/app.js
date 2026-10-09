// Aegis-DeepSpace Mission Control & Four-Pillar Client Logic

function initAegisApp() {
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
  const p2AstroSelect = document.getElementById("p2AstroSelect");
  const p2RecordVoiceBtn = document.getElementById("p2RecordVoiceBtn");
  const p2RecordIcon = document.getElementById("p2RecordIcon");
  const p2RecordText = document.getElementById("p2RecordText");
  const p2AudioFileInput = document.getElementById("p2AudioFileInput");
  const p2SelectedFileTag = document.getElementById("p2SelectedFileTag");
  const p2RecordingBanner = document.getElementById("p2RecordingBanner");
  const p2RecordTimer = document.getElementById("p2RecordTimer");
  const p2StopRecordBtn = document.getElementById("p2StopRecordBtn");
  const p2CancelRecordBtn = document.getElementById("p2CancelRecordBtn");
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
    try {
      sessionStorage.setItem("aegis_active_tab", targetTabId);
    } catch (_) {}

    // Update nav buttons
    document.querySelectorAll(".nav-tab-btn").forEach(btn => {
      if (btn.dataset.tab === targetTabId) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    // Update views dropdown items if present
    document.querySelectorAll(".views-dropdown-item").forEach(item => {
      if (item.dataset.tabTarget === targetTabId) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
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
    } else if (targetTabId === "tab-centrifuge") {
      fetchCentrifugeState();
    } else if (targetTabId === "tab-copilot") {
      updateCopilotTelemetryPreview();
      const inputField = document.getElementById("sectionCopilotInputField");
      if (inputField) setTimeout(() => inputField.focus(), 80);
    } else if (targetTabId === "tab-sync") {
      fetchSyncStatusAndTimeline();
    }
  }

  // ===================================================================
  // Interactive Dropdown Menus (Scenarios & Views)
  // ===================================================================
  const scenarioDropdownWrapper = document.getElementById("scenarioDropdownWrapper");
  const scenarioDropdownBtn = document.getElementById("scenarioDropdownBtn");
  const scenarioActiveTitle = document.getElementById("scenarioActiveTitle");
  const scenarioActiveDot = document.getElementById("scenarioActiveDot");

  const viewsDropdownWrapper = document.getElementById("viewsDropdownWrapper");
  const viewsDropdownBtn = document.getElementById("viewsDropdownBtn");
  const viewsDropdownMenu = document.getElementById("viewsDropdownMenu");

  const scenarioMeta = {
    normal: { title: "1. Nominal Baseline", dotClass: "trigger-dot" },
    solar_storm: { title: "2. Solar Storm (SPE)", dotClass: "trigger-dot critical" },
    voice_anomaly: { title: "3. Voice Anomaly", dotClass: "trigger-dot warning" },
    combined_anomaly: { title: "4. Combined Anomaly", dotClass: "trigger-dot critical" },
    offline_blackout: { title: "5. Offline Blackout", dotClass: "trigger-dot warning" },
    uncertain_data: { title: "6. Uncertain Data", dotClass: "trigger-dot warning" },
    centrifuge_despin: { title: "7. Centrifugal Despin Shock", dotClass: "trigger-dot critical" }
  };

  function updateScenarioDropdownDisplay(scenarioId) {
    const meta = scenarioMeta[scenarioId] || { title: scenarioId, dotClass: "trigger-dot" };
    if (scenarioActiveTitle) scenarioActiveTitle.textContent = meta.title;
    if (scenarioActiveDot) scenarioActiveDot.className = meta.dotClass;
  }

  function toggleDropdown(wrapper, btn) {
    if (!wrapper) return;
    const isOpen = wrapper.classList.contains("open");
    // Close other dropdowns first
    document.querySelectorAll(".dropdown-wrapper").forEach(w => {
      if (w !== wrapper) {
        w.classList.remove("open");
        const b = w.querySelector(".dropdown-trigger");
        if (b) b.setAttribute("aria-expanded", "false");
      }
    });
    wrapper.classList.toggle("open", !isOpen);
    if (btn) btn.setAttribute("aria-expanded", String(!isOpen));
  }

  function closeAllDropdowns() {
    document.querySelectorAll(".dropdown-wrapper").forEach(w => {
      w.classList.remove("open");
      const b = w.querySelector(".dropdown-trigger");
      if (b) b.setAttribute("aria-expanded", "false");
    });
  }

  if (scenarioDropdownBtn && scenarioDropdownWrapper) {
    scenarioDropdownBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleDropdown(scenarioDropdownWrapper, scenarioDropdownBtn);
    });
  }

  if (viewsDropdownBtn && viewsDropdownWrapper) {
    viewsDropdownBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleDropdown(viewsDropdownWrapper, viewsDropdownBtn);
    });
  }

  if (viewsDropdownMenu) {
    viewsDropdownMenu.addEventListener("click", (e) => {
      const item = e.target.closest(".views-dropdown-item");
      if (!item) return;
      e.preventDefault();
      const targetTab = item.dataset.tabTarget;
      if (targetTab) {
        switchTab(targetTab);
        closeAllDropdowns();
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  }

  // Close dropdowns on outside click or escape
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".dropdown-wrapper")) {
      closeAllDropdowns();
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeAllDropdowns();
    }
  });

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
  if (scenarioBtnGroup) {
    scenarioBtnGroup.addEventListener("click", (e) => {
      const btn = e.target.closest(".scenario-btn");
      if (!btn) return;

      const scenarioId = btn.dataset.scenario;
      document.querySelectorAll(".scenario-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      updateScenarioDropdownDisplay(scenarioId);
      closeAllDropdowns();

      loadScenario(scenarioId);
    });
  }

  // Toggle Comms Click Handler
  if (toggleCommsBtn) {
    toggleCommsBtn.addEventListener("click", (e) => {
      e.preventDefault();
      toggleCommsMode();
    });
  }

  const restoreCommsInlineBtn = document.getElementById("restoreCommsInlineBtn");
  if (restoreCommsInlineBtn) {
    restoreCommsInlineBtn.addEventListener("click", (e) => {
      e.preventDefault();
      toggleCommsMode();
    });
  }

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

  // Pillar 2 Voice Input Microphone & File Handlers
  if (p2RecordVoiceBtn) {
    p2RecordVoiceBtn.addEventListener("click", () => {
      startLiveVoiceRecording();
    });
  }

  if (p2StopRecordBtn) {
    p2StopRecordBtn.addEventListener("click", () => {
      stopLiveVoiceRecording();
    });
  }

  if (p2CancelRecordBtn) {
    p2CancelRecordBtn.addEventListener("click", () => {
      cancelLiveVoiceRecording();
    });
  }

  if (p2AudioFileInput) {
    p2AudioFileInput.addEventListener("change", (e) => {
      const file = e.target.files && e.target.files[0];
      if (file) {
        uploadAndProcessVoiceLog(file, file.name);
      }
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
      const scenId = data.scenario_id || data.scenario || "normal";
      updateScenarioDropdownDisplay(scenId);
      document.querySelectorAll(".scenario-btn").forEach(b => {
        b.classList.toggle("active", b.dataset.scenario === scenId);
      });
      renderState(data.crew_state, data.decision);
      fetchPillar1Analysis();
      fetchPillar2Analysis(scenId);
      fetchPillar3Analysis(scenId);
    } catch (err) {
      console.error("Failed to load initial state:", err);
    }
  }

  async function loadScenario(scenarioId) {
    try {
      updateScenarioDropdownDisplay(scenarioId);
      document.querySelectorAll(".scenario-btn").forEach(b => {
        if (b.dataset.scenario === scenarioId) {
          b.classList.add("active");
        } else {
          b.classList.remove("active");
        }
      });
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

  let isTogglingComms = false;
  async function toggleCommsMode() {
    if (isTogglingComms) {
      console.warn("Comms toggle already in progress, ignoring duplicate trigger.");
      return;
    }
    isTogglingComms = true;

    const restoreCommsInlineBtn = document.getElementById("restoreCommsInlineBtn");
    const blackoutBanner = document.getElementById("blackoutAlertBanner");

    // Optimistic UI update: Immediately reflect new button and badge state for 0ms visual latency
    const isCurrentlyOffline = commsBadge ? commsBadge.classList.contains("offline") : false;
    const willBeOffline = !isCurrentlyOffline;

    if (commsBadge) commsBadge.className = willBeOffline ? "status-indicator offline" : "status-indicator";
    if (commsStatusText) commsStatusText.textContent = willBeOffline ? "OFFLINE [20-MIN BLACKOUT ACTIVE]" : "ONLINE [EARTH LINK ACTIVE]";
    if (blackoutBanner) blackoutBanner.style.display = willBeOffline ? "flex" : "none";
    if (toggleCommsBtn) {
      toggleCommsBtn.innerHTML = willBeOffline ? "🔴 Restore Earth Link" : "⚡ Toggle Blackout";
      if (willBeOffline) toggleCommsBtn.classList.add("btn-blackout-active");
      else toggleCommsBtn.classList.remove("btn-blackout-active");
    }

    try {
      if (toggleCommsBtn) toggleCommsBtn.disabled = true;
      if (restoreCommsInlineBtn) restoreCommsInlineBtn.disabled = true;

      const res = await fetch("/api/comms/toggle", { method: "POST" });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      const data = await res.json();

      if (data && data.crew_state && data.decision) {
        renderState(data.crew_state, data.decision);
        const scenId = data.scenario_id || "normal";
        updateScenarioDropdownDisplay(scenId);
        document.querySelectorAll(".scenario-btn").forEach(b => {
          b.classList.toggle("active", b.dataset.scenario === scenId);
        });

        // Trigger pillar refreshes non-blockingly so failures or slow model runs don't affect toggle state
        fetchPillar1Analysis().catch(e => console.warn("Pillar 1 refresh warning:", e));
        fetchPillar2Analysis(scenId).catch(e => console.warn("Pillar 2 refresh warning:", e));
        fetchPillar3Analysis(scenId).catch(e => console.warn("Pillar 3 refresh warning:", e));
      } else {
        await fetchInitialState();
      }
    } catch (err) {
      console.error("Failed to toggle comms mode:", err);
      // Attempt state sync on failure
      fetchInitialState().catch(() => {});
    } finally {
      if (toggleCommsBtn) toggleCommsBtn.disabled = false;
      if (restoreCommsInlineBtn) restoreCommsInlineBtn.disabled = false;
      isTogglingComms = false;
    }
  }
  window.toggleCommsMode = toggleCommsMode;

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

  // Live Voice Input & MediaRecorder State
  let mediaRecorder = null;
  let audioChunks = [];
  let recordTimerInterval = null;
  let recordStartTime = 0;

  async function runPillar2Inference() {
    try {
      if (p2RunInferenceBtn) {
        p2RunInferenceBtn.textContent = "⏳ RUNNING WHISPER & CNN INFERENCE...";
        p2RunInferenceBtn.disabled = true;
      }
      const audioPath = p2AudioSelect ? p2AudioSelect.value : null;
      const crewId = p2AstroSelect ? p2AstroSelect.value : "ASTRO-01";

      const res = await fetch("/api/pillar2/process_audio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ audio_path: audioPath, crew_id: crewId })
      });
      const data = await res.json();
      renderPillar2Page(data);
      fetchInitialState();
    } catch (err) {
      console.error("Failed to run speech inference:", err);
    } finally {
      if (p2RunInferenceBtn) {
        p2RunInferenceBtn.textContent = "⚡ ANALYZE SELECTED AUDIO";
        p2RunInferenceBtn.disabled = false;
      }
    }
  }

  async function startLiveVoiceRecording() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("Microphone recording is not supported in this browser environment.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          audioChunks.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        if (audioChunks.length > 0) {
          const mimeType = mediaRecorder.mimeType || "audio/webm";
          const audioBlob = new Blob(audioChunks, { type: mimeType });
          const extension = mimeType.includes("wav") ? ".wav" : (mimeType.includes("ogg") ? ".ogg" : ".webm");
          await uploadAndProcessVoiceLog(audioBlob, `live_voice_input${extension}`);
        }
      };

      mediaRecorder.start();
      recordStartTime = Date.now();
      if (p2RecordingBanner) p2RecordingBanner.style.display = "flex";
      if (p2RecordVoiceBtn) p2RecordVoiceBtn.style.display = "none";

      if (p2RecordTimer) {
        p2RecordTimer.textContent = "00:00";
        clearInterval(recordTimerInterval);
        recordTimerInterval = setInterval(() => {
          const elapsedSec = Math.floor((Date.now() - recordStartTime) / 1000);
          const mins = String(Math.floor(elapsedSec / 60)).padStart(2, '0');
          const secs = String(elapsedSec % 60).padStart(2, '0');
          p2RecordTimer.textContent = `${mins}:${secs}`;
        }, 500);
      }
    } catch (err) {
      console.error("Microphone access denied or failed:", err);
      alert("Could not access microphone: " + (err.message || err));
    }
  }

  function stopLiveVoiceRecording() {
    clearInterval(recordTimerInterval);
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
    if (p2RecordingBanner) p2RecordingBanner.style.display = "none";
    if (p2RecordVoiceBtn) p2RecordVoiceBtn.style.display = "inline-flex";
  }

  function cancelLiveVoiceRecording() {
    clearInterval(recordTimerInterval);
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      audioChunks = [];
      mediaRecorder.onstop = () => {
        // Just discard tracks
      };
      mediaRecorder.stop();
    }
    if (p2RecordingBanner) p2RecordingBanner.style.display = "none";
    if (p2RecordVoiceBtn) p2RecordVoiceBtn.style.display = "inline-flex";
  }

  async function uploadAndProcessVoiceLog(fileOrBlob, filename) {
    try {
      if (p2RunInferenceBtn) {
        p2RunInferenceBtn.textContent = "⏳ PROCESSING LIVE/UPLOADED VOICE...";
        p2RunInferenceBtn.disabled = true;
      }
      if (p2SelectedFileTag) {
        p2SelectedFileTag.textContent = `Analyzing: ${filename}...`;
      }

      const crewId = p2AstroSelect ? p2AstroSelect.value : "ASTRO-01";
      const formData = new FormData();
      formData.append("file", fileOrBlob, filename);
      formData.append("crew_id", crewId);

      const res = await fetch("/api/pillar2/upload_audio", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      renderPillar2Page(data);
      fetchInitialState();

      if (p2SelectedFileTag) {
        p2SelectedFileTag.textContent = `✓ Ingested: ${filename}`;
      }
    } catch (err) {
      console.error("Failed to upload and analyze voice log:", err);
      if (p2SelectedFileTag) {
        p2SelectedFileTag.textContent = `Error: ${err.message || 'Upload failed'}`;
      }
    } finally {
      if (p2RunInferenceBtn) {
        p2RunInferenceBtn.textContent = "⚡ ANALYZE SELECTED AUDIO";
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
  let lastKnownState = null;
  let lastKnownDecision = null;

  function renderState(state, decision) {
    if (!state || !decision) return;
    lastKnownState = state;
    lastKnownDecision = decision;
    if (typeof updateCopilotTelemetryPreview === "function") {
      updateCopilotTelemetryPreview(state, decision);
    }

    // 1. Comms Mode
    const isOffline = state.comms_mode === "OFFLINE";
    if (isOffline) {
      if (commsBadge) commsBadge.className = "status-indicator offline";
      if (commsStatusText) commsStatusText.textContent = "OFFLINE [20-MIN BLACKOUT ACTIVE]";
    } else {
      if (commsBadge) commsBadge.className = "status-indicator";
      if (commsStatusText) commsStatusText.textContent = "ONLINE [EARTH LINK ACTIVE]";
    }

    if (toggleCommsBtn) {
      if (isOffline) {
        toggleCommsBtn.innerHTML = "🔴 Restore Earth Link";
        toggleCommsBtn.classList.add("btn-blackout-active");
        toggleCommsBtn.title = "Earth link currently severed (20-min delay). Click to restore online comms.";
      } else {
        toggleCommsBtn.innerHTML = "⚡ Toggle Blackout";
        toggleCommsBtn.classList.remove("btn-blackout-active");
        toggleCommsBtn.title = "Simulate 20-min communication blackout with Earth";
      }
    }

    const blackoutBanner = document.getElementById("blackoutAlertBanner");
    if (blackoutBanner) {
      blackoutBanner.style.display = isOffline ? "flex" : "none";
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
    if (p4AnomaliesCount) p4AnomaliesCount.textContent = `${activePillars} / 3 Domains`;

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
              <div class="tsc-row tsc-explanation-row" style="color: ${isTriggered ? '#ffd54f' : '#aaa'};">${sig.explanation}</div>
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
    const titleEl = stepEl.querySelector(".step-title");
    if (levelUpper === "CRITICAL") {
      stepEl.style.borderColor = "#ff1744";
      stepEl.style.background = "rgba(255, 23, 68, 0.15)";
      if (titleEl) titleEl.style.color = "#ff1744";
    } else if (levelUpper === "HIGH") {
      stepEl.style.borderColor = "#ff7043";
      stepEl.style.background = "rgba(255, 87, 34, 0.15)";
      if (titleEl) titleEl.style.color = "#ff7043";
    } else if (levelUpper === "MEDIUM" || levelUpper === "MODERATE") {
      stepEl.style.borderColor = "#ffab00";
      stepEl.style.background = "rgba(255, 171, 0, 0.15)";
      if (titleEl) titleEl.style.color = "#ffab00";
    } else {
      stepEl.style.borderColor = "#00e676";
      stepEl.style.background = "rgba(0, 230, 118, 0.15)";
      if (titleEl) titleEl.style.color = "#00e676";
    }
  }

  // ===================================================================
  // INTERACTIVE FLIGHT SURGEON SIMULATOR (DASHBOARD)
  // ===================================================================
  const simFluxSlider = document.getElementById("simFluxSlider");
  const simFluxValDisplay = document.getElementById("simFluxValDisplay");
  const simModuleSelect = document.getElementById("simModuleSelect");
  const simCommsSelect = document.getElementById("simCommsSelect");
  const simStrainSlider = document.getElementById("simStrainSlider");
  const simStrainValDisplay = document.getElementById("simStrainValDisplay");
  const simHypoxiaSlider = document.getElementById("simHypoxiaSlider");
  const simHypoxiaValDisplay = document.getElementById("simHypoxiaValDisplay");
  const simDeficitSlider = document.getElementById("simDeficitSlider");
  const simDeficitValDisplay = document.getElementById("simDeficitValDisplay");

  const simResetBtn = document.getElementById("simResetBtn");
  const simSyncDashboardBtn = document.getElementById("simSyncDashboardBtn");
  const simToggleViewBtn = document.getElementById("simToggleViewBtn");
  const simulatorBodyContainer = document.getElementById("simulatorBodyContainer");

  const simMeterScore = document.getElementById("simMeterScore");
  const simMeterArc = document.getElementById("simMeterArc");
  const simRiskLevelBadge = document.getElementById("simRiskLevelBadge");
  const simFormulaText = document.getElementById("simFormulaText");

  const simSynergyBanner = document.getElementById("simSynergyBanner");
  const simSynergyTitle = document.getElementById("simSynergyTitle");
  const simSynergyDesc = document.getElementById("simSynergyDesc");

  const simInternalDoseText = document.getElementById("simInternalDoseText");
  const simShieldPct = document.getElementById("simShieldPct");
  const simDijkstraRoute = document.getElementById("simDijkstraRoute");
  const simTransitDose = document.getElementById("simTransitDose");

  const simVoiceDevText = document.getElementById("simVoiceDevText");
  const simStrainText = document.getElementById("simStrainText");
  const simHypoxiaText = document.getElementById("simHypoxiaText");
  const simVoiceStatusText = document.getElementById("simVoiceStatusText");

  const simBoneLossText = document.getElementById("simBoneLossText");
  const simMuscleAtrophyText = document.getElementById("simMuscleAtrophyText");
  const simDeficitDaysText = document.getElementById("simDeficitDaysText");
  const simCountermeasureStatus = document.getElementById("simCountermeasureStatus");

  const simDirectiveText = document.getElementById("simDirectiveText");
  const simContingencyText = document.getElementById("simContingencyText");

  const SIM_PRESETS = {
    nominal: {
      flux: 5,
      module: "Module A",
      strain: 0.12,
      hypoxia: 0.04,
      deficit: 0,
      comms: "ONLINE"
    },
    solar_storm: {
      flux: 350,
      module: "Module D",
      strain: 0.25,
      hypoxia: 0.04,
      deficit: 0,
      comms: "ONLINE"
    },
    hypoxia: {
      flux: 5,
      module: "Module A",
      strain: 0.85,
      hypoxia: 0.52,
      deficit: 0,
      comms: "ONLINE"
    },
    gym_failure: {
      flux: 5,
      module: "Module A",
      strain: 0.20,
      hypoxia: 0.04,
      deficit: 8,
      comms: "ONLINE"
    },
    compound_crisis: {
      flux: 350,
      module: "Module D",
      strain: 0.85,
      hypoxia: 0.45,
      deficit: 8,
      comms: "OFFLINE"
    }
  };

  let simDebounceTimer = null;

  function triggerSimulatorUpdate(syncToDashboard = false) {
    clearTimeout(simDebounceTimer);
    simDebounceTimer = setTimeout(() => {
      runSimulatorEvaluation(syncToDashboard);
    }, syncToDashboard ? 0 : 40);
  }

  async function runSimulatorEvaluation(syncToDashboard = false) {
    if (!simFluxSlider) return;

    const fluxVal = parseFloat(simFluxSlider.value) || 0;
    const modVal = simModuleSelect ? simModuleSelect.value : "Module A";
    const commsVal = simCommsSelect ? simCommsSelect.value : "ONLINE";
    const strainVal = parseFloat(simStrainSlider.value) || 0;
    const hypoxiaVal = parseFloat(simHypoxiaSlider.value) || 0;
    const deficitVal = parseInt(simDeficitSlider.value, 10) || 0;

    // Update readout labels
    if (simFluxValDisplay) simFluxValDisplay.textContent = `${fluxVal.toFixed(1)} mSv/h`;
    if (simStrainValDisplay) simStrainValDisplay.textContent = strainVal.toFixed(2);
    if (simHypoxiaValDisplay) simHypoxiaValDisplay.textContent = hypoxiaVal.toFixed(2);
    if (simDeficitValDisplay) simDeficitValDisplay.textContent = `${deficitVal} days`;

    try {
      const res = await fetch("/api/simulator/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          external_flux_msv: fluxVal,
          current_module: modVal,
          cognitive_strain: strainVal,
          fatigue_score: Math.min(1.0, strainVal * 0.95),
          hypoxia_marker: hypoxiaVal,
          exercise_deficit_days: deficitVal,
          comms_mode: commsVal,
          sync_to_dashboard: syncToDashboard
        })
      });

      if (!res.ok) return;
      const data = await res.json();
      renderSimulatorResults(data);

      if (syncToDashboard) {
        renderState(data.crew_state, data.decision);
        if (simSyncDashboardBtn) {
          const origText = simSyncDashboardBtn.innerHTML;
          simSyncDashboardBtn.innerHTML = "✓ Synced Successfully!";
          setTimeout(() => {
            simSyncDashboardBtn.innerHTML = origText;
          }, 2000);
        }
      }
    } catch (err) {
      console.error("Failed to run simulator evaluation:", err);
    }
  }

  function renderSimulatorResults(data) {
    if (!data || !data.decision) return;
    const dec = data.decision;
    const sim = data.simulation_summary || {};

    // 1. Arc Meter Visual
    const score = dec.risk_score || 0.10;
    if (simMeterScore) simMeterScore.textContent = score.toFixed(2);

    if (simMeterArc) {
      // Circumference of half circle r=40 is pi * 40 ≈ 126
      const totalCircumference = 126;
      const offset = totalCircumference - (score * totalCircumference);
      simMeterArc.style.strokeDashoffset = String(Math.max(0, offset));

      let strokeColor = "#10b981"; // Low (emerald)
      if (score >= 0.75 || dec.risk_level === "CRITICAL") strokeColor = "#f43f5e";
      else if (score >= 0.50 || dec.risk_level === "HIGH") strokeColor = "#fb923c";
      else if (score >= 0.30 || dec.risk_level === "MEDIUM") strokeColor = "#f59e0b";
      simMeterArc.style.stroke = strokeColor;
    }

    if (simRiskLevelBadge) {
      simRiskLevelBadge.textContent = `${dec.risk_level} RISK`;
      simRiskLevelBadge.className = `sim-level-badge ${getBadgeClass(dec.risk_level)}`;
    }

    if (simFormulaText && sim.formula) {
      simFormulaText.textContent = sim.formula;
    }

    // 2. Synergy Banner
    if (simSynergyBanner) {
      if (sim.synergy_active) {
        simSynergyBanner.className = "sim-synergy-banner active";
        if (simSynergyTitle) simSynergyTitle.textContent = "⚡ Multi-Signal Synergy Escalated (+0.20)";
        if (simSynergyDesc) simSynergyDesc.textContent = "Compound stress cascade: Concurrent radiation surge, cognitive impairment, and physical deconditioning non-linearly accelerates failure risk.";
      } else {
        simSynergyBanner.className = "sim-synergy-banner";
        if (simSynergyTitle) simSynergyTitle.textContent = "No Multi-Signal Escalation";
        if (simSynergyDesc) simSynergyDesc.textContent = "Telemetry parameters remain within non-compounding operational thresholds.";
      }
    }

    // 3. 4-Pillar Physical Impact Matrix
    if (simInternalDoseText) simInternalDoseText.textContent = `${sim.internal_dose_rate_msv_h.toFixed(1)} mSv/h`;
    if (simShieldPct) simShieldPct.textContent = `${sim.shielding_pct}%`;
    if (simDijkstraRoute && sim.evacuation_route) {
      simDijkstraRoute.textContent = sim.evacuation_route.join(" ➔ ");
    }
    if (simTransitDose) simTransitDose.textContent = `${sim.transit_dose_msv.toFixed(2)} mSv`;

    if (simVoiceDevText) simVoiceDevText.textContent = `${sim.baseline_deviation_sigma >= 0 ? '+' : ''}${sim.baseline_deviation_sigma.toFixed(1)}σ`;
    if (simStrainText) {
      const s = parseFloat(simStrainSlider.value) || 0;
      simStrainText.textContent = `${s.toFixed(2)} (${s > 0.6 ? 'Impaired' : (s > 0.3 ? 'Elevated' : 'Nominal')})`;
    }
    if (simHypoxiaText) {
      const h = parseFloat(simHypoxiaSlider.value) || 0;
      simHypoxiaText.textContent = `${h.toFixed(2)} (${h >= 0.4 ? 'Critical Marker' : 'Clear'})`;
    }
    if (simVoiceStatusText) {
      simVoiceStatusText.textContent = (dec.risk_fusion?.p2_voice_vitals?.status) || "Within Baseline";
    }

    if (simBoneLossText) simBoneLossText.textContent = `-${sim.bone_loss_pct_mo.toFixed(1)}%/mo`;
    if (simMuscleAtrophyText) simMuscleAtrophyText.textContent = `-${sim.muscle_atrophy_pct.toFixed(1)}%`;
    if (simDeficitDaysText) {
      const d = parseInt(simDeficitSlider.value, 10) || 0;
      simDeficitDaysText.textContent = `${d} day${d === 1 ? '' : 's'}`;
    }
    if (simCountermeasureStatus) {
      simCountermeasureStatus.textContent = (dec.risk_fusion?.p3_astro_twin?.status) || "Nominal Plan";
    }

    // 4. Clinical Directive
    if (simDirectiveText) simDirectiveText.textContent = dec.recommended_action || "Continue nominal operations.";
    if (simContingencyText) simContingencyText.textContent = dec.alternative_action || "No corrective intervention required.";
  }

  function applyPreset(presetKey) {
    const config = SIM_PRESETS[presetKey];
    if (!config) return;

    if (simFluxSlider) simFluxSlider.value = config.flux;
    if (simModuleSelect) simModuleSelect.value = config.module;
    if (simStrainSlider) simStrainSlider.value = config.strain;
    if (simHypoxiaSlider) simHypoxiaSlider.value = config.hypoxia;
    if (simDeficitSlider) simDeficitSlider.value = config.deficit;
    if (simCommsSelect) simCommsSelect.value = config.comms;

    document.querySelectorAll(".preset-btn").forEach(btn => {
      if (btn.dataset.preset === presetKey) btn.classList.add("active");
      else btn.classList.remove("active");
    });

    triggerSimulatorUpdate(false);
  }

  // Bind Preset Buttons
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      applyPreset(btn.dataset.preset);
    });
  });

  // Bind Sliders & Selects
  [simFluxSlider, simStrainSlider, simHypoxiaSlider, simDeficitSlider].forEach(slider => {
    if (slider) {
      slider.addEventListener("input", () => {
        document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
        triggerSimulatorUpdate(false);
      });
    }
  });

  [simModuleSelect, simCommsSelect].forEach(select => {
    if (select) {
      select.addEventListener("change", () => {
        document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
        triggerSimulatorUpdate(false);
      });
    }
  });

  // Bind Action Buttons
  if (simResetBtn) {
    simResetBtn.addEventListener("click", () => {
      applyPreset("nominal");
    });
  }

  if (simSyncDashboardBtn) {
    simSyncDashboardBtn.addEventListener("click", () => {
      runSimulatorEvaluation(true);
    });
  }

  if (simToggleViewBtn && simulatorBodyContainer) {
    simToggleViewBtn.addEventListener("click", () => {
      const isHidden = simulatorBodyContainer.style.display === "none";
      simulatorBodyContainer.style.display = isHidden ? "block" : "none";
      simToggleViewBtn.textContent = isHidden ? "📐 Minimize View" : "🔍 Expand Simulator";
    });
  }

  // ===================================================================
  // CENTRIFUGAL RING SPIN-DOWN SIMULATOR CONTROLLER
  // ===================================================================
  let centrifugeData = null;
  let centrifugePlaybackTimer = null;
  let isCentrifugePlaying = false;

  // DOM Elements
  const btnRunCentrifugeSim = document.getElementById("btnRunCentrifugeSim");
  const btnActuateCentrifuge = document.getElementById("btnActuateCentrifuge");
  const btnInjectCentrifuge = document.getElementById("btnInjectCentrifuge");
  const btnResetCentrifuge = document.getElementById("btnResetCentrifuge");
  const btnPlayCentrifuge = document.getElementById("btnPlayCentrifuge");
  const btnCopyCentrifugeJson = document.getElementById("btnCopyCentrifugeJson");

  const cfgInitialG = document.getElementById("cfgInitialG");
  const cfgDuration = document.getElementById("cfgDuration");
  const cfgDurationVal = document.getElementById("cfgDurationVal");
  const cfgAngularDecel = document.getElementById("cfgAngularDecel");
  const cfgAngularDecelVal = document.getElementById("cfgAngularDecelVal");
  const cfgFluidShift = document.getElementById("cfgFluidShift");
  const cfgFluidShiftVal = document.getElementById("cfgFluidShiftVal");
  const cfgStrappedOnset = document.getElementById("cfgStrappedOnset");
  const cfgDeckLock = document.getElementById("cfgDeckLock");
  const cfgCountermeasures = document.getElementById("cfgCountermeasures");

  const simScrubber = document.getElementById("simScrubber");
  const simScrubberTimeText = document.getElementById("simScrubberTimeText");
  const simCurrentPhaseText = document.getElementById("simCurrentPhaseText");

  const svgHabitatRing = document.getElementById("svgHabitatRing");
  const ringGovernorTag = document.getElementById("ringGovernorTag");
  const ringRpmDisplay = document.getElementById("ringRpmDisplay");
  const ringGDisplay = document.getElementById("ringGDisplay");
  const statAngVel = document.getElementById("statAngVel");
  const statCoriolisShear = document.getElementById("statCoriolisShear");
  const statCrewKinematics = document.getElementById("statCrewKinematics");

  const badgeGLevel = document.getElementById("badgeGLevel");
  const valLiveGLevel = document.getElementById("valLiveGLevel");
  const barLiveGLevel = document.getElementById("barLiveGLevel");
  const valHydrostaticCol = document.getElementById("valHydrostaticCol");

  const badgeCvp = document.getElementById("badgeCvp");
  const valLiveCvp = document.getElementById("valLiveCvp");
  const barLiveCvp = document.getElementById("barLiveCvp");
  const valLiveFluidVol = document.getElementById("valLiveFluidVol");
  const valLiveFluidRate = document.getElementById("valLiveFluidRate");

  const badgeIcp = document.getElementById("badgeIcp");
  const valLiveIcp = document.getElementById("valLiveIcp");
  const barLiveIcp = document.getElementById("barLiveIcp");

  const badgeSms = document.getElementById("badgeSms");
  const valLiveSms = document.getElementById("valLiveSms");
  const barLiveSms = document.getElementById("barLiveSms");
  const valLiveMismatch = document.getElementById("valLiveMismatch");
  const valLiveCollision = document.getElementById("valLiveCollision");

  const pathGravity = document.getElementById("pathGravity");
  const pathCvp = document.getElementById("pathCvp");
  const pathIcp = document.getElementById("pathIcp");
  const pathSms = document.getElementById("pathSms");
  const scrubberCursorLine = document.getElementById("scrubberCursorLine");

  const centrifugeCrewGrid = document.getElementById("centrifugeCrewGrid");
  const centrifugeDirectivesContainer = document.getElementById("centrifugeDirectivesContainer");
  const centrifugeInterventionsContainer = document.getElementById("centrifugeInterventionsContainer");
  const badgeVerdictAlert = document.getElementById("badgeVerdictAlert");
  const centrifugeVerdictRationale = document.getElementById("centrifugeVerdictRationale");
  const centrifugeJsonBlock = document.getElementById("centrifugeJsonBlock");

  // Sync Slider Labels
  if (cfgDuration && cfgDurationVal) {
    cfgDuration.addEventListener("input", (e) => {
      cfgDurationVal.textContent = `${e.target.value}s`;
      if (simScrubber) simScrubber.max = e.target.value;
    });
  }
  if (cfgAngularDecel && cfgAngularDecelVal) {
    cfgAngularDecel.addEventListener("input", (e) => {
      cfgAngularDecelVal.textContent = `${e.target.value}°/s²`;
    });
  }
  if (cfgFluidShift && cfgFluidShiftVal) {
    cfgFluidShift.addEventListener("input", (e) => {
      cfgFluidShiftVal.textContent = `+${e.target.value} mL`;
    });
  }

  // Fetch Current State
  async function fetchCentrifugeState() {
    try {
      const res = await fetch("/api/centrifuge/state");
      if (!res.ok) return;
      centrifugeData = await res.json();
      applyCentrifugeData(centrifugeData);
    } catch (err) {
      console.error("Failed to fetch centrifuge state:", err);
    }
  }

  // Run Simulation
  async function runCentrifugeSimulation() {
    stopCentrifugePlayback();
    const payload = {
      initial_g: parseFloat(cfgInitialG?.value || "0.38"),
      target_g: 0.0,
      duration_seconds: parseFloat(cfgDuration?.value || "90"),
      angular_deceleration_deg_s2: parseFloat(cfgAngularDecel?.value || "2.4"),
      crew_count: 4,
      strapped_at_onset: !!cfgStrappedOnset?.checked,
      magnetic_deck_locked: !!cfgDeckLock?.checked,
      countermeasures_active: !!cfgCountermeasures?.checked,
      fluid_shift_rate_ml_min: parseFloat(cfgFluidShift?.value || "850")
    };

    try {
      const res = await fetch("/api/centrifuge/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("Simulation failed");
      centrifugeData = await res.json();
      applyCentrifugeData(centrifugeData);
      startCentrifugePlayback();
    } catch (err) {
      console.error("Simulation execution error:", err);
    }
  }

  // Deploy Autonomous Countermeasures
  async function actuateCentrifuge() {
    try {
      const res = await fetch("/api/centrifuge/actuate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lock_magnetic_deck: true,
          dispense_antiemetics: true,
          inflate_braslet_cuffs: true,
          eclss_strobe_suppression: true
        })
      });
      if (!res.ok) throw new Error("Actuation failed");
      const data = await res.json();
      centrifugeData = data.result;
      if (cfgDeckLock) cfgDeckLock.checked = true;
      if (cfgCountermeasures) cfgCountermeasures.checked = true;
      applyCentrifugeData(centrifugeData);
      // Flash feedback
      if (btnActuateCentrifuge) {
        const orig = btnActuateCentrifuge.textContent;
        btnActuateCentrifuge.textContent = "✓ INTERVENTIONS DEPLOYED";
        setTimeout(() => { btnActuateCentrifuge.textContent = orig; }, 2000);
      }
    } catch (err) {
      console.error("Actuation error:", err);
    }
  }

  // Inject Crisis to Decision Engine
  async function injectCentrifugeToEngine() {
    try {
      const res = await fetch("/api/centrifuge/inject", { method: "POST" });
      if (!res.ok) throw new Error("Injection failed");
      const data = await res.json();
      updateScenarioDropdownDisplay("centrifuge_despin");
      updateMissionControlDashboard(data.crew_state, data.decision);
      switchTab("tab-mission-control");
    } catch (err) {
      console.error("Injection error:", err);
    }
  }

  // Reset to Nominal
  function resetCentrifugeNominal() {
    stopCentrifugePlayback();
    if (cfgInitialG) cfgInitialG.value = "0.38";
    if (cfgDuration) { cfgDuration.value = "90"; cfgDurationVal.textContent = "90s"; }
    if (cfgAngularDecel) { cfgAngularDecel.value = "2.4"; cfgAngularDecelVal.textContent = "2.4°/s²"; }
    if (cfgFluidShift) { cfgFluidShift.value = "850"; cfgFluidShiftVal.textContent = "+850 mL"; }
    if (cfgStrappedOnset) cfgStrappedOnset.checked = false;
    if (cfgDeckLock) cfgDeckLock.checked = false;
    if (cfgCountermeasures) cfgCountermeasures.checked = false;
    if (simScrubber) simScrubber.value = "0";

    runCentrifugeSimulation();
  }

  // Apply Full Data Payload
  function applyCentrifugeData(data) {
    if (!data) return;

    // Config inputs sync
    if (data.config) {
      if (cfgInitialG) cfgInitialG.value = String(data.config.initial_g);
      if (cfgDuration) {
        cfgDuration.value = String(data.config.duration_seconds);
        cfgDurationVal.textContent = `${data.config.duration_seconds}s`;
        if (simScrubber) simScrubber.max = String(data.config.duration_seconds);
      }
      if (cfgAngularDecel) {
        cfgAngularDecel.value = String(data.config.angular_deceleration_deg_s2);
        cfgAngularDecelVal.textContent = `${data.config.angular_deceleration_deg_s2}°/s²`;
      }
      if (cfgFluidShift) {
        cfgFluidShift.value = String(data.config.fluid_shift_rate_ml_min);
        cfgFluidShiftVal.textContent = `+${data.config.fluid_shift_rate_ml_min} mL`;
      }
      if (cfgStrappedOnset) cfgStrappedOnset.checked = !!data.config.strapped_at_onset;
      if (cfgDeckLock) cfgDeckLock.checked = !!data.config.magnetic_deck_locked;
      if (cfgCountermeasures) cfgCountermeasures.checked = !!data.config.countermeasures_active;
    }

    // Directives & Interventions
    renderCentrifugeDirectives(data.primary_countermeasures || []);
    renderCentrifugeInterventions(data.system_interventions || {});
    renderCentrifugeCrew(data.crew_roster || []);
    renderCentrifugeTrajectoryChart(data.time_series || [], data.config?.duration_seconds || 90);

    // Verdict & JSON block
    if (data.flight_surgeon_verdict) {
      const v = data.flight_surgeon_verdict;
      if (badgeVerdictAlert) {
        badgeVerdictAlert.textContent = v.alert_classification || "RED_CRITICAL_EMERGENCY";
        badgeVerdictAlert.style.color = v.alert_classification?.includes("STABILIZED") ? "#34d399" : "#f43f5e";
        badgeVerdictAlert.style.borderColor = v.alert_classification?.includes("STABILIZED") ? "rgba(52, 211, 153, 0.5)" : "rgba(244, 63, 94, 0.5)";
      }
      if (centrifugeVerdictRationale) {
        centrifugeVerdictRationale.textContent = v.rationale || "";
      }
    }

    if (centrifugeJsonBlock) {
      const exportPacket = {
        telemetry_deltas: data.telemetry_deltas,
        acute_clinical_risks: data.acute_clinical_risks,
        primary_countermeasures: data.primary_countermeasures,
        system_interventions: data.system_interventions,
        flight_surgeon_verdict: data.flight_surgeon_verdict
      };
      centrifugeJsonBlock.textContent = JSON.stringify(exportPacket, null, 2);
    }

    // Default scrubber step to end if not currently playing
    if (!isCentrifugePlaying && data.time_series && data.time_series.length > 0) {
      updateCentrifugeScrubberVisuals(data.time_series[data.time_series.length - 1]);
      if (simScrubber) simScrubber.value = simScrubber.max;
    }
  }

  // Scrubber Update
  function updateCentrifugeScrubberVisuals(step) {
    if (!step) return;
    const dur = parseFloat(cfgDuration?.value || "90");
    if (simScrubberTimeText) {
      simScrubberTimeText.textContent = `t = ${step.time_s.toFixed(1)}s / ${dur.toFixed(1)}s`;
    }
    if (simCurrentPhaseText) {
      simCurrentPhaseText.textContent = `Phase: ${step.phase_label}`;
    }

    // Ring Animation and Overlay
    const rpm = ((step.angular_velocity_deg_s / 360) * 60).toFixed(2);
    if (ringRpmDisplay) ringRpmDisplay.textContent = `${rpm} RPM`;
    if (ringGDisplay) ringGDisplay.textContent = `${step.g_level.toFixed(3)}g`;

    if (svgHabitatRing) {
      if (step.g_level <= 0.001) {
        svgHabitatRing.style.animation = "none";
        if (ringGovernorTag) {
          ringGovernorTag.textContent = "DESPIN COMPLETE";
          ringGovernorTag.style.color = "#f43f5e";
        }
      } else {
        const animDuration = Math.max(0.5, 60 / Math.max(0.1, parseFloat(rpm)));
        svgHabitatRing.style.animation = `habitatRingSpin ${animDuration}s linear infinite`;
        if (ringGovernorTag) {
          ringGovernorTag.textContent = step.time_s === 0 ? "GOVERNOR NOMINAL" : "GOVERNOR SCRAMMED";
          ringGovernorTag.style.color = step.time_s === 0 ? "#10b981" : "#f59e0b";
        }
      }
    }

    // Kinematics and Coriolis
    if (statAngVel) statAngVel.textContent = `${step.angular_velocity_deg_s.toFixed(1)} °/s`;
    if (statCoriolisShear) {
      const shear = (parseFloat(cfgAngularDecel?.value || "2.4") * 0.175 * (step.g_level / (parseFloat(cfgInitialG?.value || "0.38") || 0.38))).toFixed(2);
      statCoriolisShear.textContent = `${shear} G`;
    }
    const isLocked = !!cfgDeckLock?.checked || !!cfgStrappedOnset?.checked;
    if (statCrewKinematics) {
      statCrewKinematics.textContent = isLocked ? "SECURED (DECK-LOCKED)" : (step.g_level < 0.05 ? "FREE-FLOAT TUMBLING" : "LOSING TRACTION");
      statCrewKinematics.style.color = isLocked ? "#10b981" : (step.g_level < 0.05 ? "#f43f5e" : "#f59e0b");
    }

    // Update Crew Dots
    const dotColor = isLocked ? "#10b981" : (step.g_level < 0.05 ? "#f43f5e" : "#f59e0b");
    [1, 2, 3, 4].forEach(id => {
      const dot = document.getElementById(`crewDot${id}`);
      if (dot) dot.setAttribute("fill", dotColor);
    });

    // Gauges: G-Level
    if (valLiveGLevel) valLiveGLevel.textContent = `${step.g_level.toFixed(3)}g`;
    if (badgeGLevel) {
      badgeGLevel.textContent = step.g_level < 0.02 ? "0.00g ZERO-G" : `${step.g_level.toFixed(2)}g MARS`;
      badgeGLevel.style.color = step.g_level < 0.02 ? "#f43f5e" : "#38bdf8";
    }
    const gPct = Math.min(100, Math.max(0, (step.g_level / (parseFloat(cfgInitialG?.value || "0.38") || 0.38)) * 100));
    if (barLiveGLevel) barLiveGLevel.style.width = `${gPct}%`;
    if (valHydrostaticCol) valHydrostaticCol.textContent = `${Math.round(gPct)}% Intact`;

    // Gauges: CVP
    if (valLiveCvp) valLiveCvp.innerHTML = `${step.cvp_mmhg.toFixed(1)} <span style="font-size: 1rem; font-weight: 500;">mmHg</span>`;
    if (badgeCvp) {
      badgeCvp.textContent = step.cvp_mmhg > 10.0 ? "CRITICAL SPIKE" : (step.cvp_mmhg > 7.0 ? "ELEVATED" : "NOMINAL");
      badgeCvp.style.color = step.cvp_mmhg > 10.0 ? "#f43f5e" : (step.cvp_mmhg > 7.0 ? "#f59e0b" : "#60a5fa");
    }
    const cvpPct = Math.min(100, (step.cvp_mmhg / 14.0) * 100);
    if (barLiveCvp) barLiveCvp.style.width = `${cvpPct}%`;
    if (valLiveFluidVol) valLiveFluidVol.textContent = `+${Math.round(step.cephalad_volume_ml)} mL`;

    // Gauges: ICP
    if (valLiveIcp) valLiveIcp.innerHTML = `${step.icp_mmhg.toFixed(1)} <span style="font-size: 1rem; font-weight: 500;">mmHg</span>`;
    if (badgeIcp) {
      const isDanger = step.icp_mmhg >= 20.0;
      badgeIcp.textContent = isDanger ? "RETROBULBAR ALERT" : (step.icp_mmhg > 14.0 ? "ELEVATED" : "NORMAL");
      badgeIcp.style.color = isDanger ? "#f43f5e" : (step.icp_mmhg > 14.0 ? "#f59e0b" : "#34d399");
    }
    const icpPct = Math.min(100, (step.icp_mmhg / 26.0) * 100);
    if (barLiveIcp) barLiveIcp.style.width = `${icpPct}%`;

    // Gauges: SMS
    if (valLiveSms) valLiveSms.innerHTML = `${step.sms_index.toFixed(1)} <span style="font-size: 1rem; font-weight: 500;">/ 100</span>`;
    if (badgeSms) {
      badgeSms.textContent = step.sms_index > 75.0 ? "PROJECTILE EMESIS" : (step.sms_index > 40.0 ? "MODERATE NAUSEA" : "MILD");
      badgeSms.style.color = step.sms_index > 75.0 ? "#f43f5e" : (step.sms_index > 40.0 ? "#f59e0b" : "#a855f7");
    }
    if (barLiveSms) barLiveSms.style.width = `${Math.min(100, step.sms_index)}%`;
    if (valLiveMismatch) valLiveMismatch.textContent = `${step.vestibular_mismatch_deg.toFixed(1)}°`;
    if (valLiveCollision) valLiveCollision.textContent = `${Math.round(step.collision_prob_pct)}%`;

    // Update cursor on SVG chart
    if (scrubberCursorLine && dur > 0) {
      const xPos = (step.time_s / dur) * 900;
      scrubberCursorLine.setAttribute("x1", xPos);
      scrubberCursorLine.setAttribute("x2", xPos);
    }
  }

  // Playback Control
  function startCentrifugePlayback() {
    stopCentrifugePlayback();
    isCentrifugePlaying = true;
    if (btnPlayCentrifuge) btnPlayCentrifuge.textContent = "⏸ Pause";

    let currTime = 0;
    const dur = parseFloat(cfgDuration?.value || "90");
    const interval = 120; // ms
    const timeDelta = dur / 30; // 30 ticks across duration

    centrifugePlaybackTimer = setInterval(() => {
      currTime += timeDelta;
      if (currTime >= dur) {
        currTime = dur;
        stopCentrifugePlayback();
      }
      if (simScrubber) simScrubber.value = String(Math.round(currTime));
      findAndApplyStep(currTime);
    }, interval);
  }

  function stopCentrifugePlayback() {
    isCentrifugePlaying = false;
    if (centrifugePlaybackTimer) {
      clearInterval(centrifugePlaybackTimer);
      centrifugePlaybackTimer = null;
    }
    if (btnPlayCentrifuge) btnPlayCentrifuge.textContent = "▶ Play";
  }

  function findAndApplyStep(targetTime) {
    if (!centrifugeData || !centrifugeData.time_series) return;
    const series = centrifugeData.time_series;
    // Find closest step
    let closest = series[0];
    let minDiff = 999999;
    series.forEach(s => {
      const diff = Math.abs(s.time_s - targetTime);
      if (diff < minDiff) {
        minDiff = diff;
        closest = s;
      }
    });
    updateCentrifugeScrubberVisuals(closest);
  }

  if (simScrubber) {
    simScrubber.addEventListener("input", (e) => {
      stopCentrifugePlayback();
      findAndApplyStep(parseFloat(e.target.value));
    });
  }

  if (btnPlayCentrifuge) {
    btnPlayCentrifuge.addEventListener("click", () => {
      if (isCentrifugePlaying) {
        stopCentrifugePlayback();
      } else {
        if (parseFloat(simScrubber?.value || "0") >= parseFloat(cfgDuration?.value || "90")) {
          if (simScrubber) simScrubber.value = "0";
        }
        startCentrifugePlayback();
      }
    });
  }

  // Trajectory Chart SVG Renderer
  function renderCentrifugeTrajectoryChart(series, duration) {
    if (!series || series.length === 0 || !duration) return;
    const width = 900;

    const gPoints = [];
    const cvpPoints = [];
    const icpPoints = [];
    const smsPoints = [];

    const maxG = parseFloat(cfgInitialG?.value || "0.38") || 0.38;

    series.forEach(s => {
      const x = (s.time_s / duration) * width;
      // Gravity [0, maxG] mapped to [180, 20]
      const yG = 180 - (s.g_level / Math.max(0.01, maxG)) * 140;
      // CVP [0, 15] mapped to [180, 20]
      const yCvp = 180 - (s.cvp_mmhg / 15.0) * 140;
      // ICP [0, 28] mapped to [180, 20]
      const yIcp = 180 - (s.icp_mmhg / 28.0) * 140;
      // SMS [0, 100] mapped to [180, 20]
      const ySms = 180 - (s.sms_index / 100.0) * 140;

      gPoints.push(`${x.toFixed(1)},${yG.toFixed(1)}`);
      cvpPoints.push(`${x.toFixed(1)},${yCvp.toFixed(1)}`);
      icpPoints.push(`${x.toFixed(1)},${yIcp.toFixed(1)}`);
      smsPoints.push(`${x.toFixed(1)},${ySms.toFixed(1)}`);
    });

    if (pathGravity) pathGravity.setAttribute("d", `M ${gPoints.join(" L ")}`);
    if (pathCvp) pathCvp.setAttribute("d", `M ${cvpPoints.join(" L ")}`);
    if (pathIcp) pathIcp.setAttribute("d", `M ${icpPoints.join(" L ")}`);
    if (pathSms) pathSms.setAttribute("d", `M ${smsPoints.join(" L ")}`);
  }

  // Crew Roster Matrix
  function renderCentrifugeCrew(roster) {
    if (!centrifugeCrewGrid) return;
    if (!roster || roster.length === 0) {
      centrifugeCrewGrid.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted);">No crew telemetry stream available.</div>`;
      return;
    }

    centrifugeCrewGrid.innerHTML = roster.map(c => `
      <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border-color); border-radius: 8px; padding: 0.85rem; border-top: 3px solid ${c.sms_score > 85 ? '#f43f5e' : (c.sms_score > 50 ? '#f59e0b' : '#10b981')};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <div>
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">${c.crew_id} &bull; ${c.role}</div>
            <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">${c.name}</div>
          </div>
          <span class="badge" style="background: ${c.sms_score > 85 ? 'rgba(244,63,94,0.2)' : 'rgba(16,185,129,0.2)'}; color: ${c.sms_score > 85 ? '#f43f5e' : '#34d399'}; font-size: 0.7rem;">
            ${c.sms_score > 85 ? 'CRITICAL' : 'MONITORED'}
          </span>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.35rem; font-size: 0.8rem; margin-bottom: 0.65rem;">
          <div style="background: rgba(255,255,255,0.02); padding: 0.3rem 0.5rem; border-radius: 4px;">
            <span style="color: var(--text-dim); font-size: 0.7rem;">HR / BP:</span>
            <div style="font-family: var(--font-mono); font-weight: 600; color: #fff;">${c.heart_rate_bpm} bpm | ${c.blood_pressure_sys}/${c.blood_pressure_dia}</div>
          </div>
          <div style="background: rgba(255,255,255,0.02); padding: 0.3rem 0.5rem; border-radius: 4px;">
            <span style="color: var(--text-dim); font-size: 0.7rem;">CVP / ICP:</span>
            <div style="font-family: var(--font-mono); font-weight: 600; color: #fff;">${c.cvp_mmhg} / ${c.icp_mmhg} mmHg</div>
          </div>
        </div>

        <div style="font-size: 0.75rem; display: flex; flex-direction: column; gap: 0.25rem;">
          <div><strong style="color: var(--text-dim);">SMS Status:</strong> <span style="color: ${c.sms_score > 80 ? '#fca5a5' : '#fff'};">${c.sms_status} (${c.sms_score})</span></div>
          <div><strong style="color: var(--text-dim);">Restraint:</strong> <span style="color: ${c.restraint_status.includes('LOCKED') || c.restraint_status.includes('HARNESSED') ? '#34d399' : '#f87171'};">${c.restraint_status}</span></div>
          <div><strong style="color: var(--text-dim);">Autoinjector:</strong> <span style="color: ${c.autoinjector_status.includes('DISPENSED') ? '#34d399' : '#60a5fa'}; font-family: var(--font-mono); font-size: 0.72rem;">${c.autoinjector_status}</span></div>
        </div>
      </div>
    `).join("");
  }

  // Directives
  function renderCentrifugeDirectives(directives) {
    if (!centrifugeDirectivesContainer) return;
    if (!directives || directives.length === 0) {
      centrifugeDirectivesContainer.innerHTML = `<p style="color: var(--text-muted);">No directives issued.</p>`;
      return;
    }

    centrifugeDirectivesContainer.innerHTML = directives.map(d => `
      <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-left: 3px solid ${d.priority === 1 ? '#f43f5e' : (d.priority === 2 ? '#f59e0b' : '#3b82f6')}; border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 0.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
          <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-dim);">PRIORITY ${d.priority} &bull; ${d.action_code}</span>
          <span class="badge" style="font-size: 0.7rem; background: ${d.status === 'EXECUTED' || d.status === 'DISPENSED' || d.status?.includes('ACTIVE') ? 'rgba(16,185,129,0.2)' : 'rgba(244,63,94,0.2)'}; color: ${d.status === 'EXECUTED' || d.status === 'DISPENSED' || d.status?.includes('ACTIVE') ? '#34d399' : '#f87171'};">
            ${d.status || 'PENDING'}
          </span>
        </div>
        <div style="font-weight: 700; color: #fff; font-size: 0.95rem; margin-bottom: 0.25rem;">${d.title}</div>
        <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4; margin-bottom: 0.35rem;">${d.clinical_rationale}</div>
        <div style="font-size: 0.75rem; color: var(--text-dim); display: flex; gap: 1rem;">
          <span>Target: <strong style="color: #fff;">${d.execution_target}</strong></span>
          <span>Max Latency: <strong style="color: #fff;">${d.latency_tolerance_sec}s</strong></span>
        </div>
      </div>
    `).join("");
  }

  // Interventions
  function renderCentrifugeInterventions(interventions) {
    if (!centrifugeInterventionsContainer) return;
    const eclss = interventions.eclss_control_signals || {};
    const med = interventions.medical_dispenser_signals || {};
    const hull = interventions.mechanical_and_hull_safing || {};

    centrifugeInterventionsContainer.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 0.85rem;">
        <!-- ECLSS Signals -->
        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.75rem 1rem;">
          <div style="font-size: 0.75rem; color: var(--accent-cyan); font-weight: 700; text-transform: uppercase; margin-bottom: 0.35rem;">ECLSS Environmental Controls</div>
          <div style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5;">
            <div>&bull; <strong>Lighting:</strong> ${eclss.cabin_lighting_state || 'Nominal 4000K'}</div>
            <div>&bull; <strong>Ventilation:</strong> ${eclss.ventilation_velocity_mps || '0.20'} m/s (${eclss.cabin_airflow_vector || 'Nominal'})</div>
            <div>&bull; <strong>Suction:</strong> ${eclss.suction_canisters_power || 'STANDBY'}</div>
          </div>
        </div>

        <!-- Medical Dispenser Signals -->
        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.75rem 1rem;">
          <div style="font-size: 0.75rem; color: #a855f7; font-weight: 700; text-transform: uppercase; margin-bottom: 0.35rem;">Medical Dispenser Signals (${med.station_id || 'STATION-01'})</div>
          <div style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5;">
            ${(med.dispense_order || []).map(o => `
              <div>&bull; <strong>${o.compound} (${o.dose}):</strong> ${o.delivery_system} &rarr; <span style="font-family: var(--font-mono); color: #67e8f9;">[${o.status}]</span></div>
            `).join("")}
          </div>
        </div>

        <!-- Mechanical / Hull Safing -->
        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.75rem 1rem;">
          <div style="font-size: 0.75rem; color: #f59e0b; font-weight: 700; text-transform: uppercase; margin-bottom: 0.35rem;">Mechanical &amp; Hull Safing Actuators</div>
          <div style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5;">
            <div>&bull; <strong>Bulkhead Nets:</strong> ${hull.bulkhead_pneumatic_arrestor_nets || 'STANDBY'}</div>
            <div>&bull; <strong>Electromagnetic Floor Lock:</strong> <span style="color: ${hull.electromagnetic_floor_deck_lock?.includes('100') ? '#34d399' : '#f87171'}; font-weight: 600;">${hull.electromagnetic_floor_deck_lock || 'DISENGAGED'}</span></div>
            <div>&bull; <strong>Damper Override:</strong> ${hull.spin_down_damper_torque_override || 'STANDBY'}</div>
          </div>
        </div>
      </div>
    `;
  }

  // Copy JSON Packet
  if (btnCopyCentrifugeJson && centrifugeJsonBlock) {
    btnCopyCentrifugeJson.addEventListener("click", () => {
      navigator.clipboard.writeText(centrifugeJsonBlock.textContent).then(() => {
        const orig = btnCopyCentrifugeJson.textContent;
        btnCopyCentrifugeJson.textContent = "✓ COPIED!";
        setTimeout(() => { btnCopyCentrifugeJson.textContent = orig; }, 1800);
      });
    });
  }

  // Bind Buttons
  if (btnRunCentrifugeSim) btnRunCentrifugeSim.addEventListener("click", runCentrifugeSimulation);
  if (btnActuateCentrifuge) btnActuateCentrifuge.addEventListener("click", actuateCentrifuge);
  if (btnInjectCentrifuge) btnInjectCentrifuge.addEventListener("click", injectCentrifugeToEngine);
  if (btnResetCentrifuge) btnResetCentrifuge.addEventListener("click", resetCentrifugeNominal);

  // =========================================================================
  // AUTONOMOUS AI FLIGHT SURGEON COPILOT CONTROLLER (DUAL SECTION & POPUP)
  // =========================================================================
  const copilotLauncherBtn = document.getElementById("copilotLauncherBtn");
  const copilotChatWindow = document.getElementById("copilotChatWindow");
  const btnCopilotClose = document.getElementById("btnCopilotClose");
  const btnCopilotClear = document.getElementById("btnCopilotClear");
  const copilotChipsContainer = document.getElementById("copilotChipsContainer");
  const copilotMessages = document.getElementById("copilotMessages");
  const copilotInputForm = document.getElementById("copilotInputForm");
  const copilotInputField = document.getElementById("copilotInputField");
  const copilotSendBtn = document.getElementById("copilotSendBtn");

  // Dedicated Section Elements
  const sectionCopilotMessages = document.getElementById("sectionCopilotMessages");
  const sectionCopilotInputForm = document.getElementById("sectionCopilotInputForm");
  const sectionCopilotInputField = document.getElementById("sectionCopilotInputField");
  const sectionCopilotSendBtn = document.getElementById("sectionCopilotSendBtn");
  const sectionChipsContainer = document.getElementById("sectionChipsContainer");
  const btnSectionClearChat = document.getElementById("btnSectionClearChat");

  function formatCopilotMarkdown(text) {
    if (!text) return "";
    let html = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    // Italic *text*
    html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
    // Code `code`
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Headings
    html = html.replace(/^### (.*$)/gim, "<h4>$1</h4>");
    html = html.replace(/^## (.*$)/gim, "<h3>$1</h3>");
    html = html.replace(/^# (.*$)/gim, "<h3>$1</h3>");

    // Unordered lists
    const lines = html.split("\n");
    let inList = false;
    const processed = [];

    for (let line of lines) {
      const listMatch = line.match(/^[\*\-]\s+(.*)/);
      if (listMatch) {
        if (!inList) {
          processed.push("<ul>");
          inList = true;
        }
        processed.push(`<li>${listMatch[1]}</li>`);
      } else {
        if (inList) {
          processed.push("</ul>");
          inList = false;
        }
        processed.push(line);
      }
    }
    if (inList) processed.push("</ul>");

    html = processed.join("\n");
    html = html.replace(/\n\n+/g, "<br><br>");
    html = html.replace(/\n/g, "<br>");
    return html;
  }

  function updateCopilotTelemetryPreview(state, decision) {
    const s = state || lastKnownState;
    const d = decision || lastKnownDecision;
    if (!s || !d) return;

    const elRisk = document.getElementById("sectionCopilotRiskScore");
    const elRad = document.getElementById("sectionCopilotRadStatus");
    const elVoice = document.getElementById("sectionCopilotVoiceStatus");
    const elCent = document.getElementById("sectionCopilotCentrifugeStatus");

    if (elRisk) {
      const score = (d.risk_score ?? d.composite_risk_score ?? 0).toFixed(2);
      const level = d.risk_level ?? d.overall_risk_level ?? "NOMINAL";
      const color = level === 'CRITICAL' ? '#f87171' : (level === 'ELEVATED' || level === 'HIGH') ? '#f59e0b' : '#34d399';
      elRisk.innerHTML = `<span style="color: ${color}; font-weight: 700;">${score} / 1.00 [${level}]</span>`;
    }

    if (elRad && s.radiation) {
      const r = s.radiation;
      const doseRate = (r.dose_rate_msv_h ?? r.dose_rate_msv_per_hour ?? 0).toFixed(2);
      const cumDose = (r.cumulative_dose_msv ?? r.cumulative_mission_dose_msv ?? 0).toFixed(1);
      elRad.textContent = `${doseRate} mSv/h (Cum: ${cumDose} mSv) • ${r.current_module || 'Nominal'}`;
    }

    if (elVoice && s.voice_vitals) {
      const v = s.voice_vitals;
      const fatigue = ((v.fatigue_score ?? v.fatigue_level ?? 0) * 100).toFixed(0);
      const hypoxia = ((v.hypoxia_indicator ?? v.hypoxia_level ?? 0) * 100).toFixed(0);
      const strain = ((v.cognitive_strain_score ?? v.cognitive_strain ?? 0) * 100).toFixed(0);
      elVoice.textContent = `Fatigue: ${fatigue}% • Hypoxia: ${hypoxia}% • Strain: ${strain}%`;
    }

    if (elCent) {
      elCent.textContent = "Centrifugal Ring 0.38g (Nominal 12.0 RPM • Standby for Despin Drills)";
    }
  }

  function toggleCopilotWindow(show) {
    if (!copilotChatWindow) return;
    const isVisible = copilotChatWindow.style.display !== "none";
    const nextState = show !== undefined ? show : !isVisible;
    copilotChatWindow.style.display = nextState ? "flex" : "none";
    if (nextState) {
      if (copilotInputField) {
        setTimeout(() => copilotInputField.focus(), 100);
      }
      scrollCopilotToBottom();
    }
  }

  function scrollCopilotToBottom() {
    if (copilotMessages) copilotMessages.scrollTop = copilotMessages.scrollHeight;
    if (sectionCopilotMessages) sectionCopilotMessages.scrollTop = sectionCopilotMessages.scrollHeight;
  }

  function appendUserMessage(text) {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const safeText = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    const createBubble = () => {
      const msgDiv = document.createElement("div");
      msgDiv.className = "copilot-msg user-msg";
      msgDiv.innerHTML = `
        <div class="msg-avatar">👤</div>
        <div class="msg-bubble">
          <div class="msg-author">Officer <span class="msg-time">${timeStr}</span></div>
          <div class="msg-content">${safeText}</div>
        </div>
      `;
      return msgDiv;
    };

    if (copilotMessages) copilotMessages.appendChild(createBubble());
    if (sectionCopilotMessages) sectionCopilotMessages.appendChild(createBubble());
    scrollCopilotToBottom();
  }

  function showCopilotTyping() {
    removeCopilotTyping();
    const createIndicator = () => {
      const typingDiv = document.createElement("div");
      typingDiv.className = "copilot-msg bot-msg copilot-typing-wrapper";
      typingDiv.innerHTML = `
        <div class="msg-avatar">🩺</div>
        <div class="msg-bubble">
          <div class="copilot-typing">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
        </div>
      `;
      return typingDiv;
    };

    if (copilotMessages) copilotMessages.appendChild(createIndicator());
    if (sectionCopilotMessages) sectionCopilotMessages.appendChild(createIndicator());
    scrollCopilotToBottom();
  }

  function removeCopilotTyping() {
    document.querySelectorAll(".copilot-typing-wrapper").forEach(el => el.remove());
  }

  function appendBotResponse(data) {
    removeCopilotTyping();
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    let citationsHtml = "";
    if (data.citations && data.citations.length > 0) {
      citationsHtml = `
        <div class="msg-meta">
          ${data.citations.map(c => `<span class="msg-citation-pill">📚 ${c}</span>`).join("")}
        </div>
      `;
    }

    let actionHtml = "";
    if (data.action_triggered) {
      const act = data.action_triggered;
      let label = act.action || "Executed";
      if (act.action === "set_scenario") label = `Scenario Activated: ${act.scenario_id}`;
      else if (act.action === "toggle_blackout") label = `Blackout Status: ${act.new_state ? "ON" : "OFF"}`;
      else if (act.action === "actuate_centrifuge") label = `Centrifuge Interventions Deployed`;
      actionHtml = `
        <div style="margin-top: 0.4rem;">
          <span class="msg-action-badge">⚡ ${label}</span>
        </div>
      `;
    }

    const formattedReply = formatCopilotMarkdown(data.reply || "");
    const createBubble = () => {
      const msgDiv = document.createElement("div");
      msgDiv.className = "copilot-msg bot-msg";
      msgDiv.innerHTML = `
        <div class="msg-avatar">🩺</div>
        <div class="msg-bubble">
          <div class="msg-author">Aegis Flight Surgeon <span class="msg-time">${timeStr}</span></div>
          <div class="msg-content">${formattedReply}</div>
          ${actionHtml}
          ${citationsHtml}
        </div>
      `;
      return msgDiv;
    };

    if (copilotMessages) copilotMessages.appendChild(createBubble());
    if (sectionCopilotMessages) sectionCopilotMessages.appendChild(createBubble());
    scrollCopilotToBottom();
  }

  async function handleCopilotQuery(query) {
    if (!query || !query.trim()) return;
    const prompt = query.trim();
    appendUserMessage(prompt);

    if (copilotInputField) copilotInputField.value = "";
    if (sectionCopilotInputField) sectionCopilotInputField.value = "";
    if (copilotSendBtn) copilotSendBtn.disabled = true;
    if (sectionCopilotSendBtn) sectionCopilotSendBtn.disabled = true;

    showCopilotTyping();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: prompt })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      appendBotResponse(data);

      // Handle triggered action on the UI
      if (data.action_triggered) {
        const act = data.action_triggered;
        if (act.action === "set_scenario" && act.scenario_id) {
          await loadScenario(act.scenario_id);
        } else if (act.action === "toggle_blackout") {
          await toggleCommsMode();
        } else if (act.action === "actuate_centrifuge") {
          await actuateCentrifuge();
        }
      }
    } catch (err) {
      console.warn("Copilot fetch failed, engaging client-side offline telemetry fallback:", err);
      removeCopilotTyping();
      
      // Synthesize client-side offline flight surgeon response using loaded habitat telemetry
      const riskScore = currentDecision ? currentDecision.risk_score.toFixed(2) : "0.10";
      const riskLvl = currentDecision ? currentDecision.risk_level : "LOW";
      const rec = currentDecision ? currentDecision.recommended_action : "Maintain routine passive flight monitoring cycle.";
      const radDose = currentState && currentState.radiation ? `${currentState.radiation.dose_rate_msv_h.toFixed(2)} mSv/h` : "0.02 mSv/h";
      const voiceFatigue = currentState && currentState.voice_vitals ? currentState.voice_vitals.fatigue_score.toFixed(2) : "0.10";

      const fallbackData = {
        reply: `**Autonomous AI Flight Surgeon (Edge Offline Telemetry Mode):**\n\n` +
               `Your query *"${prompt}"* has been evaluated locally on habitat edge hardware:\n\n` +
               `- **Mission Risk Score:** \`${riskScore} / 1.00\` (**${riskLvl}**)\n` +
               `- **Radiation Rate:** \`${radDose}\` | **Voice Strain:** \`${voiceFatigue}\`\n` +
               `- **Clinical Directive:** ${rec}\n\n` +
               `*Edge telemetry bus active. Full four-pillar multimodal monitoring operational.*`,
        intent: "CLIENT_OFFLINE_TELEMETRY",
        citations: ["NASA-STD-3001 Space Flight Human-System Standards (Offline Cache)"],
        suggested_prompts: [
          "Check current mission risk",
          "What are NASA radiation limits?",
          "Simulate Centrifugal Despin Shock"
        ]
      };
      appendBotResponse(fallbackData);
      scrollCopilotToBottom();
    } finally {
      if (copilotSendBtn) copilotSendBtn.disabled = false;
      if (sectionCopilotSendBtn) sectionCopilotSendBtn.disabled = false;
    }
  }

  function resetCopilotMessages() {
    const welcomeHtml = `
      <div class="copilot-msg bot-msg">
        <div class="msg-avatar">🩺</div>
        <div class="msg-bubble">
          <div class="msg-author">Aegis Flight Surgeon <span class="msg-time">Reset</span></div>
          <div class="msg-content">Session cleared. Ready for flight telemetry queries or clinical directives.</div>
        </div>
      </div>
    `;
    if (copilotMessages) copilotMessages.innerHTML = welcomeHtml;
    if (sectionCopilotMessages) sectionCopilotMessages.innerHTML = welcomeHtml;
  }

  // Floating Launcher Events
  if (copilotLauncherBtn) {
    copilotLauncherBtn.addEventListener("click", () => toggleCopilotWindow());
  }
  if (btnCopilotClose) {
    btnCopilotClose.addEventListener("click", () => toggleCopilotWindow(false));
  }
  if (btnCopilotClear) {
    btnCopilotClear.addEventListener("click", resetCopilotMessages);
  }
  if (btnSectionClearChat) {
    btnSectionClearChat.addEventListener("click", resetCopilotMessages);
  }

  if (copilotChipsContainer) {
    copilotChipsContainer.addEventListener("click", (e) => {
      const chip = e.target.closest(".copilot-chip");
      if (chip && chip.dataset.prompt) handleCopilotQuery(chip.dataset.prompt);
    });
  }
  if (sectionChipsContainer) {
    sectionChipsContainer.addEventListener("click", (e) => {
      const chip = e.target.closest(".copilot-chip");
      if (chip && chip.dataset.prompt) handleCopilotQuery(chip.dataset.prompt);
    });
  }

  // Global Send Dispatchers
  window.sendCopilotSectionMessage = function() {
    const field = document.getElementById("sectionCopilotInputField");
    if (!field) return;
    const val = field.value;
    if (val && val.trim()) {
      field.style.height = "auto";
      handleCopilotQuery(val.trim());
    } else {
      field.focus();
      field.placeholder = "Please enter your question or flight query...";
      const card = field.closest(".gemini-prompt-card");
      if (card) {
        card.style.boxShadow = "0 0 25px rgba(56, 189, 248, 0.6)";
        setTimeout(() => { card.style.boxShadow = ""; }, 800);
      }
    }
  };

  window.sendCopilotFloatingMessage = function() {
    const field = document.getElementById("copilotInputField");
    if (!field) return;
    const val = field.value;
    if (val && val.trim()) {
      handleCopilotQuery(val.trim());
    } else {
      field.focus();
    }
  };

  // Textarea auto-resize and Enter keydown handler (Gemini style)
  if (sectionCopilotInputField) {
    sectionCopilotInputField.addEventListener("input", () => {
      sectionCopilotInputField.style.height = "auto";
      sectionCopilotInputField.style.height = Math.min(sectionCopilotInputField.scrollHeight, 160) + "px";
    });

    sectionCopilotInputField.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        e.stopPropagation();
        window.sendCopilotSectionMessage();
      }
    });
  }

  // Floating input Enter keydown handler
  if (copilotInputField) {
    copilotInputField.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        e.stopPropagation();
        window.sendCopilotFloatingMessage();
      }
    });
  }

  // Direct Click Listeners on Gemini Send Buttons
  if (sectionCopilotSendBtn) {
    sectionCopilotSendBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      window.sendCopilotSectionMessage();
    });
  }

  if (copilotSendBtn) {
    copilotSendBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      window.sendCopilotFloatingMessage();
    });
  }

  // Handle click on hint chips inside Gemini prompt card
  document.addEventListener("click", (e) => {
    const hint = e.target.closest(".gemini-hint-chip");
    if (hint && hint.dataset.fill) {
      const prompt = hint.dataset.fill;
      const field = document.getElementById("sectionCopilotInputField");
      if (field) {
        field.value = prompt;
        field.style.height = "auto";
        field.style.height = Math.min(field.scrollHeight, 160) + "px";
      }
      handleCopilotQuery(prompt);
    }
  });

  // Backup Form Submit Interceptors
  if (copilotInputForm) {
    copilotInputForm.addEventListener("submit", (e) => {
      e.preventDefault();
      e.stopPropagation();
      window.sendCopilotFloatingMessage();
      return false;
    });
  }
  if (sectionCopilotInputForm) {
    sectionCopilotInputForm.addEventListener("submit", (e) => {
      e.preventDefault();
      e.stopPropagation();
      window.sendCopilotSectionMessage();
      return false;
    });
  }

  // ===================================================================
  // NASA-STD-3001 MEDICAL EVENT DOSSIER (MED-B) MODAL CONTROLLER
  // ===================================================================
  const openMedBriefBtn = document.getElementById("openMedBriefBtn");
  const closeMedBriefBtn = document.getElementById("closeMedBriefBtn");
  const nasaMedBriefModal = document.getElementById("nasaMedBriefModal");
  const copyDossierBtn = document.getElementById("copyDossierBtn");
  const printDossierBtn = document.getElementById("printDossierBtn");
  let currentDossierMarkdown = "";

  async function loadAndShowMedBrief() {
    if (!nasaMedBriefModal) return;
    nasaMedBriefModal.style.display = "flex";
    const docText = document.getElementById("medBriefDocText");
    if (docText) docText.textContent = "Synthesizing certified NASA Flight Surgeon Medical Event Dossier...";

    try {
      const [dossierRes, mdRes] = await Promise.all([
        fetch("/api/mission/dossier"),
        fetch("/api/mission/dossier/markdown")
      ]);
      const dossier = await dossierRes.json();
      const mdData = await mdRes.json();
      currentDossierMarkdown = mdData.markdown || "";

      // Populate meta strip
      const idEl = document.getElementById("dossierIdVal");
      if (idEl) idEl.textContent = dossier.dossier_id;
      const metEl = document.getElementById("dossierMetVal");
      if (metEl) metEl.textContent = dossier.mission_elapsed_time;
      const commsEl = document.getElementById("dossierCommsVal");
      if (commsEl) commsEl.textContent = dossier.comms_status;
      const chkEl = document.getElementById("dossierChecksumVal");
      if (chkEl) chkEl.textContent = dossier.telemetry_checksum_sha256;

      // Populate highlight chips
      const riskEl = document.getElementById("briefChipRiskVal");
      if (riskEl) {
        riskEl.textContent = `${dossier.risk_level} (${dossier.risk_score.toFixed(2)})`;
        const chipRisk = document.getElementById("chipRisk");
        if (chipRisk) {
          chipRisk.className = `brief-chip risk-${dossier.risk_level.toLowerCase()}`;
        }
      }
      const radEl = document.getElementById("briefChipRadVal");
      if (radEl) radEl.textContent = `${dossier.pillar1_environmental.dose_rate_msv_h} mSv/h`;
      const voiceEl = document.getElementById("briefChipVoiceVal");
      if (voiceEl) voiceEl.textContent = `${dossier.pillar2_neuro_vocal.baseline_drift_sigma} σ`;
      const twinEl = document.getElementById("briefChipTwinVal");
      if (twinEl) twinEl.textContent = `${dossier.pillar3_musculoskeletal.exercise_deficit_days}d Deficit`;
      const gravEl = document.getElementById("briefChipGravVal");
      if (gravEl) {
        gravEl.textContent = dossier.centrifuge_dynamics 
          ? dossier.centrifuge_dynamics.gravity_transition 
          : "0.38g (Mars AG)";
      }

      const dsnEl = document.getElementById("dossierDsnStatus");
      if (dsnEl) dsnEl.textContent = dossier.dsn_dispatch_status;

      if (docText) {
        docText.textContent = currentDossierMarkdown;
      }
    } catch (err) {
      console.error("Failed to load medical dossier:", err);
      if (docText) docText.textContent = "Error loading medical dossier from server.";
    }
  }

  window.openMedBriefModal = loadAndShowMedBrief;

  if (openMedBriefBtn) {
    openMedBriefBtn.addEventListener("click", (e) => {
      e.preventDefault();
      loadAndShowMedBrief();
    });
  }

  if (closeMedBriefBtn) {
    closeMedBriefBtn.addEventListener("click", () => {
      if (nasaMedBriefModal) nasaMedBriefModal.style.display = "none";
    });
  }

  if (nasaMedBriefModal) {
    nasaMedBriefModal.addEventListener("click", (e) => {
      if (e.target === nasaMedBriefModal) {
        nasaMedBriefModal.style.display = "none";
      }
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && nasaMedBriefModal && nasaMedBriefModal.style.display === "flex") {
      nasaMedBriefModal.style.display = "none";
    }
  });

  if (copyDossierBtn) {
    copyDossierBtn.addEventListener("click", async () => {
      if (!currentDossierMarkdown) return;
      try {
        await navigator.clipboard.writeText(currentDossierMarkdown);
        const originalText = copyDossierBtn.innerHTML;
        copyDossierBtn.innerHTML = "✓ Copied to Clipboard!";
        copyDossierBtn.style.borderColor = "var(--accent-green)";
        copyDossierBtn.style.color = "var(--accent-green)";
        setTimeout(() => {
          copyDossierBtn.innerHTML = originalText;
          copyDossierBtn.style.borderColor = "";
          copyDossierBtn.style.color = "";
        }, 2200);
      } catch (err) {
        console.error("Clipboard copy error:", err);
      }
    });
  }

  if (printDossierBtn) {
    printDossierBtn.addEventListener("click", () => {
      window.print();
    });
  }

  // System Info Modal Handlers
  const aegisSystemInfoModal = document.getElementById("aegisSystemInfoModal");
  const openSystemInfoBtn = document.getElementById("openSystemInfoBtn");
  const closeSystemInfoBtn = document.getElementById("closeSystemInfoBtn");
  const closeSystemInfoFooterBtn = document.getElementById("closeSystemInfoFooterBtn");
  const sidebarInfoBtn = document.getElementById("sidebarInfoBtn");
  const sysInfoOpenEngineBtn = document.getElementById("sysInfoOpenEngineBtn");
  const sysInfoOpenCopilotBtn = document.getElementById("sysInfoOpenCopilotBtn");

  function showSystemInfoModal(e) {
    if (e && e.preventDefault) e.preventDefault();
    if (aegisSystemInfoModal) {
      aegisSystemInfoModal.style.display = "flex";
    }
  }

  function hideSystemInfoModal() {
    if (aegisSystemInfoModal) {
      aegisSystemInfoModal.style.display = "none";
    }
  }

  window.openSystemInfoModal = showSystemInfoModal;
  window.closeSystemInfoModal = hideSystemInfoModal;

  if (openSystemInfoBtn) openSystemInfoBtn.addEventListener("click", showSystemInfoModal);
  if (sidebarInfoBtn) sidebarInfoBtn.addEventListener("click", showSystemInfoModal);
  if (closeSystemInfoBtn) closeSystemInfoBtn.addEventListener("click", hideSystemInfoModal);
  if (closeSystemInfoFooterBtn) closeSystemInfoFooterBtn.addEventListener("click", hideSystemInfoModal);

  if (aegisSystemInfoModal) {
    aegisSystemInfoModal.addEventListener("click", (e) => {
      if (e.target === aegisSystemInfoModal) {
        hideSystemInfoModal();
      }
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (aegisSystemInfoModal && aegisSystemInfoModal.style.display === "flex") {
        hideSystemInfoModal();
      }
    }
  });

  if (sysInfoOpenEngineBtn) {
    sysInfoOpenEngineBtn.addEventListener("click", () => {
      hideSystemInfoModal();
      switchTab("tab-pillar4");
    });
  }

  if (sysInfoOpenCopilotBtn) {
    sysInfoOpenCopilotBtn.addEventListener("click", () => {
      hideSystemInfoModal();
      switchTab("tab-copilot");
    });
  }

  // ===================================================================
  // FEATURE 3: ASYMMETRIC FEDERATED SYNC WITH HOUSTON GROUND CONTROL
  // ===================================================================

  async function fetchSyncStatusAndTimeline() {
    try {
      const [statusRes, groundEventsRes, queueRes, modelsRes, logsRes] = await Promise.all([
        fetch("/api/sync/status").then(r => r.json()),
        fetch("/api/sync/ground/events").then(r => r.json()).catch(() => ({ events: [] })),
        fetch("/api/sync/queue/pending").then(r => r.json()).catch(() => ({ health_events: [], telemetry_summaries: [], model_updates: [] })),
        fetch("/api/sync/ground/models").then(r => r.json()).catch(() => ({ latest_model: null, history: [] })),
        fetch("/api/sync/logs").then(r => r.json()).catch(() => ({ logs: [], state_history: [] }))
      ]);

      renderSyncStatus(statusRes);
      renderSyncTimeline(groundEventsRes.events || [], queueRes.health_events || []);
      renderFederatedModels(modelsRes, queueRes.model_updates || []);
      renderSyncLogs(logsRes.logs || []);
    } catch (err) {
      console.error("Failed to fetch sync status:", err);
    }
  }

  function renderSyncStatus(status) {
    if (!status) return;
    const isOnline = status.comms_state === "ONLINE";
    const isSyncing = status.comms_state === "SYNCING";

    const headerBadge = document.getElementById("syncHeaderBadge");
    const headerDot = document.getElementById("syncHeaderDot");
    const headerText = document.getElementById("syncHeaderStatusText");
    const sidebarBadge = document.getElementById("sidebarSyncBadge");
    const quickToggleBtn = document.getElementById("syncQuickToggleBtn");
    const actionToggleBtn = document.getElementById("syncToggleCommsActionBtn");

    if (headerBadge && headerDot && headerText) {
      if (isSyncing) {
        headerBadge.style.background = "rgba(56, 189, 248, 0.15)";
        headerBadge.style.borderColor = "rgba(56, 189, 248, 0.4)";
        headerDot.className = "status-dot";
        headerDot.style.background = "#38bdf8";
        headerText.textContent = "SYNCING [BURST DOWNLINK ACTIVE]";
        headerText.style.color = "#38bdf8";
      } else if (isOnline) {
        headerBadge.style.background = "rgba(16, 185, 129, 0.12)";
        headerBadge.style.borderColor = "rgba(16, 185, 129, 0.35)";
        headerDot.className = "status-dot online";
        headerDot.style.background = "#10b981";
        headerText.textContent = "ONLINE [EARTH LINK ACTIVE]";
        headerText.style.color = "#10b981";
      } else {
        headerBadge.style.background = "rgba(245, 158, 11, 0.15)";
        headerBadge.style.borderColor = "rgba(245, 158, 11, 0.4)";
        headerDot.className = "status-dot offline";
        headerDot.style.background = "#f59e0b";
        headerText.textContent = "OFFLINE [20-MIN BLACKOUT]";
        headerText.style.color = "#fbbf24";
      }
    }

    if (sidebarBadge) {
      sidebarBadge.textContent = status.comms_state;
      sidebarBadge.style.background = isOnline ? "rgba(16, 185, 129, 0.2)" : (isSyncing ? "rgba(56, 189, 248, 0.2)" : "rgba(245, 158, 11, 0.2)");
      sidebarBadge.style.color = isOnline ? "#10b981" : (isSyncing ? "#38bdf8" : "#fbbf24");
    }

    if (quickToggleBtn) {
      quickToggleBtn.textContent = isOnline ? "⚡ Disconnect Link" : "⚡ Restore Link";
    }
    if (actionToggleBtn) {
      actionToggleBtn.textContent = isOnline ? "⚡ Disconnect Link (Simulate Blackout)" : "⚡ Restore Earth Link (Trigger Downlink)";
    }

    // Critical Unsynced Banner
    const critBanner = document.getElementById("unsyncedCriticalAlertBanner");
    const critCountSpan = document.getElementById("unsyncedCritCountText");
    if (critBanner) {
      if (status.unsynchronized_critical_count > 0 && !isOnline) {
        critBanner.style.display = "flex";
        if (critCountSpan) critCountSpan.textContent = status.unsynchronized_critical_count;
      } else {
        critBanner.style.display = "none";
      }
    }

    // Metric Cards
    const elCardLinkState = document.getElementById("syncCardLinkState");
    const elCardPendingEvents = document.getElementById("syncCardPendingEvents");
    const elCardPendingSummaries = document.getElementById("syncCardPendingSummaries");
    const elCardPendingModels = document.getElementById("syncCardPendingModels");
    const elCardSyncedTotal = document.getElementById("syncCardSyncedTotal");
    const elCardModelVersion = document.getElementById("syncCardModelVersion");
    const elCardCriticalPill = document.getElementById("syncCardCriticalPill");
    const elCardNominalPill = document.getElementById("syncCardNominalPill");

    if (elCardLinkState) {
      elCardLinkState.textContent = status.comms_state;
      elCardLinkState.style.color = isOnline ? "#10b981" : (isSyncing ? "#38bdf8" : "#fbbf24");
    }
    if (elCardPendingEvents) elCardPendingEvents.textContent = status.pending_health_events;
    if (elCardPendingSummaries) elCardPendingSummaries.textContent = status.pending_telemetry_summaries;
    if (elCardPendingModels) elCardPendingModels.textContent = status.pending_model_updates;
    if (elCardSyncedTotal) elCardSyncedTotal.textContent = status.synced_records_total;
    if (elCardModelVersion) elCardModelVersion.textContent = status.local_model_version;

    if (elCardCriticalPill && elCardNominalPill) {
      if (status.unsynchronized_critical_count > 0) {
        elCardCriticalPill.style.display = "inline";
        elCardCriticalPill.textContent = `${status.unsynchronized_critical_count} CRITICAL`;
        elCardNominalPill.style.display = "none";
      } else {
        elCardCriticalPill.style.display = "none";
        elCardNominalPill.style.display = "inline";
      }
    }

    const lastTimeSpan = document.getElementById("syncCardLastTime");
    if (lastTimeSpan && status.last_successful_sync_utc) {
      try {
        const d = new Date(status.last_successful_sync_utc);
        lastTimeSpan.textContent = d.toLocaleTimeString();
      } catch (_) {
        lastTimeSpan.textContent = status.last_successful_sync_utc;
      }
    }
  }

  function renderSyncTimeline(groundEvents, pendingEvents) {
    const tbody = document.getElementById("syncEventsTableBody");
    if (!tbody) return;

    const all = [];

    (groundEvents || []).forEach(e => {
      all.push({
        ...e,
        is_ground: true,
        status: "SYNCED"
      });
    });

    (pendingEvents || []).forEach(e => {
      if (!all.some(item => item.event_id === e.event_id)) {
        all.push({
          ...e,
          is_ground: false,
          status: e.sync_status || "PENDING"
        });
      }
    });

    if (all.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-dim);">No events registered in persistent queue. Click <strong>1-Click E2E Mission Demo</strong> to run simulation.</td></tr>`;
      return;
    }

    all.sort((a, b) => new Date(b.occurrence_utc) - new Date(a.occurrence_utc));

    tbody.innerHTML = all.map(ev => {
      let sevBg = "rgba(100, 116, 139, 0.2)";
      let sevCol = "#94a3b8";
      if (ev.severity === "CRITICAL") {
        sevBg = "rgba(239, 68, 68, 0.2)";
        sevCol = "#f87171";
      } else if (ev.severity === "HIGH") {
        sevBg = "rgba(245, 158, 11, 0.2)";
        sevCol = "#fbbf24";
      } else if (ev.severity === "MEDIUM") {
        sevBg = "rgba(59, 130, 246, 0.2)";
        sevCol = "#60a5fa";
      }

      let latencyStr = "Buffered Offline";
      if (ev.ground_received_utc) {
        const diffMs = Math.max(0, new Date(ev.ground_received_utc) - new Date(ev.occurrence_utc));
        const diffSec = Math.round(diffMs / 1000);
        if (diffSec < 60) {
          latencyStr = `+${diffSec}s [Live Link]`;
        } else {
          const m = Math.floor(diffSec / 60);
          const s = diffSec % 60;
          latencyStr = `+${m}m ${s}s [Delayed Downlink]`;
        }
      }

      const occurFormatted = ev.occurrence_utc ? new Date(ev.occurrence_utc).toISOString().replace("T", " ").substring(11, 19) + " UTC" : "--";
      const recvFormatted = ev.ground_received_utc ? new Date(ev.ground_received_utc).toISOString().replace("T", " ").substring(11, 19) + " UTC" : "<span style='color:#f59e0b;'>In Transit</span>";

      const statusBadge = ev.status === "SYNCED" 
        ? `<span style="background: rgba(16, 185, 129, 0.15); color: #34d399; padding: 0.15rem 0.4rem; border-radius: 4px; font-weight: 700; font-size: 0.68rem;">SYNCED</span>`
        : `<span style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; padding: 0.15rem 0.4rem; border-radius: 4px; font-weight: 700; font-size: 0.68rem;">PENDING</span>`;

      return `
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.06);">
          <td style="padding: 0.55rem 0.6rem; font-family: var(--font-mono); font-size: 0.72rem; color: #38bdf8;">${ev.event_id}</td>
          <td style="padding: 0.55rem 0.6rem;">
            <span style="background: ${sevBg}; color: ${sevCol}; padding: 0.15rem 0.45rem; border-radius: 4px; font-weight: 700; font-size: 0.68rem;">${ev.severity}</span>
          </td>
          <td style="padding: 0.55rem 0.6rem; color: #cbd5e1; max-width: 140px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${ev.source_pillar || ''}">${ev.source_pillar || 'Multi-Signal'}</td>
          <td style="padding: 0.55rem 0.6rem; font-family: var(--font-mono); font-size: 0.72rem; color: #94a3b8;">${occurFormatted}</td>
          <td style="padding: 0.55rem 0.6rem; font-family: var(--font-mono); font-size: 0.72rem;">${recvFormatted}</td>
          <td style="padding: 0.55rem 0.6rem; font-size: 0.7rem; color: ${ev.ground_received_utc ? '#38bdf8' : '#f59e0b'}; font-weight: 600;">${latencyStr}</td>
          <td style="padding: 0.55rem 0.6rem;">${statusBadge}</td>
          <td style="padding: 0.55rem 0.6rem;">
            <button class="btn btn-xs btn-outline" style="font-size: 0.68rem; padding: 0.15rem 0.45rem; border-color: rgba(245, 158, 11, 0.4); color: #fbbf24; cursor: pointer;" onclick="window.inspectEventShap('${ev.event_id}')">🔬 Explain</button>
          </td>
        </tr>
      `;
    }).join("");

  }

  function renderFederatedModels(modelsData, pendingUpdates) {
    const latest = modelsData.latest_model;
    const flGroundActiveVer = document.getElementById("flGroundActiveVer");
    const flGroundTotalSamples = document.getElementById("flGroundTotalSamples");
    const flAggregationStatusBadge = document.getElementById("flAggregationStatusBadge");
    const syncCardModelRound = document.getElementById("syncCardModelRound");

    if (latest) {
      if (flGroundActiveVer) flGroundActiveVer.textContent = latest.version;
      if (flGroundTotalSamples) flGroundTotalSamples.textContent = `${latest.total_samples_trained} samples across rounds`;
      if (syncCardModelRound) syncCardModelRound.textContent = `${latest.round} (${latest.num_participating_clients} clients)`;
      if (flAggregationStatusBadge) {
        flAggregationStatusBadge.textContent = latest.round > 0 ? `ROUND ${latest.round} AGGREGATED` : "READY";
      }
    }

    const c1Update = (pendingUpdates || []).find(u => u.client_id === "HERMES-EDGE-01");
    const c2Update = (pendingUpdates || []).find(u => u.client_id === "HERMES-EDGE-02");

    const elC1Samples = document.getElementById("flClient1Samples");
    const elC1Loss = document.getElementById("flClient1Loss");
    const elC1Deltas = document.getElementById("flClient1Deltas");

    if (c1Update) {
      if (elC1Samples) elC1Samples.textContent = c1Update.num_samples;
      if (elC1Loss) elC1Loss.textContent = c1Update.loss;
      if (elC1Deltas) elC1Deltas.textContent = `Δrad: ${c1Update.weights_delta.w_rad || 0}, Δfat: ${c1Update.weights_delta.w_fatigue || 0}`;
    }

    const elC2Samples = document.getElementById("flClient2Samples");
    const elC2Loss = document.getElementById("flClient2Loss");
    const elC2Deltas = document.getElementById("flClient2Deltas");

    if (c2Update) {
      if (elC2Samples) elC2Samples.textContent = c2Update.num_samples;
      if (elC2Loss) elC2Loss.textContent = c2Update.loss;
      if (elC2Deltas) elC2Deltas.textContent = `Δstr: ${c2Update.weights_delta.w_strain || 0}, Δhyp: ${c2Update.weights_delta.w_hypoxia || 0}`;
    }
  }

  function renderSyncLogs(logs) {
    const container = document.getElementById("syncActivityLogContainer");
    if (!container) return;
    if (!logs || logs.length === 0) {
      container.innerHTML = `<div style="color: var(--text-dim); text-align: center; padding: 1rem;">No recent sync activity logged.</div>`;
      return;
    }

    container.innerHTML = logs.map(l => {
      let col = "#94a3b8";
      if (l.status === "SUCCESS") col = "#34d399";
      else if (l.status === "WARNING") col = "#fbbf24";
      else if (l.status === "ERROR") col = "#f87171";

      const timeStr = l.timestamp_utc ? new Date(l.timestamp_utc).toLocaleTimeString() : "";
      return `
        <div style="margin-bottom: 0.35rem; display: flex; gap: 0.5rem;">
          <span style="color: var(--text-dim); min-width: 65px;">[${timeStr}]</span>
          <span style="color: ${col}; font-weight: 700; min-width: 130px;">${l.action}:</span>
          <span style="color: #cbd5e1;">${l.details}</span>
        </div>
      `;
    }).join("");
  }

  window.toggleSyncCommsState = async function() {
    try {
      await fetch("/api/sync/comms/toggle", { method: "POST" });
      await fetchSyncStatusAndTimeline();
      fetchInitialState();
    } catch (err) {
      console.error("Error toggling comms state:", err);
    }
  };

  window.triggerStoreForwardSync = async function() {
    try {
      const btn = document.getElementById("syncForceUploadBtn");
      if (btn) btn.textContent = "⏳ Transmitting DSN Burst...";
      await fetch("/api/sync/trigger", { method: "POST" });
      await fetchSyncStatusAndTimeline();
      if (btn) btn.textContent = "📤 Flush Pending Queue to Houston";
    } catch (err) {
      console.error("Error triggering sync:", err);
    }
  };

  window.triggerLocalEdgeTraining = async function() {
    try {
      const btn = document.getElementById("syncTrainEdgeBtn");
      if (btn) btn.textContent = "⏳ Computing Edge Gradients...";
      await fetch("/api/sync/federated/train", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ client_target: "both", num_samples_client1: 45, num_samples_client2: 38 })
      });
      await fetchSyncStatusAndTimeline();
      if (btn) btn.textContent = "🧪 Train Onboard Edge Models (Watney & Vogel)";
    } catch (err) {
      console.error("Error training edge models:", err);
    }
  };

  window.simulateTransientDrop = async function() {
    const btn = document.getElementById("syncSimulateDropBtn");
    if (btn) btn.textContent = "⏳ Inducing Carrier Drop...";

    // 1. Immediately update the dashboard's Earth Link Status to OFFLINE without waiting
    renderSyncStatus({
      comms_state: "OFFLINE",
      unsynchronized_critical_count: parseInt(document.getElementById("syncCardPendingEvents")?.textContent || "0"),
      pending_health_events: parseInt(document.getElementById("syncCardPendingEvents")?.textContent || "0"),
      pending_telemetry_summaries: parseInt(document.getElementById("syncCardPendingSummaries")?.textContent || "0"),
      pending_model_updates: parseInt(document.getElementById("syncCardPendingModels")?.textContent || "0"),
      synced_records_total: parseInt(document.getElementById("syncCardSyncedTotal")?.textContent || "0"),
      local_model_version: document.getElementById("syncCardModelVersion")?.textContent || "v1.0.0"
    });

    const notice = document.getElementById("syncHeaderStatusText");
    if (notice) {
      notice.textContent = "OFFLINE [DSN LINK LOST - ONBOARD MONITORING ACTIVE]";
      notice.style.color = "#fbbf24";
    }

    try {
      // 2. Call backend endpoint to simulate DSN drop
      await fetch("/api/sync/comms/drop", { method: "POST" });
      await fetchSyncStatusAndTimeline();
      fetchInitialState();
    } catch (err) {
      console.error("Error inducing DSN drop:", err);
    } finally {
      if (btn) btn.textContent = "💥 Simulate DSN Drop (Retry Backoff)";
    }
  };

  window.runSyncE2EDemonstration = async function() {
    const card = document.getElementById("syncDemoConsoleCard");
    const container = document.getElementById("syncDemoStepContainer");
    const btn = document.getElementById("syncRunDemoBtn");
    if (card) card.style.display = "block";
    if (container) {
      container.innerHTML = `<div style="color: #38bdf8;">⏳ Executing 12-Step Interplanetary Health Mission Scenario...</div>`;
    }
    if (btn) btn.disabled = true;

    try {
      const res = await fetch("/api/sync/demo/run", { method: "POST" });
      const data = await res.json();

      if (container) {
        container.innerHTML = `
          <div style="color: #34d399; font-weight: 700; margin-bottom: 0.4rem;">✓ DEMONSTRATION WORKFLOW EXECUTED SUCCESSFULLY</div>
          <div style="color: #cbd5e1;">• Step 1-3: Nominal Baseline established under ONLINE link.</div>
          <div style="color: #f59e0b;">• Step 4: Disconnected link &bull; 20-min Mars Communication Blackout initiated.</div>
          <div style="color: #f87171;">• Step 5-6: Offline Health Events registered (Critical SPE storm + Acoustic Hypoxia marker).</div>
          <div style="color: #c084fc;">• Step 7: Onboard Federated Models trained locally by CDR Watney & Dr. Vogel (${data.offline_queued_models} updates queued).</div>
          <div style="color: #e2e8f0;">• Step 8: Earth link restored via Mars Relay Orbiter &bull; Auto-Sync triggered.</div>
          <div style="color: #38bdf8;">• Step 9: Houston Ground Control received ${data.ground_events_count} events with verifiable SHA-256 telemetry checksums.</div>
          <div style="color: #34d399;">• Step 10: Retried sync idempotency verified (0 duplicates generated; duplicate check passed).</div>
          <div style="color: #38bdf8;">• Step 11: Ground FedAvg aggregation completed &bull; Global Model version promoted to <strong style="color:#34d399;">${data.latest_global_model ? data.latest_global_model.version : 'v1.1.0'}</strong>.</div>
        `;
      }
      await fetchSyncStatusAndTimeline();
      fetchInitialState();
    } catch (err) {
      if (container) container.innerHTML = `<div style="color: #f87171;">Error executing demo: ${err.message}</div>`;
    } finally {
      if (btn) btn.disabled = false;
    }
  };

  window.resetSyncDemo = async function() {
    try {
      await fetch("/api/sync/demo/reset", { method: "POST" });
      const card = document.getElementById("syncDemoConsoleCard");
      if (card) card.style.display = "none";
      await fetchSyncStatusAndTimeline();
      fetchInitialState();
    } catch (err) {
      console.error("Error resetting demo:", err);
    }
  };

  window.refreshSyncTimeline = function() {
    fetchSyncStatusAndTimeline();
  };

  // ===================================================================
  // FEATURE B: EXPLAINABLE AI (SHAP) FRONTEND ENGINE
  // ===================================================================

  function renderShapExplanation(data) {
    if (!data) return;

    // Badges & Meta
    const idBadge = document.getElementById("xaiAlertIdBadge");
    const sevBadge = document.getElementById("xaiSeverityBadge");
    const modelBadge = document.getElementById("xaiModelBadge");
    const timeText = document.getElementById("xaiOccurrenceTimeText");
    const statusPill = document.getElementById("xaiStatusPill");

    if (idBadge) idBadge.textContent = `ALERT: ${data.alert_id || "CURRENT"}`;
    if (sevBadge) {
      sevBadge.textContent = `${data.severity_category || "UNKNOWN"} ANOMALY`;
      if (data.severity_category === "CRITICAL") {
        sevBadge.style.background = "rgba(239, 68, 68, 0.2)";
        sevBadge.style.color = "#f87171";
      } else if (data.severity_category === "HIGH") {
        sevBadge.style.background = "rgba(245, 158, 11, 0.2)";
        sevBadge.style.color = "#fbbf24";
      } else if (data.severity_category === "MEDIUM") {
        sevBadge.style.background = "rgba(59, 130, 246, 0.2)";
        sevBadge.style.color = "#60a5fa";
      } else {
        sevBadge.style.background = "rgba(16, 185, 129, 0.2)";
        sevBadge.style.color = "#34d399";
      }
    }

    if (modelBadge) modelBadge.textContent = `Model: ${data.model_name || "Multimodal Anomaly"} ${data.model_version || "v1.0.0"}`;
    if (timeText) {
      const dt = data.created_utc ? new Date(data.created_utc).toISOString().replace("T", " ").substring(0, 19) + " UTC" : "Live Edge Inference";
      timeText.textContent = `Generated: ${dt} • Origin: Autonomous Spacecraft Edge [${data.explainer_type || "Exact Shapley"}]`;
    }
    if (statusPill) {
      statusPill.textContent = data.status || "AVAILABLE";
      statusPill.style.color = data.status === "EXPLANATION_UNAVAILABLE" ? "#f87171" : "#34d399";
      statusPill.style.background = data.status === "EXPLANATION_UNAVAILABLE" ? "rgba(239, 68, 68, 0.15)" : "rgba(16, 185, 129, 0.15)";
    }

    // Metric numbers
    const scoreVal = document.getElementById("xaiPredictedScoreVal");
    const baseVal = document.getElementById("xaiBaseValueVal");
    const ruleText = document.getElementById("xaiClassificationRuleText");
    const effText = document.getElementById("xaiEfficiencyDetailText");

    if (scoreVal) scoreVal.textContent = (data.predicted_score !== undefined) ? data.predicted_score.toFixed(3) : "--";
    if (baseVal) baseVal.textContent = (data.base_value !== undefined) ? data.base_value.toFixed(3) : "--";
    if (ruleText) ruleText.textContent = data.classification_rule || "Configured mission threshold";
    if (effText) {
      const err = data.efficiency_error !== undefined ? data.efficiency_error.toFixed(4) : "0.0000";
      effText.textContent = `Error: ±${err} (Exact Shapley additivity verified)`;
    }

    // Narrative & Limitations
    const narrText = document.getElementById("xaiNarrativeText");
    const limitText = document.getElementById("xaiLimitationsText");
    if (narrText && data.plain_language_narrative) narrText.textContent = data.plain_language_narrative;
    if (limitText && data.limitations_disclaimer) limitText.textContent = data.limitations_disclaimer;

    // Render Bidirectional Waterfall / Bar Chart
    const chartContainer = document.getElementById("xaiWaterfallContainer");
    if (chartContainer && data.contributions && data.contributions.length > 0) {
      const maxAttribution = Math.max(0.2, ...data.contributions.map(c => Math.abs(c.attribution)));

      chartContainer.innerHTML = `
        <div style="display: grid; grid-template-columns: 200px 1fr 110px; gap: 0.75rem; padding-bottom: 0.5rem; margin-bottom: 0.6rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700;">
          <div>Feature (Observed Value)</div>
          <div style="text-align: center; position: relative;">
            <span>Negative / Mitigates &larr;</span>
            <span style="display: inline-block; width: 1px; height: 10px; background: rgba(255, 255, 255, 0.3); vertical-align: middle; margin: 0 0.5rem;"></span>
            <span>&rarr; Positive / Escalates</span>
          </div>
          <div style="text-align: right;">Model Attribution</div>
        </div>
      ` + data.contributions.map(c => {
        const isPos = c.attribution >= 0;
        const widthPct = Math.min(100, Math.round((Math.abs(c.attribution) / maxAttribution) * 100));
        const barColor = isPos ? "linear-gradient(90deg, #f59e0b, #ef4444)" : "linear-gradient(270deg, #10b981, #06b6d4)";
        const signStr = isPos ? `+${c.attribution.toFixed(3)}` : c.attribution.toFixed(3);
        const badgeCol = isPos ? "#f87171" : "#34d399";
        const badgeBg = isPos ? "rgba(239, 68, 68, 0.15)" : "rgba(16, 185, 129, 0.15)";
        const dirLabel = isPos ? "Escalates Risk" : (c.attribution < -0.001 ? "Mitigates Risk" : "Nominal");

        return `
          <div style="display: grid; grid-template-columns: 200px 1fr 110px; gap: 0.75rem; align-items: center; margin-bottom: 0.55rem; font-size: 0.75rem;">
            <!-- Feature name & value -->
            <div>
              <div style="font-weight: 700; color: #f1f5f9; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${c.feature_label}">
                #${c.rank} ${c.feature_label}
              </div>
              <div style="font-size: 0.68rem; color: var(--text-muted); font-family: var(--font-mono);">
                Observed: <strong style="color: #cbd5e1;">${c.feature_value}</strong> ${c.unit}
              </div>
            </div>

            <!-- Visual Bidirectional Center Bar -->
            <div style="background: rgba(255, 255, 255, 0.04); height: 22px; border-radius: 4px; position: relative; display: flex; align-items: center; border: 1px solid rgba(255, 255, 255, 0.05); overflow: hidden;">
              <!-- Center Axis Marker (50%) -->
              <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; background: rgba(255, 255, 255, 0.25); z-index: 2;"></div>

              ${isPos ? `
                <!-- Positive Bar (grows right from 50%) -->
                <div style="position: absolute; left: 50%; width: ${widthPct / 2}%; height: 100%; background: ${barColor}; border-radius: 0 3px 3px 0; z-index: 1;"></div>
              ` : `
                <!-- Negative Bar (grows left towards 50%) -->
                <div style="position: absolute; right: 50%; width: ${widthPct / 2}%; height: 100%; background: ${barColor}; border-radius: 3px 0 0 3px; z-index: 1;"></div>
              `}
              <span style="position: absolute; ${isPos ? 'left: calc(50% + 8px)' : 'right: calc(50% + 8px)'}; font-size: 0.65rem; font-family: var(--font-mono); font-weight: 700; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.8); z-index: 3;">
                ${signStr}
              </span>
            </div>

            <!-- Numerical Attribution Badge -->
            <div style="text-align: right;">
              <span style="background: ${badgeBg}; color: ${badgeCol}; font-family: var(--font-mono); font-weight: 800; font-size: 0.72rem; padding: 0.15rem 0.45rem; border-radius: 4px; display: inline-block;">
                ${signStr}
              </span>
              <div style="font-size: 0.62rem; color: var(--text-dim); margin-top: 0.15rem;">${dirLabel}</div>
            </div>
          </div>
        `;
      }).join("");
    }
  }

  window.explainActiveDecision = async function() {
    try {
      const res = await fetch("/api/xai/explain/decision");
      if (res.ok) {
        const data = await res.json();
        renderShapExplanation(data);
      }
    } catch (err) {
      console.error("Failed to explain active decision:", err);
    }
  };

  window.inspectEventShap = async function(eventId) {
    try {
      const res = await fetch(`/api/xai/explain/event/${encodeURIComponent(eventId)}`);
      if (res.ok) {
        const data = await res.json();
        switchTab("tab-xai");
        renderShapExplanation(data);
        window.scrollTo({ top: 0, behavior: "smooth" });
      } else {
        alert(`Could not fetch explanation for event ${eventId}`);
      }
    } catch (err) {
      console.error("Error inspecting event SHAP:", err);
    }
  };

  window.refreshXaiAuditTable = async function() {
    const tbody = document.getElementById("xaiAuditTableBody");
    if (!tbody) return;

    try {
      const [groundRes, queueRes] = await Promise.all([
        fetch("/api/sync/ground/events").then(r => r.json()).catch(() => ({ events: [] })),
        fetch("/api/sync/queue/pending").then(r => r.json()).catch(() => ({ health_events: [] }))
      ]);

      const all = [];
      (groundRes.events || []).forEach(e => all.push({ ...e, source_store: "GROUND" }));
      (queueRes.health_events || []).forEach(e => {
        if (!all.some(item => item.event_id === e.event_id)) {
          all.push({ ...e, source_store: "ONBOARD_QUEUE" });
        }
      });

      if (all.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-dim);">No health events recorded. Run 1-Click SHAP Demo or inject an anomaly scenario.</td></tr>`;
        return;
      }

      all.sort((a, b) => new Date(b.occurrence_utc) - new Date(a.occurrence_utc));

      tbody.innerHTML = all.map(ev => {
        const expl = ev.explanation || {};
        const topDriver = (expl.top_features_summary && expl.top_features_summary.length > 0)
          ? expl.top_features_summary[0]
          : "--";
        const mVersion = expl.model_version || "v1.0.0";
        const occurUtc = ev.occurrence_utc ? new Date(ev.occurrence_utc).toISOString().replace("T", " ").substring(11, 19) + " UTC" : "--";

        let sevBg = "rgba(100, 116, 139, 0.2)";
        let sevCol = "#94a3b8";
        if (ev.severity === "CRITICAL") {
          sevBg = "rgba(239, 68, 68, 0.2)";
          sevCol = "#f87171";
        } else if (ev.severity === "HIGH") {
          sevBg = "rgba(245, 158, 11, 0.2)";
          sevCol = "#fbbf24";
        } else if (ev.severity === "MEDIUM") {
          sevBg = "rgba(59, 130, 246, 0.2)";
          sevCol = "#60a5fa";
        }

        return `
          <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.06);">
            <td style="padding: 0.55rem 0.6rem; font-family: var(--font-mono); font-size: 0.72rem; color: #38bdf8;">${ev.event_id}</td>
            <td style="padding: 0.55rem 0.6rem;">
              <span style="background: ${sevBg}; color: ${sevCol}; padding: 0.15rem 0.45rem; border-radius: 4px; font-weight: 700; font-size: 0.68rem;">${ev.severity}</span>
            </td>
            <td style="padding: 0.55rem 0.6rem; color: #cbd5e1;">${ev.source_pillar || 'Multi-Signal'}</td>
            <td style="padding: 0.55rem 0.6rem; font-family: var(--font-mono); font-size: 0.72rem; color: #94a3b8;">${occurUtc}</td>
            <td style="padding: 0.55rem 0.6rem; font-family: var(--font-mono); font-size: 0.72rem; color: #34d399;">${mVersion}</td>
            <td style="padding: 0.55rem 0.6rem; font-size: 0.72rem; color: #fde68a;">${topDriver}</td>
            <td style="padding: 0.55rem 0.6rem;">
              <button class="btn btn-xs btn-outline" style="font-size: 0.68rem; padding: 0.15rem 0.45rem; border-color: rgba(245, 158, 11, 0.4); color: #fbbf24; cursor: pointer;" onclick="window.inspectEventShap('${ev.event_id}')">
                🔬 Inspect SHAP
              </button>
            </td>
          </tr>
        `;
      }).join("");
    } catch (err) {
      console.error("Failed to refresh XAI audit table:", err);
    }
  };

  window.runXaiDemoScenario = async function() {
    const consoleCard = document.getElementById("xaiDemoConsole");
    const container = document.getElementById("xaiDemoStepContainer");
    const btn = document.getElementById("xaiRunDemoBtn");

    if (consoleCard) consoleCard.style.display = "block";
    if (btn) btn.disabled = true;

    if (container) {
      container.innerHTML = `<div style="color: #fbbf24;">Initializing Feature B End-to-End SHAP Demonstration Scenario...</div>`;
    }

    try {
      const res = await fetch("/api/xai/demo/scenario", { method: "POST" });
      const data = await res.json();

      if (container) {
        container.innerHTML = `
          <div style="color: #34d399; font-weight: 700;">✓ DEMO SEQUENCE COMPLETED SUCCESSFULLY</div>
          <div style="color: #38bdf8;">• Step 1: Nominal baseline evaluated (Model Score: ${data.step1_nominal.predicted_score.toFixed(3)}, Baseline: ${data.step1_nominal.base_value.toFixed(3)}). No anomalous perturbation.</div>
          <div style="color: #f87171;">• Step 2: Anomaly 1 injected while ONLINE (Solar Flare + Cognitive Strain). SHAP attributed +${(data.step2_alert_online.contributions[0].attribution).toFixed(3)} to ${data.step2_alert_online.contributions[0].feature_label}.</div>
          <div style="color: #fbbf24;">• Step 3: Deep-Space Comms Link severed (${data.step3_comms_state}). Autonomous edge monitoring continues offline.</div>
          <div style="color: #f87171;">• Step 4: Anomaly 2 generated OFFLINE (Acoustic Hypoxia & Fatigue). Alert & SHAP explanation persisted locally in SQLite (${data.step4_offline_pending_count} pending in queue).</div>
          <div style="color: #34d399;">• Step 5: Earth link restored & store-and-forward downlink executed to Houston Ground Control (${data.step5_reconnected_sync.synced_count || 1} records transferred).</div>
          <div style="color: #38bdf8;">• Step 6: Houston Ground ingested ${data.step6_ground_records_count} events with preserved original model versions and intact SHAP explanations!</div>
        `;
      }

      // Render the offline anomaly's explanation in the hero card
      if (data.step4_offline_alert_saved) {
        renderShapExplanation(data.step4_offline_alert_saved);
      }

      window.refreshXaiAuditTable();
      fetchSyncStatusAndTimeline();
    } catch (err) {
      if (container) container.innerHTML = `<div style="color: #f87171;">Error executing XAI demo: ${err.message}</div>`;
    } finally {
      if (btn) btn.disabled = false;
    }
  };

  window.resetXaiDemo = async function() {
    try {
      await fetch("/api/xai/demo/reset", { method: "POST" });
      const consoleCard = document.getElementById("xaiDemoConsole");
      if (consoleCard) consoleCard.style.display = "none";
      await window.explainActiveDecision();
      await window.refreshXaiAuditTable();
      await fetchSyncStatusAndTimeline();
    } catch (err) {
      console.error("Error resetting XAI demo:", err);
    }
  };

  window.openCustomXaiModal = function() {
    const rad = prompt("Enter Radiation Dose Rate (mSv/h) [Nominal: 0.02, SPE: 0.72]:", "0.72");
    if (rad === null) return;
    const strain = prompt("Enter Cognitive Strain Index [0.0 - 1.0, Nominal: 0.12]:", "0.55");
    if (strain === null) return;
    const fatigue = prompt("Enter Vocal Fatigue Index [0.0 - 1.0, Nominal: 0.15]:", "0.35");
    if (fatigue === null) return;

    fetch("/api/xai/explain/custom", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        features: {
          rad_rate: parseFloat(rad) || 0.02,
          strain: parseFloat(strain) || 0.12,
          fatigue: parseFloat(fatigue) || 0.15,
          hypoxia: 0.04,
          bone_loss: 0.80,
          shear: 0.0
        }
      })
    })
    .then(r => r.json())
    .then(data => {
      renderShapExplanation(data);
    })
    .catch(err => alert("Error calculating SHAP explanation: " + err.message));
  };


  // Initial Boot
  fetchInitialState();
  fetchSyncStatusAndTimeline();
  triggerSimulatorUpdate(false);
  window.explainActiveDecision();
  window.refreshXaiAuditTable();


  // Restore previously active tab if stored in sessionStorage
  try {
    const savedTab = sessionStorage.getItem("aegis_active_tab");
    if (savedTab && document.getElementById(savedTab)) {
      switchTab(savedTab);
    }
  } catch (_) {}
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initAegisApp);
} else {
  initAegisApp();
}
