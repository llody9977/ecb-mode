// The four ECB attack vectors, as testable functions shared by the page demos and
// the test suite. Every function runs against real AES (see crypto.mjs).
//
// Scope: educational / defensive. Every oracle and service here is a self-contained,
// in-process stand-in — there is no network and no third-party system. Do not point
// any of this at a system you do not own or are not authorized to test.

import {
  BLOCK_SIZE, aesEcbEncrypt, aesEcbDecrypt, aesGcmEncrypt, aesGcmDecrypt,
  randomKey, concat, blockAt, bytesEqual, toHex, utf8, latin1Encode, latin1Decode,
} from "./crypto.mjs";

const A = 65; // filler byte 'A'

// ---------------------------------------------------------------------------
// Vector 2 — equality inference: identical plaintext -> identical ciphertext.
// users: { name: password }. Returns clusters of names sharing a password,
// found from ciphertext equality alone (no decryption).
// ---------------------------------------------------------------------------
export async function equalityInference(users, key = randomKey()) {
  const byCipher = new Map();
  const rows = [];
  for (const [name, password] of Object.entries(users)) {
    const ct = await aesEcbEncrypt(key, utf8(password));
    const h = toHex(ct);
    rows.push({ name, password, cipherHex: h });
    if (!byCipher.has(h)) byCipher.set(h, []);
    byCipher.get(h).push(name);
  }
  const clusters = [...byCipher.values()].filter((g) => g.length > 1);
  return { rows, clusters };
}

// ---------------------------------------------------------------------------
// Vector 3 — chosen-plaintext byte-at-a-time recovery.
// A suffix oracle computes ECB(attacker_input || secret). The secret falls one
// byte per ~256 queries, from ciphertext alone. Cryptopals Set 2 Challenge 12.
// ---------------------------------------------------------------------------
export function makeSuffixOracle(secret, key = randomKey()) {
  return (attackerInput) => aesEcbEncrypt(key, concat(attackerInput, secret));
}

export async function detectBlockSize(oracle, maxProbe = 64) {
  const base = (await oracle(new Uint8Array(0))).length;
  for (let i = 1; i < maxProbe; i++) {
    const len = (await oracle(new Uint8Array(i).fill(A))).length;
    if (len > base) return len - base;
  }
  throw new Error("could not detect block size");
}

async function detectSecretLength(oracle, blockSize) {
  const base = (await oracle(new Uint8Array(0))).length;
  for (let filler = 1; filler <= blockSize; filler++) {
    if ((await oracle(new Uint8Array(filler).fill(A))).length > base) return base - filler;
  }
  throw new Error("could not determine secret length");
}

// Recover the oracle's fixed secret suffix, one byte at a time.
// onStep({ index, byte, recovered, blockIndex, padLen }) is awaited after each
// byte so the UI can animate; omit it for a plain synchronous-style recovery.
export async function recoverSecret(oracle, { onStep } = {}) {
  const blockSize = await detectBlockSize(oracle);
  const secretLength = await detectSecretLength(oracle, blockSize);
  const recovered = [];
  for (let i = 0; i < secretLength; i++) {
    const padLen = ((-i - 1) % blockSize + blockSize) % blockSize;
    const blockIndex = Math.floor((i + padLen) / blockSize);
    const filler = new Uint8Array(padLen).fill(A);
    const target = blockAt(await oracle(filler), blockIndex, blockSize);
    let found = null;
    for (let c = 0; c < 256; c++) {
      const probe = concat(filler, Uint8Array.from(recovered), Uint8Array.of(c));
      if (bytesEqual(blockAt(await oracle(probe), blockIndex, blockSize), target)) { found = c; break; }
    }
    if (found === null) break; // ran into the PKCS#7 padding boundary
    recovered.push(found);
    if (onStep) await onStep({ index: i, byte: found, recovered: [...recovered], blockIndex, padLen });
  }
  return Uint8Array.from(recovered);
}

