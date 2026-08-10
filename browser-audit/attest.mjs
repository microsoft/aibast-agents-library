import fs from "node:fs/promises";
import path from "node:path";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const directory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(
  process.env.AIBAST_REPO_ROOT
  || execFileSync(
    "git",
    ["-C", directory, "rev-parse", "--show-toplevel"],
    { encoding: "utf8" },
  ).trim(),
);
const hash = (content) => createHash("sha256").update(content).digest("hex");
const requiredMutationCount = 42;
const requiredMutationContractSha256 = (
  "39a3df3b7b567822b8707b8c450eba5bda481c8015291e303afb90dcfeed2fc7"
);
const certificationOutputPaths = new Set([
  "browser-audit/audited-snapshot-manifest.json",
  "browser-audit/browser-audit.json",
  "browser-audit/browser-certification-attestation.json",
  "browser-audit/easy-contact-sheet.jpg",
  "browser-audit/hard-contact-sheet.jpg",
  "browser-audit/mutation-suite.json",
]);
const certificationInputGitStatus = (rawStatus) => rawStatus
  .split("\n")
  .filter(Boolean)
  .filter((line) => {
    const rawPath = line.slice(3);
    const candidates = rawPath
      .split(" -> ")
      .map((candidate) => candidate.replace(/^"|"$/g, ""));
    return !candidates.every((candidate) => (
      certificationOutputPaths.has(candidate)
      || candidate.startsWith("browser-audit/screenshots/")
    ));
  })
  .map((line) => `${line}\n`)
  .join("");
const read = async (name) => fs.readFile(path.join(directory, name));
const readJson = async (name) => JSON.parse((await read(name)).toString("utf8"));

const [
  auditScript,
  mutationScript,
  attestationScript,
  auditReportSource,
  mutationReportSource,
  manifestSource,
  auditReport,
  mutationReport,
  manifest,
] = await Promise.all([
  read("audit.mjs"),
  read("mutation-suite.mjs"),
  read("attest.mjs"),
  read("browser-audit.json"),
  read("mutation-suite.json"),
  read("audited-snapshot-manifest.json"),
  readJson("browser-audit.json"),
  readJson("mutation-suite.json"),
  readJson("audited-snapshot-manifest.json"),
]);

const expectedScreenshotNames = auditReport.results.flatMap(({ slug }) => [
  `${slug}-easy.png`,
  `${slug}-hard.png`,
]).sort();
const actualScreenshotNames = (await fs.readdir(path.join(directory, "screenshots")))
  .filter((name) => name.endsWith(".png"))
  .sort();
const screenshotEntries = await Promise.all(actualScreenshotNames.map(async (name) => {
  const source = await fs.readFile(path.join(directory, "screenshots", name));
  return { path: `screenshots/${name}`, bytes: source.length, sha256: hash(source) };
}));
const reportedScreenshotEntries = [...(auditReport.screenshot_artifacts || [])]
  .sort((left, right) => left.path.localeCompare(right.path));
const sortedScreenshotEntries = [...screenshotEntries]
  .sort((left, right) => left.path.localeCompare(right.path));
const contactSheetEntries = await Promise.all([
  "easy-contact-sheet.jpg",
  "hard-contact-sheet.jpg",
].map(async (name) => {
  const source = await read(name);
  return { path: name, bytes: source.length, sha256: hash(source) };
}));
const reportedContactSheetEntries = [
  ...(auditReport.contact_sheet_artifacts || []),
].sort((left, right) => left.path.localeCompare(right.path));
const sortedContactSheetEntries = [...contactSheetEntries]
  .sort((left, right) => left.path.localeCompare(right.path));

const manifestEntryMismatches = [];
const currentManifestSources = new Map();
for (const entry of manifest.entries) {
  const file = entry.path.startsWith("gate:")
    ? path.join(directory, entry.path.slice("gate:".length))
    : path.join(root, entry.path);
  try {
    const source = await fs.readFile(file);
    const actual = {
      bytes: source.length,
      sha256: hash(source),
    };
    currentManifestSources.set(entry.path, source);
    if (actual.bytes !== entry.bytes || actual.sha256 !== entry.sha256) {
      manifestEntryMismatches.push({
        path: entry.path,
        expected: { bytes: entry.bytes, sha256: entry.sha256 },
        actual,
      });
    }
  } catch (error) {
    manifestEntryMismatches.push({
      path: entry.path,
      error: error.code || String(error),
    });
  }
}
const currentAggregate = createHash("sha256");
let currentManifestBytes = 0;
const orderedManifestPaths = [
  ...manifest.entries
    .filter((entry) => !entry.path.startsWith("gate:"))
    .map((entry) => entry.path)
    .sort((left, right) => left.localeCompare(right)),
  ...manifest.entries
    .filter((entry) => entry.path.startsWith("gate:"))
    .map((entry) => entry.path)
    .sort((left, right) => left.localeCompare(right)),
];
for (const manifestPath of orderedManifestPaths) {
  const source = currentManifestSources.get(manifestPath);
  if (!source) continue;
  currentManifestBytes += source.length;
  currentAggregate.update(manifestPath);
  currentAggregate.update("\0");
  currentAggregate.update(String(source.length));
  currentAggregate.update("\0");
  currentAggregate.update(source);
  currentAggregate.update("\0");
}
const currentManifestAggregateSha256 = currentAggregate.digest("hex");
const currentGitSha = execFileSync(
  "git",
  ["-C", root, "rev-parse", "HEAD"],
  { encoding: "utf8" },
).trim();
const currentGitStatus = certificationInputGitStatus(execFileSync(
  "git",
  ["-C", root, "status", "--porcelain=v1"],
  { encoding: "utf8" },
));
const currentGitStatusSha256 = hash(currentGitStatus);

