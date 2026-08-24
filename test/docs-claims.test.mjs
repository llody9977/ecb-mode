// Deterministic guards over claims that live in the prose and the diagrams.
//
// Every one of these encodes a finding from a documentation review, so the same
// fault fails CI instead of waiting to be rediscovered by hand. A claim rendered
// inside an SVG is invisible to a grep over the prose, so each check reads every
// surface the claim appears on — page, alt text, generator, and rendered figure.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const root = new URL("../", import.meta.url);
const read = (p) => readFileSync(fileURLToPath(new URL(p, root)), "utf8");

const INDEX = read("docs/index.html");
const GENERATOR = read("docs/diagrams/generate_diagrams.py");
const VECTOR3_SVG = read("docs/diagrams/vector3-byte-at-a-time.svg");
const MODES_SVG = read("docs/diagrams/modes-ecb-cbc-gcm.svg");
const UI = read("docs/js/ui.mjs");
const ATTACKS = read("docs/js/attacks.mjs");

// Finding: the attack cost was stated as 256 x L on the page, in the diagram alt
// text, and inside the rendered SVG. The implementation spends 257 x L plus setup,
// so the demo's own counter — which the page invites the reader to check — exceeds
// the stated bound. test/attacks.test.mjs proves the real bound; this proves the
// documents agree with it, on every surface the number appears.
test("the 257 x L query bound is stated consistently and 256 x L is gone", () => {
  for (const [name, text] of [["index.html", INDEX], ["generate_diagrams.py", GENERATOR], ["vector3 svg", VECTOR3_SVG]]) {
    assert.match(text, /257\s*(?:×|x)\s*L/, `${name} must state the 257 x L bound`);
  }
  // The page names 256 legitimately ("try all 256 values"), so only reject it
  // where it is being used as a per-secret cost bound.
  const asBound = /256\s*(?:×|x)\s*L|12,?288/;
  for (const [name, text] of [["index.html", INDEX], ["generate_diagrams.py", GENERATOR], ["vector3 svg", VECTOR3_SVG]]) {
    assert.doesNotMatch(text, asBound, `${name} still states the superseded 256 x L / 12,288 bound`);
  }
  assert.match(INDEX, /12,370/, "index.html must state the corrected 48-byte worst case");
  assert.match(INDEX, /4,588/, "index.html must state the exact default-secret query count");
});

// Finding: the CBC row of the modes figure said only "XORs each block with the
// previous ciphertext". The figure draws P1, which has no previous ciphertext —
// it is XORed with the IV, and a fresh IV per message is what actually stops the
// repeat. Detached from the page the figure has to name the IV itself.
test("the modes figure names the IV and carries its freshness qualifier", () => {
  for (const [name, text] of [["generate_diagrams.py", GENERATOR], ["modes svg", MODES_SVG]]) {
    assert.match(text, /fresh random IV per message/, `${name}'s CBC row must name the IV`);
    assert.match(text, /IV \/ nonce is fresh/, `${name} must carry the reuse qualifier for detached reading`);
  }
});

// Finding: bcrypt was described as memory-hard. Its working set is a fixed ~4 KiB,
// so its cost parameter scales time, not memory.
test("bcrypt is not described as memory-hard", () => {
  assert.doesNotMatch(INDEX, /memory-hard scheme\s*—\s*Argon2id, scrypt, or bcrypt/,
    "bcrypt must not be grouped under 'memory-hard'");
  assert.match(INDEX, /time-hard rather than a memory-hard function/,
    "the bcrypt qualification must stay explicit");
});

// Finding: the page said the AEAD fix "addresses the other three vectors, not
// password storage", contradicting its own statements that a nonce defeats the
// determinism Vectors 1-3 rely on and that GCM defeats all four.
test("the page does not claim AEAD leaves Vector 2 unaddressed", () => {
  assert.doesNotMatch(INDEX, /addresses the other three vectors, not password storage/);
  assert.match(INDEX, /GCM defeats all four vectors/);
});

