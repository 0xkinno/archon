const { chromium } = require("C:/Users/hp/Downloads/veto video/demo/node_modules/playwright");
const path = require("path");
const fs = require("fs");

async function renderDiagram() {
  const browser = await chromium.launch({
    executablePath: "C:/Users/hp/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe",
    headless: true
  });
  const page = await browser.newPage({
    viewport: { width: 1400, height: 780 },
    deviceScaleFactor: 2
  });

  const svgPath = path.resolve(__dirname, "../docs/diagrams/archon-architecture.svg");
  const svgContent = fs.readFileSync(svgPath, "utf8");

  await page.setContent(`
    <!DOCTYPE html>
    <html>
      <body style="margin:0; padding:0; background:#070B14; display:flex; justify-content:center; align-items:center;">
        ${svgContent}
      </body>
    </html>
  `);

  const previewDir = path.resolve(__dirname, "../docs/diagrams/preview");
  if (!fs.existsSync(previewDir)) {
    fs.mkdirSync(previewDir, { recursive: true });
  }

  const outDark = path.resolve(previewDir, "architecture.dark.png");
  const outLight = path.resolve(previewDir, "architecture.light.png");

  await page.screenshot({ path: outDark });
  fs.copyFileSync(outDark, outLight);
  console.log("Successfully rendered diagram screenshots to", outDark);
  await browser.close();
}

renderDiagram().catch(err => {
  console.error("Render error:", err);
  process.exit(1);
});
