import {
  closeSync,
  createWriteStream,
  existsSync,
} from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";
import { Writable } from "node:stream";
import { finished, pipeline } from "node:stream/promises";

import {
  rotateLogIfLarge,
  openPrivateAppendFile,
  RedactingLineTransform,
} from "./log-redaction.mjs";

const DEFAULT_PORT = 7071;
const START_TIMEOUT_MS = 90_000;
const LOG_FLUSH_TIMEOUT_MS = 5_000;

function settleWithin(promise, timeoutMs) {
  return new Promise((resolve) => {
    const timer = setTimeout(
      () => resolve({ settled: false, error: null }),
      timeoutMs,
    );
    promise.then(
      () => {
        clearTimeout(timer);
        resolve({ settled: true, error: null });
      },
      (error) => {
        clearTimeout(timer);
        resolve({ settled: true, error });
      },
    );
  });
}

class SharedLogSink extends Writable {
  constructor(destination) {
    super();
    this.destination = destination;
  }

  _write(chunk, encoding, callback) {
    this.destination.write(chunk, encoding, callback);
  }
}

export function resolveBrainstemConfig({
  env = process.env,
  platform = process.platform,
  home = homedir(),
} = {}) {
  const paths = platform === "win32" ? path.win32 : path.posix;
  const brainstemHome = env.BRAINSTEM_HOME || paths.join(home, ".brainstem");
  const brainstemDir = env.BRAINSTEM_BETA_SOURCE_DIR
    || paths.join(brainstemHome, "src", "rapp_brainstem");
  const python = env.BRAINSTEM_BETA_PYTHON
    || (platform === "win32"
      ? paths.join(brainstemHome, "venv", "Scripts", "python.exe")
      : paths.join(brainstemHome, "venv", "bin", "python"));
  const port = Number.parseInt(
    env.BRAINSTEM_BETA_PORT || env.PORT || String(DEFAULT_PORT),
    10,
  );

  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error(`Invalid Brainstem port: ${port}`);
  }

  return {
    brainstemHome,
    brainstemDir,
    python,
    port,
    url: `http://127.0.0.1:${port}`,
    logFile: paths.join(brainstemHome, "logs", "beta-brainstem.log"),
  };
}

export function isBrainstemHealth(value) {
  return Boolean(
    value
    && typeof value === "object"
    && ["ok", "unauthenticated"].includes(value.status)
    && typeof value.version === "string"
    && Array.isArray(value.agents),
  );
}

export async function probeHealth(url, timeoutMs = 1_500) {
  try {
    const response = await fetch(`${url}/health`, {
      signal: AbortSignal.timeout(timeoutMs),
      headers: { Accept: "application/json" },
    });
    if (!response.ok) return null;
    const body = await response.json();
    return isBrainstemHealth(body) ? body : null;
  } catch {
    return null;
  }
}

export async function waitForHealth(
  url,
  {
    timeoutMs = START_TIMEOUT_MS,
    intervalMs = 500,
    probe = probeHealth,
    exited = () => false,
  } = {},
) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const health = await probe(url);
    if (health) return health;
    if (exited()) return null;
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
  return null;
}

// The environment a worker kernel runs with. Bytecode caches are off: every
// composition is its own directory, so each worker used to write its own
// __pycache__ next to the agents — 40 of the 43 MB of one developer's
// compositions directory was regenerable bytecode. The kernel's own modules
// compile in milliseconds; nothing is lost. An explicit config.env still wins.
export function buildWorkerEnvironment(config, baseEnv = process.env) {
  return {
    ...baseEnv,
    PYTHONDONTWRITEBYTECODE: "1",
    ...(config.env || {}),
    PORT: String(config.port),
    BRAINSTEM_BETA_LAUNCHER: "1",
    PYTHONUTF8: "1",
  };
}

export class BrainstemProcess {
  constructor(config = resolveBrainstemConfig()) {
    this.config = config;
    this.child = null;
    this.logFd = null;
    this.logStream = null;
    this.logFlushPromise = null;
    this.owned = false;
  }

