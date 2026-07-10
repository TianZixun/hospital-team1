const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10" x 5.625"
pres.author = "Hospital Team 1";
pres.title = "Hospital Triage Scheduler - Project Presentation";

// ============================================================
// Color Palette — Medical Trust
// ============================================================
const C = {
  darkBg:      "0F2F4F",
  darkBg2:     "1A3A5C",
  contentBg:   "F7F9FB",
  cardBg:      "FFFFFF",
  primary:     "1A6B7A",
  primaryDark: "155264",
  primaryLight:"E0F2F2",
  coral:       "E76F51",
  green:       "2D8C6E",
  textDark:    "1B2A4A",
  textBody:    "3D4F5F",
  textMuted:   "7B8A9B",
  border:      "DEE5ED",
  white:       "FFFFFF",
  highlight:   "F0F7FA",
  coralLight:  "FDF0EC",
  greenLight:  "E8F5F0",
};

// Factory helpers — fresh objects each call (pptxgenjs mutates them)
const cardShadow = () => ({ type: "outer", color: "000000", blur: 4, offset: 1.5, angle: 135, opacity: 0.08 });
const makeShadow = () => ({ type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.10 });

// ============================================================
// Slide 1 — Title Page (Dark bg)
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.darkBg };

  // Decorative circles
  s.addShape(pres.shapes.OVAL, { x: 6.5, y: -1.5, w: 5, h: 5, fill: { color: C.darkBg2, transparency: 40 } });
  s.addShape(pres.shapes.OVAL, { x: -1.5, y: 2.5, w: 4, h: 4, fill: { color: C.darkBg2, transparency: 50 } });

  // Main title
  s.addText("Hospital Triage\nScheduler", {
    x: 0.9, y: 1.0, w: 6.5, h: 2.4,
    fontSize: 44, fontFace: "Arial", bold: true,
    color: C.white, lineSpacingMultiple: 1.1,
  });

  // Coral accent bar
  s.addShape(pres.shapes.RECTANGLE, { x: 0.9, y: 3.5, w: 1.2, h: 0.06, fill: { color: C.coral } });

  // Subtitle
  s.addText("Data Structures & Algorithms — Course Project Presentation", {
    x: 0.9, y: 3.8, w: 8, h: 0.45,
    fontSize: 16, fontFace: "Calibri", color: C.textMuted,
  });

  // Info
  s.addText([
    { text: "2026-07-09", options: { breakLine: true } },
    { text: "Python + Flask + CSV + unittest", options: {} },
  ], {
    x: 5.8, y: 4.4, w: 3.8, h: 0.8,
    fontSize: 12, fontFace: "Calibri", color: C.textMuted,
    align: "right", valign: "bottom",
  });
}

