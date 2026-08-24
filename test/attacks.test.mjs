// Verifies the browser crypto + attack logic against real AES — including the
// NIST SP 800-38A AES-128-ECB test vectors, so "tested against real AES" holds
// after the move from Python to JS. Run: `node --test`.
import { test } from "node:test";
import assert from "node:assert/strict";

import {
  aesEcbEncrypt, aesEcbDecrypt, aesCbcEncrypt, aesGcmEncrypt,
  fromHex, toHex, utf8, concat, hasRepeatedBlocks, randomKey,
} from "../docs/js/crypto.mjs";
import {
  equalityInference, makeSuffixOracle, recoverSecret, encryptPixels,
  ProfileService, GcmProfileService, forgeAdminToken,
  gcmTokenRoundtrip, forgeUnderBothModes,
} from "../docs/js/attacks.mjs";

test("AES-128-ECB matches the NIST SP 800-38A F.1.1 vectors", async () => {
  const key = fromHex("2b7e151628aed2a6abf7158809cf4f3c");
  const pt = fromHex(
    "6bc1bee22e409f96e93d7e117393172a" + "ae2d8a571e03ac9c9eb76fac45af8e51" +
    "30c81c46a35ce411e5fbc1191a0a52ef" + "f69f2445df4f9b17ad2b417be66c3710");
  const want =
    "3ad77bb40d7a3660a89ecaf32466ef97" + "f5d3d58503b9699de785895a96fdbaaf" +
    "43b1cd7f598ece23881b00e3ed030688" + "7b0c785e27e8ad3f8223207104725dd4";
  const ct = await aesEcbEncrypt(key, pt, /* pad */ false);
  assert.equal(toHex(ct), want);
});

// The decrypt direction needs its own vectors: round-tripping against our own
// aesEcbEncrypt would pass even if both directions were wrong in the same way.
test("AES-128-ECB decrypt matches the NIST SP 800-38A F.1.2 vectors", async () => {
  const key = fromHex("2b7e151628aed2a6abf7158809cf4f3c");
  const ct = fromHex(
    "3ad77bb40d7a3660a89ecaf32466ef97" + "f5d3d58503b9699de785895a96fdbaaf" +
    "43b1cd7f598ece23881b00e3ed030688" + "7b0c785e27e8ad3f8223207104725dd4");
  const want =
    "6bc1bee22e409f96e93d7e117393172a" + "ae2d8a571e03ac9c9eb76fac45af8e51" +
    "30c81c46a35ce411e5fbc1191a0a52ef" + "f69f2445df4f9b17ad2b417be66c3710";
  const pt = await aesEcbDecrypt(key, ct, /* unpad */ false);
  assert.equal(toHex(pt), want);
});

test("ECB is deterministic: equal blocks -> equal ciphertext", async () => {
  const key = randomKey();
  const block = utf8("YELLOW SUBMARINE"); // exactly 16 bytes
  const ct = await aesEcbEncrypt(key, concat(block, block), false);
  assert.equal(toHex(ct.slice(0, 16)), toHex(ct.slice(16, 32)));
  const other = await aesEcbEncrypt(key, concat(block, utf8("ORANGE SUBMARINE")), false);
  assert.notEqual(toHex(other.slice(0, 16)), toHex(other.slice(16, 32)));
});

test("ECB encrypt/decrypt round-trips with PKCS#7", async () => {
  const key = randomKey();
  const msg = utf8("the quick brown fox jumps over 13 lazy dogs.");
  const round = await aesEcbDecrypt(key, await aesEcbEncrypt(key, msg));
  assert.equal(toHex(round), toHex(msg));
});

