import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";

const root = new URL("../", import.meta.url);
const read = (path) => readFileSync(fileURLToPath(new URL(path, root)), "utf8");
const workflowNames = readdirSync(fileURLToPath(new URL(".github/workflows/", root)))
  .filter((name) => name.endsWith(".yml"));
const workflows = workflowNames.map((name) => [name, read(`.github/workflows/${name}`)]);

test("third-party actions are commit-pinned and checkout never persists credentials", () => {
  for (const [name, workflow] of workflows) {
    for (const use of workflow.matchAll(/uses:\s*([^\s#]+)/g)) {
      assert.match(use[1], /@[0-9a-f]{40}$/, `${name}: ${use[1]} must be pinned to a full commit`);
    }
    const checkoutCount = [...workflow.matchAll(/uses:\s*actions\/checkout@[0-9a-f]{40}/g)].length;
    const nonPersistentCount = [...workflow.matchAll(/persist-credentials:\s*false/g)].length;
    assert.equal(nonPersistentCount, checkoutCount, `${name}: every checkout must disable credential persistence`);
  }
});

test("workflows cancel superseded runs and CI covers figures and a real browser", () => {
  for (const [name, workflow] of workflows) {
    assert.match(workflow, /concurrency:/, `${name} needs an explicit concurrency policy`);
  }
  const ci = read(".github/workflows/ci.yml");
  assert.match(ci, /name:\s*figures/);
  assert.match(ci, /git diff --exit-code -- docs\/diagrams/);
  assert.match(ci, /name:\s*browser/);
  assert.match(ci, /npm run test:browser/);
});

test("downloaded scanner is checksum-verified and Pages write access is job-scoped", () => {
  const gitleaks = read(".github/workflows/gitleaks.yml");
  assert.match(gitleaks, /551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb/);
  assert.match(gitleaks, /sha256sum --check --strict/);
  assert.doesNotMatch(gitleaks, /curl[^\n]*\|\s*tar/);

  const pages = read(".github/workflows/pages.yml");
  const beforeJobs = pages.slice(0, pages.indexOf("jobs:"));
  assert.doesNotMatch(beforeJobs, /pages:\s*write|id-token:\s*write/);
  assert.match(pages, /deploy:[\s\S]*permissions:[\s\S]*pages:\s*write[\s\S]*id-token:\s*write/);
});

test("Dependabot holds new releases for a review window", () => {
  const dependabot = read(".github/dependabot.yml");
  assert.equal([...dependabot.matchAll(/default-days:\s*7/g)].length, 2);
});
