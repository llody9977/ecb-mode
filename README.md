# ECB mode: documentation project

## Purpose

This project documents the cryptographic weaknesses of ECB (Electronic Codebook) mode — the simplest block cipher mode of operation, and the one most often misused. The goal is a precise technical reference that explains:

- what ECB mode actually does mechanically (independent, unchained block encryption under a fixed key);
- why that construction fails to provide semantic security — identical plaintext blocks always produce identical ciphertext blocks under the same key, which leaks the structural pattern of the plaintext regardless of key strength;
- how that weakness is exploited in practice (pattern leakage, block reordering, block replay, cut-and-paste manipulation);
- what mitigates or replaces it (authenticated modes such as AES-GCM, or CBC/CTR with a random IV and a separate MAC), and the residual risk that remains after switching.

Content is organized as a security-flaw deep dive on a single primary subject, not a general cryptography survey — ECB mode's boundary with other block cipher modes (CBC, CTR, GCM) is covered only to the extent needed to explain what ECB gets wrong and what a correct alternative looks like.

**Assumption (unconfirmed):** this README is written for a general technical reader (an engineer or reviewer evaluating block-cipher-mode choices), not exclusively for the author's own future recall. The direct technical voice required by this project's writing standard works either way, but if the intended audience or publication venue is different, say so and the framing can be adjusted.

## Standards

This project follows two standing skills, shared across all of the author's documentation projects (not local to this repository):

- **doc-writing** (`~/.claude/skills/doc-writing/SKILL.md`) — voice, structure, the five approved writing frameworks, and accuracy/citation discipline. ECB mode's content fits the **Threat → Attack Mechanics → Defensive Control → Residual Risk** framework.
- **doc-review** (`~/.claude/skills/doc-review/SKILL.md`) — targeted verification vs. fresh review, mandatory review dimensions, gap analysis, and closure requirements.

See [`AGENTS.md`](AGENTS.md) for the enforcement pointer.

## Structure

- `docs/` — content pages (created as content is written).
- `reviews/` — review records, the durable content-decision register (`CONTENT_DECISIONS.yml`), and the review template. Bootstrapped from the `doc-review` skill's assets.
- `scripts/` — review tooling (`capture_review_state.py`, `verify_content_decisions.py`), copied from the `doc-review` skill's assets. Both are generic and depend only on `git` and this repository's `reviews/CONTENT_DECISIONS.yml`.