// ============================================================
// Slide 2 — Project Background & Goal
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.contentBg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.primary } });

  s.addText("02", { x: 0.5, y: 0.25, w: 0.5, h: 0.35, fontSize: 11, fontFace: "Calibri", bold: true, color: C.primary });
  s.addText("Project Background & Goal", { x: 0.5, y: 0.5, w: 9, h: 0.55, fontSize: 30, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  // ---- Left card: Problem ----
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.25, w: 4.3, h: 2.9, fill: { color: C.cardBg }, shadow: cardShadow() });
  s.addShape(pres.shapes.OVAL, { x: 0.75, y: 1.45, w: 0.22, h: 0.22, fill: { color: C.coral } });
  s.addText("The Problem", { x: 1.1, y: 1.4, w: 3.2, h: 0.38, fontSize: 17, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  s.addText([
    { text: "Emergency departments face unpredictable patient arrivals with varying severity.", options: { breakLine: true, bullet: true, paraSpaceAfter: 6 } },
    { text: "Traditional FIFO fails when critical patients queue behind minor cases.", options: { breakLine: true, bullet: true, paraSpaceAfter: 6 } },
    { text: "We need a priority-based system that respects clinical urgency and is testable.", options: { bullet: true } },
  ], { x: 0.8, y: 1.95, w: 3.7, h: 2.0, fontSize: 12, fontFace: "Calibri", color: C.textBody, lineSpacingMultiple: 1.2, valign: "top" });

  // ---- Right card: Goal ----
  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.25, w: 4.3, h: 2.9, fill: { color: C.cardBg }, shadow: cardShadow() });
  s.addShape(pres.shapes.OVAL, { x: 5.45, y: 1.45, w: 0.22, h: 0.22, fill: { color: C.primary } });
  s.addText("Our Goal", { x: 5.8, y: 1.4, w: 3.2, h: 0.38, fontSize: 17, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  s.addText([
    { text: "Build a modular hospital triage scheduler with custom data structures end-to-end.", options: { breakLine: true, bullet: true, paraSpaceAfter: 6 } },
    { text: "Implement Heap-based and Ordered-Linked priority queues from scratch.", options: { breakLine: true, bullet: true, paraSpaceAfter: 6 } },
    { text: "Simulate, analyze, and visualize patient flow via a real-time Flask dashboard.", options: { breakLine: true, bullet: true, paraSpaceAfter: 6 } },
    { text: "Validate correctness with 47 comprehensive unit tests, zero failures.", options: { bullet: true } },
  ], { x: 5.45, y: 1.95, w: 3.7, h: 2.0, fontSize: 12, fontFace: "Calibri", color: C.textBody, lineSpacingMultiple: 1.2, valign: "top" });

  // ---- Bottom flow strip ----
  const flowLabels = ["Patient", "Queue", "Treatment", "Analysis", "Dashboard"];
  const flowColors = ["1A6B7A", "2D8C6E", "1A6B7A", "2D8C6E", "E76F51"];
  const stepW = 1.5, startX = 1.55, flowY = 4.55;
  flowLabels.forEach((label, i) => {
    const cx = startX + i * (stepW + 0.2);
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: flowY, w: stepW, h: 0.5, fill: { color: flowColors[i] } });
    s.addText(label, { x: cx, y: flowY, w: stepW, h: 0.5, fontSize: 12, fontFace: "Calibri", bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    if (i < flowLabels.length - 1) {
      s.addText("▶", { x: cx + stepW, y: flowY, w: 0.2, h: 0.5, fontSize: 10, color: C.textMuted, align: "center", valign: "middle", margin: 0 });
    }
  });
}

// ============================================================
// Slide 3 — Project Structure + main.py
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.contentBg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.primary } });
  s.addText("03", { x: 0.5, y: 0.25, w: 0.5, h: 0.35, fontSize: 11, fontFace: "Calibri", bold: true, color: C.primary });
  s.addText("Project Structure", { x: 0.5, y: 0.5, w: 9, h: 0.55, fontSize: 30, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  const modules = [
    { name: "models", desc: "Patient & triage\nlevel definitions", color: C.primary },
    { name: "structures", desc: "Linked-list\nWaitingRoom", color: C.primaryDark },
    { name: "queues", desc: "Heap & ordered-\nlinked queues", color: C.primary },
    { name: "data", desc: "CSV loader &\ndataset generator", color: C.primaryDark },
    { name: "simulation", desc: "Shift simulation\n& compliance", color: C.primary },
    { name: "analysis", desc: "Wait analytics &\ntimeout prediction", color: C.primaryDark },
    { name: "visualization", desc: "Flask dashboard\n& GUI server", color: C.primary },
    { name: "tests", desc: "18 test files\n47 tests passed", color: C.coral },
  ];

  const cardW = 2.05, cardH = 1.65;
  const gapX = 0.25, gapY = 0.15;
  const row1Y = 1.25, row2Y = row1Y + cardH + gapY;
  const startColX = 0.5;

  modules.forEach((m, i) => {
    const col = i % 4;
    const row = Math.floor(i / 4);
    const cx = startColX + col * (cardW + gapX);
    const cy = row === 0 ? row1Y : row2Y;

    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: cy, w: cardW, h: cardH, fill: { color: C.cardBg }, shadow: cardShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: cy, w: cardW, h: 0.05, fill: { color: m.color } });
    s.addText(m.name, { x: cx + 0.15, y: cy + 0.2, w: cardW - 0.3, h: 0.35, fontSize: 15, fontFace: "Consolas", bold: true, color: m.color, margin: 0 });
    s.addText(m.desc, { x: cx + 0.15, y: cy + 0.6, w: cardW - 0.3, h: 0.85, fontSize: 11, fontFace: "Calibri", color: C.textBody, lineSpacingMultiple: 1.2, margin: 0, valign: "top" });
  });

  // main.py note
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.35, w: 9, h: 0.55, fill: { color: C.primaryLight } });
  s.addText([
    { text: "Entry Point: ", options: { bold: true, fontFace: "Consolas" } },
    { text: "main.py — a lightweight local demo that wires all modules together. It validates Part 1 core functionality end-to-end.", options: { fontFace: "Calibri" } },
  ], { x: 0.75, y: 4.35, w: 8.5, h: 0.55, fontSize: 12, fontFace: "Calibri", color: C.primaryDark, valign: "middle", margin: 0 });
}

