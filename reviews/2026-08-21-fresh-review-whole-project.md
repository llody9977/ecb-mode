# Fresh review record: whole project

## Status and baseline

- Status: Complete with findings (both required findings fixed during this session)
- Review mode: Fresh review
- Review date: 2026-08-21
- Reviewer: Claude (doc-review skill, whole-project scope, user-selected)
- Branch: main
- Commit: `83e09c03dae53d84f10b3da22da2ddcf0ba47dac`
- Worktree at review start: Dirty — unstaged `AGENTS.md` deleted, `README.md` modified, `docs/ecb-mode-unsafe.md` modified (all pre-existing before this session; `AGENTS.md`'s removal is a deliberate, previously-recorded repo decision, not something this review evaluated for correctness).
- Review state ID (post-fix, via the repaired `scripts/capture_review_state.py --output`): `43557124a10f7393887d603492e0361538e8e8931b06c89afbbe6f0699265c54`
- Scoped content fingerprint (post-fix): `e4326e04f701c8012345844f142d9a268d0062e294783b25bb73d4888447085b`
- State-capture command: `python3 scripts/capture_review_state.py`
- Baseline changed during review: **Yes.** The original baseline (`AGENTS.md` deleted / `README.md`, `docs/ecb-mode-unsafe.md` modified) was reviewed first, read-only. The user then authorized implementation ("fix all"); `reviews/CONTENT_DECISIONS.yml` and `scripts/capture_review_state.py` were edited in a second pass, and the affected checks (registry validation, pytest, the script's own dirty-worktree handling) were re-run against the new state. `docs/ecb-mode-unsafe.md` and `README.md` were not touched further beyond the fixes listed below.
- One transient deviation, corrected: an isolated notebook re-run's `plt.savefig` overwrote the tracked `notebooks/ecb_pattern_leakage.png` (nbconvert's execution cwd = the notebook's directory). Caught via `git status`, reverted with `git checkout --`; restored SHA-256 (`57e646f0...`) confirmed to match baseline.

## Scope inventory

| Artifact | Type | Direct dependents or generated counterpart | Inspected |
| --- | --- | --- | --- |
| `README.md` | doc | — | Yes |
| `docs/ecb-mode-unsafe.md` | doc | `notebooks/ecb_mode_deep_dive.ipynb` (companion), `notebooks/ecb_pattern_leakage.png` (embedded figure) | Yes |
| `src/ecb_lab/crypto_helpers.py` | code | `tests/test_crypto_helpers.py` | Yes |
| `src/ecb_lab/detection.py` | code | `tests/test_detection.py` | Yes |
| `src/ecb_lab/pattern_leakage.py` | code | `tests/test_pattern_leakage.py` | Yes |
| `src/ecb_lab/oracle_attack.py` | code | `tests/test_oracle_attack.py` | Yes |
| `src/ecb_lab/cut_and_paste.py` | code | `tests/test_cut_and_paste.py` | Yes |
| `src/ecb_lab/__init__.py` | code | — | Yes |
| `tests/*.py` (5 files) | test | corresponding `src/ecb_lab` modules | Yes |
| `notebooks/ecb_mode_deep_dive.ipynb` | executable asset | `docs/ecb-mode-unsafe.md` (companion) | Yes — re-executed end to end |
| `notebooks/ecb_pattern_leakage.png` | generated asset | Vector 1 figure in `docs/ecb-mode-unsafe.md` | Yes |
| `reviews/REVIEW_TEMPLATE.md` | tooling | — | Yes |
| `reviews/CONTENT_DECISION_GUIDE.md` | tooling | — | Yes |
| `reviews/CONTENT_DECISIONS.yml` | tooling/registry | validated by `scripts/verify_content_decisions.py` | Yes — edited |
| `scripts/capture_review_state.py` | tooling | — | Yes — edited (bug fix) |
| `scripts/verify_content_decisions.py` | tooling | — | Yes |
| `pyproject.toml`, `requirements.txt`, `.gitignore` | config | — | Yes (light pass; no issues) |
| `AGENTS.md` (deleted) | doc | — | Confirmed absent, confirmed zero dangling references repo-wide |

Out-of-scope boundaries and reason: dependency-freshness audit of `requirements.txt` pins was not performed in depth (floor versions only, no CVE/deprecation sweep) — the project is a documentation/teaching repo, not a deployed service, so this was judged low-risk and out of the doc-review skill's core mandate.

## Review passes

| Pass | Complete | Evidence or notes |
| --- | --- | --- |
| Factual and technical correctness | Yes | Full manual trace of `cut_and_paste.py`'s block-splice arithmetic and `oracle_attack.py`'s byte-at-a-time recovery against the code; corroborated by 22/22 passing tests and a live notebook re-execution. |
| Evidence, authority, version, date, jurisdiction, applicability | Yes | See material-claim ledger — every citation in the real-world evidence table and Primary References fetched and checked against primary/first-party text this session. |
| Adversarial wording, assumptions, attacker state, counterexamples | Yes | Found and fixed Vector 4's missing attacker-state qualifier; verified IND-CPA proof construction; verified scope-note logic. |
| Terminology, taxonomy, conceptual boundaries | Yes | Vector header pattern now consistent across all four vectors. |
| Cross-format consistency | Yes | README ↔ `docs/ecb-mode-unsafe.md` ↔ `src/ecb_lab/` ↔ `tests/` ↔ notebook module/vector references cross-checked; all consistent post-fix. |
| Cross-page consistency, prerequisites, sequence, duplication | Yes | Single-document project; internal section flow and the doc/README/notebook triad checked for duplication and drift — none found. |
| Topic completeness | Yes | See completeness matrix below. |
| Mechanical, link, generator, executable, rendered-output validation | Yes | `pytest` (22/22), isolated notebook re-execution (all cells reproduce claimed output), `verify_content_decisions.py`, PNG dimension/format check, `capture_review_state.py` exercised against the dirty worktree (bug found and fixed). |
| Durable content-decision reconciliation | Yes | CD-0001 reaffirmed (unchanged scope); CD-0002 newly added for the two primary-source-verified corrections in this diff; CD-0001's `related_decisions` updated to cross-link. |
| Residual exhaustion | Yes | Re-read Vector 1–4 headers, Residual risk section, and Primary References after fixes were drafted, specifically checking for further citation-symmetry or taxonomy-pattern issues; none found beyond what's reported. |

## Material-claim ledger

| ID | Artifact and location | Material claim | Classification | Primary source or verification | Repetitions checked | Result |
| --- | --- | --- | --- | --- | --- | --- |
| C-001 | `docs/ecb-mode-unsafe.md`, Scope note | ECB's determinism is harmless only for a single, never-repeated block; SP 800-38A does not itself carve out this exception | Standards attribution | See CD-0002 (NIST SP 800-38A §6.1, verified zero-match; corroborated by 2022 revision proposal) | README (no restatement) | Closed — verified accurate; **was inaccurate before this session's uncommitted fix** (old text falsely attributed a key-wrapping exception to NIST) |
| C-002 | `docs/ecb-mode-unsafe.md`, real-world evidence table (Naveed/Kamara/Wright row) | ℓp-optimization attack recovered mortality risk for 100% of patients in ≥99% of the 200 largest hospitals | Numerical/statistical, security-sensitive | See CD-0002 (CCS 2015 author PDF §9.1, quote on file) | Primary References entry | Closed — verified accurate |
| C-003 | `docs/ecb-mode-unsafe.md`, same row | Sorting attack against OPE recovered admission month and mortality risk for 100% of patients in ≥90% of hospitals | Numerical/statistical | Same paper, §9.2: density=1 for 100% of hospitals (Mortality Risk) and 90% of hospitals (Admission Month); "at least 90%" is a true, if slightly conflated, floor for both | — | Closed — true but imprecise (mortality risk is actually 100%, not just ≥90%); noted, not corrected — see Optional coverage |
| C-004 | `docs/ecb-mode-unsafe.md`, Zoom row | AES-128-ECB, single key per meeting; contradicted marketed AES-256 | Security-sensitive, CVE-backed | CVE-2020-11500 (NVD) + Citizen Lab report, both fetched and quoted this session | README | Closed — verified accurate |
| C-005 | `docs/ecb-mode-unsafe.md`, Microsoft OME row | ECB usage, bug bounty paid, no fix shipped, "does not meet the bar for security servicing" | Security-sensitive, vendor-response claim | WithSecure/BleepingComputer coverage (WithSecure's own advisory page 301-redirected; corroborated via BleepingComputer with the same exact Microsoft quote) | — | Closed — verified accurate |
| C-006 | `docs/ecb-mode-unsafe.md`, CCS 2013 row | 11,748 apps, 88% made a mistake, 7,656 violated "no ECB," 5,656 via BouncyCastle default | Statistical, prevalence claim | Egele, Brumley, Fratantonio & Kruegel, ACM CCS 2013 (fetched); figures match exactly, including the 5,656/2,000 sub-split | detection.py's `KNOWN_ECB_DEFAULT_FOOTGUNS`, README | Closed — verified accurate |
| C-007 | `docs/ecb-mode-unsafe.md`, Adobe row | ~153M records, 3DES inferred (not confirmed) from 8-byte block, unsalted, hint-assisted cracking | Security-sensitive, historical | filippo.io analysis (fetched, quoted); Schneier blog request 403'd, not independently re-fetched this session | — | Closed — verified accurate; Schneier corroboration disclosed as a limitation, not a gap (filippo.io independently substantiates every sub-claim) |
| C-008 | `docs/ecb-mode-unsafe.md`, MEGA/bilibili/Aarogya Setu footnote | Three real GitHub issues report `Cipher.getInstance("AES")` → ECB default | Code-instance claim | All three issues fetched directly (`meganz/android#299`, `10miaomiao/bilimiao2#270`, `nic-delhi/AarogyaSetu_Android#203`) | `detection.py` `KNOWN_ECB_DEFAULT_FOOTGUNS` | Closed — verified accurate |
| C-009 | `docs/ecb-mode-unsafe.md`, Vectors 3/4 | Techniques correspond to Cryptopals Set 2 Ch.12 (byte-at-a-time, simple), Ch.13 (cut-and-paste), Ch.14 (harder/prefixed, not implemented) | Attribution | cryptopals.com/sets/2 fetched; titles confirmed exactly | Set 1 Ch.8 also confirmed for the detection section | Closed — verified accurate |
| C-010 | `docs/ecb-mode-unsafe.md`, Residual risk | Nonce reuse is "the actual mechanism behind real-world GCM breaks" | Security-sensitive, previously uncited | Böck, Zauner, Devlin, Somorovsky & Jovanovic, USENIX WOOT 2016 (eprint.iacr.org/2016/475, fetched and quoted: 184 HTTPS servers found repeating nonces, working forgery PoC) | Primary References | **Fixed this session** — citation added; was previously an uncited assertion |
| C-011 | `README.md` | Vectors 1, 3, 4 have dedicated `src/ecb_lab/` modules + tests; Vector 2 is notebook-only | Structural/accuracy | Direct code inspection: `pattern_leakage.py`/`oracle_attack.py`/`cut_and_paste.py` exist and map 1:1; no Vector-2-specific module or test found anywhere | `tests/` directory listing | Closed — verified accurate (this was the subject of the pre-existing uncommitted README fix) |
| C-012 | `README.md` | "22 tests, all four vectors + detection + crypto helpers" | Numerical | `pytest -q` → 22 passed; `--collect-only` enumerated matches the claim | — | Closed — verified accurate |
| C-013 | `docs/ecb-mode-unsafe.md`, Vector headers | Each vector states `(root cause, attacker state)` | Taxonomy/structure | Direct inspection: Vectors 1–3 followed the pattern, Vector 4 omitted the attacker-state half | — | **Fixed this session** — Vector 4 now reads `(no integrity, active splice)` |

## Topic completeness matrix

| Topic | Definition | Boundaries | Actors/components | Mechanism/sequence | Assumptions/dependencies | Threats/failures | Limits/residual risk | Selection/use | Operations/evidence | Recovery/lifecycle | Interoperability/migration | Unsafe alternatives |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ECB mechanism & failure | Covered | Covered (scope note) | Covered (implicit, per-vector) | Covered | Covered | Covered (4 vectors) | Covered | Covered (Defensive control) | Covered (Detecting ECB / Verification) | Optional extension (not covered; deliberately out of README's stated scope) | Optional extension (not covered; same reason) | Covered (CBC/CTR+MAC vs. AEAD tradeoff) |

Single row because the document treats one cohesive subject; the deliberate scope boundary ("not a general cryptography survey," per README) is the stated reason categories 10–11 are unaddressed, judged a legitimate, disclosed scope choice rather than a gap.

## Cross-format and cross-page ledger

| Concept or claim | Representations compared | Result |
| --- | --- | --- |
| Vector→module mapping | README bullet list, `docs/ecb-mode-unsafe.md` prose, actual `src/ecb_lab/` files, `tests/` files, notebook imports | Consistent across all five |
| Test count (22) | README, live `pytest` run | Consistent |
| ECB detection functions | `docs/ecb-mode-unsafe.md` "Detecting ECB mode usage", `detection.py`, notebook detection cell, `test_detection.py` | Consistent |
| GCM defensive control | `docs/ecb-mode-unsafe.md` Defensive control + Residual risk, `crypto_helpers.aes_gcm_encrypt`, notebook GCM cells, `test_crypto_helpers.py` | Consistent; live re-execution confirms `InvalidTag` behavior matches the doc's claim |
| Vector header taxonomy pattern | Vectors 1–4 headers | Was inconsistent (Vector 4 missing attacker-state qualifier) — fixed |

## Applicable durable content decisions

| Decision ID | Affected concept | Disposition | Current evidence and rationale |
| --- | --- | --- | --- |
| CD-0001 | 2-root-cause/4-vector taxonomy, detection as first-class section | Reaffirmed | Unchanged by this session's diff; still matches current `docs/ecb-mode-unsafe.md` structure and `src/ecb_lab/detection.py`. `related_decisions` updated to cross-link CD-0002. |
| CD-0002 | SP 800-38A scope-note claim; CCS 2015 mortality-risk statistic precision | New (added this session) | Both underlying claims independently re-verified against primary sources (NIST SP 800-38A PDF, NIST revision-proposal page, CCS 2015 author PDF) before the record was written; register previously had zero applicable decisions for these concepts, which was itself Required finding 1 of this review. |

## Mechanical and rendered checks

| Check | Scope | Result | What this does not prove |
| --- | --- | --- | --- |
| `pytest -q` | `tests/` against `src/ecb_lab/` | 22/22 pass, before and after fixes | Correctness of documentation prose, only that the code behaves as its tests assert |
| Isolated notebook re-execution | `notebooks/ecb_mode_deep_dive.ipynb` (copy, not the tracked file) | All 7 code cells re-ran cleanly; ECB/CBC/GCM repeated-block results, secret recovery, forged-token role, and `InvalidTag` tamper rejection all reproduced | Does not prove the notebook's *prose* commentary is accurate, only that its code executes and matches its own printed claims |
| `verify_content_decisions.py` | `reviews/CONTENT_DECISIONS.yml` | Valid before (1 decision) and after (2 decisions) this session's edit | Validates registry structure/references only, not the technical correctness of a decision's content (stated by the tool itself) |
| `capture_review_state.py` (post-fix) | Whole repo, dirty worktree including the deleted `AGENTS.md` | Runs cleanly, records `AGENTS.md` with `"status": "deleted"` instead of aborting | Does not prove the fingerprint algorithm is cryptographically tamper-evident beyond SHA-256's normal guarantees |
| PNG format/dimension check | `notebooks/ecb_pattern_leakage.png` | 1667×466 RGBA PNG, byte-identical to pre-review baseline after the transient-overwrite/revert | Does not prove the image content is a genuine, unedited AES-ECB ciphertext render (that's established instead by the passing `test_pattern_leakage.py` + live re-execution) |
| GitHub issue fetches (×3) | MEGA #299, bilibili #270, Aarogya Setu #203 | All three real, public, and confirm the claimed `Cipher.getInstance("AES")` → ECB pattern | Does not prove these are the *only* such instances, only that the three cited are real and accurately described |

## Open required findings

None. Both required findings from the review pass were fixed in this session:

1. ~~Missing durable decision records for the SP 800-38A and CCS 2015 corrections.~~ **Fixed** — CD-0002 added to `reviews/CONTENT_DECISIONS.yml`, cross-linked with CD-0001, registry re-validated.
2. ~~`scripts/capture_review_state.py` crashes on a tracked-but-working-tree-deleted file.~~ **Fixed** — `capture()` and `resolve_scope()` now record such files with `"status": "deleted"` instead of aborting; verified against both the no-scope-argument path and an explicit `--scope AGENTS.md` request.

## Optional coverage

- **Fixed this session:** Vector 4's header now reads `(no integrity, active splice)`, matching the `(root cause, attacker state)` pattern used by Vectors 1–3.
- **Fixed this session:** The Residual risk section's nonce-reuse claim now cites Böck et al. (USENIX WOOT 2016), matching the citation discipline used for the four main vectors; added to Primary References.
- **Not fixed, by design:** Recovery/lifecycle and interoperability/migration coverage remains absent — this matches README's explicit scope statement ("not a general cryptography survey") and was not treated as a defect.
- **Not fixed, disclosed as imprecise but not incorrect:** C-003's "at least 90%" framing for the OPE sorting attack slightly conflates two different exact per-attribute figures (Mortality Risk is actually 100% of hospitals, Admission Month is 90%) into one shared floor. True in both directions, just not maximally precise; left as-is since fixing it would require restating two separate percentages mid-table-cell, and the user's "fix all" was scoped against the findings actually reported (this nuance was noted in the ledger, not raised as a finding, in the original review).

## Limitations and uncertainty

- Schneier's blog post (secondary Adobe-case source) returned HTTP 403 to `WebFetch` and was not independently re-fetched this session; filippo.io's first-party technical analysis already substantiates every Adobe-row sub-claim, so this is disclosed rather than treated as an open gap.
- Cryptopals Challenge 14's exact "random/unknown prefix" mechanic was confirmed only by title match ("Byte-at-a-time ECB decryption (Harder)"), not by fetching the full challenge body text — this is well-established, widely-documented public knowledge, but flagged as a lighter-touch verification than the other citations.
- `requirements.txt` version floors were sanity-checked but not swept for CVEs or deprecation notices.
- The `jupyter nbconvert` bare-command PATH issue encountered in this reviewer's environment (worked via `python3 -m nbconvert` instead) was judged environment-specific and not a documentation defect; not fixed, not filed as a finding.

## Closure attestation

- [x] Every in-scope artifact was inventoried and read in full.
- [x] Every material claim was entered in the ledger and dispositioned.
- [x] Every topic received a completeness classification for every category.
- [x] Every mandatory pass was completed separately.
- [x] Current primary sources were used for standards-sensitive and time-sensitive claims.
- [x] Prose, metadata, diagrams, captions, alt text, examples, summaries, navigation, and generators were reconciled.
- [x] Applicable mechanical and rendered checks passed or their limitations are recorded.
- [x] Applicable durable content decisions were reconciled after the independent claim review, and every reversal or supersession is justified.
- [x] Residual exhaustion was completed after findings were assembled.
- [x] The baseline remained frozen, or changes and repeated passes are documented.
- [x] Required findings, optional coverage, and limitations are separated.

**Closure conclusion:** Complete, no open required findings. Both required findings and both optional fixes above were implemented and mechanically re-verified this session (pytest, registry validator, script re-run, doc re-read) — see Open required findings / Optional coverage. Remaining items are disclosed scope exclusions or limitations only (see above); none block closure. The three pre-existing uncommitted content edits (README vector-coverage wording, SP 800-38A scope note, CCS 2015 statistic) were independently verified accurate before this record was written.
