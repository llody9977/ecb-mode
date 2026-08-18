# Repository instructions

These instructions apply to the entire repository. See [`README.md`](README.md) for the project's purpose and scope.

Before writing or editing content in this repository, load and follow the **doc-writing** skill (`~/.claude/skills/doc-writing/SKILL.md`) completely.

Before reviewing content in this repository, load and follow both the **doc-writing** and **doc-review** skills (`~/.claude/skills/doc-review/SKILL.md`) completely. The current source files are authoritative; do not assume that earlier pages, review comments, or statements that an issue was fixed are accurate.

Reviewing is read-only unless the user explicitly requests changes. Do not edit, rewrite, regenerate, commit, or push files during a review-only request.

Interpret **verify** as targeted verification of the named findings. Interpret **fresh review**, **clean review**, **full review**, **complete review**, **final pass**, or **determine gaps** as a complete current-source review using every mandatory dimension and closure requirement in the doc-review skill.

Do not claim that all issues are fixed or that a review is complete unless the doc-review skill's closure requirements have been satisfied and the reviewed commit or worktree state is identified.

This repository's review scaffolding (`reviews/`, `scripts/`) was bootstrapped from the doc-review skill's `assets/` — see that skill for how to refresh it if the shared standard changes. For the durable content-decision workflow (`reviews/CONTENT_DECISIONS.yml`), follow `reviews/CONTENT_DECISION_GUIDE.md`.