// ============================================================
// Slide 4 — Patient Model + Core Data Structures (merged)
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.contentBg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.primary } });
  s.addText("04", { x: 0.5, y: 0.25, w: 0.5, h: 0.35, fontSize: 11, fontFace: "Calibri", bold: true, color: C.primary });
  s.addText("Patient Model & Core Data Structures", { x: 0.5, y: 0.5, w: 9, h: 0.55, fontSize: 28, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  // ---- Left card: Patient Model ----
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.25, w: 4.1, h: 3.6, fill: { color: C.cardBg }, shadow: cardShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.25, w: 4.1, h: 0.5, fill: { color: C.primary } });
  s.addText("Patient Model", { x: 0.75, y: 1.25, w: 3.6, h: 0.5, fontSize: 15, fontFace: "Arial", bold: true, color: C.white, margin: 0, valign: "middle" });

  // Fields table
  const fields = [
    ["Field", "Type", "Description"],
    ["patient_id", "str", "Unique identifier"],
    ["triage_level", "enum", "1–4 severity level"],
    ["arrival_time", "float", "Entry timestamp (min)"],
    ["treatment_time", "float", "Treatment duration"],
  ];
  const colW = [1.3, 0.85, 1.65];
  const tableData = fields.map((row, ri) =>
    row.map((cell, ci) => ({
      text: cell,
      options: {
        fill: { color: ri === 0 ? C.primary : (ri % 2 === 0 ? C.highlight : C.cardBg) },
        color: ri === 0 ? C.white : C.textBody,
        bold: ri === 0 || ci === 0,
        fontSize: 11,
        fontFace: ci === 0 ? "Consolas" : "Calibri",
        align: "left", valign: "middle",
      },
    }))
  );

  s.addTable(tableData, { x: 0.7, y: 1.9, w: 3.7, colW: colW, rowH: [0.33, 0.32, 0.32, 0.32, 0.32], border: { pt: 0.5, color: C.border }, margin: [3, 6, 3, 6] });

  // Priority Rule
  s.addText([
    { text: "Priority Rule (__lt__):  ", options: { bold: true, fontSize: 12 } },
    { text: "triage_level → arrival_time", options: { fontSize: 12 } },
  ], { x: 0.7, y: 3.6, w: 3.7, h: 0.3, fontFace: "Consolas", color: C.primaryDark, margin: 0 });

  // Thresholds
  s.addText([
    { text: "Critical", options: { bold: true, color: C.coral } }, { text: " 0 min", options: { breakLine: true } },
    { text: "Urgent", options: { bold: true, color: C.coral } }, { text: " 20 min", options: { breakLine: true } },
    { text: "Semi-Urgent", options: { bold: true, color: C.coral } }, { text: " 35 min", options: { breakLine: true } },
    { text: "Non-Urgent", options: { bold: true, color: C.coral } }, { text: " 60 min", options: {} },
  ], { x: 0.7, y: 3.9, w: 3.7, h: 0.85, fontSize: 11, fontFace: "Calibri", color: C.textBody, lineSpacingMultiple: 1.1, margin: 0 });

  // ---- Right card: Data Structures ----
  s.addShape(pres.shapes.RECTANGLE, { x: 4.9, y: 1.25, w: 4.6, h: 3.6, fill: { color: C.cardBg }, shadow: cardShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 4.9, y: 1.25, w: 4.6, h: 0.5, fill: { color: C.primaryDark } });
  s.addText("Core Data Structures", { x: 5.15, y: 1.25, w: 4.1, h: 0.5, fontSize: 15, fontFace: "Arial", bold: true, color: C.white, margin: 0, valign: "middle" });

  // WaitingRoom section
  s.addShape(pres.shapes.RECTANGLE, { x: 5.1, y: 1.9, w: 4.2, h: 1.5, fill: { color: C.highlight } });
  s.addText("WaitingRoom (Linked List)", { x: 5.3, y: 1.95, w: 3.8, h: 0.3, fontSize: 13, fontFace: "Arial", bold: true, color: C.primaryDark, margin: 0 });
  s.addText("Singly linked list managing patient queue order.\nOperations: add, pop, peek, remove, to_list.", { x: 5.3, y: 2.3, w: 3.8, h: 0.5, fontSize: 11, fontFace: "Calibri", color: C.textBody, lineSpacingMultiple: 1.3, margin: 0 });

  // Linked list visual: P-1 → P-2 → P-3 → ...
  const nodeY = 2.9;
  ["P-1", "P-2", "P-3", "…"].forEach((label, i) => {
    const nx = 5.3 + i * 0.95;
    s.addShape(pres.shapes.RECTANGLE, { x: nx, y: nodeY, w: 0.65, h: 0.33, fill: { color: C.primaryLight } });
    s.addText(label, { x: nx, y: nodeY, w: 0.65, h: 0.33, fontSize: 9, fontFace: "Consolas", color: C.primaryDark, align: "center", valign: "middle", margin: 0 });
    if (i < 3) {
      s.addText("→", { x: nx + 0.65, y: nodeY, w: 0.3, h: 0.33, fontSize: 11, color: C.textMuted, align: "center", valign: "middle", margin: 0 });
    }
  });

  // Queues section
  s.addShape(pres.shapes.RECTANGLE, { x: 5.1, y: 3.6, w: 4.2, h: 1.05, fill: { color: C.highlight } });
  s.addText([
    { text: "Two Priority Queue Implementations", options: { bold: true, fontSize: 12, breakLine: true } },
    { text: "HeapPriorityQueue — O(log n) enqueue/dequeue (Min-Heap)", options: { fontSize: 10, breakLine: true } },
    { text: "OrderedLinkedPriorityQueue — O(n) insert, O(1) pop", options: { fontSize: 10 } },
  ], { x: 5.3, y: 3.65, w: 3.8, h: 0.9, fontFace: "Consolas", color: C.textBody, lineSpacingMultiple: 1.35, margin: 0 });
}

