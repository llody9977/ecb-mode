// The four ECB attack vectors, as testable functions shared by the page demos and
// the test suite. Every function runs against real AES (see crypto.mjs).
//
// Scope: educational / defensive. Every oracle and service here is a self-contained,
// in-process stand-in — there is no network and no third-party system. Do not point
// any of this at a system you do not own or are not authorized to test.

import {
  BLOCK_SIZE, GCM_NONCE_SIZE, aesEcbEncrypt, aesEcbDecrypt, aesCbcEncrypt,
  aesGcmEncrypt, aesGcmDecrypt,
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
const PROFILE_FOR = (email) => `email=${String(email).replace(/[&=]/g, "")}&uid=1000&role=user`;

function roleFromProfile(text) {
  const fields = {};
  for (const pair of text.split("&")) {
    const j = pair.indexOf("=");
    if (j >= 0) fields[pair.slice(0, j)] = pair.slice(j + 1);
  }
  return fields.role ?? null;
}

export class ProfileService {
  constructor(key = randomKey()) { this.key = key; }

  // A token is opaque bytes to the caller. ECB carries no header, so the
  // ciphertext starts at offset 0.
  static headerSize = 0;

  async issueToken(email) {
    return aesEcbEncrypt(this.key, latin1Encode(PROFILE_FOR(email)));
  }

  async roleForToken(token) {
    let plaintext;
    try { plaintext = await aesEcbDecrypt(this.key, token); } catch { return null; }
    return roleFromProfile(latin1Decode(plaintext));
  }
}

// The same profile service under AES-GCM. Identical public interface and identical
// token layout apart from the 12-byte nonce header, so the cut-and-paste forgery
// below can be pointed at either one and the mode is the only thing that differs.
export class GcmProfileService {
  constructor(key = randomKey()) { this.key = key; }

  static headerSize = GCM_NONCE_SIZE;

  async issueToken(email) {
    const { nonce, ciphertext } = await aesGcmEncrypt(this.key, latin1Encode(PROFILE_FOR(email)));
    return concat(nonce, ciphertext); // nonce ‖ ciphertext ‖ tag
  }

  async roleForToken(token) {
    const nonce = token.slice(0, GCM_NONCE_SIZE);
    const body = token.slice(GCM_NONCE_SIZE);
    let plaintext;
    // The tag is verified before any plaintext is returned, so a token that was
    // spliced or otherwise altered never reaches roleFromProfile at all.
    try { plaintext = await aesGcmDecrypt(this.key, nonce, body); } catch { return null; }
    return roleFromProfile(latin1Decode(plaintext));
  }
}

// Splice a legitimate token into one that decrypts with role=admin, using only
// the public issueToken() interface — no access to the key.
//
// The service declares its own cleartext header size (0 for ECB, 12 for the GCM
// nonce) so the block surgery lands on the ciphertext either way. It is read from
// the service rather than passed in deliberately: a caller who omitted the
// argument would still produce a token GCM rejects, so the ECB/GCM comparison
// would pass while demonstrating something weaker — a mangled nonce breaking
// decryption, rather than the tag catching a splice. Run this against
// ProfileService and GcmProfileService to see the same attack succeed and then
// fail with nothing but the mode changed.
export async function forgeAdminToken(service) {
  const headerSize = service.constructor.headerSize ?? 0;
  // "email=" (6) + 10-byte local part pushes an "admin"+padding block onto its
  // own 16-byte boundary, isolated as ciphertext block 1.
  const padByte = BLOCK_SIZE - "admin".length; // 11
  const adminBlockPlain = concat(utf8("admin"), new Uint8Array(padByte).fill(padByte));
  const donorToken = await service.issueToken("x".repeat(10) + latin1Decode(adminBlockPlain));
  const adminBlock = blockAt(donorToken.slice(headerSize), 1);

  // "email=" (6) + email + "&uid=1000&role=" (15) must land on a block boundary so
  // the trailing "user"+padding block is isolated and can be dropped.
  const fieldLen = "email=".length + "&uid=1000&role=".length; // 21
  const emailLen = ((-fieldLen) % BLOCK_SIZE + BLOCK_SIZE) % BLOCK_SIZE || BLOCK_SIZE; // 11
  const baseToken = await service.issueToken("a".repeat(emailLen));
  const header = baseToken.slice(0, headerSize);
  const base = baseToken.slice(headerSize);
  const kept = base.slice(0, base.length - BLOCK_SIZE); // drop trailing "user"+padding
  return concat(header, kept, adminBlock);
}

// ---------------------------------------------------------------------------
// Defensive control — the same token scheme under AES-GCM.
//
// Two separate results, because they prove different things. The bit flip shows
// the tag catches the smallest possible alteration; the splice shows it catches
// the exact Vector 4 attack, run by the same forgeAdminToken() against the same
// service interface. Only the splice closes Vector 4 — a bit flip does not
// demonstrate that, since Vector 4 never flips a bit.
// ---------------------------------------------------------------------------
export async function gcmTokenRoundtrip(email, key = randomKey()) {
  const { nonce, ciphertext } = await aesGcmEncrypt(key, latin1Encode(PROFILE_FOR(email)));
  const tampered = Uint8Array.from(ciphertext);
  tampered[0] ^= 1; // flip one bit
  let tamperRejected = false;
  try { await aesGcmDecrypt(key, nonce, tampered); } catch { tamperRejected = true; }
  const clean = latin1Decode(await aesGcmDecrypt(key, nonce, ciphertext));
  return { tamperRejected, decryptedProfile: clean };
}

// Run the Vector 4 cut-and-paste against both services and return both outcomes.
//
// The ECB half is executed rather than asserted. Reporting a remembered "ECB gives
// role=admin" beside a computed GCM result would put an assertion and a measurement
// side by side as though both were measurements — which is the failure this whole
// demonstration exists to correct.
export async function forgeUnderBothModes(ecbKey = randomKey(), gcmKey = randomKey()) {
  const ecb = new ProfileService(ecbKey);
  const gcm = new GcmProfileService(gcmKey);
  return {
    ecbForgedRole: await ecb.roleForToken(await forgeAdminToken(ecb)), // "admin" — accepted
    gcmForgedRole: await gcm.roleForToken(await forgeAdminToken(gcm)), // null — tag rejects it
    gcmHonestRole: await gcm.roleForToken(await gcm.issueToken("alice@example.com")), // "user"
  };
}

// ---------------------------------------------------------------------------
// Vector 1 — pattern leakage over image pixels. Encrypt raw RGBA bytes under
// each mode; ECB preserves structure, CBC/GCM do not. Returns Uint8Arrays the
// same length as the input for redrawing onto a canvas.
// ---------------------------------------------------------------------------
export async function encryptPixels(rgba, key = randomKey()) {
  const ecb = (await aesEcbEncrypt(key, rgba, true)).slice(0, rgba.length);
  const cbc = (await aesCbcEncrypt(key, rgba)).ciphertext.slice(0, rgba.length);
  const gcm = (await aesGcmEncrypt(key, rgba)).ciphertext.slice(0, rgba.length);
  return { ecb, cbc, gcm };
}
