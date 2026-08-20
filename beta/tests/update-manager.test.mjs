import assert from "node:assert/strict";
import {
  mkdirSync,
  mkdtempSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import {
  checkForUpdates,
  compareBetaVersions,
  githubRawUrl,
  inferManagedBetaHome,
  parseGitHubRepository,
  readUpdateConfiguration,
  resolveManagedInstall,
  validateUpdateRef,
} from "../electron/update-manager.mjs";

const CURRENT_COMMIT = "1".repeat(40);
const LATEST_COMMIT = "2".repeat(40);

test("GitHub repository URLs support HTTPS and SSH remotes", () => {
  assert.deepEqual(
    parseGitHubRepository(
      "https://github.com/microsoft/aibast-agents-library.git",
    ),
    {
      owner: "microsoft",
      repo: "aibast-agents-library",
      slug: "microsoft/aibast-agents-library",
    },
  );
  assert.equal(
    parseGitHubRepository("git@github.com:microsoft/aibast-agents-library.git")
      .slug,
    "microsoft/aibast-agents-library",
  );
  assert.equal(parseGitHubRepository("https://example.com/owner/repo.git"), null);
  assert.equal(
    githubRawUrl(
      "https://github.com/microsoft/aibast-agents-library.git",
      LATEST_COMMIT,
      "install.ps1",
    ),
    `https://raw.githubusercontent.com/microsoft/aibast-agents-library/${LATEST_COMMIT}/install.ps1`,
  );
});

test("update branch validation rejects unsafe refs", () => {
  assert.equal(validateUpdateRef("main"), "main");
  assert.equal(validateUpdateRef("preview/beta"), "preview/beta");
  for (const ref of ["", "-main", "../main", "main..next", "main lock"]) {
    assert.throws(() => validateUpdateRef(ref));
  }
});

test("update checks fetch the configured GitHub branch", async () => {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-beta-update-"));
  const packageDir = path.join(root, "beta");
  mkdirSync(packageDir);
  writeFileSync(path.join(packageDir, "VERSION"), "0.1.0-beta.1\n");
  const calls = [];
  const runGit = async (cwd, args) => {
    calls.push({ cwd, args });
    const command = args.join(" ");
    if (command === "rev-parse --show-toplevel") return `${root}\n`;
    if (command === "remote get-url origin") {
      return "https://github.com/microsoft/aibast-agents-library.git\n";
    }
    if (command === "rev-parse HEAD") return `${CURRENT_COMMIT}\n`;
    if (command === "status --porcelain --untracked-files=no") return "";
    if (command.startsWith("fetch ")) return "";
    if (command === "rev-parse FETCH_HEAD") return `${LATEST_COMMIT}\n`;
    if (command === `show ${LATEST_COMMIT}:beta/VERSION`) {
      return "0.1.0-beta.2\n";
    }
    throw new Error(`Unexpected git call: ${command}`);
  };

  try {
    const update = await checkForUpdates({
      packageDir,
      env: { BRAINSTEM_BETA_UPDATE_REF: "preview/beta" },
      runGit,
    });
    assert.equal(update.available, true);
    assert.equal(update.currentVersion, "0.1.0-beta.1");
    assert.equal(update.latestVersion, "0.1.0-beta.2");
    assert.equal(update.published, true);
    assert.equal(update.repository, "microsoft/aibast-agents-library");
    assert.ok(calls.some(({ args }) => (
      args.join(" ")
      === "fetch --quiet --filter=blob:none --depth 1 origin refs/heads/preview/beta"
    )));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("a branch without a beta manifest is not an update failure", async () => {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-beta-update-"));
  const packageDir = path.join(root, "beta");
  mkdirSync(packageDir);
  writeFileSync(path.join(packageDir, "VERSION"), "0.1.0-beta.1\n");
  const runGit = async (_cwd, args) => {
    const command = args.join(" ");
    if (command === "rev-parse --show-toplevel") return `${root}\n`;
    if (command === "remote get-url origin") {
      return "https://github.com/microsoft/aibast-agents-library.git\n";
    }
    if (command === "rev-parse HEAD") return `${CURRENT_COMMIT}\n`;
    if (command === "status --porcelain --untracked-files=no") return "";
    if (command.startsWith("fetch ")) return "";
    if (command === "rev-parse FETCH_HEAD") return `${LATEST_COMMIT}\n`;
    if (command === `show ${LATEST_COMMIT}:beta/VERSION`) {
      throw new Error(
        "fatal: path 'beta/VERSION' exists on disk, but not in "
        + `'${LATEST_COMMIT}'`,
      );
    }
    throw new Error(`Unexpected git call: ${command}`);
  };

  try {
    const update = await checkForUpdates({ packageDir, runGit });
    assert.equal(update.available, false);
    assert.equal(update.published, false);
    assert.equal(update.latestVersion, null);
    assert.equal(update.latestCommit, LATEST_COMMIT);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

function channelGit({ latestVersion }) {
  return async (_cwd, args) => {
    const command = args.join(" ");
    if (command === "rev-parse --show-toplevel") return "__ROOT__";
    if (command === "remote get-url origin") {
      return "https://github.com/microsoft/aibast-agents-library.git\n";
    }
    if (command === "rev-parse HEAD") return `${CURRENT_COMMIT}\n`;
    if (command === "status --porcelain --untracked-files=no") return "";
    if (command.startsWith("fetch ")) return "";
    if (command === "rev-parse FETCH_HEAD") return `${LATEST_COMMIT}\n`;
    if (command === `show ${LATEST_COMMIT}:beta/VERSION`) {
      return `${latestVersion}\n`;
    }
    throw new Error(`Unexpected git call: ${command}`);
  };
}

async function channelCheck({ installedVersion, latestVersion }) {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-beta-update-"));
  const packageDir = path.join(root, "beta");
  mkdirSync(packageDir);
  writeFileSync(path.join(packageDir, "VERSION"), `${installedVersion}\n`);
  const base = channelGit({ latestVersion });
  const runGit = async (cwd, args) => {
    const result = await base(cwd, args);
    return result === "__ROOT__" ? `${root}\n` : result;
  };
  try {
    return await checkForUpdates({ packageDir, runGit });
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

test("a channel serving an older version is never offered as an update", async () => {
  const update = await channelCheck({
    installedVersion: "0.1.0-beta.6",
    latestVersion: "0.1.0-beta.4",
  });
  assert.equal(update.available, false);
  assert.equal(update.channelBehind, true);
  assert.equal(update.published, true);
  assert.equal(update.latestVersion, "0.1.0-beta.4");
});

test("a same-version channel refresh and a newer channel are both updates", async () => {
  const refresh = await channelCheck({
    installedVersion: "0.1.0-beta.6",
    latestVersion: "0.1.0-beta.6",
  });
  assert.equal(refresh.available, true);
  assert.equal(refresh.channelBehind, false);

  const newer = await channelCheck({
    installedVersion: "0.1.0-beta.6",
    latestVersion: "0.1.0-beta.7",
  });
  assert.equal(newer.available, true);
  assert.equal(newer.channelBehind, false);
});

test("beta version ordering is prerelease-aware", () => {
  assert.equal(compareBetaVersions("0.1.0-beta.6", "0.1.0-beta.4"), 1);
  assert.equal(compareBetaVersions("0.1.0-beta.4", "0.1.0-beta.6"), -1);
  assert.equal(compareBetaVersions("0.1.0-beta.10", "0.1.0-beta.9"), 1);
  assert.equal(compareBetaVersions("0.1.0", "0.1.0-beta.7"), 1);
  assert.equal(compareBetaVersions("0.1.0-beta.7", "0.1.0"), -1);
  assert.equal(compareBetaVersions("0.1.1-beta.1", "0.1.0"), 1);
  assert.equal(compareBetaVersions("0.1.0-beta.6", "0.1.0-beta.6"), 0);
  assert.equal(compareBetaVersions("0.1.0-alpha.2", "0.1.0-beta.1"), -1);
  assert.equal(compareBetaVersions("garbage", "0.1.0"), null);
});

test("hyphenated prereleases keep their full tail in ordering", () => {
  // split("-", 2) used to truncate everything after the second hyphen, so a
  // hotfix build compared EQUAL to its base and the downgrade guard misjudged.
  assert.equal(
    compareBetaVersions("0.1.0-beta.7-hotfix.1", "0.1.0-beta.7"),
    1,
  );
  assert.equal(
    compareBetaVersions("0.1.0-beta.7", "0.1.0-beta.7-hotfix.1"),
    -1,
  );
  assert.equal(
    compareBetaVersions("0.1.0-beta.7-rc.2", "0.1.0-beta.7-rc.1"),
    1,
  );
  assert.equal(
    compareBetaVersions("0.1.0-beta.7-rc.1", "0.1.0-beta.7-rc.2"),
    -1,
  );
  assert.equal(
    compareBetaVersions("0.1.0-beta.7-hotfix.1", "0.1.0-beta.7-hotfix.1"),
    0,
  );
  assert.equal(compareBetaVersions("0.1.0-beta.8", "0.1.0-beta.7-hotfix.1"), 1);
  // Trailing junk in a core part is unparseable, not silently equal.
  assert.equal(compareBetaVersions("0.1.0junk", "0.1.0"), null);
  assert.equal(compareBetaVersions("0.1.0-", "0.1.0"), null);
});

test("a channel behind an installed hotfix build is never offered as an update", async () => {
  const update = await channelCheck({
    installedVersion: "0.1.0-beta.8-hotfix.1",
    latestVersion: "0.1.0-beta.8",
  });
  assert.equal(update.available, false);
  assert.equal(update.channelBehind, true);
  assert.equal(update.published, true);
});

test("managed installs resolve the portable Node and Electron runtimes", () => {
  const betaHome = mkdtempSync(path.join(tmpdir(), "rapp-beta-managed-"));
  const repoRoot = path.join(betaHome, "src");
  const packageDir = path.join(repoRoot, "beta");
  const node = path.join(
    betaHome,
    "node-v24.19.0-darwin-arm64",
    "bin",
    "node",
  );
  const electron = path.join(
    packageDir,
    "node_modules",
    "electron",
    "dist",
    "Electron.app",
    "Contents",
    "MacOS",
    "Electron",
  );
  mkdirSync(path.dirname(node), { recursive: true });
  mkdirSync(path.dirname(electron), { recursive: true });
  writeFileSync(node, "");
  writeFileSync(electron, "");
  writeFileSync(
    path.join(betaHome, "update-config.json"),
    `${JSON.stringify({
      repositoryUrl: "https://github.com/microsoft/aibast-agents-library.git",
      updateRef: "preview/beta",
    })}\n`,
  );

  try {
    assert.equal(inferManagedBetaHome(packageDir, {}), betaHome);
    assert.equal(
      readUpdateConfiguration(packageDir, {}).updateRef,
      "preview/beta",
    );
    assert.deepEqual(
      resolveManagedInstall({
        packageDir,
        repoRoot,
        env: {},
        platform: "darwin",
        arch: "arm64",
      }),
      { betaHome, electron, node },
    );
  } finally {
    rmSync(betaHome, { recursive: true, force: true });
  }
});