// ============================================================
// Slide 5 — CSV Dataset Workflow
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.contentBg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.primary } });
  s.addText("05", { x: 0.5, y: 0.25, w: 0.5, h: 0.35, fontSize: 11, fontFace: "Calibri", bold: true, color: C.primary });
  s.addText("Dataset Input & CSV Workflow", { x: 0.5, y: 0.5, w: 9, h: 0.55, fontSize: 30, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  const stages = [
    { title: "1. CSV File", desc: "patients_dataset.csv\nStores: patient_id, triage,\narrival, treatment time\nLocation: datasets/", color: C.primary },
    { title: "2. CSV Loader", desc: "csv_loader.py reads each row\nand converts it into\na Patient object with\ntriage_level + arrival_time", color: C.primaryDark },
    { title: "3. Sorted Queue", desc: "Patients sorted by arrival_time\nand fed into the WaitingRoom.\nNow ready for simulation\nand dispatch.", color: C.coral },
  ];

  stages.forEach((st, i) => {
    const sx = 0.45 + i * 3.2;
    const sy = 1.35, sw = 2.8, sh = 3.0;

    s.addShape(pres.shapes.RECTANGLE, { x: sx, y: sy, w: sw, h: sh, fill: { color: C.cardBg }, shadow: cardShadow() });
    // Step circle
    s.addShape(pres.shapes.OVAL, { x: sx + sw / 2 - 0.4, y: sy + 0.2, w: 0.8, h: 0.8, fill: { color: st.color } });
    s.addText(String(i + 1), { x: sx + sw / 2 - 0.4, y: sy + 0.2, w: 0.8, h: 0.8, fontSize: 22, fontFace: "Arial", bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.addText(st.title, { x: sx + 0.2, y: sy + 1.15, w: sw - 0.4, h: 0.4, fontSize: 16, fontFace: "Arial", bold: true, color: C.textDark, align: "center", margin: 0 });
    s.addText(st.desc, { x: sx + 0.25, y: sy + 1.6, w: sw - 0.5, h: 1.2, fontSize: 11, fontFace: "Calibri", color: C.textBody, align: "center", lineSpacingMultiple: 1.3, margin: 0 });
  });

  // Arrows between
  [1.1, 2].forEach((i) => {
    const ax = 0.45 + i * 3.2 - 0.35;
    s.addText("▶", { x: ax, y: 2.65, w: 0.35, h: 0.4, fontSize: 18, color: C.textMuted, align: "center", valign: "middle", margin: 0 });
  });

  // Bottom note
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.65, w: 9, h: 0.55, fill: { color: C.primaryLight } });
  s.addText("Key point: The system is not hard-coded — it reads real CSV data, instantiates Patient objects, and sorts by arrival time.", {
    x: 0.75, y: 4.65, w: 8.5, h: 0.55, fontSize: 13, fontFace: "Calibri", color: C.primaryDark, valign: "middle", margin: 0,
  });
}

// ============================================================
// Slide 6 — Simulation Logic
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.contentBg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.primary } });
  s.addText("06", { x: 0.5, y: 0.25, w: 0.5, h: 0.35, fontSize: 11, fontFace: "Calibri", bold: true, color: C.primary });
  s.addText("Shift Simulation Logic", { x: 0.5, y: 0.5, w: 9, h: 0.55, fontSize: 30, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  // ---- Left: Simulation Setup ----
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.3, w: 4.3, h: 3.5, fill: { color: C.cardBg }, shadow: cardShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.3, w: 0.07, h: 3.5, fill: { color: C.primary } });
  s.addText("Simulation Setup", { x: 0.85, y: 1.4, w: 3.7, h: 0.35, fontSize: 16, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  s.addText([
    { text: "3 Workstations", options: { bold: true, breakLine: true, fontSize: 26, color: C.primary } },
    { text: "default configuration", options: { breakLine: true, fontSize: 12, color: C.textMuted } },
  ], { x: 0.85, y: 1.9, w: 3.7, h: 0.7, fontFace: "Arial", margin: 0, align: "center" });

  const simSteps = [
    "1. Patients arrive at their scheduled time",
    "2. Critical patients → treated immediately",
    "3. Others enter the WaitingRoom queue",
    "4. Free workstations pull from queue",
    "5. Wait times recorded for analysis",
  ];
  simSteps.forEach((step, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: 0.85, y: 2.8 + i * 0.42, w: 3.7, h: 0.36, fill: { color: i % 2 === 0 ? C.highlight : C.cardBg } });
    s.addText(step, { x: 1.0, y: 2.8 + i * 0.42, w: 3.4, h: 0.36, fontSize: 11, fontFace: "Calibri", color: C.textBody, margin: 0, valign: "middle" });
  });

  // ---- Right: Compliance & Output ----
  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.3, w: 4.3, h: 3.5, fill: { color: C.cardBg }, shadow: cardShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.3, w: 0.07, h: 3.5, fill: { color: C.coral } });
  s.addText("Compliance & Output", { x: 5.55, y: 1.4, w: 3.7, h: 0.35, fontSize: 16, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  // Compliance
  s.addShape(pres.shapes.RECTANGLE, { x: 5.55, y: 1.95, w: 3.6, h: 1.1, fill: { color: C.coralLight } });
  s.addText([
    { text: "Compliance Check", options: { bold: true, fontSize: 14, breakLine: true } },
    { text: "Compares actual wait time vs. triage threshold for every patient. Flags violations and generates pass/fail report.", options: { fontSize: 11 } },
  ], { x: 5.75, y: 2.0, w: 3.2, h: 1.0, fontFace: "Calibri", color: C.textBody, lineSpacingMultiple: 1.3, margin: 0 });

  // Report
  s.addShape(pres.shapes.RECTANGLE, { x: 5.55, y: 3.25, w: 3.6, h: 1.1, fill: { color: C.greenLight } });
  s.addText([
    { text: "Simulation Report", options: { bold: true, fontSize: 14, breakLine: true } },
    { text: "Aggregates: total patients, avg wait time, compliance %, and priority inversions detected.", options: { fontSize: 11 } },
  ], { x: 5.75, y: 3.3, w: 3.2, h: 1.0, fontFace: "Calibri", color: C.textBody, lineSpacingMultiple: 1.3, margin: 0 });

  s.addText("Key files: simulation/shift_simulation.py, compliance.py, report.py", {
    x: 5.55, y: 4.5, w: 3.6, h: 0.3, fontSize: 10, fontFace: "Consolas", color: C.textMuted, margin: 0,
  });
}

// ============================================================
// Slide 7 — Analysis & Risk Prediction
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.contentBg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.primary } });
  s.addText("07", { x: 0.5, y: 0.25, w: 0.5, h: 0.35, fontSize: 11, fontFace: "Calibri", bold: true, color: C.primary });
  s.addText("Analysis & Risk Prediction", { x: 0.5, y: 0.5, w: 9, h: 0.55, fontSize: 30, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  // 4 stat cards
  const stats = [
    { value: "Avg Wait", label: "Per triage level", color: C.primary },
    { value: "Inversions", label: "Priority violations\ndetected", color: C.coral },
    { value: "Predicted", label: "Wait time for\nnew patients", color: C.primaryDark },
    { value: "Risk Alerts", label: "Patients at risk\nof timeout", color: C.coral },
  ];

  const statW = 2.05, statH = 1.4;
  const statGap = 0.25, statStartX = 0.5, statY = 1.25;

  stats.forEach((st, i) => {
    const sx = statStartX + i * (statW + statGap);
    s.addShape(pres.shapes.RECTANGLE, { x: sx, y: statY, w: statW, h: statH, fill: { color: C.cardBg }, shadow: cardShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: sx, y: statY, w: statW, h: 0.05, fill: { color: st.color } });
    s.addText(st.value, { x: sx + 0.1, y: statY + 0.1, w: statW - 0.2, h: 0.55, fontSize: 26, fontFace: "Arial", bold: true, color: st.color, align: "center", margin: 0 });
    s.addText(st.label, { x: sx + 0.1, y: statY + 0.7, w: statW - 0.2, h: 0.55, fontSize: 12, fontFace: "Calibri", color: C.textMuted, align: "center", lineSpacingMultiple: 1.2, margin: 0 });
  });

  // 2 feature cards + 1 screenshot placeholder
  const features = [
    { title: "Waiting Room Analytics", items: "Per-level average wait time\nQueue length over time\nPatient flow statistics", color: C.primary },
    { title: "Timeout Prediction", items: "Estimates new patient wait\nFlags exceeding threshold\nPriority inversion detection", color: C.coral },
  ];

  const featW = 2.8, featGap = 0.3, featStartX = 0.5, featY = 2.95;

  features.forEach((f, i) => {
    const fx = featStartX + i * (featW + featGap);
    s.addShape(pres.shapes.RECTANGLE, { x: fx, y: featY, w: featW, h: 2.0, fill: { color: C.cardBg }, shadow: cardShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: fx, y: featY, w: featW, h: 0.45, fill: { color: f.color } });
    s.addText(f.title, { x: fx + 0.15, y: featY, w: featW - 0.3, h: 0.45, fontSize: 13, fontFace: "Arial", bold: true, color: C.white, margin: 0, valign: "middle" });
    s.addText(f.items, { x: fx + 0.15, y: featY + 0.6, w: featW - 0.3, h: 1.25, fontSize: 11, fontFace: "Calibri", color: C.textBody, lineSpacingMultiple: 1.4, margin: 0, valign: "top" });
  });

  // Screenshot placeholder: performance comparison chart
  const imgX = featStartX + 2 * (featW + featGap); // 0.5 + 2*3.1 = 6.7
  s.addShape(pres.shapes.RECTANGLE, { x: imgX, y: featY, w: 2.8, h: 2.0, fill: { color: C.highlight }, line: { color: C.border, width: 1.5, dashType: "dash" }, shadow: cardShadow() });
  s.addText([
    { text: "📷", options: { fontSize: 28, breakLine: true, align: "center" } },
    { text: "Insert: results/performance_comparison.png", options: { fontSize: 11, bold: true, breakLine: true, align: "center" } },
    { text: "Heap vs Ordered Linked Queue\nbenchmark chart", options: { fontSize: 10, color: C.textMuted, align: "center" } },
  ], { x: imgX + 0.15, y: featY + 0.25, w: 2.5, h: 1.5, fontFace: "Calibri", color: C.primaryDark, lineSpacingMultiple: 1.3, margin: 0, valign: "middle" });
}

// ============================================================
// Slide 8 — Flask Dashboard
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.contentBg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.primary } });
  s.addText("08", { x: 0.5, y: 0.25, w: 0.5, h: 0.35, fontSize: 11, fontFace: "Calibri", bold: true, color: C.primary });
  s.addText("Flask Dashboard Design", { x: 0.5, y: 0.5, w: 9, h: 0.55, fontSize: 30, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  // Top bar
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.2, w: 9, h: 0.65, fill: { color: C.primary } });
  s.addText("Hospital Triage Dashboard — Real-time Monitoring", { x: 0.7, y: 1.2, w: 8.6, h: 0.65, fontSize: 16, fontFace: "Arial", bold: true, color: C.white, valign: "middle", margin: 0 });

  // 4 summary cards
  const cards = [
    { label: "Total Patients", val: "N", color: C.primary },
    { label: "Waiting Now", val: "M", color: C.primaryDark },
    { label: "Avg Wait", val: "W min", color: C.green },
    { label: "At Risk", val: "R", color: C.coral },
  ];

  cards.forEach((c, i) => {
    const cx = 0.5 + i * 2.3;
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: 2.05, w: 2.05, h: 0.9, fill: { color: C.cardBg }, shadow: cardShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: 2.05, w: 2.05, h: 0.05, fill: { color: c.color } });
    s.addText(c.val, { x: cx + 0.1, y: 2.05, w: 1.85, h: 0.5, fontSize: 24, fontFace: "Arial", bold: true, color: c.color, align: "center", valign: "middle", margin: 0 });
    s.addText(c.label, { x: cx + 0.1, y: 2.55, w: 1.85, h: 0.3, fontSize: 10, fontFace: "Calibri", color: C.textMuted, align: "center", margin: 0 });
  });

  // Content panels
  // Left: Queue
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.15, w: 4.3, h: 1.7, fill: { color: C.cardBg }, shadow: cardShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.15, w: 4.3, h: 0.4, fill: { color: C.primaryDark } });
  s.addText("Waiting Queue (Heap)", { x: 0.7, y: 3.15, w: 3.9, h: 0.4, fontSize: 13, fontFace: "Arial", bold: true, color: C.white, valign: "middle", margin: 0 });
  s.addText("Real-time patient queue ordered by priority.\nShows patient ID, triage level, estimated wait.\nHighlights patients approaching their threshold.", {
    x: 0.7, y: 3.7, w: 3.9, h: 0.95, fontSize: 11, fontFace: "Calibri", color: C.textBody, lineSpacingMultiple: 1.4, margin: 0,
  });

  // Right: Screenshot placeholder
  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 3.15, w: 4.3, h: 1.7, fill: { color: C.highlight }, line: { color: C.border, width: 1.5, dashType: "dash" }, shadow: cardShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 3.15, w: 4.3, h: 0.4, fill: { color: C.coral } });
  s.addText("📷 Dashboard Screenshot", { x: 5.4, y: 3.15, w: 3.9, h: 0.4, fontSize: 13, fontFace: "Arial", bold: true, color: C.white, valign: "middle", margin: 0 });
  s.addText([
    { text: "Start the dashboard:", options: { bold: true, breakLine: true } },
    { text: "  python visualization/gui.py", options: { fontFace: "Consolas", breakLine: true, color: C.primaryDark } },
    { text: "Then screenshot the browser window", options: { breakLine: true } },
    { text: "and insert here.", options: {} },
  ], { x: 5.4, y: 3.7, w: 3.9, h: 0.95, fontSize: 11, fontFace: "Calibri", color: C.textBody, lineSpacingMultiple: 1.4, margin: 0 });

  // File references
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.95, w: 9, h: 0.32, fill: { color: C.highlight } });
  s.addText("visualization/gui.py  ·  dashboard_data.py  ·  templates/dashboard.html  ·  static/dashboard.css", {
    x: 0.7, y: 4.95, w: 8.6, h: 0.32, fontSize: 9, fontFace: "Consolas", color: C.primaryDark, valign: "middle", margin: 0,
  });
}

