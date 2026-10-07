// Aegis-DeepSpace Pillar 4 Dashboard Client Logic

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const commsBadge = document.getElementById("commsBadge");
  const commsStatusText = document.getElementById("commsStatusText");
  const toggleCommsBtn = document.getElementById("toggleCommsBtn");
  const dataFreshness = document.getElementById("dataFreshness");
  const scenarioBtnGroup = document.getElementById("scenarioBtnGroup");

  // Pillar 1 Elements
  const radRiskBadge = document.getElementById("radRiskBadge");
  const p1DoseRate = document.getElementById("p1DoseRate");
  const p1CumDose = document.getElementById("p1CumDose");
  const p1SpeActive = document.getElementById("p1SpeActive");
  const p1CurrentModule = document.getElementById("p1CurrentModule");
  const p1Shielding = document.getElementById("p1Shielding");
  const p1SafeModule = document.getElementById("p1SafeModule");

  // Pillar 2 Elements
  const voiceRiskBadge = document.getElementById("voiceRiskBadge");
  const barCognitive = document.getElementById("barCognitive");
  const valCognitive = document.getElementById("valCognitive");
  const barFatigue = document.getElementById("barFatigue");
  const valFatigue = document.getElementById("valFatigue");
  const barHypoxia = document.getElementById("barHypoxia");
  const valHypoxia = document.getElementById("valHypoxia");
  const valBaselineDev = document.getElementById("valBaselineDev");

  // Pillar 3 Elements
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

  // Initialize
  fetchInitialState();

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

  async function fetchInitialState() {
    try {
      const res = await fetch("/api/state");
      const data = await res.json();
      renderState(data.crew_state, data.decision);
    } catch (err) {
      console.error("Failed to load initial state:", err);
    }
  }

  async function loadScenario(scenarioId) {
    try {
      const res = await fetch(`/api/scenarios/${scenarioId}`, { method: "POST" });
      const data = await res.json();
      renderState(data.crew_state, data.decision);
    } catch (err) {
      console.error(`Failed to load scenario ${scenarioId}:`, err);
    }
  }

  async function toggleCommsMode() {
    try {
      const res = await fetch("/api/comms/toggle", { method: "POST" });
      const data = await res.json();
      // Re-fetch current state to sync UI
      fetchInitialState();
    } catch (err) {
      console.error("Failed to toggle comms mode:", err);
    }
  }

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

    // 2. Pillar 1: Radiation Safe-Route
    const rad = state.radiation;
    p1DoseRate.innerHTML = `${rad.dose_rate_msv_h.toFixed(2)} <small>mSv/h</small>`;
    p1CumDose.innerHTML = `${rad.cumulative_dose_msv.toFixed(1)} <small>mSv</small>`;
    p1SpeActive.textContent = rad.spe_active ? "YES (ACTIVE)" : "NO";
    p1CurrentModule.textContent = rad.current_module;
    p1Shielding.textContent = `(${rad.shielding_rating_g_cm2.toFixed(1)} g/cm²)`;
    p1SafeModule.textContent = rad.recommended_safe_module;

    setSeverityBadge(radRiskBadge, rad.risk_level);

    // 3. Pillar 2: Voice Vitals
    const voice = state.voice_vitals;
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
    const voiceLevel = voice.cognitive_strain_score > 0.5 ? "HIGH" : (voice.cognitive_strain_score > 0.3 ? "MEDIUM" : "LOW");
    setSeverityBadge(voiceRiskBadge, voiceLevel);

    // 4. Pillar 3: Astro-Twin
    const twin = state.astro_twin;
    p3BoneLoss.innerHTML = `${twin.projected_bone_loss_pct_mo.toFixed(1)}% <small>/mo</small>`;
    p3MuscleLoss.innerHTML = `${twin.projected_muscle_atrophy_pct.toFixed(1)}%`;
    p3DeficitDays.innerHTML = `${twin.exercise_deficit_days} <small>days</small>`;
    p3Countermeasure.textContent = twin.countermeasure_status === "NOMINAL"
      ? "Adherence nominal; bone mineral density within normal variance."
      : `Warning: Exercise deficit active (${twin.exercise_deficit_days}d). Countermeasure adjustment flagged.`;

    const twinLevel = twin.exercise_deficit_days > 2 ? "HIGH" : (twin.exercise_deficit_days > 0 ? "MEDIUM" : "LOW");
    setSeverityBadge(twinStatusBadge, twinLevel);

    // 5. Risk Fusion Breakdown (Mathematical trace from decision_engine.py)
    const rf = decision.risk_fusion;
    if (rf) {
      fusionFormulaDisplay.textContent = rf.formula;

      // Base
      fcBasePoints.textContent = `+${rf.baseline_score.toFixed(2)}`;
      fcBaseStatus.textContent = "NOMINAL";

      // P1 Radiation
      const p1 = rf.p1_radiation;
      fcP1Points.textContent = `+${p1.score_addition.toFixed(2)}`;
      fcP1Status.textContent = p1.status;
      fcP1Detail.textContent = p1.detail;
      setFusionCardStyle(fcP1Card, p1.score_addition, p1.status);

      // P2 Voice Vitals
      const p2 = rf.p2_voice_vitals;
      fcP2Points.textContent = `+${p2.score_addition.toFixed(2)}`;
      fcP2Status.textContent = p2.status;
      fcP2Detail.textContent = p2.detail;
      setFusionCardStyle(fcP2Card, p2.score_addition, p2.status);

      // P3 Astro-Twin
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

      // Flow diagram result step badge
      flowResultText.textContent = `${decision.risk_level} (${decision.risk_score.toFixed(2)})`;
      setFlowResultStyle(flowResultBadge, decision.risk_level);
    }

    // 6. Pillar 4: Autonomous Decision Object
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
  }

  function setSeverityBadge(badgeEl, level) {
    badgeEl.textContent = level;
    badgeEl.className = `badge ${getBadgeClass(level)}`;
  }

  function getBadgeClass(level) {
    switch (level?.toUpperCase()) {
      case "CRITICAL": return "badge-critical";
      case "HIGH": return "badge-high";
      case "MEDIUM":
      case "MODERATE": return "badge-medium";
      default: return "badge-low";
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
});
