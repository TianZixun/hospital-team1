const dashboardPage = document.querySelector(".dashboard-page");

if (dashboardPage) {
  const toastStack = document.getElementById("toast-stack");
  const queuePanel = document.getElementById("queue-inspection");
  const liveClockNode = document.getElementById("live-clock");
  const queueModeSelect = document.querySelector("[data-queue-mode-select]");
  const patientCards = [...document.querySelectorAll(".patient-card[data-patient-id]")];
  const actionButtons = [...document.querySelectorAll(".button-stack .control-button")];
  const completeButtons = [...document.querySelectorAll("[data-action='complete-patient']")];
  const heapNodes = [...document.querySelectorAll("[data-heap-node]")];

  const runSimulationUrl = dashboardPage.dataset.runSimulationUrl;
  const addPatientUrl = dashboardPage.dataset.addPatientUrl;
  const completePatientUrlTemplate = dashboardPage.dataset.completePatientUrlTemplate;
  const datasetUrl = dashboardPage.dataset.datasetUrl;
  const nextOffset = Number.parseInt(dashboardPage.dataset.nextOffset ?? "0", 10);
  const currentOffset = Number.parseInt(dashboardPage.dataset.currentOffset ?? "0", 10);
  const liveClockSeed = dashboardPage.dataset.liveClockIso;
  let currentQueueMode = dashboardPage.dataset.currentQueueMode ?? "heap";

  let liveClock = liveClockSeed ? new Date(liveClockSeed) : null;

  function pad(value) {
    return String(value).padStart(2, "0");
  }

  function formatClock(date) {
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  }

  function renderLiveClock() {
    if (!liveClockNode || !liveClock) {
      return;
    }
    liveClockNode.textContent = formatClock(liveClock);
  }

  function startLiveClock() {
    if (!liveClock) {
      return;
    }
    renderLiveClock();
    window.setInterval(() => {
      liveClock = new Date(liveClock.getTime() + 1000);
      renderLiveClock();
    }, 1000);
  }

  function showToast(message, tone = "info") {
    if (!toastStack) {
      return;
    }
    const toast = document.createElement("div");
    toast.className = `toast ${tone}`;
    toast.textContent = message;
    toastStack.appendChild(toast);
    window.setTimeout(() => {
      toast.remove();
    }, 3200);
  }

  function pulseButton(button) {
    if (!button) {
      return;
    }
    button.classList.add("pressed");
    window.setTimeout(() => button.classList.remove("pressed"), 180);
  }

  function setBusy(button, busy) {
    if (!button) {
      return;
    }
    button.classList.toggle("is-busy", busy);
    button.disabled = busy;
  }

  function withSnapshotOffset(urlText) {
    const url = new URL(urlText, window.location.origin);
    url.searchParams.set(
      "snapshot_offset",
      String(Number.isNaN(currentOffset) ? 0 : currentOffset),
    );
    url.searchParams.set("queue_mode", currentQueueMode);
    return url.toString();
  }

  function focusQueuePanel() {
    if (!queuePanel) {
      return;
    }
    queuePanel.scrollIntoView({ behavior: "smooth", block: "start" });
    queuePanel.classList.add("is-highlighted");
    window.setTimeout(() => queuePanel.classList.remove("is-highlighted"), 1800);
  }

  function saveLastAddedPatient(patient) {
    if (!patient || !window.sessionStorage) {
      return;
    }

    window.sessionStorage.setItem("lastAddedPatientId", patient.patient_id ?? "");
    window.sessionStorage.setItem("lastAddedPatientName", patient.name ?? "");
  }

  function readLastAddedPatient() {
    if (!window.sessionStorage) {
      return null;
    }

    const patientId = window.sessionStorage.getItem("lastAddedPatientId");
    const patientName = window.sessionStorage.getItem("lastAddedPatientName");

    if (!patientId) {
      return null;
    }

    window.sessionStorage.removeItem("lastAddedPatientId");
    window.sessionStorage.removeItem("lastAddedPatientName");

    return { patientId, patientName };
  }

  function highlightLastAddedPatient() {
    const patient = readLastAddedPatient();
    if (!patient) {
      return;
    }

    const card = patientCards.find((item) => item.dataset.patientId === patient.patientId);
    if (card) {
      focusQueuePanel();
      card.classList.add("is-recent");
      card.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
      showToast(`${patient.patientId} added to the current queue view.`, "success");
      return;
    }

    showToast(
      `${patient.patientId} has been added, but this board only shows the first 10 visible patients.`,
      "info",
    );
  }

  async function postAction(url, button) {
    setBusy(button, true);
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { Accept: "application/json" },
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.message || "Request failed.");
      }
      showToast(payload.message, "success");
      window.setTimeout(() => {
        window.location.reload();
      }, 500);
    } catch (error) {
      showToast(error.message || "Action failed.", "warning");
      console.error(error);
    } finally {
      setBusy(button, false);
    }
  }

  async function addPatient(button) {
    if (!addPatientUrl) {
      showToast("Add-patient route is missing.", "warning");
      return;
    }

    setBusy(button, true);
    try {
      const response = await fetch(withSnapshotOffset(addPatientUrl), {
        method: "POST",
        headers: { Accept: "application/json" },
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.message || "Request failed.");
      }

      saveLastAddedPatient(payload.patient);
      window.location.reload();
    } catch (error) {
      showToast(error.message || "Action failed.", "warning");
      console.error(error);
    } finally {
      setBusy(button, false);
    }
  }

  async function runSimulation(button) {
    if (!runSimulationUrl) {
      showToast("Simulation route is missing.", "warning");
      return;
    }
    setBusy(button, true);
    try {
      const response = await fetch(withSnapshotOffset(runSimulationUrl), {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        throw new Error(`Simulation request failed: ${response.status}`);
      }
      const payload = await response.json();
      showToast(payload.message, "success");
    } catch (error) {
      showToast("Simulation failed. Please try again.", "warning");
      console.error(error);
    } finally {
      setBusy(button, false);
    }
  }

  function openDataset() {
    if (!datasetUrl) {
      showToast("Dataset link is missing.", "warning");
      return;
    }
    window.open(datasetUrl, "_blank", "noopener,noreferrer");
  }

  function refreshSnapshot() {
    const targetUrl = new URL(window.location.href);
    targetUrl.searchParams.set(
      "snapshot_offset",
      String(Number.isNaN(nextOffset) ? 0 : nextOffset),
    );
    targetUrl.searchParams.set("queue_mode", currentQueueMode);
    window.location.assign(targetUrl.toString());
  }

  function updateQueueMode(value) {
    currentQueueMode = value || "heap";
    const targetUrl = new URL(window.location.href);
    targetUrl.searchParams.set("queue_mode", currentQueueMode);
    targetUrl.searchParams.set(
      "snapshot_offset",
      String(Number.isNaN(currentOffset) ? 0 : currentOffset),
    );
    window.location.assign(targetUrl.toString());
  }

  function updateHeapDetail(node) {
    if (!node) {
      return;
    }

    heapNodes.forEach((item) => item.classList.remove("is-selected"));
    node.classList.add("is-selected");

    const detailMap = {
      "heap-detail-label": node.dataset.label,
      "heap-detail-status": node.dataset.status,
      "heap-detail-name": `Name (姓名): ${node.dataset.name}`,
      "heap-detail-priority": `Priority (优先级): ${node.dataset.priority}`,
      "heap-detail-arrival": `Arrival (到达时间): ${node.dataset.arrival}`,
      "heap-detail-wait": `Estimated Wait (预计等待): ${node.dataset.wait}`,
      "heap-detail-treatment": `Treatment (诊疗时长): ${node.dataset.treatment} min`,
    };

    Object.entries(detailMap).forEach(([id, text]) => {
      const element = document.getElementById(id);
      if (element) {
        element.textContent = text;
      }
    });
  }

  function completeFromButton(button) {
    const patientId = button.dataset.patientId;
    if (!patientId || !completePatientUrlTemplate) {
      showToast("Patient action is missing.", "warning");
      return;
    }
    const actionUrl = completePatientUrlTemplate.replace(
      "__PATIENT_ID__",
      encodeURIComponent(patientId),
    );
    postAction(withSnapshotOffset(actionUrl), button);
  }

  actionButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      pulseButton(button);

      switch (button.dataset.action) {
        case "run-simulation":
          await runSimulation(button);
          break;
        case "add-patient":
          await addPatient(button);
          break;
        case "open-dataset":
          openDataset();
          break;
        case "inspect-queue":
          focusQueuePanel();
          showToast("Queue section focused.", "info");
          break;
        case "refresh-snapshot":
          showToast("Refreshing to the next simulation snapshot...", "info");
          window.setTimeout(refreshSnapshot, 220);
          break;
        default:
          break;
      }
    });
  });

  completeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      pulseButton(button);
      completeFromButton(button);
    });
  });

  heapNodes.forEach((node) => {
    node.addEventListener("click", () => {
      updateHeapDetail(node);
      showToast(`${node.dataset.label} selected.`, "info");
    });
  });

  if (heapNodes.length > 0) {
    updateHeapDetail(heapNodes[0]);
  }

  if (queueModeSelect) {
    queueModeSelect.addEventListener("change", () => {
      updateQueueMode(queueModeSelect.value);
    });
  }

  highlightLastAddedPatient();
  startLiveClock();
}
