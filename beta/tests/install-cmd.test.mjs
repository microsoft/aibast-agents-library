import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  existsSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const betaRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const installer = readFileSync(path.join(betaRoot, "install.cmd"), "utf8");
const pinnedReset = installer.indexOf(
  '"%GIT_EXE%" -C "%BETA_SOURCE%" reset --hard "%REPO_COMMIT%"',
);
const verificationStart = installer.lastIndexOf(
  "if defined REPO_COMMIT (",
  pinnedReset,
);
const verificationEnd = installer.indexOf(
  'if not exist "%BETA_SOURCE%\\beta\\package.json" (',
  verificationStart,
);
const verificationBlock =
  verificationStart >= 0 && verificationEnd > verificationStart
    ? installer.slice(verificationStart, verificationEnd).trimEnd()
    : "";

test("Windows installer pins the checkout directly to the release commit", () => {
  assert.ok(verificationBlock, "commit verification block not found");
});

function runVerification(t, expectedCommit = "") {
  const directory = mkdtempSync(
    path.join(tmpdir(), "brainstem-install-cmd-"),
  );
  t.after(() => rmSync(directory, { recursive: true, force: true }));

  const sourceDirectory = path.join(
    directory,
    "Checkout Source (Pinned) & Data",
  );
  const programFilesGit = path.join(
    process.env.ProgramFiles ?? "C:\\Program Files",
    "Git",
    "cmd",
    "git.exe",
  );
  const gitExe = existsSync(programFilesGit) ? programFilesGit : "git.exe";
  const runGit = (...args) =>
    spawnSync(gitExe, args, { encoding: "utf8", windowsHide: true });

  assert.equal(runGit("init", sourceDirectory).status, 0);
  assert.equal(
    runGit(
      "-C",
      sourceDirectory,
      "-c",
      "user.name=Frontier Installer Test",
      "-c",
      "user.email=frontier-installer@example.invalid",
      "commit",
      "--allow-empty",
      "-m",
      "fixture",
    ).status,
    0,
  );
  const availableCommit = runGit(
    "-C",
    sourceDirectory,
    "rev-parse",
    "HEAD",
  ).stdout.trim();
  const requestedCommit = expectedCommit || availableCommit;

  const harness = path.join(directory, "verify.cmd");
  writeFileSync(
    harness,
    [
      "@echo off",
      "setlocal EnableExtensions EnableDelayedExpansion",
      `set "GIT_EXE=${gitExe}"`,
      `set "BETA_SOURCE=${sourceDirectory}"`,
      `set "REPO_COMMIT=${requestedCommit}"`,
      verificationBlock,
      "echo PINNED=%REPO_COMMIT%",
      "exit /b 0",
      ":fail",
      "exit /b 1",
      "",
    ].join("\r\n"),
  );

  return spawnSync(
    process.env.ComSpec ?? "cmd.exe",
    ["/d", "/c", harness],
    { encoding: "utf8", windowsHide: true },
  );
}

test(
  "commit pinning supports quoted paths with metacharacters",
  { skip: process.platform !== "win32" },
  (t) => {
    const result = runVerification(t);

    assert.equal(
      result.status,
      0,
      [result.stdout, result.stderr].filter(Boolean).join("\n"),
    );
    assert.match(result.stdout, /PINNED=[0-9a-f]{40}/);
  },
);

test(
  "commit pinning rejects an unavailable commit",
  { skip: process.platform !== "win32" },
  (t) => {
    const result = runVerification(
      t,
      "0123456789abcdef0123456789abcdef01234567",
    );

    assert.equal(result.status, 1);
    assert.match(result.stdout, /Beta checkout could not be pinned to 01234567/);
  },
);
