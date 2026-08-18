import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import test from "node:test";

import {
  resolveFfmpegExecutable,
  resolveFfprobeExecutable,
  videoToolInternals,
} from "../electron/video-tools.mjs";


test("bundled ffmpeg and ffprobe binaries are executable", () => {
  for (const executable of [
    resolveFfmpegExecutable({}),
    resolveFfprobeExecutable({}),
  ]) {
    assert.equal(existsSync(executable), true, executable);
    const result = spawnSync(executable, ["-version"], {
      encoding: "utf8",
      windowsHide: true,
    });
    assert.equal(result.status, 0, result.stderr);
  }
  if (process.platform === "darwin" && process.arch === "arm64") {
    const architecture = spawnSync(
      "file",
      [resolveFfprobeExecutable({})],
      { encoding: "utf8" },
    );
    assert.equal(architecture.status, 0, architecture.stderr);
    assert.match(architecture.stdout, /arm64|universal/i);
  }
});

test("packaged video-tool paths resolve outside app.asar on every platform", () => {
  for (const [input, expected] of [
    [
      "/tmp/app.asar/node_modules/tool/bin",
      "/tmp/app.asar.unpacked/node_modules/tool/bin",
    ],
    [
      String.raw`C:\tmp\app.asar\node_modules\tool\bin.exe`,
      String.raw`C:\tmp\app.asar.unpacked\node_modules\tool\bin.exe`,
    ],
  ]) {
    assert.equal(videoToolInternals.unpackedPath(input), expected);
  }
});
