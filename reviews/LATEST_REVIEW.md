# Review record: ecb-mode — full project content review

> Lives at `reviews/LATEST_REVIEW.md` and is overwritten by each new review — this file always holds the
> most recent one. Earlier records are in git, not in this folder:
> `git log -p --follow reviews/LATEST_REVIEW.md` for the full series,
> `git show <commit>:reviews/LATEST_REVIEW.md` for one in full.
>
> The machine-readable pass state lives beside it in `reviews/REVIEW_STATE.json`, written by
> `scripts/review_passes.py --record`. That file is the router's input; this one is the human record.

## Status and baseline

- Status: **Complete with no open findings** — 9 required findings from this review's own passes, plus 2 fix-introduced defects caught by residual exhaustion and 3 more caught by the pre-check-in `review-pr` gate, were all remediated and re-verified against a new baseline.
- Review date: 2026-08-24
- Reviewer: Claude Opus 5, under the `doc-review` standard, at the user's request for a clean review with all findings fixed
- Model / effort this review: `claude-opus-5` / `high`
- Branch: `main`
- Commit at review start: `403a2566a33f27e0710649ebe4e7b0e8f72c74f7`
- Worktree at review start: **Dirty**, but only outside the content scope — `reviews/` was emptied and re-bootstrapped and `scripts/` was re-synced from the skill assets, both at the user's instruction. Every in-scope content file (`docs/`, `README.md`, `test/`, the policy files) was at the clean commit.
- Review state ID: `aabf1ef51ab4fa21c749fdaf8dbefb5020fda4fb246c0f0370dccb71007544f7`
- Scoped content fingerprint at review start: `80598afd5124237cdebc780a1316d804faba23deadf21d7708a68d1b0551f67c` (15 files)
- Scoped content fingerprint after remediation: `3032bc186e0e7f83d78a12be63dcc71cb3e87a58126fd5a6b39326927045b1a1` (16 files)
- State-capture command: `python3 scripts/capture_review_state.py --scope docs --scope README.md --scope DISCLAIMER.md --scope SECURITY.md --scope CONTRIBUTING.md --scope test`
- Pass-routing command: `python3 scripts/review_passes.py --model claude-opus-5 --effort high`
- Pass state recorded with: `--record` naming all 11 passes, each of which actually ran
- Baseline changed during review: **Yes.** The user asked for review *and* remediation in one pass, so these were run as two phases. The review phase completed against `80598afd…` with the baseline frozen; remediation then produced `3032bc18…`; the always-run tier, the residual-exhaustion pass, and every pass whose inputs the fixes touched were repeated against the new baseline. The recorded verdicts describe the remediated content, per the standard's rule that the verdict records what the run found, not what is still open.

### Prior review this one builds on

- Prior review date / model / effort: **none carried forward.** The user asked for the `reviews/` folder to be emptied and a clean review run. `reviews/REVIEW_STATE.json` did not exist, so the router reported *"No prior review state — every pass runs (first review under pass versioning)"* and scheduled all 11.
- Prior commit: n/a
- Passes carried forward from it: **none.** Nothing in this record rests on an earlier run.

> **What emptying the folder cost, stated plainly.** The previous register held 13 decisions (CD-0001…CD-0013 at commit `403a2566`), three of them deliberate *rejections* whose only purpose was to stop a future review re-arguing them. Deleting the register removed that protection, so this review re-derived those questions from scratch. Two of the three were re-reached independently and are re-recorded here as CD-0011 and CD-0012; one (a GCM deployment-modelling rejection) did not arise. The full prior register is recoverable with
> `git show 403a2566:reviews/CONTENT_DECISIONS.yml`. Decision IDs in the new register are **not** continuous with the old ones — CD-0001 here is a different decision from CD-0001 there.

## Scope inventory

