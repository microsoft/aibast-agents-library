const BASELINE_REPLY = "Reverted to Grail baseline — your memories are intact.";
const RESTORE_REPLY = "Restored the latest verified molts — your memories are intact.";
const DISABLED_REPLY = "Molt Lineage is turned off on this Brainstem (RAPP_MOLT_LINEAGE=0), so there is nothing to change — you are already running the Grail baseline.";

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
  const report = command.action === "baseline"
    ? routeManager.rollbackLineage()
    : routeManager.restoreLineage();
  // The kill switch gates writes too, so nothing moved. Say so rather than
  // claiming a change that did not happen.
  if (report?.disabled) {
    return {
      intercepted: true,
      action: command.action,
      disabled: true,
      fallback: null,
      reply: DISABLED_REPLY,
    };
  }
  const route = await routeManager.startDefault();
  const fallback = routeManager.lastLineageFallback || null;
  let reply = command.action === "baseline" ? BASELINE_REPLY : RESTORE_REPLY;
  if (report?.failed?.length) {
    reply = command.action === "baseline"
      ? "Reverted what I could to Grail baseline, but "
        + `${report.failed.length} agent(s) could not be reverted — your memories are intact.`
      : "Restored what I could, but "
        + `${report.failed.length} agent(s) could not be updated — your memories are intact.`;
  } else if (command.action === "restore" && fallback?.rejected?.length) {
    reply = fallback.accepted?.length
      ? "Restored compatible verified molts, but kept last-good code for incompatible rings — your memories are intact."
      : "Restore could not activate the latest verified molts; kept the last-good composition — your memories are intact.";
  } else if (command.action === "restore" && !report?.changed?.length) {
    // Nothing actually moved. Saying "restored" here would confirm a recovery
    // that did not happen — and if the user's molts are gone or pinned, that
    // false confirmation is the moment they stop looking for them.
    reply = report?.unchanged?.length
      ? "There was nothing to restore — every agent is already at the newest "
        + "version it has, or is pinned to its baseline. Your memories are intact."
      : "There was nothing to restore. Your memories are intact.";
  }
  return {
    intercepted: true,
    action: command.action,
    fallback,
    reply,
    compositionHash: route.compositionHash,
    restored: command.action === "restore"
      ? Boolean(report?.changed?.length) && !fallback?.rejected?.length
      : undefined,
    changed: report?.changed?.length ?? 0,
    unchanged: report?.unchanged?.length ?? 0,
    url: route.url,
  };
}

export const lineageControlReplies = {
  baseline: BASELINE_REPLY,
  restore: RESTORE_REPLY,
  disabled: DISABLED_REPLY,
};