const assertions = {
  audit_schema: auditReport.schema === "aibast-browser-visual-audit/4.8",
  audit_complete: auditReport.total === 51
    && auditReport.passed === 51
    && auditReport.failed === 0,
  immutable_inputs: auditReport.immutable_snapshot_complete === true
    && auditReport.audited_inputs_unchanged === true
    && auditReport.rejected_snapshot_requests.length === 0
    && auditReport.rejected_external_requests.length === 0
    && auditReport.rejected_websocket_requests.length === 0
    && auditReport.service_workers_policy === "block"
    && auditReport.observed_service_workers.length === 0,
  manifest_bound: hash(manifestSource) === auditReport.snapshot_manifest.sha256
    && manifest.aggregate_sha256 === auditReport.audited_inputs.sha256
    && manifestEntryMismatches.length === 0
    && currentManifestAggregateSha256 === manifest.aggregate_sha256
    && currentManifestSources.size === manifest.files
    && currentManifestBytes === manifest.bytes,
  repository_current: currentGitSha === auditReport.git_sha
    && currentGitStatusSha256 === auditReport.git_status_sha256,
  mutation_schema: mutationReport.schema === "aibast-browser-audit-mutations/1.10",
  mutations_complete: mutationReport.release_eligible === true
    && mutationReport.total === requiredMutationCount
    && mutationReport.total === mutationReport.mutation_names.length
    && mutationReport.mutation_contract_sha256
      === requiredMutationContractSha256
    && mutationReport.passed === mutationReport.total
    && mutationReport.failed === 0
    && mutationReport.baseline_restored === true,
  mutation_baseline_bound: mutationReport.baseline_audited_inputs_sha256
    === auditReport.audited_inputs.sha256,
  scripts_bound: mutationReport.bindings.audit_script_sha256 === hash(auditScript)
    && mutationReport.bindings.mutation_script_sha256 === hash(mutationScript)
    && mutationReport.bindings.attestation_script_sha256 === hash(attestationScript),
  screenshots_complete: JSON.stringify(actualScreenshotNames)
    === JSON.stringify(expectedScreenshotNames),
  screenshot_count: screenshotEntries.length === 102
    && screenshotEntries.every((entry) => entry.bytes > 0),
  screenshots_bound: JSON.stringify(sortedScreenshotEntries)
    === JSON.stringify(reportedScreenshotEntries),
  contact_sheets_present: contactSheetEntries.every((entry) => entry.bytes > 0),
  contact_sheets_bound: JSON.stringify(sortedContactSheetEntries)
    === JSON.stringify(reportedContactSheetEntries),
};
const failedAssertions = Object.entries(assertions)
  .filter(([_name, passed]) => !passed)
  .map(([name]) => name);
if (failedAssertions.length) {
  throw new Error(`Certification attestation failed: ${failedAssertions.join(", ")}`);
}

const payload = {
  schema: "aibast-browser-certification-attestation/1.8",
  repository: "microsoft/aibast-agents-library",
  git_sha: auditReport.git_sha,
  git_dirty: auditReport.git_dirty,
  git_status_sha256: auditReport.git_status_sha256,
  audited_inputs_sha256: auditReport.audited_inputs.sha256,
  audited_files: auditReport.audited_inputs.files,
  audited_bytes: auditReport.audited_inputs.bytes,
  audit: {
    schema: auditReport.schema,
    total: auditReport.total,
    passed: auditReport.passed,
    failed: auditReport.failed,
    rejected_snapshot_requests: auditReport.rejected_snapshot_requests,
    rejected_external_requests: auditReport.rejected_external_requests,
    rejected_websocket_requests: auditReport.rejected_websocket_requests,
    service_workers_policy: auditReport.service_workers_policy,
    observed_service_workers: auditReport.observed_service_workers,
  },
  mutations: {
    schema: mutationReport.schema,
    total: mutationReport.total,
    passed: mutationReport.passed,
    failed: mutationReport.failed,
    baseline_restored: mutationReport.baseline_restored,
    release_eligible: mutationReport.release_eligible,
    mutation_contract_sha256: mutationReport.mutation_contract_sha256,
    names: mutationReport.mutation_names,
  },
  execution_environment: auditReport.execution_environment,
  assertions,
  bindings: {
    audit_script_sha256: hash(auditScript),
    mutation_script_sha256: hash(mutationScript),
    attestation_script_sha256: hash(attestationScript),
    audit_report_sha256: hash(auditReportSource),
    mutation_report_sha256: hash(mutationReportSource),
    snapshot_manifest_sha256: hash(manifestSource),
    current_manifest_aggregate_sha256: currentManifestAggregateSha256,
    current_git_sha: currentGitSha,
    current_git_status_sha256: currentGitStatusSha256,
    screenshots: screenshotEntries,
    contact_sheets: contactSheetEntries,
  },
};
const canonicalPayload = `${JSON.stringify(payload)}\n`;
const attestation = {
  ...payload,
  integrity_sha256: hash(canonicalPayload),
};
await fs.writeFile(
  path.join(directory, "browser-certification-attestation.json"),
  `${JSON.stringify(attestation, null, 2)}\n`,
);
console.log(JSON.stringify({
  schema: attestation.schema,
  audited_inputs_sha256: attestation.audited_inputs_sha256,
  mutations: attestation.mutations.total,
  workshops: attestation.audit.total,
  screenshots: screenshotEntries.length,
  integrity_sha256: attestation.integrity_sha256,
}));
