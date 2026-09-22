import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const docs = fileURLToPath(new URL("../docs/", import.meta.url));
const types = new Map([
  [".css", "text/css; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".mjs", "text/javascript; charset=utf-8"],
  [".svg", "image/svg+xml"],
]);

const server = createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
    const relative = pathname === "/" ? "index.html" : pathname.slice(1);
    const file = normalize(join(docs, relative));
    if (!file.startsWith(docs)) throw new Error("path outside document root");
    const body = await readFile(file);
    response.writeHead(200, { "Content-Type": types.get(extname(file)) ?? "application/octet-stream" });
    response.end(body);
  } catch {
    response.writeHead(404).end("Not found");
  }
});

await new Promise((resolve, reject) => {
  server.once("error", reject);
  server.listen(0, "127.0.0.1", resolve);
});

const browser = await chromium.launch();
const page = await browser.newPage();
const failures = [];
page.on("console", (message) => {
  if (message.type() === "error") failures.push(`console: ${message.text()}`);
});
page.on("pageerror", (error) => failures.push(`page: ${error.message}`));

try {
  const { port } = server.address();
  await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: "networkidle" });

  await page.locator("#img-run").waitFor({ state: "visible" });
  await assertCanvasChanged(page, "#img-original");
  await assertCanvasChanged(page, "#img-ecb");
  await assertCanvasChanged(page, "#img-cbc");
  await assertCanvasChanged(page, "#img-gcm");

  await page.click("#blk-ecb");
  await assertText(page, "#blk-verdict", "ECB pattern leakage active");
  assert.ok(await page.locator("#blk-out .match").count() >= 2, "ECB repeats must be highlighted");

  await page.click("#blk-cbc");
  await assertText(page, "#blk-verdict", "no repeats");

  await page.click("#eq-run");
  await assertText(page, "#eq-verdict", "alice + carol");
  await assertText(page, "#eq-verdict", "bob + erin");
  await page.locator("#users-in").fill("__proto__: same\n__proto__: same\nconstructor: different");
  await page.click("#eq-run");
  assert.equal(await page.locator("#eq-out tbody tr").count(), 3, "duplicate and prototype-like names must be preserved");
  await assertText(page, "#eq-verdict", "__proto__ + __proto__");

  await page.click("#orc-run");
  await page.waitForFunction(() => !document.querySelector("#orc-run").disabled);
  await assertText(page, "#orc-verdict", "4,588 oracle queries");

  await page.click("#frg-issue");
  await assertText(page, "#frg-verdict", "role = user");
  await page.click("#frg-forge");
  await assertText(page, "#frg-verdict", "role = admin");

  await page.click("#gcm-run");
  await page.waitForFunction(() => !document.querySelector("#gcm-run").disabled);
  await assertText(page, "#gcm-verdict", "Vector 4 closed");
  await assertText(page, "#gcm-out", "no plaintext was returned");
  await assertText(page, "#gcm-out", "role=user");

  assert.deepEqual(failures, [], "the page must not emit console or runtime errors");
} finally {
  await browser.close();
  await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
}

async function assertText(page, selector, expected) {
  const text = await page.locator(selector).innerText();
  assert.match(text, new RegExp(expected.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i"));
}

async function assertCanvasChanged(page, selector) {
  const changed = await page.locator(selector).evaluate((canvas) => {
    const pixels = canvas.getContext("2d").getImageData(0, 0, canvas.width, canvas.height).data;
    return pixels.some((byte) => byte !== 0);
  });
  assert.equal(changed, true, `${selector} must contain rendered pixels`);
}
