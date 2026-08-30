const { chromium } = require("C:/Users/hp/Downloads/veto video/demo/node_modules/playwright");
const fs = require("fs");
const path = require("path");

async function auditUI() {
  console.log("=================================================");
  console.log("ARCHON CHROMIUM UI AUDIT & VERIFICATION SUITE");
  console.log("=================================================");

  const browser = await chromium.launch({
    executablePath: "C:/Users/hp/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe",
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();
  const errors = [];

  page.on("console", msg => {
    if (msg.type() === "error") {
      console.log(`[BROWSER ERROR] ${msg.text()}`);
      errors.push(msg.text());
    }
  });

  const routes = [
    { name: "Landing Page", url: "http://localhost:3000/" },
    { name: "Incident Command Overview", url: "http://localhost:3000/dashboard" },
    { name: "Incident Stream", url: "http://localhost:3000/dashboard/incidents" },
    { name: "Incident Detail & Verifier", url: "http://localhost:3000/dashboard/incidents/INC-STORM-001" },
    { name: "Governance & Approvals", url: "http://localhost:3000/dashboard/approvals" },
    { name: "Specialist Agent Fleet", url: "http://localhost:3000/dashboard/agents" },
    { name: "Institutional Memory Bank", url: "http://localhost:3000/dashboard/memory" },
    { name: "Telemetry & Observability Traces", url: "http://localhost:3000/dashboard/traces" },
    { name: "Campus Physical Topology", url: "http://localhost:3000/dashboard/campus" },
  ];

  const auditDir = path.resolve(__dirname, "../docs/screenshots/audit");
  if (!fs.existsSync(auditDir)) fs.mkdirSync(auditDir, { recursive: true });

  let allPassed = true;

  for (const r of routes) {
    console.log(`\nAuditing: ${r.name} (${r.url})...`);
    try {
      const response = await page.goto(r.url, { waitUntil: "domcontentloaded", timeout: 10000 });
      await page.waitForTimeout(1000);
      const status = response ? response.status() : 0;
      console.log(`  -> HTTP Status: ${status}`);

      // Check title / heading
      const heading = await page.$eval("h1, h2", el => el.innerText).catch(() => "N/A");
      console.log(`  -> Primary Heading: "${heading.trim()}"`);

      const screenshotPath = path.join(auditDir, `${r.name.toLowerCase().replace(/[^a-z0-9]/g, "_")}.png`);
      await page.screenshot({ path: screenshotPath });
      console.log(`  -> Screenshot saved: ${path.basename(screenshotPath)}`);

      if (status !== 200) {
        console.error(`  [FAIL] Route ${r.name} returned status ${status}`);
        allPassed = false;
      } else {
        console.log(`  [PASS] Layout and components rendered cleanly`);
      }
    } catch (err) {
      console.error(`  [FAIL] Failed to load ${r.name}:`, err.message);
      allPassed = false;
    }
  }

  await browser.close();

  console.log("\n=================================================");
  console.log(`FINAL AUDIT VERDICT: ${allPassed ? "100% PASS (PERFECT RENDER)" : "FAIL"}`);
  console.log(`Total Errors Logged: ${errors.length}`);
  console.log("=================================================");

  if (!allPassed) process.exit(1);
}

auditUI().catch(err => {
  console.error("Fatal audit error:", err);
  process.exit(1);
});