// ============================================================
// Slide 9 — Testing & Validation
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.contentBg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.primary } });
  s.addText("09", { x: 0.5, y: 0.25, w: 0.5, h: 0.35, fontSize: 11, fontFace: "Calibri", bold: true, color: C.primary });
  s.addText("Testing & Validation", { x: 0.5, y: 0.5, w: 9, h: 0.55, fontSize: 30, fontFace: "Arial", bold: true, color: C.textDark, margin: 0 });

  // BIG stat callout - left
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.25, w: 3.5, h: 2.4, fill: { color: C.primary } });
  s.addText("47", { x: 0.5, y: 1.35, w: 3.5, h: 1.1, fontSize: 68, fontFace: "Arial", bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
  s.addText("Tests Passed", { x: 0.5, y: 2.35, w: 3.5, h: 0.45, fontSize: 18, fontFace: "Arial", bold: true, color: C.primaryLight, align: "center", margin: 0 });
  s.addText("python -m unittest\ndiscover -s tests", { x: 0.5, y: 2.75, w: 3.5, h: 0.55, fontSize: 10, fontFace: "Consolas", color: C.white, align: "center", margin: 0, lineSpacingMultiple: 1.2 });

  // Right stats (2 rows)
  const testStats = [
    { big: "7", small: "test directories", detail: "models, structures, queues, data, simulation, analysis, visualization" },
    { big: "18", small: "test files — 0 failures", detail: "Edge cases: empty queue, single element, same priority, etc." },
  ];

  testStats.forEach((ts, i) => {
    const ty = 1.25 + i * 1.1;
    s.addShape(pres.shapes.RECTANGLE, { x: 4.3, y: ty, w: 5.2, h: 0.95, fill: { color: C.cardBg }, shadow: cardShadow() });
    s.addText(ts.big, { x: 4.45, y: ty, w: 0.7, h: 0.95, fontSize: 36, fontFace: "Arial", bold: true, color: C.primary, align: "center", valign: "middle", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 5.25, y: ty + 0.15, w: 0.04, h: 0.65, fill: { color: C.border } });
    s.addText([
      { text: ts.small, options: { bold: true, fontSize: 14, breakLine: true } },
      { text: ts.detail, options: { fontSize: 11, color: C.textMuted } },
    ], { x: 5.45, y: ty + 0.08, w: 3.85, h: 0.79, fontFace: "Calibri", color: C.textDark, lineSpacingMultiple: 1.2, margin: 0, valign: "middle" });
  });

  // Screenshot placeholder: test terminal output
  s.addShape(pres.shapes.RECTANGLE, { x: 4.3, y: 3.55, w: 5.2, h: 0.95, fill: { color: C.highlight }, line: { color: C.border, width: 1.5, dashType: "dash" }, shadow: cardShadow() });
  s.addText([
    { text: "📷 Insert: terminal test output screenshot", options: { bold: true, fontSize: 12, breakLine: true } },
    { text: "Run: python -m unittest discover -s tests -v", options: { fontSize: 10, fontFace: "Consolas", color: C.primaryDark } },
  ], { x: 4.5, y: 3.6, w: 4.8, h: 0.85, fontFace: "Calibri", color: C.textBody, lineSpacingMultiple: 1.3, margin: 0, valign: "middle" });

  // Bottom bar
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.6, w: 9, h: 0.6, fill: { color: C.greenLight } });
  s.addText([
    { text: "Test quality: ", options: { bold: true } },
    { text: "Covers empty queues, single-element cases, same-priority ordering, linked-list edge cases, simulation workflows, CSV round-trips, and dashboard data API.", options: {} },
  ], { x: 0.75, y: 4.6, w: 8.5, h: 0.6, fontSize: 12, fontFace: "Calibri", color: C.textDark, valign: "middle", margin: 0 });
}