// Finding: encryptPixels() was exported and documented as the Vector 1
// implementation but imported by nothing, while ui.mjs kept an inline duplicate —
// leaving the page's headline demo as the only vector without a test.
test("the image demo uses the tested encryptPixels() rather than an inline copy", () => {
  assert.match(UI, /import \{[^}]*\bencryptPixels\b[^}]*\} from "\.\/attacks\.mjs"/s,
    "ui.mjs must import encryptPixels from attacks.mjs");
  assert.match(UI, /await encryptPixels\(/, "runImage must call encryptPixels");
  assert.doesNotMatch(UI, /aesEcbEncrypt\(key, new Uint8Array\(rgba\)/,
    "the inline pixel-encryption duplicate has come back");
});

// Finding: the GCM demo flipped one bit while the page claimed it closed Vector 4,
// which is a cut-and-paste splice. The contrast only holds if the same forge runs
// against both services.
test("the GCM demo runs the Vector 4 splice, not only a bit flip", () => {
  // Match the call, not the identifier: an unused import would satisfy a bare
  // name check while the demo quietly stopped running the splice.
  assert.match(UI, /await forgeUnderBothModes\(/, "runGcm must actually run the splice under both modes");
  assert.doesNotMatch(UI, /Flipping one ciphertext bit[^"]*This is what closes Vector 4/,
    "a bit flip must not be presented as the demonstration that closes Vector 4");
});

// The ECB half of the GCM panel was briefly a hardcoded string sitting beside
// three computed results. On a page whose lede promises every claim has a
// runnable demonstration, an assertion dressed as a measurement is the exact
// defect this panel was rewritten to fix.
test("the GCM panel computes its ECB line rather than asserting it", () => {
  assert.match(UI, /role\(ecbForgedRole\)/, "the ECB outcome must come from a live run");
  assert.doesNotMatch(UI, /tag bad">ECB<\/span><span>[^`]*role\("admin"\)/,
    "the ECB outcome must not be a hardcoded literal");
});

// Finding: forgeAdminToken took the token's header size as a caller argument
// defaulting to 0. Omitting it for a GCM service produced a token that was still
// rejected and still 64 bytes, so no behavioural check could tell the two apart —
// the comparison would have passed while demonstrating something weaker. The
// defect is structural (where the offset comes from), so the guard is structural.
test("forgeAdminToken reads the token layout from the service, not from a caller argument", () => {
  assert.match(ATTACKS, /const headerSize = service\.constructor\.headerSize/,
    "the offset must be read from the service");
  assert.doesNotMatch(ATTACKS, /function forgeAdminToken\(\s*service\s*,/,
    "a caller-supplied offset parameter has been reintroduced");
});

// Finding: "a repeated ciphertext block is sufficient evidence of deterministic,
// block-independent encryption" — across a corpus, constant-IV CBC or nonce-reused
// CTR produces the same signature without being block-independent.
test("the detection claim does not assert repeats are sufficient evidence", () => {
  assert.doesNotMatch(INDEX, /sufficient evidence of deterministic, block-independent encryption/);
  assert.match(INDEX, /constant IV/, "the corpus counterexample must be stated");
});

// Every figure must carry its own scope line, because a figure detaches from the
// page far more readily than prose does.
test("every attack figure carries its own scope line", () => {
  for (const name of ["taxonomy", "vector3-byte-at-a-time", "vector4-cut-and-paste"]) {
    const svg = read(`docs/diagrams/${name}.svg`);
    assert.match(svg, /Scope:/, `${name}.svg must carry a scope line when read detached`);
  }
});

// Alt text is content. It must carry the figure's conclusion at the same strength
// as the prose, not merely exist.
test("every figure has non-trivial alt text", () => {
  const imgs = [...INDEX.matchAll(/<img\s[^>]*alt="([^"]*)"/g)].map((m) => m[1]);
  assert.ok(imgs.length >= 4, `expected at least 4 figures, found ${imgs.length}`);
  for (const alt of imgs) {
    assert.ok(alt.length > 120, `alt text too short to carry the figure's claim: ${alt.slice(0, 60)}…`);
  }
});
