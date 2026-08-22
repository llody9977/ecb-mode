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
  equalityInference, makeSuffixOracle, recoverSecret,
  ProfileService, forgeAdminToken, gcmTokenRoundtrip,
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

test("Vector 4 — cut-and-paste forges role=admin from a role=user service", async () => {
  const service = new ProfileService(randomKey());
  assert.equal(await service.roleForToken(await service.issueToken("alice@example.com")), "user");
  const forged = await forgeAdminToken(service);
  assert.equal(await service.roleForToken(forged), "admin");
});

test("Defensive — GCM rejects a one-byte tamper before any role is read", async () => {
  const { tamperRejected, decryptedProfile } = await gcmTokenRoundtrip("alice@example.com", randomKey());
  assert.equal(tamperRejected, true);
  assert.match(decryptedProfile, /role=user/);
});
