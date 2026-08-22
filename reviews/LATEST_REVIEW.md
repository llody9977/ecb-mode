# Fresh review record: post-pivot GitHub Pages site

> Lives at `reviews/LATEST_REVIEW.md` and is overwritten by each new review — this file always holds the
> most recent one. Earlier records are in git, not in this folder:
> `git log -p --follow reviews/LATEST_REVIEW.md` for the full series,
> `git show <commit>:reviews/LATEST_REVIEW.md` for one in full.

## Status and baseline

- Status: Complete with findings — all required and optional findings remediated in this session
- Review mode: Fresh review (whole project), followed by an authorized implementation phase
- Review date: 2026-08-22
- Reviewer: Claude (doc-review skill, whole-project scope, user-invoked `/doc-review`)
- Branch: `fix/post-pivot-doc-review`
- Commit: `64b9ad67ce886976bcf58b396f9b0b87195e4cae`
- Worktree at review start: **Clean.** The read-only review pass ran against the committed state with no local modifications.
- Scoped content fingerprint at review start: `e5e5d4b7f084429d0d5c5671075436ce4d5c4e8cec55b65636f1ee961559a1c5`
- Scoped content fingerprint after remediation: `db82644af5f4118efb00c42d9d8eca34bee167a7d9b4b563a5db271c0195665a`
- Scoped content fingerprint after the subsequent `reviews/` compaction pass: `5f245855820bdcf1ff3e8f253cca45ef55eed39692abfd2e08cd662464656a0c`
- Compaction pass (2026-08-22, after this review closed): housekeeping only, per the doc-review skill's **Periodic compaction** section — ledger and disposition entries that restated a durable decision now reference its ID, and restated narration was cut from `CONTENT_DECISIONS.yml`, and the 2026-08-21 record was consolidated into the appendix below (its full text remains in git at `c0dc291`). No fact, number, source URL, or direct quote was altered; no finding, disposition, or limitation was changed. Compaction is not a review pass and extends this record's coverage to nothing beyond the state attested below.
- State-capture command: `python3 scripts/capture_review_state.py`
- Baseline changed during review: **No during, yes after.** The complete review — every pass, every finding — was performed read-only against clean `64b9ad6`. The user then authorized remediation ("remediate all"); edits were made as a separate phase and every affected check was re-run against the resulting state (13 modified files, listed below). No in-scope file was edited while findings were still being gathered.
- The preceding review covered commit `83e09c0`, a **pre-pivot** state whose scope (`docs/ecb-mode-unsafe.md`, `src/ecb_lab/`, `notebooks/`) no longer exists. It was treated as context only and supplied no coverage for this state; before this record, the post-pivot content had never been reviewed. Its record file was consolidated into the appendix below — see **Prior review provenance**.

## Scope inventory

