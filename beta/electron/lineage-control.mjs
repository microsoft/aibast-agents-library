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
  const environmentsWord = configuredWord(
    env.RAPP_ENVIRONMENTS_WORD,
    "environments",
  );
  const promoteWord = configuredWord(env.RAPP_PROMOTE_WORD, "promote");
  const driftWord = configuredWord(env.RAPP_DRIFT_WORD, "drift");
  if (trimmed === baselineWord) {
    return { action: "baseline", original, word: baselineWord };
  }
  if (trimmed === restoreWord) {
    return { action: "restore", original, word: restoreWord };
  }
  if (trimmed === environmentsWord) {
    return { action: "environments", original, word: environmentsWord };
  }
  if (
    trimmed === promoteWord
    || trimmed.startsWith(`${promoteWord} `)
  ) {
    const args = trimmed.slice(promoteWord.length).trim().split(/\s+/)
      .filter(Boolean);
    return args.length === 2
      ? {
          action: "promote",
          original,
          word: promoteWord,
          fromEnv: args[0],
          toEnv: args[1],
        }
      : {
          action: "promote",
          original,
          word: promoteWord,
          invalid: true,
        };
  }
  if (trimmed === driftWord || trimmed.startsWith(`${driftWord} `)) {
    const args = trimmed.slice(driftWord.length).trim().split(/\s+/)
      .filter(Boolean);
    return args.length === 1
      ? {
          action: "drift",
          original,
          word: driftWord,
          env: args[0],
        }
      : {
          action: "drift",
          original,
          word: driftWord,
          invalid: true,
        };
  }
  return null;
}

function disabledResult(action) {
  return {
    intercepted: true,
    action,
    disabled: true,
    fallback: null,
    reply: DISABLED_REPLY,
  };
}

function shortRing(entry) {
  if (!entry || entry.isBaseline) return "baseline";
  const match = /:([0-9a-f]{64})$/i.exec(String(entry.head || ""));
  return match ? match[1].slice(0, 8) : "baseline";
}

function environmentsReply(report) {
  if (!report?.loci?.length) {
    return "No Molt Lineage loci are available.";
  }
  const lines = report.loci.map((locus) => {
    const environments = locus.environments
      .map((entry) => `${entry.env} → ${shortRing(entry)}`)
      .join(", ");
    const drift = locus.drifted ? " (baseline drift)" : "";
    return `- ${locus.filename}: ${environments}${drift}`;
  });
  return `Molt Lineage environments:\n${lines.join("\n")}`;
}

function promotionReply(report, fromEnv, toEnv) {
  const changed = report?.changed?.length ?? 0;
  const conflicts = report?.conflicts || [];
  const failed = report?.failed || [];
  if (conflicts.length) {
    const conflict = conflicts[0];
    const agent = conflict.filename || conflict.ancestorRappid || "unknown agent";
    if (!changed) {
      return `CONFLICT on ${agent}: ${toEnv} has a molt ${fromEnv} never built on — nothing moved.`;
    }
    return `Promoted ${changed} agents to ${toEnv}; CONFLICT on ${agent}: ${toEnv} has a molt ${fromEnv} never built on, so that agent did not move.`;
  }
  if (failed.length) {
    if (!changed) {
      return `Promotion failed for ${failed.length} agents — nothing moved.`;
    }
    return `Promoted ${changed} agents to ${toEnv}, but ${failed.length} agents were refused.`;
  }
  if (!changed) return `${fromEnv} and ${toEnv} are already in sync.`;
  return `Promoted ${changed} agents to ${toEnv}.`;
}

function driftReply(report) {
  const drifted = report?.drifted || [];
  if (!drifted.length) {
    return `No drift detected in ${report.env} against ${report.baseEnv}.`;
  }
  const agents = drifted
    .map((locus) => locus.filename || locus.ancestorRappid)
    .join(", ");
  return `Drift detected in ${report.env} against ${report.baseEnv}: ${agents}.`;
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
  if (command.invalid) {
    const usage = command.action === "promote"
      ? `${command.word} <from> <to>`
      : `${command.word} <environment>`;
    return {
      intercepted: true,
      action: command.action,
      reply: `Usage: ${usage}`,
    };
  }

  if (command.action === "environments") {
    const report = routeManager.lineageEnvironments();
    if (report?.disabled) return disabledResult(command.action);
    return {
      intercepted: true,
      action: command.action,
      disabled: false,
      reply: environmentsReply(report),
      environments: report.loci || [],
    };
  }

  if (command.action === "drift") {
    const report = routeManager.lineageDrift(command.env);
    if (report?.disabled) return disabledResult(command.action);
    return {
      intercepted: true,
      action: command.action,
      disabled: false,
      reply: driftReply(report),
      env: report.env,
      baseEnv: report.baseEnv,
      drifted: report.drifted || [],
      loci: report.loci || [],
    };
  }

  if (command.action === "promote") {
    const report = routeManager.promoteLineage({
      fromEnv: command.fromEnv,
      toEnv: command.toEnv,
    });
    if (report?.disabled) return disabledResult(command.action);
    const route = await routeManager.startDefault();
    return {
      intercepted: true,
      action: command.action,
      disabled: false,
      reply: promotionReply(report, report.fromEnv, report.toEnv),
      compositionHash: route.compositionHash,
      changed: report.changed?.length ?? 0,
      unchanged: report.unchanged?.length ?? 0,
      conflicts: report.conflicts || [],
      failed: report.failed || [],
      fromEnv: report.fromEnv,
      toEnv: report.toEnv,
      url: route.url,
    };
  }

  const report = command.action === "baseline"
    ? routeManager.rollbackLineage()
    : routeManager.restoreLineage();
  // The kill switch gates writes too, so nothing moved. Say so rather than
  // claiming a change that did not happen.
  if (report?.disabled) {
    return disabledResult(command.action);
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
