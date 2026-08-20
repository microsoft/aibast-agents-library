import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";


const betaRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = path.resolve(betaRoot, "..");
const proofScript = path.join(betaRoot, "scripts", "organism-gitmolt-proof.sh");
const corpusAgent = path.join(
  "cat-agent-skills",
  "rapp-agent-converter",
  "assets",
  "hello_rapp_agent.py",
);

function probe(command, args, options = {}) {
  return spawnSync(command, args, {
    cwd: repositoryRoot,
    encoding: "utf8",
    windowsHide: true,
    timeout: 15_000,
    ...options,
  });
}

test("git-molt keeps two live Brainstem organisms healthy", {
  timeout: 190_000,
}, (t) => {
  if (process.platform === "win32") {
    t.skip("the proof targets Bash 3.2-compatible macOS and Linux hosts");
    return;
  }

  const python = process.env.BRAINSTEM_PYTHON
    || path.join(homedir(), ".brainstem", "venv", "bin", "python");
  if (!existsSync(python)) {
    t.skip(`Brainstem venv Python is unavailable: ${python}`);
    return;
  }
  const pythonProbe = probe(python, ["-c", "import flask"]);
  if (pythonProbe.status !== 0) {
    t.skip(`Brainstem venv Python cannot import Flask: ${python}`);
    return;
  }

  const gitProbe = probe("git", ["--version"]);
  if (gitProbe.status !== 0) {
    t.skip("git is unavailable");
    return;
  }

  const corpus = process.env.RAPP_SKILLS_DIR;
  if (corpus) {
    assert.ok(
      existsSync(path.join(corpus, corpusAgent)),
      `RAPP_SKILLS_DIR has no ${corpusAgent}`,
    );
  } else {
    const networkProbe = probe("git", [
      "ls-remote",
      "--exit-code",
      "https://github.com/kody-w/rapp-skills",
      "HEAD",
    ]);
    if (networkProbe.status !== 0) {
      t.skip("network access to github.com/kody-w/rapp-skills is unavailable");
      return;
    }
  }

  const result = spawnSync("bash", [proofScript], {
    cwd: repositoryRoot,
    encoding: "utf8",
    env: {
      ...process.env,
      BRAINSTEM_PYTHON: python,
    },
    maxBuffer: 8 * 1024 * 1024,
    timeout: 180_000,
    windowsHide: true,
  });
  assert.equal(
    result.status,
    0,
    [
      `proof exit: ${result.status}`,
      result.error?.message || "",
      result.stdout || "",
      result.stderr || "",
    ].filter(Boolean).join("\n"),
  );
  assert.match(result.stdout, /## PASS\/FAIL table/);
  assert.match(result.stdout, /valid collision exposes gate\/kernel disagreement \| PASS/);
  assert.match(result.stdout, /foreign verified trailer currently transfers authority \| PASS/);
  assert.match(result.stdout, /Summary: \d+ claim\(s\), 0 failure\(s\)/);
});
