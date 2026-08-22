// Wires the in-page demos to the tested attack logic. No crypto lives here — it
// all comes from crypto.mjs / attacks.mjs, the same code the test suite verifies.
import {
  aesEcbEncrypt, aesCbcEncrypt, aesGcmEncrypt, hasRepeatedBlocks,
  toHex, fromHex, utf8, splitBlocks, BLOCK_SIZE,
} from "./crypto.mjs";
import {
  equalityInference, makeSuffixOracle, recoverSecret,
  ProfileService, forgeAdminToken, gcmTokenRoundtrip,
} from "./attacks.mjs";

const $ = (id) => document.getElementById(id);
const esc = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
const printable = (b) => [...b].map((x) => (x >= 32 && x < 127 ? String.fromCharCode(x) : "·")).join("");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// key input: 32-hex => raw bytes; otherwise a passphrase zero-padded to 16 bytes
// (demonstration key handling only — never a real KDF; an empty box is all-zero).
function readKey(value) {
  const v = value.trim();
  if (/^[0-9a-fA-F]{32}$/.test(v)) return fromHex(v);
  const out = new Uint8Array(16);
  out.set(utf8(v).slice(0, 16));
  return out;
}
function verdict(el, kind, html) { el.className = `verdict show ${kind}`; el.innerHTML = html; }

