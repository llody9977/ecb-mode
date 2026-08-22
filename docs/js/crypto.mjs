// AES helpers for the ECB weakness demonstrations.
//
// WebCrypto (crypto.subtle) deliberately omits AES-ECB because it is unsafe. We
// reconstruct one ECB block as AES-CBC with an all-zero IV: for a single block,
// CBC computes E_K(P XOR 0) = E_K(P) = ECB(P). Multi-block ECB is then just each
// block encrypted independently (CBC's chaining is never allowed to kick in).
// This runs identically in the browser and in Node's WebCrypto, and is verified
// against the NIST SP 800-38A test vectors in the test suite.
//
// ECB is used here intentionally, alongside CBC and GCM, to demonstrate the
// failure it causes. Do not copy the ECB path into a system that needs
// confidentiality.

const subtle = globalThis.crypto.subtle;
export const BLOCK_SIZE = 16;
const ZERO_IV = new Uint8Array(BLOCK_SIZE);

// ---- byte / string helpers ----
export const toHex = (b) => [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
export const fromHex = (s) => new Uint8Array(s.match(/../g)?.map((h) => parseInt(h, 16)) ?? []);
export const utf8 = (s) => new TextEncoder().encode(s);
// latin1: one char <-> one byte (matches Python's .encode/.decode("latin1"),
// so raw PKCS#7 padding bytes survive a round-trip through a string field).
export const latin1Encode = (s) => Uint8Array.from(s, (c) => c.charCodeAt(0) & 0xff);
export const latin1Decode = (b) => String.fromCharCode(...new Uint8Array(b));

export function concat(...arrays) {
  const total = arrays.reduce((n, a) => n + a.length, 0);
  const out = new Uint8Array(total);
  let o = 0;
  for (const a of arrays) { out.set(a, o); o += a.length; }
  return out;
}

export function splitBlocks(data, blockSize = BLOCK_SIZE) {
  const out = [];
  for (let i = 0; i < data.length; i += blockSize) out.push(data.slice(i, i + blockSize));
  return out;
}

export function blockAt(data, index, blockSize = BLOCK_SIZE) {
  return data.slice(index * blockSize, (index + 1) * blockSize);
}

export function bytesEqual(a, b) {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
  return true;
}

// ---- PKCS#7 ----
export function padPkcs7(data, blockSize = BLOCK_SIZE) {
  const padLen = blockSize - (data.length % blockSize);
  return concat(data, new Uint8Array(padLen).fill(padLen));
}

export function unpadPkcs7(data, blockSize = BLOCK_SIZE) {
  if (data.length === 0 || data.length % blockSize !== 0) throw new Error("data length is not a multiple of the block size");
  const padLen = data[data.length - 1];
  if (padLen < 1 || padLen > blockSize) throw new Error("invalid PKCS#7 padding");
  for (let i = data.length - padLen; i < data.length; i++) if (data[i] !== padLen) throw new Error("invalid PKCS#7 padding");
  return data.slice(0, data.length - padLen);
}

// ---- one ECB block, via CBC + zero IV ----
async function ecbEncryptBlockK(cryptoKey, block16) {
  const ct = await subtle.encrypt({ name: "AES-CBC", iv: ZERO_IV }, cryptoKey, block16);
  return new Uint8Array(ct).slice(0, BLOCK_SIZE); // drop CBC's padding block
}

async function ecbEncryptBlock(keyBytes, block16) {
  const k = await subtle.importKey("raw", keyBytes, { name: "AES-CBC" }, false, ["encrypt"]);
  return ecbEncryptBlockK(k, block16);
}

async function ecbDecryptBlock(keyBytes, block16) {
  // CBC-decrypt [block16, X] with IV=0 gives P1 = D(block16) (the ECB plaintext we
  // want) and P2 = D(X) XOR block16. WebCrypto strips PKCS#7 from the last block and
  // throws if it is invalid, so choose X = E_K(block16 XOR 0x10^16), making
  // P2 = (block16 XOR 0x10^16) XOR block16 = a full 0x10 padding block that strips cleanly.
  const xored = block16.map((b) => b ^ BLOCK_SIZE);
  const X = await ecbEncryptBlock(keyBytes, xored);
  const k = await subtle.importKey("raw", keyBytes, { name: "AES-CBC" }, false, ["decrypt"]);
  const pt = await subtle.decrypt({ name: "AES-CBC", iv: ZERO_IV }, k, concat(block16, X));
  return new Uint8Array(pt).slice(0, BLOCK_SIZE);
}

// ---- AES-ECB (intentionally insecure; for demonstration only) ----
export async function aesEcbEncrypt(keyBytes, plaintext, pad = true) {
  const data = pad ? padPkcs7(plaintext) : plaintext;
  const k = await subtle.importKey("raw", keyBytes, { name: "AES-CBC" }, false, ["encrypt"]); // import once
  const out = new Uint8Array(data.length);
  for (let i = 0; i < data.length; i += BLOCK_SIZE) {
    out.set(await ecbEncryptBlockK(k, data.slice(i, i + BLOCK_SIZE)), i);
  }
  return out;
}

export async function aesEcbDecrypt(keyBytes, ciphertext, unpad = true) {
  const out = new Uint8Array(ciphertext.length);
  for (let i = 0; i < ciphertext.length; i += BLOCK_SIZE) {
    out.set(await ecbDecryptBlock(keyBytes, ciphertext.slice(i, i + BLOCK_SIZE)), i);
  }
  return unpad ? unpadPkcs7(out) : out;
}

// ---- real AES-CBC (fresh random IV). WebCrypto applies PKCS#7 itself. ----
export async function aesCbcEncrypt(keyBytes, plaintext, iv = null) {
  iv = iv ?? globalThis.crypto.getRandomValues(new Uint8Array(BLOCK_SIZE));
  const k = await subtle.importKey("raw", keyBytes, { name: "AES-CBC" }, false, ["encrypt"]);
  const ct = new Uint8Array(await subtle.encrypt({ name: "AES-CBC", iv }, k, plaintext));
  return { iv, ciphertext: ct };
}

// ---- real AES-GCM (fresh random 96-bit nonce, authenticated) ----
export async function aesGcmEncrypt(keyBytes, plaintext) {
  const nonce = globalThis.crypto.getRandomValues(new Uint8Array(12));
  const k = await subtle.importKey("raw", keyBytes, { name: "AES-GCM" }, false, ["encrypt"]);
  const ct = new Uint8Array(await subtle.encrypt({ name: "AES-GCM", iv: nonce }, k, plaintext));
  return { nonce, ciphertext: ct }; // ct includes the 16-byte auth tag
}

export async function aesGcmDecrypt(keyBytes, nonce, ciphertextWithTag) {
  const k = await subtle.importKey("raw", keyBytes, { name: "AES-GCM" }, false, ["decrypt"]);
  return new Uint8Array(await subtle.decrypt({ name: "AES-GCM", iv: nonce }, k, ciphertextWithTag)); // throws on tamper
}

export function randomKey(bytes = 16) {
  return globalThis.crypto.getRandomValues(new Uint8Array(bytes));
}

// Detect repeated 16-byte blocks (the black-box ECB signature).
export function hasRepeatedBlocks(data, blockSize = BLOCK_SIZE) {
  const seen = new Set();
  for (const b of splitBlocks(data, blockSize)) {
    const h = toHex(b);
    if (seen.has(h)) return true;
    seen.add(h);
  }
  return false;
}
