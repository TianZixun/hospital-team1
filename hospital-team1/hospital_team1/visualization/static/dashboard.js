const dashboardPage = document.querySelector(".dashboard-page");

if (dashboardPage) {
  const toastStack = document.getElementById("toast-stack");
  const queuePanel = document.getElementById("queue-inspection");
  const runtimeNode = document.getElementById("simulation-runtime");
  const clockNodes = [...document.querySelectorAll("[data-clock-role='clock']")];
  const actionButtons = [...document.querySelectorAll(".button-stack .control-button")];

  const runSimulationUrl = dashboardPage.dataset.runSimulationUrl;
  const datasetUrl = dashboardPage.dataset.datasetUrl;
  const nextOffset = Number.parseInt(dashboardPage.dataset.nextOffset ?? "0", 10);
  const clockSeed = dashboardPage.dataset.clockIso;
  const shiftStartSeed = dashboardPage.dataset.shiftStartIso;

  let liveClock = clockSeed ? new Date(clockSeed) : null;
  const shiftStart = shiftStartSeed ? new Date(shiftStartSeed) : null;

  function pad(value) {
    return String(value).padStart(2, "0");
  }

  function formatClock(date) {
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  }

  function formatRuntime(date, shiftStartDate) {
    if (!shiftStartDate) {
      return "00:00:00";
    }
    const diffSeconds = Math.max(0, Math.floor((date.getTime() - shiftStartDate.getTime()) / 1000));
    const hours = Math.floor(diffSeconds / 3600);
    const minutes = Math.floor((diffSeconds % 3600) / 60);
    const seconds = diffSeconds % 60;
    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
  }

  function renderClock() {
    if (!liveClock) {
      return;
    }
    const text = formatClock(liveClock);
    clockNodes.forEach((node) => {
      node.textContent = text;
    });
    if (runtimeNode) {
      runtimeNode.textContent = formatRuntime(liveClock, shiftStart);
    }
  }

  function startClock() {
    if (!liveClock) {
      return;
    }
    renderClock();
    window.setInterval(() => {
      liveClock = new Date(liveClock.getTime() + 1000);
      renderClock();
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
    }, 3600);
  }

  function pulseButton(button) {
    button.classList.add("pressed");
    window.setTimeout(() => button.classList.remove("pressed"), 180);
  }

  function setBusy(button, busy) {
    button.classList.toggle("is-busy", busy);
    button.disabled = busy;
  }

  function focusQueuePanel() {
    if (!queuePanel) {
      return;
    }
    queuePanel.scrollIntoView({ behavior: "smooth", block: "start" });
    queuePanel.classList.add("is-highlighted");
    window.setTimeout(() => queuePanel.classList.remove("is-highlighted"), 1800);
  }

  async function runSimulation(button) {
    if (!runSimulationUrl) {
      showToast("Simulation route is missing.", "warning");
      return;
    }
    setBusy(button, true);
    try {
      const response = await fetch(runSimulationUrl, {
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
    targetUrl.searchParams.set("snapshot_offset", String(Number.isNaN(nextOffset) ? 0 : nextOffset));
    window.location.assign(targetUrl.toString());
  }

  actionButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      pulseButton(button);

      switch (button.dataset.action) {
        case "run-simulation":
          await runSimulation(button);
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

  startClock();
}
