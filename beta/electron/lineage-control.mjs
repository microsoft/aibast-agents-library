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
  const fallback = routeManager.lastLineageFallback || null;
  let reply = command.action === "baseline" ? BASELINE_REPLY : RESTORE_REPLY;
  if (command.action === "restore" && fallback?.rejected?.length) {
    reply = fallback.accepted?.length
      ? "Restored compatible verified molts, but kept last-good code for incompatible rings — your memories are intact."
      : "Restore could not activate the latest verified molts; kept the last-good composition — your memories are intact.";
  }
  return {
    intercepted: true,
    action: command.action,
    fallback,
    reply,
    compositionHash: route.compositionHash,
    restored: command.action === "restore"
      ? !fallback?.rejected?.length
      : undefined,
    url: route.url,
  };
}

export const lineageControlReplies = {
  baseline: BASELINE_REPLY,
  restore: RESTORE_REPLY,
};