test("repeated-block detector flags ECB but not CBC or GCM", async () => {
  const key = randomKey();
  const repeated = concat(utf8("YELLOW SUBMARINE"), utf8("YELLOW SUBMARINE"));
  assert.equal(hasRepeatedBlocks(await aesEcbEncrypt(key, repeated, false)), true);
  assert.equal(hasRepeatedBlocks((await aesCbcEncrypt(key, repeated)).ciphertext), false);
  assert.equal(hasRepeatedBlocks((await aesGcmEncrypt(key, repeated)).ciphertext), false);
});

test("Vector 2 — equality inference clusters shared passwords with no decryption", async () => {
  const { clusters } = await equalityInference({
    alice: "sunshine1", bob: "letmein123", carol: "sunshine1", dave: "qwerty", erin: "letmein123",
  }, randomKey());
  const sets = clusters.map((g) => g.slice().sort().join(",")).sort();
  assert.deepEqual(sets, ["alice,carol", "bob,erin"]);
});

test("Vector 3 — byte-at-a-time recovers the exact secret", async () => {
  const secret = utf8("Rollin' in my 5.0 with my rag-top down so my hair can blow");
  const oracle = makeSuffixOracle(secret, randomKey());
  const recovered = await recoverSecret(oracle);
  assert.equal(toHex(recovered), toHex(secret));
});

test("Vector 3 — onStep fires once per recovered byte, in order", async () => {
  const secret = utf8("abcdef");
  const steps = [];
  await recoverSecret(makeSuffixOracle(secret, randomKey()), { onStep: (s) => steps.push(s.byte) });
  assert.equal(toHex(Uint8Array.from(steps)), toHex(secret));
});

// Guard for the query-cost bound stated in docs/index.html and in
// diagrams/vector3-byte-at-a-time.svg. The old text claimed 256 x L, which the
// implementation exceeds: each position also costs one query to capture the
// target block, and sizing the oracle up costs a fixed amount on top. An
// all-0xff secret is the worst case, because the candidate loop scans 0..255
// and only matches on the last value.
test("Vector 3 — worst-case query count respects the documented 257 x L + 34 bound", async () => {
  for (const L of [1, 8, 16, 20]) {
    const secret = new Uint8Array(L).fill(0xff);
    let queries = 0;
    const oracle = makeSuffixOracle(secret, randomKey());
    const recovered = await recoverSecret((input) => { queries++; return oracle(input); });
    assert.equal(toHex(recovered), toHex(secret), `recovery failed at L=${L}`);
    assert.ok(queries <= 257 * L + 34, `L=${L}: ${queries} queries exceeds the documented 257 x L + 34 bound`);
    // The bound the docs used to state. Asserting it is genuinely violated stops
    // anyone reinstating 256 x L on the assumption that it holds.
    assert.ok(queries > 256 * L, `L=${L}: ${queries} queries — 256 x L would now be a valid bound, so the docs need rechecking`);
  }
});

// The page states an exact figure for its default secret and invites the reader
// to check it against the counter the demo prints. It is key-independent: the
// candidate loop's length depends only on the secret's byte values.
test("Vector 3 — the page's default secret costs exactly 4,588 queries, whatever the key", async () => {
  const secret = utf8("the eagle lands at midnight; bring the umbrella.");
  assert.equal(secret.length, 48, "the page describes this as the 48-byte default");
  for (let run = 0; run < 3; run++) {
    let queries = 0;
    const oracle = makeSuffixOracle(secret, randomKey());
    const recovered = await recoverSecret((input) => { queries++; return oracle(input); });
    assert.equal(toHex(recovered), toHex(secret));
    assert.equal(queries, 4588);
  }
});

test("Vector 4 — cut-and-paste forges role=admin from a role=user service", async () => {
  const service = new ProfileService(randomKey());
  assert.equal(await service.roleForToken(await service.issueToken("alice@example.com")), "user");
  const forged = await forgeAdminToken(service);
  assert.equal(await service.roleForToken(forged), "admin");
});

