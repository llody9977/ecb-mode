# ECB mode: documentation project

## Purpose

This project answers one question with runnable proof, not theory: **why is AES-ECB mode unsafe, and how would you know if a system is using it?** The primary reference is [`docs/ecb-mode-unsafe.md`](docs/ecb-mode-unsafe.md), covering:

- what ECB mode does mechanically, and the formal proof that it breaks semantic security (IND-CPA), independent of key strength;
- a comprehensive attack surface reduced to its two actual root causes — determinism, and no integrity/chaining — and the four vectors that follow from them (pattern leakage, equality/frequency inference, chosen-plaintext byte-at-a-time recovery, block malleability/cut-and-paste);
- real-world evidence for each vector, independently verified against primary sources (Adobe 2013, Zoom CVE-2020-11500, Microsoft Office 365 Message Encryption, the CCS 2013 Android crypto-misuse study, CCS 2015 hospital-record inference attacks);
- how to detect ECB usage, both black-box (ciphertext/oracle analysis) and white-box (the library-default footguns that cause most accidental ECB use in practice);
- the defensive control (authenticated encryption) and the residual risk that remains after adopting it.

Every attack and every detection technique is implemented in [`src/ecb_lab/`](src/ecb_lab/), covered by tests in [`tests/`](tests/), and run end-to-end with real captured output in [`notebooks/ecb_mode_deep_dive.ipynb`](notebooks/ecb_mode_deep_dive.ipynb) — nothing in the documentation is asserted without code behind it.

Content is organized as a security-flaw deep dive on a single primary subject, not a general cryptography survey — ECB mode's boundary with other block cipher modes (CBC, CTR, GCM) is covered only to the extent needed to explain what ECB gets wrong and what a correct alternative looks like.

## Standards

This project follows two standing skills, shared across all of the author's documentation projects (not local to this repository):

- **doc-writing** (`~/.claude/skills/doc-writing/SKILL.md`) — voice, structure, the five approved writing frameworks, and accuracy/citation discipline. ECB mode's content fits the **Threat → Attack Mechanics → Defensive Control → Residual Risk** framework.
- **doc-review** (`~/.claude/skills/doc-review/SKILL.md`) — targeted verification vs. fresh review, mandatory review dimensions, gap analysis, and closure requirements.

See [`AGENTS.md`](AGENTS.md) for the enforcement pointer.

## Structure

- `docs/ecb-mode-unsafe.md` — the primary written reference.
- `src/ecb_lab/` — the tested implementation: `crypto_helpers.py` (AES-ECB/CBC/GCM), `detection.py` (black-box and white-box ECB detection), `pattern_leakage.py`, `oracle_attack.py`, `cut_and_paste.py` — one module per attack vector.
- `tests/` — pytest coverage for every module above; run with `pytest` (block size, key, and cipher IO are exercised against real AES, not mocked).
- `notebooks/ecb_mode_deep_dive.ipynb` — runs every vector end-to-end with real, captured output; the companion notebook to `docs/ecb-mode-unsafe.md`.
- `reviews/` — review records, the durable content-decision register (`CONTENT_DECISIONS.yml`), and the review template. Bootstrapped from the `doc-review` skill's assets.
- `scripts/` — review tooling (`capture_review_state.py`, `verify_content_decisions.py`), copied from the `doc-review` skill's assets. Both are generic and depend only on `git` and this repository's `reviews/CONTENT_DECISIONS.yml`.

## Running it

```bash
pip install -r requirements.txt
pytest                                    # 19 tests, all four vectors + detection + crypto helpers
jupyter nbconvert --execute --to notebook --inplace notebooks/ecb_mode_deep_dive.ipynb
```
