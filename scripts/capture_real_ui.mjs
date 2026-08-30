import { chromium } from "C:/Users/hp/Downloads/veto video/demo/node_modules/playwright/index.js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outputDir = path.join(__dirname, "../docs/screenshots");

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

async function capture() {
  console.log("Launching Chromium browser...");
  const browser = await chromium.launch({
    executablePath: "C:/Users/hp/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe",
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 2, // 2x scale for 3840x2160 UHD crispness
  });

  const page = await context.newPage();

  // 1. Landing Page Hero & Problem
  console.log("Capturing Landing Page...");
  await page.goto("http://localhost:3000", { waitUntil: "domcontentloaded", timeout: 15000 });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(outputDir, "real_landing_hero.png"), fullPage: false });

  // 2. Landing Fleet & Architecture
  await page.evaluate(() => window.scrollBy(0, 1100));
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(outputDir, "real_landing_fleet.png"), fullPage: false });

  // 3. Dashboard Overview & Metrics
  console.log("Capturing Dashboard...");
  await page.goto("http://localhost:3000/dashboard", { waitUntil: "domcontentloaded", timeout: 15000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(outputDir, "real_dashboard_overview.png") });

  // 4. Trigger Storm Response Simulation
  console.log("Triggering Storm Response Simulation...");
  try {
    const simButton = await page.$("button:has-text('Simulate Storm Response')");
    if (simButton) {
      await simButton.click();
      console.log("Clicked Simulate Storm Response button!");
      await page.waitForTimeout(4000); // Allow cascading websocket events to arrive
      await page.screenshot({ path: path.join(outputDir, "real_dashboard_simulating.png") });
    }
  } catch (e) {
    console.log("Simulate click notice:", e);
  }

  // 5. Approvals Queue
  console.log("Capturing Approvals Page...");
  await page.goto("http://localhost:3000/dashboard/approvals", { waitUntil: "domcontentloaded", timeout: 15000 });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(outputDir, "real_governance_approvals.png") });

  // 6. Memory Bank
  console.log("Capturing Memory Bank Page...");
  await page.goto("http://localhost:3000/dashboard/memory", { waitUntil: "domcontentloaded", timeout: 15000 });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(outputDir, "real_memory_bank.png") });

  // 7. Traces
  console.log("Capturing Traces Page...");
  await page.goto("http://localhost:3000/dashboard/traces", { waitUntil: "domcontentloaded", timeout: 15000 });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(outputDir, "real_traces_observability.png") });

  // 8. Campus Topology
  console.log("Capturing Campus Page...");
  await page.goto("http://localhost:3000/dashboard/campus", { waitUntil: "domcontentloaded", timeout: 15000 });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(outputDir, "real_campus_topology.png") });

  // 9. Agent Fleet
  console.log("Capturing Agent Fleet Page...");
  await page.goto("http://localhost:3000/dashboard/agents", { waitUntil: "domcontentloaded", timeout: 15000 });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(outputDir, "real_agent_fleet.png") });

  await browser.close();
  console.log("All real UI states captured successfully into docs/screenshots!");
}

capture().catch((err) => {
  console.error("Capture error:", err);
  process.exit(1);
});
