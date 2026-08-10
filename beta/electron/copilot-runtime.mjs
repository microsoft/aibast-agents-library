import { existsSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";

import { CopilotClient, RuntimeConnection } from "@github/copilot-sdk";

const require = createRequire(import.meta.url);
const DEFAULT_START_TIMEOUT_MS = 30_000;

export function copilotPackageName(
  platform = process.platform,
  arch = process.arch,
) {
  const os = platform === "win32"
    ? "win32"
    : platform === "darwin"
      ? "darwin"
      : "linux";
  return `@github/copilot-${os}-${arch}`;
}

export function resolveCopilotCliPath(
  platform = process.platform,
  arch = process.arch,
) {
  const packageName = copilotPackageName(platform, arch);
  try {
    const resolved = require.resolve(packageName);
    if (existsSync(resolved)) return resolved;
  } catch {}

  try {
    const packageDir = path.dirname(
      require.resolve(`${packageName}/package.json`),
    );
    const binaryName = platform === "win32" ? "copilot.exe" : "copilot";
    const binaryPath = path.join(packageDir, binaryName);
    if (existsSync(binaryPath)) return binaryPath;
  } catch {}

  return undefined;
}

export function withTimeout(
  promise,
  label,
  timeoutMs = DEFAULT_START_TIMEOUT_MS,
) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(
      () => reject(new Error(`${label} did not start within ${timeoutMs}ms`)),
      timeoutMs,
    );
    promise.then(
      (value) => {
        clearTimeout(timer);
        resolve(value);
      },
      (error) => {
        clearTimeout(timer);
        reject(error);
      },
    );
  });
}

export class CopilotRuntime {
  constructor({ timeoutMs = DEFAULT_START_TIMEOUT_MS } = {}) {
    this.timeoutMs = timeoutMs;
    this.client = null;
    this.startPromise = null;
  }

  async start() {
    if (this.startPromise) return this.startPromise;

    this.startPromise = (async () => {
      const cliPath = resolveCopilotCliPath();
      const options = cliPath
        ? { connection: RuntimeConnection.forStdio({ path: cliPath }) }
        : undefined;
      const client = new CopilotClient(options);

      try {
        await withTimeout(
          client.start(),
          "Bundled GitHub Copilot CLI",
          this.timeoutMs,
        );
        const auth = await client.getAuthStatus();
        this.client = client;
        return {
          available: true,
          authenticated: Boolean(auth?.isAuthenticated),
          login: auth?.login || null,
          cliPath: cliPath || null,
        };
      } catch (error) {
        await client.stop().catch(() => undefined);
        throw error;
      }
    })();

    try {
      return await this.startPromise;
    } catch (error) {
      this.startPromise = null;
      throw error;
    }
  }

  async stop() {
    const client = this.client;
    this.client = null;
    this.startPromise = null;
    if (client) await client.stop().catch(() => undefined);
  }
}