// ============================================================
// Slide 10 — Conclusion & Future Work (Dark)
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.darkBg };

  // Decorative circles
  s.addShape(pres.shapes.OVAL, { x: -1.2, y: 3.5, w: 3.5, h: 3.5, fill: { color: C.darkBg2, transparency: 30 } });
  s.addShape(pres.shapes.OVAL, { x: 7.5, y: -1.0, w: 3.5, h: 3.5, fill: { color: C.darkBg2, transparency: 40 } });

  // Title
  s.addText("Conclusion & Future Work", { x: 0.7, y: 0.4, w: 8.6, h: 0.65, fontSize: 32, fontFace: "Arial", bold: true, color: C.white, margin: 0 });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 1.05, w: 1.0, h: 0.05, fill: { color: C.coral } });

  // Left: What We Built
  s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 1.35, w: 4.1, h: 3.4, fill: { color: C.darkBg2, transparency: 20 } });
  s.addText("What We Built", { x: 0.95, y: 1.4, w: 3.6, h: 0.4, fontSize: 18, fontFace: "Arial", bold: true, color: C.primaryLight, margin: 0 });
  s.addText([
    { text: "Modular patient model with 4-level triage", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "Custom heap + ordered linked priority queues", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "CSV-driven data pipeline (not hard-coded)", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "Shift simulation with compliance checking", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "Wait analytics + timeout risk prediction", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "Flask dashboard with real-time updates", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "47 unit tests across 7 test directories", options: { bullet: true } },
  ], { x: 0.95, y: 1.9, w: 3.6, h: 2.7, fontSize: 12, fontFace: "Calibri", color: C.white, lineSpacingMultiple: 1.1, margin: 0, valign: "top" });

  // Right: Future Work
  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.35, w: 4.1, h: 3.4, fill: { color: C.darkBg2, transparency: 20 } });
  s.addText("Future Work", { x: 5.45, y: 1.4, w: 3.6, h: 0.4, fontSize: 18, fontFace: "Arial", bold: true, color: C.primaryLight, margin: 0 });
  s.addText([
    { text: "Larger-scale datasets for stress testing", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "More interactive dashboard controls", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "Database backend (SQLite / PostgreSQL)", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "Machine learning priority prediction", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "Containerized deployment (Docker)", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "Multi-shift scheduling optimization", options: { bullet: true } },
  ], { x: 5.45, y: 1.9, w: 3.6, h: 2.7, fontSize: 12, fontFace: "Calibri", color: C.white, lineSpacingMultiple: 1.1, margin: 0, valign: "top" });

  // Bottom line + tagline
  s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 4.95, w: 8.6, h: 0.05, fill: { color: C.coral } });
  s.addText("Hospital Triage Scheduler — Data Structures & Algorithms Course Project", {
    x: 0.7, y: 5.1, w: 8.6, h: 0.35, fontSize: 13, fontFace: "Calibri", color: C.textMuted, align: "center", margin: 0,
  });
}

// ============================================================
// Write File
// ============================================================
pres.writeFile({ fileName: "c:/Users/fjzda/Desktop/hospital-team1/Hospital_Triage_Presentation.pptx" })
  .then(() => console.log("SUCCESS: Presentation saved."))
  .catch(err => console.error("ERROR:", err));