| Artifact | Type | Direct dependents or generated counterpart | Inspected |
| --- | --- | --- | --- |
| `docs/index.html` | doc (primary) | all four SVGs, `styles.css`, `docs/js/*.mjs` | Yes — edited |
| `docs/styles.css` | presentation | `docs/index.html` | Yes — edited |
| `docs/js/crypto.mjs` | code | `test/attacks.test.mjs` | Yes — edited (comment only) |
| `docs/js/attacks.mjs` | code | `test/attacks.test.mjs`, `docs/js/ui.mjs` | Yes |
| `docs/js/ui.mjs` | code | `docs/index.html` | Yes — edited |
| `docs/diagrams/generate_diagrams.py` | generator | all four committed SVGs | Yes — edited |
| `docs/diagrams/modes-ecb-cbc-gcm.svg` | generated figure | `docs/index.html` | Yes — edited via generator |
| `docs/diagrams/taxonomy.svg` | generated figure | `docs/index.html`, `README.md` | Yes — edited via generator |
| `docs/diagrams/vector3-byte-at-a-time.svg` | generated figure | `docs/index.html` | Yes — edited via generator |
| `docs/diagrams/vector4-cut-and-paste.svg` | generated figure | `docs/index.html` | Yes — edited via generator |
| `test/attacks.test.mjs` | test | `docs/js/*.mjs` | Yes |
| `README.md` | doc | `docs/diagrams/taxonomy.svg` (embedded) | Yes — edited |
| `DISCLAIMER.md`, `SECURITY.md`, `CONTRIBUTING.md` | doc | — | Yes — `DISCLAIMER.md` edited |
| `.github/workflows/{ci,pages,codeql,gitleaks,dependency-review}.yml` | config | — | Yes — `ci.yml` edited |
| `package.json`, `eslint.config.mjs`, `.gitignore`, `.pre-commit-config.yaml` | config | — | Yes (light pass) |
| `reviews/CONTENT_DECISIONS.yml` | registry | `scripts/verify_content_decisions.py` | Yes — edited |
| `reviews/REVIEW_TEMPLATE.md`, `reviews/CONTENT_DECISION_GUIDE.md` | tooling | — | Yes — not edited (bootstrapped verbatim from the skill's assets) |
| `scripts/capture_review_state.py`, `scripts/verify_content_decisions.py` | tooling | — | Yes |

Out-of-scope boundaries and reason: `LICENSE` (verbatim Apache-2.0 text) and `package-lock.json` (generated) were confirmed present but not read line by line. CI runtime pinning was reviewed as a repo-standards adjacency rather than as documentation content, and is reported as such.

## Review passes

| Pass | Complete | Evidence or notes |
| --- | --- | --- |
| 1. Factual and technical correctness | Yes | Every material claim traced to source or to executed code; see ledger. |
| 2. Evidence, authority, version, date, applicability | Yes | SP 800-38A/38D text extracted from the NIST PDFs directly; SP 800-63B revision and date confirmed; Node release schedule checked against the review date. |
| 3. Adversarial wording, assumptions, threat state | Yes | Produced findings on "necessary" (GCM nonce), "never sees the same input twice" (CBC caption), and the NIST attribution in §The mechanism. |
| 4. Terminology, taxonomy, conceptual boundaries | Yes | Produced the root-cause overlap finding — "no chaining" was doing work inside both causes. |
| 5. Cross-format consistency | Yes | Found the five-location "one vs one or both" split and the two divergent alt texts for one SVG. |
| 6. Visual content (independent correctness) | Yes | Run separately from pass 5; see **Visual content pass** below. |
| 7. Cross-page consistency, prerequisites, duplication | Yes | README lede/alt text reconciled with `docs/index.html`; DISCLAIMER scope statement checked against actual site content. |
| 8. Topic completeness matrix | Yes | See below. |
| 9. Mechanical, executable, link, generator, rendered validation | Yes | See **Mechanical and rendered checks**. |
| 10. Decision-history reconciliation | Yes | All four pre-existing decisions dispositioned; see below. |
| 11. Residual exhaustion | Yes | Re-read every unit touched by a finding; this produced the CBC "never" caption overclaim and the Citizen Lab URL redirect, neither of which was in the first assembled finding set. |

## Material-claim ledger

Where a claim's source and verification are recorded durably in `CONTENT_DECISIONS.yml`, this table references the decision ID rather than restating them; the decision record is the authoritative copy.

| # | Claim | Location | Verification | Disposition |
| --- | --- | --- | --- | --- |
| 1 | ECB determinism property and "should not be used" | `index.html` §The mechanism | See CD-0005 (§6.1 quoted verbatim from the NIST PDF) | Corrected — the detection *consequence* was attributed to NIST; now separated |
| 2 | IND-CPA advantage 1, independent of key size | `index.html` §Why determinism… | Argument checked; holds under the standard `2·Pr[win]−1` convention | Correct as written |
| 3 | The IND-CPA break needs ≥2 blocks | `index.html` §Why determinism… | Follows from claim 2; see CD-0005 (SP 800-38F as the approved key-wrapping path) | Restored — had been deleted by the pivot |
| 4 | Two root causes, four vectors, no third | `index.html`, `taxonomy.svg`, `README.md` | See CD-0006 (forged token decrypted block by block to establish that position-independence carries the splice) | Refined — root cause 2 narrowed to authentication; Vector 4 depends on both |
| 5 | ~153M Adobe records, 3DES inferred from 8-byte blocks, unsalted, hints used | `index.html` evidence table | filippo.io: "152,982,479 entries"; "allegedly 3DES, in ECB mode"; "It is not salted" | Correct as written |
| 6 | Password storage requires salted hashing, not encryption | `index.html` Vector 2 | See CD-0008 (SP 800-63B-4 Rev 4, 2025-08-26, §3.1.1.2) | Added — the gap was real |
| 7 | CCS 2015 frequency-analysis recovery on DTE columns, HCUP NIS data | `index.html` Vector 2 | See CD-0005 (scope difference from ECB stated on the page) | Re-anchored — was an orphaned reference |
| 8 | Byte-at-a-time cost | `index.html` Vector 3, alt text, `vector3-*.svg` | See CD-0009 (5 instrumented runs: mean **4,588** vs the stated 256×L = 12,288) | Corrected — bound restated as at-most/average, `L` defined |
| 9 | Zoom: one AES-128 key in ECB per meeting; AES-256 marketed | `index.html` evidence table | CVE-2020-11500 text; Citizen Lab: "a single AES-128 key is used in ECB mode by all participants" | Correct as written |
| 10 | O365 OME used ECB; Microsoft declined to fix | `index.html` evidence table | WithSecure: "was not considered meeting the bar for security servicing"; no code change, no CVE | Claim correct; **citation was dead** — replaced with the archived copy |
| 11 | Egele et al. 11,748 / 7,656 / 5,656 | `index.html` evidence table | See CD-0010 (figures confirmed; the default came from the **BouncyCastle** provider on Android) | Correct as written |
| 12 | `Cipher.getInstance("AES")` resolves to ECB | `index.html` §Detecting ECB | See CD-0010 (Oracle JCA guide: the *provider* supplies the default; the JCA defines none) | Corrected |
| 13 | GCM nonce requirement | `index.html` §Residual risk | See CD-0007 (SP 800-38D §8 uniqueness bound, §8.2.1/§8.2.2 constructions, §8.3 2³² cap) | Corrected |
| 14 | Böck et al.: 184 servers, authenticity broken | `index.html` §Residual risk | See CD-0007 (abstract quoted verbatim from the extracted PDF) | Correct as written |
| 15 | Demos run real AES locally, no network | `index.html` hero, scope callout, footer | Browser resource timing shows **zero** non-same-origin requests | Correct as written |
| 16 | ECB preserves image structure | Vector 1 demo | Two pixels inside the uniform circle are byte-identical under ECB, differ under CBC/GCM; 456 distinct colors vs ~9,213 | Correct as written |
| 17 | Test suite verifies against NIST vectors | footer, `README.md`, `crypto.mjs` | `node --test` 10/10; F.1.1 (encrypt) and F.1.2 (decrypt), four blocks each, so "vectors" plural | Correct; `crypto.mjs` comment pluralized, F.1.2 coverage added |

## Topic completeness matrix

Single primary topic: *why AES-ECB is unsafe, and what to use instead.*

| # | Category | Before | After |
| --- | --- | --- | --- |
| 1 | Definition and purpose | Covered | Covered |
| 2 | Scope and conceptual boundaries | **Required gap** — no single-block boundary | Covered (CD-0005) |
| 3 | Actors, components, assets | Covered | Covered |
| 4 | Mechanism, data flow, sequence | Covered | Covered |
| 5 | Assumptions, prerequisites, dependencies | Covered | Covered |
| 6 | Threats, failure modes, attacker state | Covered | Covered |
| 7 | Limitations and residual risk | **Required gap** — GCM 2³² limit absent | Covered (CD-0007) |
| 8 | Selection criteria and appropriate use | **Required gap** — no password-storage control | Covered (CD-0008) |
| 9 | Operations, observability, testing, evidence | Covered | Covered |
| 10 | Recovery, lifecycle, revocation | Covered — migration and key-rotation paragraph | Covered |
| 11 | Interoperability and migration | Covered | Covered |
| 12 | Deprecated, unsafe, incompatible alternatives | Covered | Covered |
| 13 | Visual representation | Covered — four figures, none decorative | Covered |

## Visual content pass

Run separately from the cross-format pass. Each figure was assessed for independent correctness, self-sufficiency when detached, generator provenance, and standalone dual-use defensibility.

| Figure | Finding | Resolution |
| --- | --- | --- |
| `modes-ecb-cbc-gcm.svg` | CBC caption asserted the cipher "never sees the same input twice" — an absolute that fails at the birthday bound | Reworded to "identical blocks enter AES differently" |
| `taxonomy.svg` | Subtitle said "one or both root causes" while the arrows drew exactly one per vector; no scope line | Root causes redefined, dashed determinism→Vector 4 arrow added, scope line added |
| `vector3-byte-at-a-time.svg` | Headline number used an undefined `L`; stated a worst case as typical; amber/purple cell coding had no legend | `L` bound inline, bound restated as at-most/average, three-swatch legend added |
| `vector4-cut-and-paste.svg` | Donor row drew 3 blocks; the real donor token is 4 | Redrawn on a 4-column grid; splice rerouted through the free channel so it no longer crosses the block it replaces |

- **Provenance:** `python3 docs/diagrams/generate_diagrams.py` re-run before and after; output is byte-identical across consecutive runs, and matched the committed SVGs exactly at review start. Correspondence established by regeneration, not assumed.
- **Detached-artifact test:** every figure carries its own title, comparison axis, and — for the three attack figures — an inline scope line naming the local in-page oracle.
- **Dual-use defensibility:** `vector3` and `vector4` name `attacks.mjs makeSuffixOracle` / `ProfileService` as local stand-ins; `taxonomy.svg` gained an equivalent line since it names four attack vectors.
- **Text-in-image:** the `256 × L` claim existed in prose, alt text, and inside an SVG. Located by opening every figure, not by grep — grep cannot see inside the rendered artifact.

## Cross-format and cross-page ledger

| Claim | Locations reconciled |
| --- | --- |
| Root causes / vector attribution | `index.html` lede, §Two root causes, figure alt text, closing callout; `taxonomy.svg` title, subtitle, box labels, arrows; `README.md` lede and alt text |
| Byte-at-a-time cost | `index.html` Vector 3 prose, figure alt text, `vector3-*.svg` summary box |
| Taxonomy figure alt text | `index.html` (conclusion-bearing) vs `README.md` (named the picture only) — README brought to parity |
| GCM nonce guidance | §The fix, §Residual risk, closing callout |
| No-network claim | hero, scope callout, footer — verified by resource timing |

## Mechanical and rendered checks

| Check | Result | What it does and does not prove |
| --- | --- | --- |
| `npm test` | 10/10 pass | Proves the modules behave as the page claims, in both directions: NIST SP 800-38A F.1.1 (encrypt) and F.1.2 (decrypt). Does not prove the demos are pedagogically clear, only that they compute what the page says. |
| `npm run lint` | Clean | Style/static only. |
| `python3 docs/diagrams/generate_diagrams.py` ×2 | Byte-identical | Proves generator↔artifact correspondence and determinism. Does not prove the figures are semantically correct — that was the visual pass. |
| `python3 scripts/verify_content_decisions.py` | 10 decisions validated | Structure and references only, explicitly not technical correctness. |
| Link check (16 URLs) | 14×200, 2×403 | The two 403s are ACM DOIs bot-blocking; both resolve for humans. **Redirect targets were compared, not just status codes** — that is what exposed the WithSecure hub redirect that a plain `curl -L` reports as 200. |
| Rendered validation | All 4 SVGs + full page, dark **and** light | Confirms theme-aware CSS, no clipping, no overlap, and that the rerouted splice arrow clears the base row. |
| Live demo drive-through | All 5 demos | Vector 3 reported **4,588 queries** on-screen, matching the corrected prose. |
| Resource timing | Zero external requests | Substantiates the "no network, no server" claim. |

## Open required findings

None. All ten required findings were remediated and re-verified against the post-remediation state.

## Optional coverage

All ten optional items were also remediated: root-cause overlap, donor block count, missing figure legend, stale `CD-0001` outcome paths, template comment in `DISCLAIMER.md`, unused `.scope` CSS, the equality demo's misleading ellipsis, `taxonomy.svg` scope line, singular/plural "test vector", and the absent post-pivot review record (this file).

Two items surfaced during the residual-exhaustion and remediation passes and were fixed although they were not in the originally reported set: the CBC caption's absolute "never" claim, and the Citizen Lab citation's redirect to a renamed canonical URL.

## Known review limitations

- Rendered checks used the in-app Chromium at desktop width in both light and dark schemes. **Not verified:** Safari, Firefox, mobile viewport widths, and GitHub's own Markdown renderer for the README's embedded SVG. Bounded deliberately — see **CD-0011**; do not re-report as a coverage gap without meeting an invalidation condition there.
- The ACM DOIs return 403 to automated fetches. The Egele and Naveed figures were verified against secondary reporting of those papers, not the paywalled PDFs themselves. Accepted deliberately — see **CD-0012**.
- The `2³²` GCM invocation ceiling is stated as SP 800-38D states it. Whether any given deployment approaches it was not modelled — a deliberate scope boundary, see **CD-0013**.
- CI now pins Node 24 (Active LTS at this date). This was verified against the Node release schedule, not by observing a CI run — no push was made.

## Applicable durable decisions

| ID | Disposition | Basis |
| --- | --- | --- |
| CD-0001 | **Superseded by CD-0006** | Taxonomy retained; the boundary between the two root causes was refined and the approved outcome still named deleted pre-pivot paths. No invalidation condition was met — no third root cause was found — so this is a refinement recorded as a supersession, not a reversal. |
| CD-0002 | **Superseded by CD-0005** | Both approved outcomes were absent from the post-pivot source while the record still read `implemented`. Reopened under the "page scope changed" condition; content restored and re-anchored. |
| CD-0003 | Superseded (unchanged) | Already superseded by CD-0004; preserved as history. Its README alt-text requirement had regressed and was reinstated under CD-0006. |
| CD-0004 | **Reaffirmed** | Four committed theme-aware SVGs, generator committed, regeneration byte-identical, scope lines present. Outcome holds and was extended, not reversed. |
| CD-0011 – CD-0013 | New (rejected) | Three limitations this review accepted rather than fixed, now recorded so a later review can tell them from new defects: bounded rendered verification (CD-0011), secondary verification of the two paywalled ACM papers (CD-0012), and the GCM capacity-modelling scope boundary (CD-0013). |
| CD-0005 – CD-0010 | New | Six decisions recorded for the material changes above: single-block scope note and CCS 2015 re-anchor (CD-0005), root-cause boundary (CD-0006), GCM IV uniqueness and the 2³² ceiling (CD-0007), password-storage control (CD-0008), attack-cost bounds (CD-0009), provider-default attribution (CD-0010). See the registry for each record's sources, verification and invalidation conditions. |

## Closure attestation

Every in-scope file and asset was inventoried and inspected. The review baseline was clean and unchanged throughout the read-only review; remediation was performed as a separate authorized phase and every affected pass was re-run against the resulting state. A material-claim ledger and per-topic completeness matrix were completed. All mandatory review dimensions were applied. Standards-sensitive claims were checked against primary sources — SP 800-38A, SP 800-38D and SP 800-63B text was extracted from the publications themselves rather than taken from summaries. Adversarial-claim, cross-format, cross-page, visual-content, and knowledge-gap passes were run separately. Applicable durable decisions were reconciled, with each reversal justified against a recorded invalidation condition. Every visual was reviewed for independent correctness, detached self-sufficiency, generator provenance, and standalone defensibility. A residual-exhaustion pass was run after findings were assembled and produced two further items.

This record is evidence of coverage for scoped fingerprint `db82644af5f4118efb00c42d9d8eca34bee167a7d9b4b563a5db271c0195665a` on branch `fix/post-pivot-doc-review`, with the working tree modified relative to commit `64b9ad6`. It is not proof that later content remains correct. The limitations above are open and undischarged.

---

## Appendix — Prior review provenance (2026-08-21)

The doc-review skill keeps exactly one record, at the fixed path `reviews/LATEST_REVIEW.md`, overwritten by
each review. The 2026-08-21 record predates that rule and was consolidated into this appendix; the full
147-line original remains in git history and is retrieved with:

```
git show c0dc291:reviews/2026-08-21-fresh-review-whole-project.md
```

That review is the provenance for CD-0001, CD-0002 and CD-0003, all three now superseded but preserved in
`CONTENT_DECISIONS.yml`. The facts below are what this project still depends on; everything else in the
original concerned files the pivot deleted.

| Field | Value |
| --- | --- |
| Review date | 2026-08-21 |
| Commit | `83e09c03dae53d84f10b3da22da2ddcf0ba47dac` (branch `main`) |
| Scoped content fingerprint (post-fix) | `e4326e04f701c8012345844f142d9a268d0062e294783b25bb73d4888447085b` |
| Review state ID (post-fix) | `43557124a10f7393887d603492e0361538e8e8931b06c89afbbe6f0699265c54` |
| Mode | Fresh review, whole project, followed by an authorized fix phase |
| Worktree at start | Dirty — `AGENTS.md` deleted, `README.md` and `docs/ecb-mode-unsafe.md` modified, all pre-existing |
| Baseline changed during review | Yes — documented in the original; affected checks were re-run against the new state |

**Scope reviewed (pre-pivot layout):** `README.md`, `docs/ecb-mode-unsafe.md`, six `src/ecb_lab/` modules,
five `tests/*.py`, `notebooks/ecb_mode_deep_dive.ipynb` (re-executed end to end),
`notebooks/ecb_pattern_leakage.png`, the `reviews/` and `scripts/` tooling, and config files. `AGENTS.md`
was confirmed absent with zero dangling references repo-wide.

**Required findings — both fixed in that session:**

1. Missing durable decision records for the SP 800-38A scope-note and CCS 2015 corrections → CD-0002 added
   and cross-linked to CD-0001.
2. `scripts/capture_review_state.py` crashed on a tracked-but-working-tree-deleted file → `capture()` and
   `resolve_scope()` now record such files with `"status": "deleted"`. **This fix is still local to this
   repository and has not been pushed back to the doc-review skill's asset copy.**

**Optional fixes made:** Vector 4's header gained its missing attacker-state qualifier `(no integrity,
active splice)`; the nonce-reuse claim gained its Böck et al. (USENIX WOOT 2016) citation.

**Mechanical checks:** `pytest` 22/22; isolated notebook re-execution reproduced every claimed output;
registry validator passed at 1 then 2 decisions; `ecb_pattern_leakage.png` verified 1667×466 RGBA and
byte-identical to baseline after a transient overwrite was caught and reverted.

**Limitations disclosed then, never discharged:** Schneier's Adobe post returned HTTP 403 and was not
independently re-fetched (filippo.io substantiates every Adobe sub-claim); Cryptopals Challenge 14 was
confirmed by title match only; `requirements.txt` floors were not swept for CVEs or deprecations. The first
two no longer apply to the current site — Schneier is still cited, and the Cryptopals reference is now a
bare Sets 1 & 2 link. The third is moot: `requirements.txt` no longer exists.