// ---------- Vector 1a: image ----------
function drawBitmap(canvas) {
  const ctx = canvas.getContext("2d");
  const { width: w, height: h } = canvas;
  ctx.fillStyle = "#e6e9ef"; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = "#0f2d5a"; ctx.beginPath(); ctx.arc(w / 2, h / 2, w / 2 - 4, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = "#e6e9ef"; ctx.fillRect(w / 2 - 12, h / 2 - 22, 24, 44);
  ctx.strokeStyle = "#c0392b"; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(w / 2, 12); ctx.lineTo(w - 16, h / 2); ctx.lineTo(w / 2, h - 12); ctx.lineTo(16, h / 2); ctx.closePath(); ctx.stroke();
}
function putBytes(canvas, rgba) {
  const ctx = canvas.getContext("2d");
  ctx.putImageData(new ImageData(new Uint8ClampedArray(rgba), canvas.width, canvas.height), 0, 0);
}
async function runImage() {
  const btn = $("img-run"); btn.disabled = true; btn.textContent = "Encrypting…";
  const orig = $("img-original"); drawBitmap(orig);
  const rgba = orig.getContext("2d").getImageData(0, 0, orig.width, orig.height).data;
  const key = crypto.getRandomValues(new Uint8Array(16));
  const len = rgba.length;
  const ecb = (await aesEcbEncrypt(key, new Uint8Array(rgba), true)).slice(0, len);
  const cbc = (await aesCbcEncrypt(key, new Uint8Array(rgba))).ciphertext.slice(0, len);
  const gcm = (await aesGcmEncrypt(key, new Uint8Array(rgba))).ciphertext.slice(0, len);
  // force alpha opaque so the structure is visible, not modulated by random alpha
  for (const buf of [ecb, cbc, gcm]) for (let i = 3; i < buf.length; i += 4) buf[i] = 255;
  putBytes($("img-ecb"), ecb); putBytes($("img-cbc"), cbc); putBytes($("img-gcm"), gcm);
  btn.disabled = false; btn.textContent = "Regenerate & encrypt";
}

// ---------- Vector 1b: block playground ----------
function renderBlocks(container, ciphertext, { safe = false } = {}) {
  const blocks = splitBlocks(ciphertext).map(toHex);
  const counts = blocks.reduce((m, h) => (m.set(h, (m.get(h) || 0) + 1), m), new Map());
  container.innerHTML = blocks.map((h, i) =>
    `<div class="blk ${!safe && counts.get(h) > 1 ? "match" : ""} ${safe ? "safe" : ""}">
       <div class="blk-label">Block ${i + 1}</div>
       <div class="blk-hex">${h}</div>
       <div class="blk-tag">⚠ identical block</div>
     </div>`).join("");
}
async function runBlockEcb() {
  const pt = utf8($("pt-in").value); const key = readKey($("key-in").value);
  const ct = await aesEcbEncrypt(key, pt);
  renderBlocks($("blk-out"), ct);
  const leaks = hasRepeatedBlocks(ct);
  verdict($("blk-verdict"), leaks ? "bad" : "good",
    leaks ? "<strong>ECB pattern leakage active.</strong> Identical plaintext blocks produced identical ciphertext blocks — highlighted above. An observer learns which blocks repeat without any key."
          : "No repeated blocks in <em>this</em> sample — but that only means this plaintext had no repeats. Try the default (four identical blocks); ECB will leak them every time.");
}
function blocksHtml(ciphertext) {
  return `<div class="blocks">${splitBlocks(ciphertext).map((b, i) =>
    `<div class="blk safe"><div class="blk-label">Block ${i + 1}</div><div class="blk-hex">${toHex(b)}</div></div>`).join("")}</div>`;
}
async function runBlockCompare() {
  const pt = utf8($("pt-in").value); const key = readKey($("key-in").value);
  const cbc = (await aesCbcEncrypt(key, pt)).ciphertext;
  const gcm = (await aesGcmEncrypt(key, pt)).ciphertext;
  $("blk-out").innerHTML =
    `<div style="width:100%"><strong style="color:var(--green)">AES-CBC (random IV)</strong>${blocksHtml(cbc)}</div>` +
    `<div style="width:100%;margin-top:10px"><strong style="color:var(--green)">AES-GCM (AEAD)</strong>${blocksHtml(gcm)}</div>`;
  verdict($("blk-verdict"), "good", "<strong>Same plaintext, same key — no repeats.</strong> CBC's per-block chaining and GCM's per-message nonce both destroy the equal-in/equal-out property.");
}

// ---------- Vector 2: equality inference ----------
async function runEquality() {
  const users = {};
  for (const line of $("users-in").value.split("\n")) {
    const i = line.indexOf(":"); if (i < 0) continue;
    const name = line.slice(0, i).trim(); const pw = line.slice(i + 1).trim();
    if (name) users[name] = pw;
  }
  const { rows, clusters } = await equalityInference(users);
  const shared = new Map();
  clusters.forEach((g, gi) => g.forEach((n) => shared.set(n, gi)));
  const palette = ["#dc2626", "#6d28d9", "#b45309", "#2563eb"];
  const out = $("eq-out"); out.style.display = "block";
  out.innerHTML = `<table><thead><tr><th>User</th><th>Password</th><th>Ciphertext (AES-ECB)</th></tr></thead><tbody>${
    rows.map((r) => {
      const gi = shared.get(r.name);
      const color = gi != null ? palette[gi % palette.length] : "";
      const dot = gi != null ? `<span style="color:${color}">● </span>` : "";
      return `<tr><td>${dot}${esc(r.name)}</td><td>${esc(r.password)}</td><td class="tok" style="${gi != null ? `color:${color}` : ""}">${r.cipherHex.slice(0, 32)}…</td></tr>`;
    }).join("")}</tbody></table>`;
  const desc = clusters.map((g) => g.join(" + ")).join("; ");
  verdict($("eq-verdict"), clusters.length ? "bad" : "good",
    clusters.length ? `<strong>Shared passwords found with zero decryption:</strong> ${esc(desc)}. Matching ciphertext ⇒ matching password.`
                    : "No two users share a password here, so no ciphertext collides — add a duplicate to see the clustering.");
}

// ---------- Vector 3: byte-at-a-time ----------
let oracleRunning = false;
// Show the current 16-byte target block: `padLen` filler A's, then the bytes
// recovered so far that live in this block (newest highlighted).
function renderCells(container, padLen, recovered, blockIndex, index) {
  const known = recovered.slice(blockIndex * BLOCK_SIZE, index + 1);
  const cells = [];
  for (let i = 0; i < padLen; i++) cells.push('<div class="cell">A</div>');
  known.forEach((b, i) => cells.push(`<div class="cell ${i === known.length - 1 ? "unknown" : "known"}">${esc(printable([b]))}</div>`));
  container.innerHTML = cells.join("");
}
async function runOracle() {
  if (oracleRunning) return; oracleRunning = true;
  const btn = $("orc-run"); btn.disabled = true;
  const secret = utf8($("secret-in").value);
  const oracle = makeSuffixOracle(secret);
  $("orc-recovered").innerHTML = '<span class="cursor">▋</span>';
  $("orc-verdict").className = "verdict"; let queries = 0;
  const wrapped = (input) => { queries++; return oracle(input); };
  const recovered = await recoverSecret(wrapped, {
    onStep: async ({ recovered, padLen, blockIndex, index }) => {
      renderCells($("orc-cells"), padLen, recovered, blockIndex, index);
      $("orc-recovered").innerHTML = esc(printable(recovered)) + '<span class="cursor">▋</span>';
      $("orc-status").textContent = `${recovered.length} / ${secret.length} bytes · ${queries} oracle queries`;
      await sleep(28);
    },
  });
  $("orc-recovered").textContent = printable(recovered);
  const ok = toHex(recovered) === toHex(secret);
  verdict($("orc-verdict"), ok ? "bad" : "good",
    ok ? `<strong>Full secret recovered from ciphertext alone</strong> in ${queries} oracle queries — the key was never exposed.`
       : "Recovery stopped early (unexpected for this oracle).");
  btn.disabled = false; oracleRunning = false;
}

// ---------- Vector 4: cut-and-paste ----------
const service = new ProfileService();
function blockStrip(ct, highlightIdx) {
  return `<div class="blocks">${splitBlocks(ct).map((b, i) =>
    `<div class="blk ${i === highlightIdx ? "match" : ""}"><div class="blk-label">block ${i}</div><div class="blk-hex">${toHex(b)}</div></div>`).join("")}</div>`;
}
async function issueNormal() {
  const token = await service.issueToken($("email-in").value);
  const role = await service.roleForToken(token);
  $("frg-out").innerHTML = `<strong>Legitimate token issued.</strong>${blockStrip(token)}`;
  verdict($("frg-verdict"), "good", `Server reads role = <strong>${esc(role)}</strong> from this token — as expected.`);
}
async function forge() {
  const forged = await forgeAdminToken(service);
  const role = await service.roleForToken(forged);
  $("frg-out").innerHTML = `<strong>Forged token</strong> — built from two calls to the public <code>issueToken()</code>, no key: the last block is a spliced <code>admin</code> block.${blockStrip(forged, splitBlocks(forged).length - 1)}`;
  verdict($("frg-verdict"), role === "admin" ? "bad" : "good",
    role === "admin" ? "<strong>Privilege escalation.</strong> The server decrypts this and reads role = <strong>admin</strong> — no integrity check to catch the splice."
                     : `Server read role = ${esc(String(role))} (forge did not take).`);
}

// ---------- Defensive: GCM ----------
async function runGcm() {
  const { tamperRejected, decryptedProfile } = await gcmTokenRoundtrip($("email-in").value);
  $("gcm-out").innerHTML = `Clean decrypt → <code>${esc(decryptedProfile)}</code>`;
  verdict($("gcm-verdict"), "good",
    tamperRejected ? "<strong>Tamper rejected.</strong> Flipping one ciphertext bit made GCM's authentication tag fail — decryption raised before any role could be read. This is what closes Vector 4."
                   : "Unexpected: tamper was not rejected.");
}

// ---------- wire up ----------
addEventListener("DOMContentLoaded", () => {
  $("img-run").addEventListener("click", runImage); runImage();
  $("blk-ecb").addEventListener("click", runBlockEcb);
  $("blk-cbc").addEventListener("click", runBlockCompare);
  $("blk-reset").addEventListener("click", () => {
    $("pt-in").value = "ATTACKATDAWN1234".repeat(4);
    $("key-in").value = "000102030405060708090a0b0c0d0e0f";
    $("blk-out").innerHTML = ""; $("blk-verdict").className = "verdict";
  });
  $("eq-run").addEventListener("click", runEquality);
  $("orc-run").addEventListener("click", runOracle);
  $("frg-issue").addEventListener("click", issueNormal);
  $("frg-forge").addEventListener("click", forge);
  $("gcm-run").addEventListener("click", runGcm);
});