// ---------------------------------------------------------------------------
// Vector 4 — block malleability / cut-and-paste privilege escalation.
// Cryptopals Set 2 Challenge 13.
// ---------------------------------------------------------------------------
export class ProfileService {
  constructor(key = randomKey()) { this.key = key; }

  async issueToken(email) {
    const sanitized = String(email).replace(/[&=]/g, "");
    const profile = `email=${sanitized}&uid=1000&role=user`;
    return aesEcbEncrypt(this.key, latin1Encode(profile));
  }

  async roleForToken(token) {
    let plaintext;
    try { plaintext = await aesEcbDecrypt(this.key, token); } catch { return null; }
    const fields = {};
    for (const pair of latin1Decode(plaintext).split("&")) {
      const j = pair.indexOf("=");
      if (j >= 0) fields[pair.slice(0, j)] = pair.slice(j + 1);
    }
    return fields.role ?? null;
  }
}

// Splice a legitimate token into one that decrypts with role=admin, using only
// the public issueToken() interface — no access to the key.
export async function forgeAdminToken(service) {
  // "email=" (6) + 10-byte local part pushes an "admin"+padding block onto its
  // own 16-byte boundary, isolated as ciphertext block 1.
  const padByte = BLOCK_SIZE - "admin".length; // 11
  const adminBlockPlain = concat(utf8("admin"), new Uint8Array(padByte).fill(padByte));
  const donor = await service.issueToken("x".repeat(10) + latin1Decode(adminBlockPlain));
  const adminBlock = blockAt(donor, 1);

  // "email=" (6) + email + "&uid=1000&role=" (15) must land on a block boundary so
  // the trailing "user"+padding block is isolated and can be dropped.
  const prefixLen = "email=".length + "&uid=1000&role=".length; // 21
  const emailLen = ((-prefixLen) % BLOCK_SIZE + BLOCK_SIZE) % BLOCK_SIZE || BLOCK_SIZE; // 11
  const base = await service.issueToken("a".repeat(emailLen));
  const baseBlocks = base.slice(0, base.length - BLOCK_SIZE); // drop trailing "user"+padding
  return concat(baseBlocks, adminBlock);
}

// ---------------------------------------------------------------------------
// Defensive control — the same token scheme under AES-GCM. A one-byte tamper
// fails the authentication tag before any role is read.
// ---------------------------------------------------------------------------
export async function gcmTokenRoundtrip(email, key = randomKey()) {
  const profile = `email=${String(email).replace(/[&=]/g, "")}&uid=1000&role=user`;
  const { nonce, ciphertext } = await aesGcmEncrypt(key, latin1Encode(profile));
  const tampered = Uint8Array.from(ciphertext);
  tampered[0] ^= 1; // flip one bit
  let tamperRejected = false;
  try { await aesGcmDecrypt(key, nonce, tampered); } catch { tamperRejected = true; }
  const clean = latin1Decode(await aesGcmDecrypt(key, nonce, ciphertext));
  return { tamperRejected, decryptedProfile: clean };
}

// ---------------------------------------------------------------------------
// Vector 1 — pattern leakage over image pixels. Encrypt raw RGBA bytes under
// each mode; ECB preserves structure, CBC/GCM do not. Returns Uint8Arrays the
// same length as the input for redrawing onto a canvas.
// ---------------------------------------------------------------------------
export async function encryptPixels(rgba, key = randomKey()) {
  const ecb = (await aesEcbEncrypt(key, rgba, true)).slice(0, rgba.length);
  const { aesCbcEncrypt } = await import("./crypto.mjs");
  const cbc = (await aesCbcEncrypt(key, rgba)).ciphertext.slice(0, rgba.length);
  const gcm = (await aesGcmEncrypt(key, rgba)).ciphertext.slice(0, rgba.length);
  return { ecb, cbc, gcm };
}
