const BASELINE_REPLY = "Reverted to Grail baseline — your memories are intact.";
const RESTORE_REPLY = "Restored the latest verified molts — your memories are intact.";

function configuredWord(value, fallback) {
  const word = String(value || "").trim();
  return word || fallback;
}

export function parseLineageCommand(message, env = process.env) {
  const original = String(message ?? "");
  const trimmed = original.trim();
  const baselineWord = configuredWord(
    env.RAPP_BASELINE_SAFEWORD,
    "baseline",
  );
  const restoreWord = configuredWord(env.RAPP_RESTORE_WORD, "restore");
  if (trimmed === baselineWord) {
    return { action: "baseline", original, word: baselineWord };
  }
  if (trimmed === restoreWord) {
    return { action: "restore", original, word: restoreWord };
  }
  return null;
}

export async function executeLineageCommand({
  message,
  routeManager,
  env = process.env,
} = {}) {
  const command = parseLineageCommand(message, env);
  if (!command) {
    return {
      intercepted: false,
      message,
    };
  }
  if (!routeManager) {
    throw new Error("Molt Lineage control requires the Frontier route manager.");
  }
  if (command.action === "baseline") {
    routeManager.rollbackLineage();
  } else {
    routeManager.restoreLineage();
  }
  const route = await routeManager.startDefault();
  return {
    intercepted: true,
    action: command.action,
    reply: command.action === "baseline" ? BASELINE_REPLY : RESTORE_REPLY,
    compositionHash: route.compositionHash,
    url: route.url,
  };
}

export const lineageControlReplies = {
  baseline: BASELINE_REPLY,
  restore: RESTORE_REPLY,
};
