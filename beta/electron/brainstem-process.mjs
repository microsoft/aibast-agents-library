import {
  closeSync,
  existsSync,
  mkdirSync,
  openSync,
} from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";

const DEFAULT_PORT = 7071;
const START_TIMEOUT_MS = 90_000;

export function resolveBrainstemConfig({
  env = process.env,
  platform = process.platform,
  home = homedir(),
} = {}) {
  const brainstemHome = env.BRAINSTEM_HOME || path.join(home, ".brainstem");
  const brainstemDir = env.BRAINSTEM_BETA_SOURCE_DIR
    || path.join(brainstemHome, "src", "rapp_brainstem");
  const python = env.BRAINSTEM_BETA_PYTHON
    || (platform === "win32"
      ? path.join(brainstemHome, "venv", "Scripts", "python.exe")
      : path.join(brainstemHome, "venv", "bin", "python"));
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
    logFile: path.join(brainstemHome, "logs", "beta-brainstem.log"),
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

export class BrainstemProcess {
  constructor(config = resolveBrainstemConfig()) {
    this.config = config;
    this.child = null;
    this.logFd = null;
    this.owned = false;
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

    mkdirSync(path.dirname(this.config.logFile), { recursive: true });
    this.logFd = openSync(this.config.logFile, "a");
    this.child = spawn(this.config.python, ["brainstem.py"], {
      cwd: this.config.brainstemDir,
      env: {
        ...process.env,
        ...(this.config.env || {}),
        PORT: String(this.config.port),
        BRAINSTEM_BETA_LAUNCHER: "1",
        PYTHONUTF8: "1",
      },
      windowsHide: true,
      shell: false,
      stdio: ["ignore", this.logFd, this.logFd],
    });
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

    if (child && child.exitCode === null) {
      child.kill("SIGTERM");
      await Promise.race([
        new Promise((resolve) => child.once("exit", resolve)),
        new Promise((resolve) => setTimeout(resolve, 5_000)),
      ]);
      if (child.exitCode === null) child.kill("SIGKILL");
    }

    if (this.logFd !== null) {
      closeSync(this.logFd);
      this.logFd = null;
    }
  }
}
