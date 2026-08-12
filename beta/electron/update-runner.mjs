import { spawn, spawnSync } from "node:child_process";
import {
  closeSync,
  existsSync,
  openSync,
  readFileSync,
  renameSync,
  rmSync,
  writeFileSync,
  writeSync,
} from "node:fs";

const COMMIT_PATTERN = /^[0-9a-f]{40}$/i;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function processExists(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return error?.code === "EPERM";
  }
}

async function waitForParent(pid, timeoutMs = 120_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (!processExists(pid)) return;
    await sleep(250);
  }
  throw new Error("The beta application did not exit before the update timeout.");
}

function requireString(request, key) {
  const value = request[key];
  if (typeof value !== "string" || !value) {
    throw new Error(`Update request is missing ${key}.`);
  }
  return value;
}

function loadRequest(requestPath) {
  const request = JSON.parse(readFileSync(requestPath, "utf8"));
  for (const key of [
    "betaHome",
    "betaExpectedHead",
    "betaRepoRoot",
    "brainstemHome",
    "brainstemExpectedHead",
    "brainstemRepoRoot",
    "electronPath",
    "gitExecutable",
    "installerPath",
    "logPath",
    "packageDir",
    "remoteUrl",
    "requestPath",
    "resultPath",
    "runnerPath",
    "updateRef",
  ]) {
    requireString(request, key);
  }
  if (!Number.isInteger(request.parentPid) || request.parentPid < 1) {
    throw new Error("Update request has an invalid parent process.");
  }
  if (!COMMIT_PATTERN.test(request.commit || "")) {
    throw new Error("Update request has an invalid commit.");
  }
  return request;
}

function gitOutput(request, cwd, args) {
  const result = spawnSync(request.gitExecutable, ["-C", cwd, ...args], {
    encoding: "utf8",
    env: process.env,
    windowsHide: true,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    throw new Error(
      `Git verification failed in ${cwd}: ${(result.stderr || "").trim()}`,
    );
  }
  return (result.stdout || "").trim();
}

function assertCheckoutUnchanged(request, cwd, expectedHead, label) {
  const head = gitOutput(request, cwd, ["rev-parse", "HEAD"]).toLowerCase();
  if (head !== expectedHead) {
    throw new Error(`${label} changed after the update was approved.`);
  }
  const dirty = gitOutput(
    request,
    cwd,
    ["status", "--porcelain", "--untracked-files=no"],
  );
  if (dirty) {
    throw new Error(`${label} gained tracked local changes after approval.`);
  }
}

function writeResult(request, result) {
  const temporaryPath = `${request.resultPath}.${process.pid}.tmp`;
  writeFileSync(
    temporaryPath,
    `${JSON.stringify({
      ...result,
      commit: request.commit,
      currentVersion: request.currentVersion,
      latestVersion: request.latestVersion,
      logPath: request.logPath,
    }, null, 2)}\n`,
  );
  renameSync(temporaryPath, request.resultPath);
}

function installUpdate(request, logFd) {
  const env = {
    ...process.env,
    BRAINSTEM_HOME: request.brainstemHome,
    BRAINSTEM_BETA_COMMIT: request.commit,
    BRAINSTEM_BETA_HOME: request.betaHome,
    BRAINSTEM_BETA_NO_LAUNCH: "1",
    BRAINSTEM_BETA_REPO_URL: request.remoteUrl,
    BRAINSTEM_BETA_UPDATE_REF: request.updateRef,
  };
  if (request.bootstrapUrl) {
    env.BRAINSTEM_BETA_BOOTSTRAP_URL = request.bootstrapUrl;
  }

  if (request.platform === "win32") {
    env.BRAINSTEM_BETA_INSTALLER_PATH = request.installerPath;
    return spawnSync(
      "powershell.exe",
      [
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        "& $env:BRAINSTEM_BETA_INSTALLER_PATH",
      ],
      {
        env,
        stdio: ["ignore", logFd, logFd],
        windowsHide: true,
      },
    );
  }

  return spawnSync("/bin/bash", [request.installerPath], {
    env,
    stdio: ["ignore", logFd, logFd],
  });
}

function relaunch(request) {
  if (!existsSync(request.electronPath)) {
    throw new Error(`Electron is missing after the update: ${request.electronPath}`);
  }
  const child = spawn(request.electronPath, [request.packageDir], {
    detached: true,
    env: {
      ...process.env,
      BRAINSTEM_HOME: request.brainstemHome,
      BRAINSTEM_BETA_HOME: request.betaHome,
      BRAINSTEM_BETA_REPO_URL: request.remoteUrl,
      BRAINSTEM_BETA_UPDATE_REF: request.updateRef,
    },
    stdio: "ignore",
    windowsHide: false,
  });
  child.unref();
}

async function main() {
  const requestPath = process.argv[2];
  if (!requestPath) throw new Error("Update request path is required.");
  const request = loadRequest(requestPath);
  const logFd = openSync(request.logPath, "a");
  let result;

  try {
    writeSync(
      logFd,
      `\n[${new Date().toISOString()}] Updating RAPP Brainstem Frontier to ${request.commit}\n`,
    );
    await waitForParent(request.parentPid);
    assertCheckoutUnchanged(
      request,
      request.betaRepoRoot,
      request.betaExpectedHead,
      "The beta launcher source",
    );
    assertCheckoutUnchanged(
      request,
      request.brainstemRepoRoot,
      request.brainstemExpectedHead,
      "The shared Brainstem source",
    );
    const install = installUpdate(request, logFd);
    if (install.error) throw install.error;
    if (install.status !== 0) {
      throw new Error(
        `The beta installer exited with code ${install.status ?? "unknown"}.`,
      );
    }
    result = { success: true };
  } catch (error) {
    result = { success: false, error: String(error?.message || error) };
    writeSync(logFd, `[X] ${result.error}\n`);
  } finally {
    closeSync(logFd);
    writeResult(request, result);
    for (const temporaryPath of [
      request.installerPath,
      request.requestPath,
      request.runnerPath,
    ]) {
      try {
        rmSync(temporaryPath, { force: true });
      } catch {
        // Windows cannot remove the running copy of this script. It is harmless
        // in the private cache and a later updater can replace it.
      }
    }
  }

  try {
    relaunch(request);
  } catch (error) {
    writeResult(request, {
      success: false,
      error: `${result.error ? `${result.error} ` : ""}Could not reopen the app: ${
        String(error?.message || error)
      }`,
    });
  }
}

main().catch((error) => {
  process.stderr.write(`${String(error?.stack || error)}\n`);
  process.exitCode = 1;
});