| Artifact | Type | Direct dependents or generated counterpart | Inspected |
| --- | --- | --- | --- |
| `docs/index.html` | Prose, metadata, demo markup | All four SVGs; `docs/js/*`; `docs/styles.css` | Yes — read in full |
| `docs/styles.css` | Presentation | `docs/index.html` | Yes |
| `docs/js/crypto.mjs` | AES primitives (ECB/CBC/GCM, PKCS#7) | `attacks.mjs`, `ui.mjs`, test suite | Yes — read in full |
| `docs/js/attacks.mjs` | The four vectors + defensive controls | `ui.mjs`, test suite | Yes — read in full |
| `docs/js/ui.mjs` | Demo wiring | `docs/index.html` | Yes — read in full |
| `docs/diagrams/generate_diagrams.py` | Generator for all four figures | The four committed SVGs | Yes — read in full |
| `docs/diagrams/modes-ecb-cbc-gcm.svg` | Figure | Generated; alt text in `index.html` | Yes — regenerated and rendered |
| `docs/diagrams/taxonomy.svg` | Figure | Generated; alt text in `index.html` and `README.md` | Yes — regenerated and rendered |
| `docs/diagrams/vector3-byte-at-a-time.svg` | Figure | Generated; alt text in `index.html` | Yes — regenerated and rendered |
| `docs/diagrams/vector4-cut-and-paste.svg` | Figure | Generated; alt text in `index.html` | Yes — regenerated and rendered |
| `README.md` | Prose, lede, badges | Mirrors `index.html` lede; embeds `taxonomy.svg` | Yes |
| `test/attacks.test.mjs` | Executable evidence for demo claims | `docs/js/*` | Yes — read in full, executed |
| `test/docs-claims.test.mjs` | **New.** Documentation-claim guards | `docs/index.html`, generator, SVGs, `ui.mjs` | Yes — authored by this review |
| `DISCLAIMER.md` | Dual-use scope statement | `README.md`, `index.html` footer | Yes |
| `SECURITY.md` | Reporting policy | `README.md` | Yes |
| `CONTRIBUTING.md` | Contributor policy | `README.md` | Yes |

Out-of-scope boundaries and reason: `.github/` workflows, `.gitleaks.toml`, `.pre-commit-config.yaml`, `package.json`, `eslint.config.mjs` and `LICENSE` are repository infrastructure governed by the `repo-standards` skill, not documentation content. `eslint.config.mjs` was edited once, as a consequence of a fix (adding the `URL` global the new test file needs), not as a reviewed artifact. `node_modules/` is vendored.

## Review passes

Copy the router's decision verbatim. A **cached** pass is carried forward on its own recorded
evidence — it was not verified by this review, and must never be described as if it were.

| id | Ver | Ran or cached | Reason (router's words) | Verdict | Evidence, or the run it rests on |
| --- | --- | --- | --- | --- | --- |
| `factual-correctness` | v1 | **run** | no recorded run for this pass | findings | F1 (query bound), F3 (bcrypt), F4 (IND-CPA scope). Ledger C-001…C-018. |
| `evidence-authority` | v1 | **run** | no recorded run for this pass | findings | Every cited URL fetched and quoted text matched verbatim; F8 (unsourced timing claim). |
| `adversarial-claims` | v1 | **run** | no recorded run for this pass | findings | F5 (necessary/sufficient), F4 (attacker state). |
| `terminology-taxonomy` | v1 | **run** | no recorded run for this pass | clean | Two-root-cause/four-vector taxonomy applied consistently across prose, figures, README and code. See CD-0010. |
| `cross-format` | v1 | **run** | no recorded run for this pass | findings | F1 and F6 each appeared on 3–4 surfaces; F9 across README. |
| `visual-content` | v2 | **run** | no recorded run for this pass | findings | F6. All four figures rendered in both color schemes; generator correspondence established byte-for-byte. |
| `cross-page` | v1 | **run** | no recorded run for this pass | findings | README's description of the fix demo went stale as a consequence of F2's remediation; corrected. |
| `topic-completeness` | v1 | **run** | no recorded run for this pass | clean | Matrix below. No required gaps; two optional extensions. |
| `argument-integrity` | v2 | **run** | no recorded run for this pass | findings | F2 (demonstration sufficiency), F4 (thesis scoping), F9 (internal contradiction). Thesis lines below. |
| `executable-demonstration` | v2 | **run** | no recorded run for this pass | findings | F1 measured against adversarial (all-`0xff`) inputs; F2; F7. |
| `decision-reconciliation` | v1 | **run** | no recorded run for this pass | clean | Register was empty at review start by instruction; 12 decisions written from this review's outcomes. |

Always-run tier — never cached, because it is cheap, deterministic, and model-independent:

| Check | Result | What it does not prove |
| --- | --- | --- |
| Mechanical, link, generator, and rendered-output validation | **Pass.** `npm test` 24/24; `npm run lint` clean; generator regeneration byte-identical to the committed SVGs; all 21 external links resolve; all four figures and the full page rendered in Chromium in both color schemes. | That the content is factually correct, that claims are supported, or that a figure depicts what its generator intends. Link resolution proves reachability, not that the target still says what is quoted — that is `evidence-authority`'s job, and it ran. |
| Guard regression — every guard from a previous finding still fires | **Not applicable at review start** (no prior guards existed). **10 new guards authored and each verified to fire** — see the mechanization table. | That guards cover findings they were not written for. |
| Residual exhaustion — only when a pass produced a finding | **Run after remediation.** Found two further defects introduced by the fixes themselves: a dangling "That boundary" referent in the rewritten IND-CPA paragraph, and a stale README bullet describing the old bit-flip demo. Both corrected; see F4-r and F2-r. | That no defect survives — only that the units touched by a finding were re-read against the same reasoning. |

### Method versions bumped by this review

Each bump reopens that pass for every project on the next review. Leave empty if none.

| id | Old → new | What the old method missed |
| --- | --- | --- |
| — | — | None. This project had no prior recorded state, so nothing here indicates the standard was too shallow. `executable-demonstration` v2 and `visual-content` v2 were already at the versions that caught F1 and F6. |

### Findings mechanized into guards

The durable output of a review. A finding that could have been mechanized and was not will be
rediscovered by hand every time — record why.

| Finding | Guard added (and where it runs) | Verified to fire on the original fault | If not mechanized, why |
| --- | --- | --- | --- |
| F1 — wrong query bound | `test/attacks.test.mjs`: measures the worst case at L ∈ {1,8,16,20} and asserts it is within `257 × L + 34` **and** genuinely exceeds `256 × L`. Plus `test/docs-claims.test.mjs`: asserts every surface states `257 × L` and none states `256 × L` or `12,288`. | **Yes** — reinstating `256 × L` in `index.html` fails the docs-claims test. | — |
| F1 — exact default cost | `test/attacks.test.mjs`: asserts the 48-byte default costs exactly 4,588 queries across 3 independent random keys. | Implicitly — any change to the probe strategy breaks the equality. | — |
| F2 — demo did not show the contrast | `test/attacks.test.mjs`: one key, same `forgeAdminToken` → `admin` under ECB and `null` under GCM. Plus `test/docs-claims.test.mjs`: asserts `runGcm` **calls** `gcmForgeAttempt`. | **Yes** — after strengthening. The first version matched the bare identifier and stayed silent when the call was removed but the import left; it now matches `await gcmForgeAttempt(`. | — |
| F3 — bcrypt as memory-hard | `test/docs-claims.test.mjs` | **Yes** | — |
| F4 — IND-CPA scoping | — | — | **Not mechanized.** The defect is the *meaning* of a paragraph, not a string. A grep guard would either be trivially satisfiable or would freeze the wording. The `argument-integrity` pass is the control here. |
| F5 — "sufficient evidence" | `test/docs-claims.test.mjs`: rejects the superseded sentence, requires the constant-IV counterexample. | **Yes** | Partial — the guard pins the specific fault, not the general class of over-strong claim. |
| F6 — figure omitted the IV | `test/docs-claims.test.mjs`: asserts the IV string and the freshness qualifier appear in **both** the generator and the committed SVG. | **Yes** | — |
| F7 — dead `encryptPixels`, untested Vector 1 | `test/attacks.test.mjs`: behavioural test for `encryptPixels`. Plus `test/docs-claims.test.mjs`: asserts `ui.mjs` calls it and the inline duplicate has not returned. | **Yes** | — |
| F8 — unsourced timing claim | — | — | **Not mechanized.** "Is this figure sourced?" is not decidable by grep. `evidence-authority` is the control. |
| F9 — AEAD/Vector 2 contradiction | `test/docs-claims.test.mjs` | **Yes** | — |
| F2-g — hardcoded ECB line in the GCM panel | `test/docs-claims.test.mjs`: asserts the line renders `ecbForgedRole` and is not a literal. Plus `test/attacks.test.mjs`: asserts `forgeUnderBothModes()` returns `admin` for the ECB half. | **Yes** | — |
| F2-h — caller-supplied header offset | `test/docs-claims.test.mjs`: asserts the offset is read from `service.constructor.headerSize` and that no offset parameter exists. | **Yes**, after two non-firing attempts — see the method note above. | Structural rather than behavioural, of necessity: both offsets produce a 64-byte token that GCM rejects, so no observable behaviour separates them. |
| F2-i — button stuck on throw | — | — | **Not mechanized.** Would need a fault-injecting DOM harness; the project has no browser test runner, and adding one for a one-line `try/finally` is disproportionate. |
| General — figure scope lines and alt-text substance | `test/docs-claims.test.mjs`: every attack figure carries a `Scope:` line; every figure's alt text exceeds 120 characters. | **Yes** — stripping a scope line fails. | Alt-text length is a proxy for substance, not a measure of it. Stated as a limitation. |

Guard-fire verification method: each fault was reintroduced by `sed` into a working copy, `npm test` was run and the specific test asserted to fail, then the file was restored from backup and the full suite re-run green. **Three guards were found defective by this procedure and reworked** — which is the entire argument for running it rather than assuming a written guard works:

- The F2 guard matched the bare identifier `gcmForgeAttempt`, so it stayed silent when the call was deleted but the import left. Now matches the call.
- The F2-h guard first asserted `forgeAdminToken.length === 1`. `Function.prototype.length` counts parameters *before the first default*, so it reads 1 for both `(service)` and `(service, h = 0)` — it could never have fired. A replacement behavioural guard comparing forged-token lengths also failed to fire, because both offsets yield 64 bytes. Only a structural guard works here, and that limitation is now stated in the test itself.
- The F2-g guard's companion assertion hardcoded a token length of 36 bytes derived from the wrong email; it now derives the profile length instead of asserting a constant.

## Material-claim ledger

| ID | Artifact and location | Material claim | Classification | Primary source or verification | Repetitions checked | Result |
| --- | --- | --- | --- | --- | --- | --- |
| C-001 | `index.html` §The mechanism | SP 800-38A §6.1: "under a given key, any given plaintext block always gets encrypted to the same ciphertext block" / "if this property is undesirable in a particular application, the ECB mode should not be used" | Standards quote | SP 800-38A PDF extracted and searched; both fragments matched **verbatim**, immediately preceding §6.2 | Prose only | **Verified** |
| C-002 | `index.html` §The mechanism | A block cipher under a fixed key is a permutation, so equal ciphertext blocks ⟺ equal plaintext blocks | Cryptographic property, explicitly *not* attributed to NIST | Definitional; the page's own attribution disclaimer is correct | Prose; taxonomy figure | **Verified** |
| C-003 | `index.html` §Why determinism…, `README.md` lede | ECB fails IND-CPA with adversary advantage 1, regardless of key size | Security property | Standard IND-CPA game; the two-block distinguisher is sound and the oracle-based one holds at any length | Lede ×2, meta description, body | **Verified** |
| C-004 | `index.html` §Why determinism… (scope note) | "It needs at least two blocks that can repeat… this particular break does not apply" | Security property, **scoping** | The CPA oracle defeats determinism at one block. Claim was true of the illustration, misleading about the break | Prose only | **F4 — corrected** |
| C-005 | `index.html` §Why determinism… | SP 800-38F (KW, KWP, TKW) are the modes NIST approves for key wrapping | Standards attribution | SP 800-38F is *Methods for Key Wrapping*; link resolves 200 | Prose only | **Verified** |
| C-006 | `index.html` §Vector 2 + evidence table | Adobe 2013: 152,982,479 records, 8-byte block cipher "allegedly 3DES", ECB, unsalted; 8-char block overlap leaks a portion | Historical/numeric | filippo.io: "152,982,479 entries"; "allegedly 3DES, in ECB mode"; "It is not salted"; "anyone with a 8-characters block in common with you will now (all or a portion of) your password" | Vector 2 prose; evidence table | **Verified after F8 correction** |
| C-007 | `index.html` §Vector 2 + evidence table | Adobe: hints used to confirm common values "within hours" | Timing | **Not supported by either cited source** | Evidence table | **F8 — removed** |
| C-008 | `index.html` §Vector 2 | Naveed, Kamara & Wright (CCS 2015) recovered attributes from DTE-encrypted columns by frequency analysis against public auxiliary data, on HCUP NIS records; target was EDB systems, not ECB | Research finding | Author-hosted PDF: DTE and OPE columns, frequency analysis, "National Inpatient Sample (NIS) database of the Healthcare Cost and Utilization Project (HCUP)", 200 US hospitals | Prose; references list | **Verified** |
| C-009 | `index.html` §Vector 2 | SP 800-63B-4 §3.1.1.2 SHALL: salt and hash with a suitable password hashing scheme; salt ≥ 32 bits; cost factor SHOULD be as high as practical | Standards quote, **normative strength** | SP 800-63B-4 HTML fetched; all three matched verbatim, with SHALL/SHOULD correctly distinguished after correction | Prose only | **Verified after F3 correction** |
| C-010 | `index.html` §Vector 2 | Argon2id, scrypt and bcrypt are "a memory-hard scheme" | Technical classification | bcrypt's working set is a fixed ~4 KiB Blowfish S-box table; its cost parameter scales iterations, not memory | Prose only | **F3 — corrected** |
| C-011 | `index.html` §Vector 2 | "The AEAD fix below addresses the other three vectors, not password storage" | Internal consistency | Contradicts §The fix ("determinism Vectors 1–3") and §Residual risk ("GCM defeats all four vectors") | Prose ×3 | **F9 — corrected** |
| C-012 | `index.html` §Vector 3, alt text, `vector3-*.svg`, generator | Recovery costs ≤ `256 × L` queries, ~`128 × L` average; 48-byte default ≈4,600 vs 12,288 worst case | Numeric bound | Measured: L=1→289 (>256), L=8→2,074 (>2,048), L=16→4,146 (>4,096), L=48→12,370 (>12,288). Real bound `257 × L + ≤34` | Prose, alt text, SVG box, generator | **F1 — corrected on all four surfaces** |
| C-013 | `index.html` §Vector 3, demo | 48-byte default takes exactly 4,588 queries, key-independent | Numeric | Node harness (12 random keys) and the in-page counter in Chromium both returned 4,588 | Prose; live demo counter | **Verified** |
| C-014 | `index.html` §Vector 4, `vector4-*.svg` | Donor/base/forged block layouts and the splice arithmetic | Implementation behaviour | Block layouts derived from `attacks.mjs` and compared character-by-character with every figure label: exact match, including the 10 `x`s and 11 `a`s | Prose; figure; code; test | **Verified** |
| C-015 | `index.html` §Detecting ECB | Oracle JCA: "the SunJCE and SunPKCS11 providers use ECB as the default mode, and PKCS5Padding as the default padding for many symmetric ciphers"; the JCA itself defines no default | Standards/vendor quote | JDK 21 JCA reference guide fetched; matched **verbatim**. The guide confirms the default is provider-chosen | Prose only | **Verified** |
| C-016 | `index.html` §Detecting ECB | A repeated ciphertext block is *sufficient* evidence of deterministic, block-independent encryption | Logical claim | Constant-IV CBC and nonce-reused CTR produce the same signature across a corpus — which is the case the page's own Vector 2 demo exhibits | Prose only | **F5 — corrected** |
| C-017 | `index.html` §Detecting ECB | BouncyCastle was the provider behind most of the Android findings | Historical attribution | Egele et al.: "Android (since version 2.1) uses BouncyCastle as its default cryptographic service provider"; 5,656 of 7,656 (74%) | Prose; evidence table | **Verified** |
| C-018 | `index.html` §The fix | The authentication tag "closes Vector 4" — demonstrated by flipping one ciphertext bit | Demonstration claim | Vector 4 is a block splice, not a bit flip. Demo did not exercise the attack it claimed to defeat | Prose; demo verdict string; README bullet | **F2 — corrected** |
| C-019 | `index.html` §Evidence table | Zoom 2020 (CVE-2020-11500): one AES-128 key in ECB for all audio/video; AES-128 not the marketed AES-256 | Historical | Citizen Lab: "in each Zoom meeting, a single AES-128 key is used in ECB mode by all participants to encrypt and decrypt audio and video" | Table only | **Verified** |
| C-020 | `index.html` §Evidence table | MS OME 2022: ECB; Microsoft replied the report "was not considered meeting the bar for security servicing"; no code change, no CVE | Historical quote | Archived WithSecure advisory: "The report was not considered meeting the bar for security servicing, nor is it considered a breach. No code change was made and so no CVE was issued for this report." | Table only | **Verified** |
| C-021 | `index.html` §Evidence table | Egele et al.: 11,748 apps; ECB most-violated rule at 7,656; 5,656 via the provider default | Research statistics | Author-hosted PDF: all three figures matched exactly, incl. Table 2 | Table; §Detecting ECB | **Verified** |
| C-022 | `index.html` §Residual risk | Böck et al. (WOOT 2016) found 184 HTTPS servers repeating AES-GCM nonces, fully breaking authenticity | Research finding | Paper abstract, **verbatim**: "With an Internet-wide scan we identified 184 HTTPS servers repeating nonces, which fully breaks the authenticity of the connections." §5: "We found 184 devices that used a duplicate nonce." | Prose only | **Verified** |
| C-023 | `index.html` §Residual risk | SP 800-38D §8 states the IV requirement as a probability bound of 2⁻³² | Standards quote | SP 800-38D PDF §8, **verbatim**: "The probability that the authenticated encryption function ever will be invoked with the same IV and the same key on two (or more) distinct sets of input data shall be no greater than 2-32." | Prose; references list | **Verified** |
| C-024 | `index.html` §Residual risk | §8.2.1 deterministic = fixed field + invocation field; §8.2.2 RBG-based ≥ 96 random bits | Standards summary | SP 800-38D §8.2.1 and §8.2.2 read in full: "the fixed field shall identify the device, or, more generally, the context"; "the length of the random field shall be at least 96 bits" | Prose only | **Verified** |
| C-025 | `index.html` §Residual risk | §8.3 caps invocations at 2³² for any implementation not using 96-bit deterministic IVs | Standards summary, numeric | SP 800-38D §8.3, **verbatim**: "unless an implementation only uses 96-bit IVs that are generated by the deterministic construction: The total number of invocations of the authenticated encryption function shall not exceed 2^32" | Prose; references list | **Verified** |
| C-026 | `crypto.mjs` header, `README.md` | ECB reconstructed as AES-CBC with a zero IV, verified against SP 800-38A vectors | Implementation claim | `test/attacks.test.mjs` asserts both the F.1.1 encrypt and F.1.2 decrypt vectors; both pass. Decrypt uses a separate vector so a symmetric bug cannot pass | Code comment; README; page footer | **Verified** |
| C-027 | `index.html` footer | "The block/oracle/service logic is the same code that backs the test suite" | Provenance | True of block/oracle/service. **Not** true of the image path, which `ui.mjs` duplicated inline while `encryptPixels` sat unused and untested | Footer; README; `ui.mjs` header comment | **F7 — corrected; the claim is now true of the image path too** |
| C-028 | `index.html` §The fix | CBC with a fresh unpredictable IV, or CTR with a never-reused counter block, plus encrypt-then-MAC verified before decryption | Engineering guidance | Standard construction; correctly ordered (verify before decrypt) and correctly hedged as "more to get wrong" | Prose only | **Verified** |
| C-029 | `index.html` §The fix | Migration: rewriting old ECB data requires decrypt-and-re-encrypt plus key rotation | Operational guidance | Internally consistent; no external claim | Prose only | **Verified** |
| C-030 | `modes-*.svg` CBC row | "XORs each block with the previous ciphertext first" | Mechanism, **inside a figure** | The figure draws P₁, which has no previous ciphertext — it is XORed with the IV. SP 800-38A §6.2: "The CBC mode requires an IV to combine with the first plaintext block" | Figure; alt text; prose | **F6 — corrected on all three** |

## Topic completeness matrix

**covered** / **n/a** (with reason) / **REQUIRED GAP** / *optional extension*

| Topic | Definition | Boundaries | Actors/components | Mechanism/sequence | Assumptions/dependencies | Threats/failures | Limits/residual risk | Selection/use | Operations/evidence | Recovery/lifecycle | Interoperability/migration | Unsafe alternatives | Visual representation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ECB mechanism | covered | covered (single-block boundary, corrected by F4) | covered | covered | covered | covered | covered | covered | covered | n/a — no lifecycle at mechanism level | n/a | covered (SP 800-38F pointer) | covered (modes figure) |
| Vector 1 — pattern leakage | covered | covered | covered | covered | covered | covered | covered | covered | covered (test added by F7) | n/a | n/a | covered | covered (live canvases) |
| Vector 2 — equality/frequency | covered | covered | covered | covered | covered | covered | covered | covered | covered | covered (rehash on next login) | n/a | covered | *optional: a frequency-analysis figure* |
| Vector 3 — byte-at-a-time | covered | covered | covered | covered | covered | covered | covered (cost bounds, corrected by F1) | covered | covered | n/a | n/a | covered | covered |
| Vector 4 — cut-and-paste | covered | covered | covered | covered | covered | covered | covered | covered | covered | n/a | n/a | covered | covered |
| ECB detection | covered | covered (necessary/sufficient, corrected by F5) | covered | covered | covered | covered | covered | covered | covered | n/a | n/a | covered | *optional: a decision flow for the two tests* |
| The AEAD fix | covered | covered | covered | covered | covered | covered | covered | covered | covered (contrast demo, added by F2) | covered (rewrite + key rotation) | covered | covered | covered |
| GCM residual risk | covered | covered | covered | covered | covered | covered | covered | covered | covered | covered (rekey schedule) | covered | covered | n/a — a two-item construction choice reads clearly as a list |

**No required gaps.** Two optional extensions recorded below.

## Argument integrity

**Thesis AS STATED** (title, H1 "AES-ECB mode is unsafe", lede, meta description): *AES-ECB is unsafe: its determinism alone breaks confidentiality outright, failing IND-CPA with adversary advantage 1 regardless of key size, and its lack of authentication turns that same determinism into forgery.*

**Thesis AS SUPPORTED** (what this artifact's own sources establish, at their strength and scope): *AES-ECB is unsafe: SP 800-38A documents the equal-block property and directs that ECB "should not be used" where it is undesirable; determinism makes ECB fail IND-CPA with advantage 1 at any message length once the adversary holds the CPA oracle; and four documented vectors plus four attested real-world failures (Adobe, Zoom, MS OME, 7,656 Android apps) follow from determinism and the missing authentication.*

**Gap between the two lines: none.** The two lines are written out in full rather than collapsed to a verdict, per the standard. They differ in specificity, not in force or scope: the supported line names the sources; the stated line makes no claim the sources do not carry. In particular "regardless of key size" is correct — the break is in the mode, and the IND-CPA failure is unconditional on key length. Note this verdict holds *after* F4: before it, the body carved out a single-block case that the lede did not, which pulled in the opposite direction (the body understated what the lede correctly asserted). That is why F4 is filed as a required finding rather than a wording preference.

| Test | Result | Evidence or finding |
| --- | --- | --- |
| Thesis support | **Pass** | Every load-bearing citation verified verbatim against its primary source (C-001, C-009, C-015, C-020, C-022, C-023, C-025). The aggregate does not exceed what the parts establish. |
| Detached headline | **Pass** | H1 "AES-ECB mode is unsafe" — supported unconditionally; SP 800-38A itself says not to use it where the property is undesirable, and no deployment is exempted by the standard. `<title>` "Why AES-ECB mode is unsafe — interactive" — same claim plus a format note. Meta description — enumerates without overstating. README opening is byte-identical to the lede, so it inherits the same verdict. Each was judged as the only sentence a reader sees. |
| Comparison-set validity | **Pass** | Two comparison sets. (a) ECB vs CBC vs GCM — all three are modes a reader can select, compared on one axis (what feeds each block encryption). (b) AEAD vs CBC/CTR-plus-MAC in §The fix — both selectable, compared on the same axis, with the trade-off stated. Password *hashing* schemes are correctly presented as a different decision, not as a fourth mode. |
| Demonstration sufficiency | **Finding → fixed (F2)** | Image demo: shows ECB, CBC and GCM under one key — contrast complete. Block playground: ECB then CBC/GCM — complete. Vector 4 + GCM: **was incomplete** — the attack was a splice, the defence demonstrated a bit flip. Now the same `forgeAdminToken()` runs against both services with the mode as the only variable. |
| Dangling claims | **Pass after residual pass** | Every term introduced is developed: IND-CPA, codebook, malleability, encrypt-then-MAC, memory-hard (now explained rather than asserted), the 2³² ceiling (with its operational consequence). ChaCha20-Poly1305, KW/KWP/TKW and PBKDF2 appear as pointers within selection lists, which is sufficient development for that role. One genuine dangler was **introduced by F4's own fix** — "That boundary" lost its referent when the preceding paragraph was rewritten — and was caught by residual exhaustion. |
| Structure serves the decision | **Pass** | Mechanism → why it breaks → taxonomy → four vectors (each paired with its demo) → detection → fix → evidence → residual risk → recall. Detection precedes the fix, which is the order a reader acts in: find it, then fix it. Headings name what the reader is deciding. |

## Cross-format and cross-page ledger

| Concept or claim | Representations compared | Result |
| --- | --- | --- |
| Attack cost `257 × L` | `index.html` prose; figure alt text; `vector3-*.svg` summary box; generator source; live demo counter; test assertions | Was inconsistent-and-wrong on 4 surfaces (F1). Now consistent on all 6, with a guard on 3. |
| CBC mechanism / IV | `index.html` §The mechanism prose; modes figure alt text; `modes-*.svg` caption; generator | Was wrong in the figure and silent about the IV in the alt text (F6). Now consistent on all 4. |
| AEAD closes Vector 4 | `index.html` §The fix; demo verdict string in `ui.mjs`; `README.md` bullet; test suite | Was a claim with no matching demonstration (F2). All 4 now describe the splice contrast. |
| Adobe record count | `index.html` §Vector 2 ("~153M"); evidence table ("~153M") | Now `152,982,479` in both, matching the source exactly. |
| AEAD and Vector 2 | §Vector 2 ("other three vectors"); §The fix ("Vectors 1–3"); §Residual risk ("all four vectors") | Was a three-way contradiction (F9). Now consistent. |
| "same code the test suite verifies" | `index.html` footer; `README.md`; `ui.mjs` header comment; actual imports | Was false for the image path (F7). Now true for all four vectors. |
| Two-root-cause taxonomy | `index.html` prose; `taxonomy.svg`; its alt text ×2 (`index.html`, `README.md`); `attacks.mjs` structure | Consistent throughout. See CD-0010. |
| Lede | `index.html` lede; `README.md` opening paragraph | Byte-identical. Deliberate. |
| Educational-scope framing | `index.html` callout + footer; `DISCLAIMER.md`; `README.md`; `attacks.mjs` header; three figure scope lines | Consistent; authorized-use-only stated on every surface. |

## Visual content ledger

Assessed independently of the prose — agreement with the text is not correctness.

| Visual | Claims it asserts | Independently correct? | Self-sufficient when detached | Caption and alt text verified | Generator and correspondence check | Standalone defensibility | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `modes-ecb-cbc-gcm.svg` | P₁ = P₂ under one key; ECB → C₁ = C₂ "the pattern leaks"; CBC → C₁ ≠ C₂; GCM → C₁ ≠ C₂; three mechanism captions | **Was NOT** — the CBC caption was wrong for P₁, one of the two blocks it draws | **Was NOT** — the IV was named nowhere, so read alone it taught that chaining, not a fresh IV, is what stops the repeat | Alt text carried the same omission; corrected | Regenerated byte-identical before and after the fix | Yes — a mode comparison, no technique or targeting depicted | **F6 — corrected;** IV named in the CBC row, plus a footer qualifier on IV/nonce reuse |
| `taxonomy.svg` | Two root causes; four vectors; solid arrows RC1→V1,V2,V3 and RC2→V4; dashed RC1→V4 "needs determinism too"; passive/active labels per vector; "there is no third" | **Yes** — every arrow traced to the prose and to `attacks.mjs`; the dashed dual-dependency arrow is correct | **Yes** — subtitle bounds the "no third" claim to the vectors drawn; scope line present | Alt text conveys the full tree and the conclusion, in both `index.html` and `README.md` | Byte-identical | Yes — scope line names the local in-page oracle | **Pass.** See CD-0010. |
| `vector3-byte-at-a-time.svg` | Oracle definition; legend (filler / secret byte / candidate); Step 1 = 15 filler + S0; Step 2 = 14 filler + S0,S1; cost box; scope line | Structure and cell colouring correct against `attacks.mjs` and the legend; **cost box was wrong** | Legend, oracle definition and scope line all present | Alt text repeated the wrong bound | Byte-identical before and after | Yes — scope line names `makeSuffixOracle` and forbids third-party use | **F1 — corrected** in the box and the alt text |
| `vector4-cut-and-paste.svg` | Donor 4 blocks; base 3 blocks with block 2 struck through; forged = base 0–1 + donor block 1; splice arrow; outcome; scope line | **Yes** — every block label verified character-by-character against the profile strings the code produces, including the 10-`x` and 11-`a` local parts | **Yes** — scope line states `ProfileService` is a local stand-in with the key in-process | Alt text describes the donor/base/splice mechanism and the outcome | Byte-identical | Yes — no real service, no targeting capability | **Pass** |

Rendered validation: all four SVGs and the complete page were loaded in Chromium at 1280×720 under `prefers-color-scheme: light` and `dark`. No clipping, overflow, or text collision — including at the enlarged heights the F1 and F6 fixes introduced (540 px and 656 px, from 512 and 636). The theme-aware CSS variables resolve correctly in both schemes.

### Representation opportunities

| Location | What is dense | Proposed form | Required gap or optional extension |
| --- | --- | --- | --- |
| §Vector 2 | Frequency analysis is described in prose; the demo only shows clustering | A histogram pairing an encrypted column against a public auxiliary distribution | **Optional extension.** The prose is clear and the claim is correctly attributed to Naveed et al. rather than demonstrated. |
| §Detecting ECB | Two tests with different necessary/sufficient properties, now with a corpus caveat (F5) | A small decision flow: single message vs corpus → what a repeat does and does not establish | **Optional extension.** The corrected prose is explicit about both directions. |

## Applicable durable content decisions

The register was **empty at review start** — the user asked for `reviews/` to be cleared. Current sources and primary evidence were therefore evaluated with no prior decision available to pre-classify anything, which is the independence the standard asks for and, in this case, the only option. All 12 records below were **written by this review**, not reconciled against.

| Decision ID | Affected concept | Disposition | Current evidence and rationale |
| --- | --- | --- | --- |
| CD-0001 | Vector 3 attack cost | **New** | F1. Measured worst case exceeds the stated bound at every tested length. |
| CD-0002 | Demonstration sufficiency for Vector 4's mitigation | **New** | F2. Same forge, two services, mode as the only variable. |
| CD-0003 | Single-block scope vs IND-CPA | **New** | F4. The CPA oracle defeats determinism at one block. |
| CD-0004 | bcrypt, memory-hardness, SP 800-132 | **New** | F3. bcrypt's ~4 KiB working set scales time, not memory. |
| CD-0005 | AEAD and Vector 2 | **New** | F9. Resolves a three-way internal contradiction. |
| CD-0006 | Detection necessary/sufficient | **New** | F5. Constant-IV CBC is a documented real defect (1,932 apps). |
| CD-0007 | Modes figure must name the IV | **New** | F6. Wrong for the first block the figure draws. |
| CD-0008 | Vector 1 test coverage / dead code | **New** | F7. `encryptPixels` was exported, documented, and unused. |
| CD-0009 | Adobe row figures and citation | **New** | F8. Exact count; unsourced timing claim removed. |
| CD-0010 | Two-root-cause taxonomy | **New — `rejected`** | Considered and deliberately not changed. Padding-oracle and length-leakage were weighed as candidate third causes and rejected. Recorded so it is not re-argued. |
| CD-0011 | ACM paywalled citations | **New — `rejected`** | dl.acm.org 403 is bot mitigation, not link rot. Both papers verified in author-hosted copies. Recorded so the 403 is not re-raised. |
| CD-0012 | Single-engine rendered verification | **New — `rejected`** | Chromium-only, both color schemes, disclosed rather than expanded. Recorded as a standing accepted limitation. |

Register validation: `python3 scripts/verify_content_decisions.py` → *"Validated 12 durable content decisions."*

## Mechanical and rendered checks

| Check | Scope | Result | What this does not prove |
| --- | --- | --- | --- |
| `npm test` (`node --test`) | `test/attacks.test.mjs` (15) + `test/docs-claims.test.mjs` (9) | **24 passed, 0 failed** | That untested behaviour is correct, or that a passing documentation guard means the surrounding prose is accurate — each guard pins one specific claim. |
| `npm run lint` (eslint) | `docs/js/**`, `test/**` | **Clean** | Nothing about semantics or cryptographic correctness. |
| NIST SP 800-38A vector check | `aesEcbEncrypt` (F.1.1) and `aesEcbDecrypt` (F.1.2) | **Both pass** | Only that AES-128-ECB matches NIST for these vectors. Decrypt uses independent vectors, so a symmetric bug in both directions cannot pass. |
| Generator correspondence | `generate_diagrams.py` → all four SVGs | **Byte-identical** on re-run, before and after the fixes | That a figure is *correct* — only that the committed artifact is what the generator currently produces. Correctness was assessed separately in the visual ledger. |
| External link resolution | 21 distinct URLs in `index.html` + `README.md` | **All resolve.** Two `dl.acm.org` DOIs return 403 to automated fetches (Cloudflare bot mitigation, not link rot) — see CD-0011. | That a resolving page still contains the quoted text. Every quotation was separately re-fetched and matched — see the ledger. |
| Rendered validation | 4 SVGs + full page, Chromium 1280×720, light and dark | **No clipping, overflow, or collision** in either scheme | Behaviour on Gecko or WebKit — see CD-0012. |
| Live demo execution | All six in-page demos driven via DOM in Chromium | **All produce their documented outputs**, including the 4,588 counter and the new ECB-vs-GCM splice contrast | That the demos are correct for inputs not exercised. Adversarial inputs were applied specifically to the Vector 3 cost claim. |
| Browser console | Full page, all demos run | **No errors, no warnings** | — |
| Guard-fire verification | All 10 new guards | **All 10 fire** on their reintroduced fault (3 required rework — see below) | That the guards cover faults they were not written for. |
| `verify_content_decisions.py` | `reviews/CONTENT_DECISIONS.yml` | **12 decisions validated** | Registry structure and references only — explicitly not technical correctness. |

## Open required findings

**None.** All nine required findings were remediated during this review and re-verified against the post-fix baseline `3032bc186e0e7f83d78a12be63dcc71cb3e87a58126fd5a6b39326927045b1a1`. They are recorded here because the record must show what the review found, and in the register as CD-0001…CD-0009.

| # | Location | Issue | Classification | Impact | Decision |
| --- | --- | --- | --- | --- | --- |
| F1 | `index.html` §Vector 3; alt text; `vector3-*.svg`; generator | Cost stated as `≤ 256 × L` (48-byte worst case 12,288). Real bound is `257 × L` plus ≤34 setup — each position also costs one query to capture the target block. Measured 12,370 at L=48. | Factual / executable-demonstration / cross-format / visual | Highest. The page tells the reader to check this against a counter that disproves it. | CD-0001 |
| F2 | `index.html` §The fix; `ui.mjs`; `attacks.mjs`; `README.md` | The page claimed the tag "closes Vector 4"; the demo flipped one bit. Vector 4 is a block splice. | Argument integrity — demonstration sufficiency | The central defensive claim had no matching demonstration. | CD-0002 |
| F3 | `index.html` §Vector 2 | bcrypt grouped with Argon2id and scrypt as "a memory-hard scheme". | Factual / terminology | Misstates the property that motivates memory-hard functions. | CD-0004 |
| F4 | `index.html` §Why determinism… | "It needs at least two blocks that can repeat… this particular break does not apply" reads as a limit on the IND-CPA break. The CPA oracle defeats determinism at any length. | Argument integrity / attacker-state precision | A reader concludes single-block ECB is IND-CPA-safe. It is not. | CD-0003 |
| F5 | `index.html` §Detecting ECB | "Sufficient evidence of deterministic, block-independent encryption" — false across a corpus, which is the case the page's own Vector 2 demo exhibits. | Adversarial claims / overclaim | Detection guidance readers act on. | CD-0006 |
| F6 | `modes-*.svg`; generator; alt text; prose | CBC row said "XORs each block with the previous ciphertext" — wrong for P₁, which the figure draws; the IV was named nowhere in the figure. | Visual content — independent correctness + detached self-sufficiency | Read alone, the figure taught the wrong mechanism for CBC's protection. | CD-0007 |
| F7 | `attacks.mjs`; `ui.mjs` | `encryptPixels` exported, documented as Vector 1, imported by nothing; `ui.mjs` carried an inline duplicate. Vector 1 was the only untested vector. | Code/demonstration correctness / duplication | The "same code the test suite verifies" claim was false for the image path. | CD-0008 |
| F8 | `index.html` evidence table | "within hours" — unsourced; the row was also the only one without an inline citation. | Evidence authority | Minor, but it was the one figure in the row nothing supported. | CD-0009 |
| F9 | `index.html` §Vector 2 vs §The fix vs §Residual risk | "The AEAD fix below addresses the other three vectors" contradicted "Vectors 1–3" and "all four vectors". | Internal contradiction | A reader concludes GCM leaves equality inference intact. | CD-0005 |

Two further defects were introduced **by the fixes themselves** and caught by residual exhaustion:

| # | Location | Issue | Resolution |
| --- | --- | --- | --- |
| F4-r | `index.html` §Why determinism… | The following paragraph opened "That boundary is inference from…", whose referent F4's rewrite had removed — it now read as contradicting the paragraph above it. | Reworded to "Even that narrower reading…", re-anchoring to the passive reading and closing on the two conditions the claim depends on. |
| F2-r | `README.md` | The fix bullet still described "flip one bit and watch the authentication tag reject it". | Rewritten to describe the splice contrast. |
| F2-g | `ui.mjs` | The `ECB — same splice → role=admin` line in the rewritten GCM panel was a **hardcoded string** beside three computed results — an assertion dressed as a measurement, on a page whose lede promises otherwise. | `forgeUnderBothModes()` now executes both halves; the panel renders `ecbForgedRole`. Guarded. |
| F2-h | `attacks.mjs` | `forgeAdminToken(service, headerSize = 0)` took the token layout from the caller. A GCM caller omitting it still got a rejected 64-byte token, so the ECB/GCM comparison would pass while proving only that a mangled nonce breaks decryption. | Header size now read from `service.constructor.headerSize`. Guarded **structurally** — no behavioural check can separate the two, which is why the defect was invisible. |
| F2-i | `ui.mjs` | `runGcm` disabled its button with no `try/finally`, so any throw left the demo stuck until reload. | Wrapped in `try/finally`. |

F2-g, F2-h and F2-i were found by the **pre-check-in `review-pr` gate**, not by this review's own passes — the gate ran `code-review` at high effort over the remediation diff. They are recorded here because a closure claim that omitted three real defects found after the record was written would be false. All three are folded into **CD-0002**.

## Dismissal ledger — candidates considered and dropped

| What was noticed | Artifact and location | Why it is not a finding |
| --- | --- | --- |
| The modes figure carries no educational-scope footer, while the other three do | `modes-ecb-cbc-gcm.svg` | It depicts a mode comparison, not an attack technique, and shows no targeting capability. It is defensible read alone. The `docs-claims` guard deliberately requires scope lines only on the three *attack* figures. |
| "Only ECB leaks structure" is unqualified as a figure title | `modes-ecb-cbc-gcm.svg` title | The three compared modes are drawn in the same frame, so the scope is visible without the page. The new footer qualifier further bounds it by naming IV/nonce reuse. |
| "The BouncyCastle provider behind most of the Android findings did the same" carries no inline citation | `index.html` §Detecting ECB | Supported by the Egele et al. row it explicitly points to ("below"), which is linked in that table: 5,656 of 7,656 = 74%. Verified at C-017. |
| The Vector 2 demo clusters on ciphertext equality but never demonstrates frequency analysis | `index.html` demo `#demo-equality` | The demo's heading claims only clustering. Frequency recovery is attributed to Naveed et al. in prose, not claimed as demonstrated. Optional extension, recorded above. |
| "Every vector traces back to these two root causes and to no third" is an authorial taxonomy stated as fact | `index.html`; `taxonomy.svg` | Bounded on its face to the four vectors enumerated; the figure subtitle states the bound. Candidate third causes (padding-oracle behaviour, length leakage) were weighed and rejected. Recorded as **CD-0010** so it is not re-argued. |
| `esc()` escapes only `&`, `<`, `>` — not quotes | `ui.mjs:13` | Every interpolation reaches a text node or an attribute whose value comes from a fixed palette, never user input. No injection path exists. |
| `detectBlockSize`'s `maxProbe = 64` is effectively unreachable (it returns by 16) | `attacks.mjs` | Defensive bound on a loop, not a documented claim. No reader-facing consequence. |
| `dl.acm.org` returns 403 to automated fetches | Two citations | Cloudflare bot mitigation, not link rot; both resolve in a browser and both papers were verified in author-hosted copies. Recorded as **CD-0011**. |
| Rendered checks ran on one engine only | All figures and the page | Real limitation, deliberately accepted rather than expanded: the SVGs use only CSS custom properties and `prefers-color-scheme`. Recorded as **CD-0012** and disclosed below. |
| The lede is duplicated verbatim between `index.html` and `README.md` | Both | Deliberate and correct — a single canonical statement of the thesis. Duplication of a *thesis* is consistency, not drift. |
| `README.md` links `docs/diagrams/taxonomy.svg` by relative path, which GitHub renders but Pages does not serve at that path | `README.md:22` | The README is a GitHub artifact, not a Pages page; the path is correct in the context the file is read in. |

## Optional coverage

Both are enrichment, not correctness defects. Neither is required.

1. **Frequency-analysis figure for Vector 2.** The page describes frequency recovery in prose and cites Naveed et al., but neither demonstrates nor illustrates it. A histogram pairing an encrypted column with a public auxiliary distribution would show why equality plus frequency names values rather than merely grouping them.
2. **Detection decision flow.** After F5 the detection section correctly distinguishes single-message from corpus analysis in both the necessary and sufficient directions. A small flow diagram would make the two-by-two explicit.
3. **Partial-block leakage in the Vector 2 demo.** The Adobe row now records that sharing any 8-character block leaked that portion of a password (C-006). The live demo still clusters on whole-record equality only. Demonstrating sub-record block overlap would connect the demo to the historical case more tightly.

## Limitations and uncertainty

1. **Single rendering engine.** All rendered validation ran in one Chromium build, in both `prefers-color-scheme` settings. Gecko and WebKit rendering of the theme-aware SVGs is **unverified**. Deliberate — see CD-0012.
2. **ACM sources verified through author-hosted copies.** Egele et al. and Naveed et al. were verified against `seclab.cs.ucsb.edu` and `cs.brown.edu` PDFs, not the ACM versions of record, which block automated fetches. Every quoted figure matched. See CD-0011.
3. **WithSecure advisory verified through the Internet Archive.** The original URL now redirects to a landing page; the page already links the archived snapshot, and the quote was verified there. The archived copy is assumed faithful.
4. **Alt-text guard measures length, not substance.** `docs-claims` asserts each figure's alt text exceeds 120 characters. That catches an emptied or stub alt attribute; it cannot detect alt text that is long and wrong. Substance was assessed by hand in the visual ledger.
5. **Adversarial input testing was targeted, not exhaustive.** Adversarial inputs (all-`0xff` secrets) were applied specifically to the Vector 3 cost claim, because that was where a bound was asserted. The other demos were driven with their documented inputs plus the paired ECB/GCM contrast. This is disclosed sampling for `executable-demonstration`.
6. **Two review dimensions are not mechanized.** F4 (claim scoping) and F8 (source sufficiency) resist deterministic guards — see the mechanization table. They remain dependent on `argument-integrity` and `evidence-authority` running.
7. **The prior decision register was destroyed by instruction.** Three deliberate rejections from the previous register no longer protect against re-argument; two were re-derived independently and re-recorded. Recoverable at `git show 403a2566:reviews/CONTENT_DECISIONS.yml`.
8. **Review and remediation ran in one session.** The standard prefers these as separate phases with a frozen baseline between them, which is what was done — but the same reviewer wrote and then re-verified the fixes. Two fix-introduced defects were caught by residual exhaustion; an independent reviewer might catch more.

## Closure attestation

- [x] Every pass is either run-and-clean or validly cached, and every cached one names the run it rests on. — **All 11 ran; none cached.**
- [x] The router's RUN/CACHED split was followed, not overridden by judgement or by how the request was phrased.
- [x] Every in-scope artifact covered by a running pass was inventoried and read in full.
- [x] Every material claim was entered in the ledger and dispositioned. — **30 claims.**
- [x] Every topic received a completeness classification for every category. — **8 topics × 13 categories.**
- [x] Every mandatory pass was completed separately, or is validly cached.
- [x] Current primary sources were used for standards-sensitive and time-sensitive claims. — **SP 800-38A, 38D, 38F, 63B-4, 132; JCA 21; Egele 2013; Naveed 2015; Böck 2016; Citizen Lab; WithSecure; filippo.io — all fetched this session.**
- [x] Prose, metadata, diagrams, captions, alt text, examples, summaries, navigation, and generators were reconciled.
- [x] Every visual was reviewed as its own artifact for independent correctness, detached self-sufficiency, generator provenance, and standalone defensibility, separately from the cross-format pass.
- [x] Applicable mechanical and rendered checks passed or their limitations are recorded.
- [x] Applicable durable content decisions were reconciled after the independent claim review, and every reversal or supersession is justified. — **Register empty at start by instruction; 12 written.**
- [x] The argument-integrity pass was completed, with the thesis recorded both as stated and as supported, and each of title / H1 / lede / meta description judged read-alone.
- [x] Every candidate finding that was considered and dropped is in the dismissal ledger with its reason. — **11 dismissals.**
- [x] Residual exhaustion was completed after findings were assembled. — **Caught F4-r and F2-r.**
- [x] Every guard from a previous finding was executed and still fires. — **None existed; 10 authored, all 10 verified to fire.**
- [x] Each remediated finding gained a guard, or the reason it could not be mechanized is recorded. — **10 of 12 mechanized; F4 and F8 recorded as not mechanizable, with reasons.**
- [x] The pass state was written with `review_passes.py --record`, naming only passes that actually ran.
- [x] The baseline remained frozen, or changes and repeated passes are documented. — **Changed by remediation; documented above.**
- [x] Required findings, optional coverage, and limitations are separated.

**Closure conclusion.** The content at scoped fingerprint `3032bc186e0e7f83d78a12be63dcc71cb3e87a58126fd5a6b39326927045b1a1` is **closed with no open required findings**. Every one of the 11 passes was freshly run at `claude-opus-5`/`high` on 2026-08-24; nothing in this record is carried forward from an earlier run, and nothing rests on assurance older than this review. Nine required findings were identified and remediated, two fix-introduced defects were caught by residual exhaustion and three more by the pre-check-in gate, all remediated, and ten deterministic guards were added and individually verified to fire on the faults they exist to catch.

This is a claim about a pass state at one content state, not a guarantee of future correctness. Six limitations are disclosed above and remain undischarged — most materially, single-engine rendered verification (CD-0012) and the two dimensions that resist mechanization.
