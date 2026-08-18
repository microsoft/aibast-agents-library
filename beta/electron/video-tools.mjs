import { existsSync } from "node:fs";

import ffmpegStatic from "ffmpeg-static";
import ffprobeInstaller from "@ffprobe-installer/ffprobe";


function unpackedPath(filePath) {
  return String(filePath || "").replace(
    /([\\/])app\.asar([\\/])/,
    "$1app.asar.unpacked$2",
  );
}

function resolveTool(explicit, bundled, fallback) {
  if (explicit) return explicit;
  const unpacked = unpackedPath(bundled);
  if (unpacked && existsSync(unpacked)) return unpacked;
  if (bundled && existsSync(bundled)) return bundled;
  return fallback;
}

export function resolveFfmpegExecutable(env = process.env) {
  return resolveTool(
    env.BRAINSTEM_BETA_FFMPEG,
    ffmpegStatic,
    "ffmpeg",
  );
}

export function resolveFfprobeExecutable(env = process.env) {
  return resolveTool(
    env.BRAINSTEM_BETA_FFPROBE,
    ffprobeInstaller.path,
    "ffprobe",
  );
}

export const videoToolInternals = {
  unpackedPath,
};