// The demonstration the page relies on to show AEAD closes Vector 4. A bit-flip
// test does not establish this: Vector 4 never flips a bit. The contrast only
// holds if the same forgeAdminToken() runs against both services.
test("Defensive — the same splice that forges role=admin under ECB is rejected under GCM", async () => {
  const { ecbForgedRole, gcmForgedRole, gcmHonestRole } = await forgeUnderBothModes();
  assert.equal(ecbForgedRole, "admin", "the ECB half must be executed, not assumed");
  assert.equal(gcmForgedRole, null, "GCM must reject the spliced token before returning any plaintext");
  assert.equal(gcmHonestRole, "user", "the GCM service must still issue working tokens");
});

// forgeAdminToken used to take the header size as a parameter defaulting to 0.
// A GCM caller that omitted it still got a rejected token, so the ECB/GCM
// comparison passed while proving only that mangling a nonce breaks decryption.
// The service now declares its own layout. Note the *behavioural* consequence is
// not observable from outside: both offsets yield a 64-byte token that GCM
// rejects, which is precisely why the bug was invisible. The structural guard
// lives in test/docs-claims.test.mjs; this test pins the layout constants.
test("each service declares its own token header size", async () => {
  assert.equal(ProfileService.headerSize, 0, "an ECB token has no cleartext header");
  assert.equal(GcmProfileService.headerSize, 12, "a GCM token is prefixed by its 96-bit nonce");

  const gcm = new GcmProfileService(randomKey());
  const email = "alice@example.com";
  const token = await gcm.issueToken(email);
  // GCM is a stream construction: no padding, so the ciphertext is exactly the
  // profile length. Derived rather than hardcoded, so it stays true if the
  // profile template changes.
  const profileLen = `email=${email}&uid=1000&role=user`.length;
  assert.equal(token.length, GcmProfileService.headerSize + profileLen + 16, "nonce + ciphertext + tag");
  assert.equal(await gcm.roleForToken(token), "user");

  // ECB pads to a block boundary, so its token carries no header and rounds up.
  const ecbToken = await new ProfileService(randomKey()).issueToken(email);
  assert.equal(ecbToken.length, (Math.floor(profileLen / 16) + 1) * 16);
});

test("Defensive — GCM rejects a one-byte tamper before any role is read", async () => {
  const { tamperRejected, decryptedProfile } = await gcmTokenRoundtrip("alice@example.com", randomKey());
  assert.equal(tamperRejected, true);
  assert.match(decryptedProfile, /role=user/);
});

// Vector 1 is the page's headline demo. It went untested while ui.mjs carried its
// own inline copy of this logic and encryptPixels() was exported but unused.
test("Vector 1 — encryptPixels preserves repeated pixel blocks under ECB but not CBC or GCM", async () => {
  // A flat region: 64 identical 16-byte blocks, the structure ECB leaks.
  const rgba = new Uint8Array(16 * 64).fill(0);
  for (let i = 0; i < rgba.length; i += 4) { rgba[i] = 200; rgba[i + 1] = 30; rgba[i + 2] = 60; rgba[i + 3] = 255; }
  const { ecb, cbc, gcm } = await encryptPixels(rgba, randomKey());
  for (const [name, buf] of [["ecb", ecb], ["cbc", cbc], ["gcm", gcm]]) {
    assert.equal(buf.length, rgba.length, `${name} output must be canvas-sized`);
  }
  assert.equal(hasRepeatedBlocks(ecb), true, "ECB must reproduce the repeated blocks");
  assert.equal(hasRepeatedBlocks(cbc), false);
  assert.equal(hasRepeatedBlocks(gcm), false);
});

test("GcmProfileService round-trips a normal token and rejects an altered one", async () => {
  const service = new GcmProfileService(randomKey());
  const token = await service.issueToken("alice@example.com");
  assert.equal(await service.roleForToken(token), "user");
  const altered = Uint8Array.from(token);
  altered[altered.length - 1] ^= 1;
  assert.equal(await service.roleForToken(altered), null);
});