  captureOutput(child) {
    const pumps = [child.stdout, child.stderr].map((output) => (
      pipeline(
        output,
        new RedactingLineTransform(),
        new SharedLogSink(this.logStream),
      )
    ));
    this.logFlushPromise = (async () => {
      const results = await Promise.allSettled(pumps);
      let finishError = null;
      try {
        if (!this.logStream.destroyed && !this.logStream.writableEnded) {
          this.logStream.end();
        }
        await finished(this.logStream, { cleanup: true });
      } catch (error) {
        finishError = error;
      }
      const failed = results.find((result) => result.status === "rejected");
      if (failed) throw failed.reason;
      if (finishError) throw finishError;
    })();
    void this.logFlushPromise.catch(() => {});
  }

  async closeLog(child = null) {
    let failure = null;
    if (this.logFlushPromise) {
      const timeoutMs = Number.isFinite(this.config.logFlushTimeoutMs)
        ? Math.max(1, this.config.logFlushTimeoutMs)
        : LOG_FLUSH_TIMEOUT_MS;
      let outcome = await settleWithin(this.logFlushPromise, timeoutMs);
      if (!outcome.settled) {
        child?.stdout?.destroy();
        child?.stderr?.destroy();
        outcome = await settleWithin(
          this.logFlushPromise,
          Math.min(timeoutMs, 1_000),
        );
        if (!outcome.settled) {
          this.logStream?.destroy();
          await settleWithin(
            this.logFlushPromise,
            Math.min(timeoutMs, 1_000),
          );
        }
        failure = new Error(
          `Timed out flushing Brainstem output to ${this.config.logFile}.`,
        );
      } else {
        failure = outcome.error;
      }
    } else if (this.logStream && !this.logStream.writableEnded) {
      try {
        this.logStream.end();
        await finished(this.logStream, { cleanup: true });
      } catch (error) {
        failure = error;
      }
    }
    this.logFlushPromise = null;
    this.logStream = null;
    if (this.logFd !== null) {
      closeSync(this.logFd);
      this.logFd = null;
    }
    if (failure) throw failure;
  }

  async start() {
    const existing = await probeHealth(this.config.url);
    if (existing) {
      this.owned = false;
      return { reused: true, health: existing, ...this.config };
    }

    const serverFile = path.join(this.config.brainstemDir, "brainstem.py");
    if (!existsSync(serverFile)) {
      throw new Error(
        `Brainstem source is missing at ${this.config.brainstemDir}. Re-run the Frontier installer.`,
      );
    }
    if (!existsSync(this.config.python)) {
      throw new Error(
        `Brainstem Python environment is missing at ${this.config.python}. Re-run the Frontier installer.`,
      );
    }

    rotateLogIfLarge(this.config.logFile, {
      maxBytes: this.config.maxLogBytes ?? 5 * 1024 * 1024,
    });
    this.logFd = openPrivateAppendFile(this.config.logFile);
    this.logStream = createWriteStream(this.config.logFile, {
      fd: this.logFd,
      autoClose: false,
    });
    try {
      const spawnProcess = this.config.spawnImpl || spawn;
      this.child = spawnProcess(this.config.python, ["brainstem.py"], {
        cwd: this.config.brainstemDir,
        env: buildWorkerEnvironment(this.config),
        windowsHide: true,
        shell: false,
        stdio: ["ignore", "pipe", "pipe"],
      });
      this.captureOutput(this.child);
    } catch (error) {
      this.logStream.destroy();
      this.logStream = null;
      closeSync(this.logFd);
      this.logFd = null;
      throw error;
    }
    this.owned = true;

    const health = await waitForHealth(this.config.url, {
      exited: () => this.child?.exitCode !== null,
    });
    if (!health) {
      const exitCode = this.child?.exitCode;
      await this.stop();
      throw new Error(
        `Brainstem did not become healthy${exitCode === null ? "" : ` (exit ${exitCode})`}. See ${this.config.logFile}.`,
      );
    }

    return { reused: false, health, ...this.config };
  }

  async stop() {
    const child = this.child;
    this.child = null;
    this.owned = false;

    if (
      child
      && child.exitCode === null
      && child.signalCode === null
    ) {
      child.kill("SIGTERM");
      await Promise.race([
        new Promise((resolve) => child.once("exit", resolve)),
        new Promise((resolve) => setTimeout(resolve, 5_000)),
      ]);
      if (child.exitCode === null && child.signalCode === null) {
        child.kill("SIGKILL");
        await Promise.race([
          new Promise((resolve) => child.once("exit", resolve)),
          new Promise((resolve) => setTimeout(resolve, 5_000)),
        ]);
      }
    }

    await this.closeLog(child);
  }
}
