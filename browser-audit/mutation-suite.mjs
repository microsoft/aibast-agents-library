import fs from "node:fs/promises";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";

const mutationScriptPath = fileURLToPath(import.meta.url);
const out = path.dirname(mutationScriptPath);
const root = path.resolve(
  process.env.AIBAST_REPO_ROOT
  || execFileSync(
    "git",
    ["-C", out, "rev-parse", "--show-toplevel"],
    { encoding: "utf8" },
  ).trim(),
);
const auditPath = path.join(out, "audit.mjs");
const attestationPath = path.join(out, "attest.mjs");
const mutationOut = path.join(out, "mutation-runs");
const reportPath = path.join(mutationOut, "browser-audit.json");
const mutationReportPath = path.join(out, "mutation-suite.json");
const questPath = path.join(root, "solutions", "account-intelligence", "quest.html");
const catalogPath = path.join(root, "solutions", "catalog.json");
const registryPath = path.join(root, "registry.json");
const temporaryAuditPath = path.join(out, ".audit-provenance-mutation.mjs");
const temporaryServiceWorkerPath = path.join(
  root,
  "solutions",
  "account-intelligence",
  "audit-service-worker.js",
);
const trackedPaths = [questPath, catalogPath, registryPath, attestationPath];
const originals = new Map(
  await Promise.all(
    trackedPaths.map(async (file) => [file, await fs.readFile(file, "utf8")]),
  ),
);
const sha256 = (content) => createHash("sha256").update(content).digest("hex");
const sanitizeOutput = (value) => String(value || "")
  .replaceAll(root, "$REPO")
  .replaceAll(out, "$AUDIT_DIR");

function replaceOnce(source, search, replacement, label) {
  if (!source.includes(search)) {
    throw new Error(`Mutation anchor not found: ${label}`);
  }
  return source.replace(search, replacement);
}

function injectStyle(source, css) {
  return replaceOnce(source, "</style>", `${css}\n  </style>`, "style close");
}

function injectBody(source, markup) {
  return replaceOnce(source, "</body>", `${markup}\n</body>`, "body close");
}

function crc32(source) {
  let crc = 0xffffffff;
  for (const value of source) {
    crc ^= value;
    for (let bit = 0; bit < 8; bit += 1) {
      crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function addPngTextChunk(source) {
  const signature = source.subarray(0, 8).toString("hex");
  if (signature !== "89504e470d0a1a0a") throw new Error("Expected PNG mutation input");
  let offset = 8;
  while (offset + 12 <= source.length) {
    const length = source.readUInt32BE(offset);
    const type = source.subarray(offset + 4, offset + 8).toString("ascii");
    if (type === "IEND") {
      const data = Buffer.from("Comment\0AIBAST decoded-identity mutation", "latin1");
      const chunk = Buffer.alloc(12 + data.length);
      chunk.writeUInt32BE(data.length, 0);
      chunk.write("tEXt", 4, 4, "ascii");
      data.copy(chunk, 8);
      chunk.writeUInt32BE(
        crc32(chunk.subarray(4, 8 + data.length)),
        8 + data.length,
      );
      return Buffer.concat([
        source.subarray(0, offset),
        chunk,
        source.subarray(offset),
      ]);
    }
    offset += 12 + length;
  }
  throw new Error("PNG IEND chunk not found");
}

async function restoreTrackedFiles() {
  await Promise.all(
    [...originals].map(([file, content]) => fs.writeFile(file, content)),
  );
  await fs.rm(temporaryServiceWorkerPath, { force: true });
}

async function runAudit(scriptPath = auditPath) {
  await fs.mkdir(mutationOut, { recursive: true });
  await fs.rm(reportPath, { force: true });
  const result = spawnSync(process.execPath, [scriptPath], {
    cwd: out,
    env: {
      ...process.env,
      AUDIT_OUT: mutationOut,
      AUDIT_SLUG: "account-intelligence",
    },
    encoding: "utf8",
    timeout: 240000,
  });
  let report = null;
  try {
    report = JSON.parse(await fs.readFile(reportPath, "utf8"));
  } catch (_error) {
    report = null;
  }
  return {
    status: result.status,
    signal: result.signal,
    stdout: result.stdout,
    stderr: result.stderr,
    report,
  };
}

function allImageFailures(report) {
  const row = report?.results?.[0];
  return [
    ...(row?.desktopImageFailures || []),
    ...(row?.mobileImageFailures || []),
  ];
}

const originalQuest = originals.get(questPath);
const firstImageSource = originalQuest.match(
  /<img\b[^>]*\bdata-evidence-status="reusable"[^>]*\bsrc="([^"]+)"/,
)?.[1];
if (!firstImageSource) throw new Error("No reusable image source found for mutations");
const reusableSources = [...originalQuest.matchAll(
  /<img\b[^>]*\bdata-evidence-status="reusable"[^>]*\bsrc="([^"]+)"/g,
)].map((match) => match[1]);
const secondImageSource = reusableSources[1];
const hardPanelSource = originalQuest.split('data-path="hard"', 2)[1] || "";
const firstHardImageSource = hardPanelSource.match(
  /<img\b[^>]*\bdata-evidence-status="reusable"[^>]*\bsrc="([^"]+)"/,
)?.[1];
if (!secondImageSource || !firstHardImageSource) {
  throw new Error("Expected multiple Easy images and at least one Hard image");
}
const firstImagePath = path.join(
  root,
  "solutions",
  "account-intelligence",
  firstImageSource,
);
const firstHardImagePath = path.join(
  root,
  "solutions",
  "account-intelligence",
  firstHardImageSource,
);
originals.set(firstHardImagePath, await fs.readFile(firstHardImagePath));

const mutations = [
  {
    name: "catalog-scope-count",
    apply: async () => {
      const catalog = JSON.parse(originals.get(catalogPath));
      const key = Object.keys(catalog.solutions || {})[0];
      delete catalog.solutions[key];
      await fs.writeFile(catalogPath, `${JSON.stringify(catalog, null, 2)}\n`);
    },
    assert: ({ status, stderr }) => (
      status !== 0
      && (
        stderr.includes("Expected 51 catalog workshops")
        || stderr.includes("Registry-only solution lacks exclusion proof")
      )
    ),
  },
  {
    name: "catalog-display-identity",
    apply: async () => {
      const catalog = JSON.parse(originals.get(catalogPath));
      catalog.solutions["@aibast-agents-library/account-intelligence"].display_name
        = "Wrong Advertised Workshop Title";
      await fs.writeFile(catalogPath, `${JSON.stringify(catalog, null, 2)}\n`);
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.results?.[0]?.catalogIdentity === false
    ),
  },
  {
    name: "registry-quest-identity",
    apply: async () => {
      const registry = JSON.parse(originals.get(registryPath));
      const agent = registry.agents.find(
        (row) => row?._solution?.package?.slug === "account-intelligence",
      );
      agent._solution.package.quest_url = "solutions/wrong/quest.html";
      await fs.writeFile(registryPath, `${JSON.stringify(registry, null, 2)}\n`);
    },
    assert: ({ status, stderr }) => (
      status !== 0 && stderr.includes("Registry quest URL mismatch")
    ),
  },
  {
    name: "served-input-provenance",
    script: temporaryAuditPath,
    apply: async () => {
      const audit = await fs.readFile(auditPath, "utf8");
      const mutated = replaceOnce(
        audit,
        '"x-aibast-audit-inputs": auditedInputs.sha256,',
        '"x-aibast-audit-inputs": "tampered-input-digest",',
        "provenance response header",
      );
      await fs.writeFile(temporaryAuditPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0 && report?.results?.[0]?.provenance === false
    ),
  },
  {
    name: "audited-input-toctou",
    script: temporaryAuditPath,
    apply: async () => {
      const audit = await fs.readFile(auditPath, "utf8");
      const anchor = "const baseUrl = `http://127.0.0.1:${address.port}`;";
      const injected = `${anchor}
setTimeout(() => {
  void fs.appendFile(
    path.join(root, "solutions", "account-intelligence", "quest.html"),
    "\\n<!-- deliberate audit TOCTOU mutation -->\\n",
  );
}, 100);`;
      await fs.writeFile(
        temporaryAuditPath,
        replaceOnce(audit, anchor, injected, "audit server base URL"),
      );
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.audited_inputs_unchanged === false
      && report?.results?.[0]?.provenance === false
    ),
  },
  {
    name: "gate-companion-toctou",
    script: temporaryAuditPath,
    apply: async () => {
      const audit = await fs.readFile(auditPath, "utf8");
      const anchor = "const baseUrl = `http://127.0.0.1:${address.port}`;";
      const injected = `${anchor}
setTimeout(() => {
  void fs.appendFile(
    path.join(auditDirectory, "attest.mjs"),
    "\\n// deliberate companion-script TOCTOU mutation\\n",
  );
}, 100);`;
      await fs.writeFile(
        temporaryAuditPath,
        replaceOnce(audit, anchor, injected, "audit server base URL"),
      );
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.audited_inputs_unchanged === false
      && report?.results?.[0]?.provenance === false
    ),
  },
  {
    name: "screenshot-capture-toctou",
    script: temporaryAuditPath,
    apply: async () => {
      const audit = await fs.readFile(auditPath, "utf8");
      const anchor = `    easyCaptureArtifact = await captureContext(
      easyImage,
      path.join(out, easyScreenshotRelative),
      easyScreenshotRelative,
    );`;
      const injected = `${anchor}
    await fs.writeFile(
      path.join(out, easyScreenshotRelative),
      auditedInputContents.get(
        "solutions/account-intelligence/screenshots/assisted/annotated/03-ai-02.png",
      ),
    );`;
      await fs.writeFile(
        temporaryAuditPath,
        replaceOnce(audit, anchor, injected, "Easy screenshot capture"),
      );
    },
    assert: ({ status, report }) => {
      const row = report?.results?.[0];
      return Boolean(
        status !== 0
        && row?.screenshotsBound === false
        && row?.screenshotArtifacts?.[0]?.bytes > 0
        && row?.writtenScreenshotArtifacts?.[0]?.bytes > 0
        && row.screenshotArtifacts[0].sha256
          !== row.writtenScreenshotArtifacts[0].sha256,
      );
    },
  },
  {
    name: "workshop-body-identity",
    apply: async () => {
      const mutated = replaceOnce(
        originalQuest,
        'data-workshop-slug="account-intelligence"',
        'data-workshop-slug="wrong-workshop"',
        "workshop slug",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0 && report?.results?.[0]?.identity?.slug === false
    ),
  },
  {
    name: "live-dom-evidence-swap",
    apply: async () => {
      const script = `
  <script>
    addEventListener("DOMContentLoaded", () => {
      const image = document.querySelector(
        'img[data-evidence-status="reusable"]'
      );
      image.src = ${JSON.stringify(secondImageSource)};
      image.alt = "Mutated evidence substituted after immutable HTML parsing";
    });
  </script>`;
      await fs.writeFile(questPath, injectBody(originalQuest, script));
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.results?.[0]?.questInventoryMatches === false
      && report?.results?.[0]?.completeImageInventory === false
    ),
  },
  {
    name: "aria-tab-linkage",
    apply: async () => {
      const mutated = replaceOnce(
        originalQuest,
        'aria-controls="mode-panel-easy"',
        'aria-controls="missing-panel"',
        "easy aria-controls",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.results?.[0]?.easy?.tabSemantics === false
    ),
  },
  {
    name: "inactive-mode-visible-descendant",
    apply: async () => {
      const css = `
    [data-path="hard"][hidden] {
      display: block !important;
      visibility: hidden !important;
      position: fixed !important;
      inset: 0 !important;
      z-index: 999999 !important;
      pointer-events: none !important;
    }
    [data-path="hard"][hidden] * {
      pointer-events: none !important;
    }
    [data-path="hard"][hidden] .hard-overview {
      display: block !important;
      visibility: visible !important;
      position: fixed !important;
      right: 20px !important;
      bottom: 20px !important;
      width: 320px !important;
      height: 160px !important;
      background: #fff !important;
    }`;
      await fs.writeFile(questPath, injectStyle(originalQuest, css));
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.results?.[0]?.easy?.oppositeHidden === false
      && report?.results?.[0]?.easy?.oppositeRenderedDescendants > 0
    ),
  },
  {
    name: "dynamic-image-inventory",
    apply: async () => {
      const script = `
  <script>
    document.querySelector('[data-mode="hard"]').addEventListener("click", () => {
      const panel = document.querySelector('[data-path="hard"]');
      if (panel.querySelector("[data-audit-dynamic-image]")) return;
      const image = document.createElement("img");
      image.dataset.auditDynamicImage = "";
      image.dataset.evidenceStatus = "reusable";
      image.src = "${firstImageSource}";
      image.alt = "Injected inventory mutation";
      panel.appendChild(image);
    });
  </script>`;
      await fs.writeFile(questPath, injectBody(originalQuest, script));
    },
    assert: ({ status, report }) => (
      status !== 0 && report?.results?.[0]?.dynamicImageInventory === false
    ),
  },
  {
    name: "dynamic-resource-outside-snapshot",
    apply: async () => {
      const script = `
  <script>
    const resource = document.createElement("script");
    resource.src = "audit-unmanifested-resource.js";
    document.head.appendChild(resource);
  </script>`;
      await fs.writeFile(questPath, injectBody(originalQuest, script));
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.immutable_snapshot_complete === false
      && report?.rejected_snapshot_requests?.some(
        (request) => request.endsWith("audit-unmanifested-resource.js"),
      )
    ),
  },
  {
    name: "external-script-request",
    apply: async () => {
      await fs.writeFile(
        questPath,
        injectBody(
          originalQuest,
          '  <script src="https://audit.invalid/external-script.js"></script>',
        ),
      );
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.immutable_snapshot_complete === false
      && report?.rejected_external_requests?.some(
        (request) => request === "https://audit.invalid/external-script.js",
      )
    ),
  },
  {
    name: "external-stylesheet-request",
    apply: async () => {
      const markup = (
        '  <link rel="stylesheet" href="https://audit.invalid/external-style.css">'
      );
      await fs.writeFile(
        questPath,
        replaceOnce(originalQuest, "</head>", `${markup}\n</head>`, "head close"),
      );
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.immutable_snapshot_complete === false
      && report?.rejected_external_requests?.some(
        (request) => request === "https://audit.invalid/external-style.css",
      )
    ),
  },
  {
    name: "external-fetch-request",
    apply: async () => {
      const script = `
  <script>
    fetch("https://audit.invalid/external-fetch.json").catch(() => {});
  </script>`;
      await fs.writeFile(questPath, injectBody(originalQuest, script));
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.immutable_snapshot_complete === false
      && report?.rejected_external_requests?.some(
        (request) => request === "https://audit.invalid/external-fetch.json",
      )
    ),
  },
  {
    name: "external-srcset-request",
    apply: async () => {
      const mutated = replaceOnce(
        originalQuest,
        `src="${firstImageSource}"`,
        `src="${firstImageSource}" srcset="https://audit.invalid/external-evidence.png 1x"`,
        "first reusable image source",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.immutable_snapshot_complete === false
      && report?.rejected_external_requests?.some(
        (request) => request === "https://audit.invalid/external-evidence.png",
      )
      && report?.results?.[0]?.expectedQuestInventory?.valid === false
    ),
  },
  {
    name: "external-websocket-request",
    apply: async () => {
      const script = `
  <script>
    (() => {
      const socket = new WebSocket("wss://audit.invalid/socket");
      socket.addEventListener("error", () => {});
    })();
  </script>`;
      await fs.writeFile(questPath, injectBody(originalQuest, script));
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.immutable_snapshot_complete === false
      && report?.rejected_websocket_requests?.some(
        (request) => request === "wss://audit.invalid/socket",
      )
    ),
  },
  {
    name: "service-worker-synthetic-resource",
    apply: async () => {
      await fs.writeFile(
        temporaryServiceWorkerPath,
        `self.addEventListener("fetch", (event) => {
  if (new URL(event.request.url).pathname.endsWith("/audit-sw-synthetic")) {
    event.respondWith(new Response("synthetic service-worker response"));
  }
});
`,
      );
      const preload = (
        '  <link rel="preload" href="audit-service-worker.js" as="script">'
      );
      const script = `
  <script>
    navigator.serviceWorker.register("audit-service-worker.js")
      .then(() => navigator.serviceWorker.ready)
      .then(() => fetch("audit-sw-synthetic"))
      .then((response) => response.text())
      .then((value) => { window.__auditServiceWorkerValue = value; })
      .catch((error) => {
        console.error("Service worker registration blocked:", error.message);
      });
  </script>`;
      const withPreload = replaceOnce(
        originalQuest,
        "</head>",
        `${preload}\n</head>`,
        "head close",
      );
      await fs.writeFile(questPath, injectBody(withPreload, script));
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.service_workers_policy === "block"
      && report?.observed_service_workers?.length === 0
      && report?.results?.[0]?.serviceWorkerAttempts?.some(
        (attempt) => attempt.scriptURL === "audit-service-worker.js",
      )
    ),
  },
  {
    name: "transparent-image-content",
    apply: async () => {
      const transparentSvg = "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='1424'%20height='863'%3E%3C/svg%3E";
      const mutated = replaceOnce(
        originalQuest,
        `src="${firstImageSource}"`,
        `src="${transparentSvg}"`,
        "first reusable image source",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.pixelEvidence?.opaqueRatio === 0,
      )
    ),
  },
  {
    name: "blank-image-content",
    apply: async () => {
      const blankSvg = "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='1424'%20height='863'%3E%3Crect%20width='100%25'%20height='100%25'%20fill='%23ffffff'/%3E%3C/svg%3E";
      const mutated = replaceOnce(
        originalQuest,
        `src="${firstImageSource}"`,
        `src="${blankSvg}"`,
        "first reusable image source",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.pixelEvidence?.opaqueRatio === 1
          && image.pixelEvidence?.meaningful === false,
      )
    ),
  },
  {
    name: "mostly-transparent-image-content",
    apply: async () => {
      const sparseSvg = "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='1424'%20height='863'%3E%3Crect%20width='5%25'%20height='50%25'%20fill='%23ff0000'/%3E%3Crect%20x='5%25'%20width='5%25'%20height='50%25'%20fill='%2300ff00'/%3E%3Crect%20x='10%25'%20width='5%25'%20height='50%25'%20fill='%230000ff'/%3E%3Crect%20x='15%25'%20width='5%25'%20height='50%25'%20fill='%23ffff00'/%3E%3C/svg%3E";
      const mutated = replaceOnce(
        originalQuest,
        `src="${firstImageSource}"`,
        `src="${sparseSvg}"`,
        "first reusable image source",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.pixelEvidence?.opaqueRatio < 0.8
          && image.pixelEvidence?.quantizedColors >= 4,
      )
    ),
  },
  {
    name: "mostly-blank-image-content",
    apply: async () => {
      const sparseSvg = "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='1424'%20height='863'%3E%3Crect%20width='100%25'%20height='100%25'%20fill='%23ffffff'/%3E%3Crect%20width='5%25'%20height='20%25'%20fill='%23ff0000'/%3E%3Crect%20x='5%25'%20width='5%25'%20height='20%25'%20fill='%2300ff00'/%3E%3Crect%20x='10%25'%20width='5%25'%20height='20%25'%20fill='%230000ff'/%3E%3Crect%20x='15%25'%20width='5%25'%20height='20%25'%20fill='%23ffff00'/%3E%3C/svg%3E";
      const mutated = replaceOnce(
        originalQuest,
        `src="${firstImageSource}"`,
        `src="${sparseSvg}"`,
        "first reusable image source",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.pixelEvidence?.opaqueRatio === 1
          && image.pixelEvidence?.detailedTiles < 3
          && image.pixelEvidence?.quantizedColors >= 4,
      )
    ),
  },
  {
    name: "segmented-mostly-blank-boundary",
    apply: async () => {
      const colors = [
        "#ff0000", "#00ff00", "#0000ff", "#ffff00",
        "#ff00ff", "#00ffff", "#880000", "#008800",
        "#000088", "#888800", "#880088", "#008888",
        "#ff8800", "#88ff00", "#0088ff", "#ff0088",
      ];
      const stripes = colors.map((color, index) => (
        `<rect x="${index * 6.25}%" y="0" width="6.25%" height="25%" fill="${color}"/>`
      )).join("");
      const svg = encodeURIComponent(
        `<svg xmlns="http://www.w3.org/2000/svg" width="1424" height="863">`
        + '<rect width="100%" height="100%" fill="#ffffff"/>'
        + stripes
        + "</svg>",
      );
      const mutated = replaceOnce(
        originalQuest,
        `src="${firstImageSource}"`,
        `src="data:image/svg+xml,${svg}"`,
        "first reusable image source",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.pixelEvidence?.quantizedColors >= 8
          && image.pixelEvidence?.detailedTiles >= 3
          && image.pixelEvidence?.foregroundTiles < 5
          && image.pixelEvidence?.meaningful === false,
      )
    ),
  },
  {
    name: "five-tile-sparse-noise",
    apply: async () => {
      const colors = [
        "#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff",
        "#00ffff", "#880000", "#008800", "#000088", "#888800",
        "#880088", "#008888", "#ff8800", "#88ff00", "#0088ff",
      ];
      const origins = [[1, 1], [17, 1], [33, 1], [49, 1], [1, 17]];
      const pixels = origins.flatMap(([originX, originY], originIndex) => (
        Array.from({ length: 25 }, (_value, index) => {
          const x = originX + (index % 5);
          const y = originY + Math.floor(index / 5);
          const color = colors[(originIndex * 5 + index) % colors.length];
          return `<rect x="${x}" y="${y}" width="1" height="1" fill="${color}"/>`;
        })
      )).join("");
      const svg = encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1424" height="863" '
        + 'viewBox="0 0 64 64" preserveAspectRatio="none">'
        + '<rect width="64" height="64" fill="#ffffff"/>'
        + pixels
        + "</svg>",
      );
      const mutated = replaceOnce(
        originalQuest,
        `src="${firstImageSource}"`,
        `src="data:image/svg+xml,${svg}"`,
        "first reusable image source",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.pixelEvidence?.foregroundRatio >= 0.024
          && image.pixelEvidence?.foregroundTiles >= 5
          && image.pixelEvidence?.edgeTiles < 8
          && image.pixelEvidence?.meaningful === false,
      )
    ),
  },
  {
    name: "eight-tile-isolated-noise",
    apply: async () => {
      const colors = [
        "#ff0000", "#00ff00", "#0000ff", "#ffff00",
        "#ff00ff", "#00ffff", "#880000", "#008800",
        "#000088", "#888800", "#880088", "#008888",
        "#ff8800", "#88ff00", "#0088ff", "#ff0088",
      ];
      const origins = [
        [0, 0], [16, 0], [32, 0], [48, 0],
        [0, 16], [16, 16], [32, 32], [48, 32],
      ];
      const offsets = [
        [1, 1], [4, 1], [7, 1], [10, 1], [13, 1],
        [1, 4], [4, 4], [7, 4], [10, 4], [13, 4],
        [1, 7], [4, 7], [7, 7],
      ];
      const pixels = origins.flatMap(([originX, originY], originIndex) => (
        offsets.map(([xOffset, yOffset], pixelIndex) => {
          const color = colors[(originIndex + pixelIndex) % colors.length];
          return (
            `<rect x="${originX + xOffset}" y="${originY + yOffset}" `
            + `width="1" height="1" fill="${color}"/>`
          );
        })
      )).join("");
      const svg = encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1424" height="863" '
        + 'viewBox="0 0 64 64" preserveAspectRatio="none">'
        + '<rect width="64" height="64" fill="#ffffff"/>'
        + pixels
        + "</svg>",
      );
      const mutated = replaceOnce(
        originalQuest,
        `src="${firstImageSource}"`,
        `src="data:image/svg+xml,${svg}"`,
        "first reusable image source",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.pixelEvidence?.foregroundRatio >= 0.024
          && image.pixelEvidence?.edgeTiles >= 8
          && image.pixelEvidence?.edgeRows >= 3
          && image.pixelEvidence?.edgeColumns >= 4
          && (
            image.pixelEvidence?.structuredForegroundRatio < 0.0195
            || image.pixelEvidence?.dominantColorRatio > 0.973
          )
          && image.pixelEvidence?.meaningful === false,
      )
    ),
  },
  {
    name: "eight-tile-connected-diagonal-noise",
    apply: async () => {
      const colors = [
        "#ff0000", "#00ff00", "#0000ff", "#ffff00",
        "#ff00ff", "#00ffff", "#880000", "#008800",
        "#000088", "#888800", "#880088", "#008888",
        "#ff8800", "#88ff00", "#0088ff", "#ff0088",
      ];
      const origins = [
        [0, 0], [16, 0], [32, 0], [48, 0],
        [0, 16], [16, 16], [32, 32], [48, 32],
      ];
      const largeCluster = Array.from(
        { length: 25 },
        (_value, index) => [index % 5, Math.floor(index / 5)],
      ).filter(([x, y]) => !(
        (x === 0 || x === 4)
        && (y === 0 || y === 4)
      ));
      const diagonalCluster = [
        [0, 0], [1, 0], [0, 1], [1, 1],
        [2, 1], [1, 2], [2, 2],
        [3, 2], [2, 3], [3, 3],
        [4, 3], [3, 4], [4, 4], [4, 2],
      ];
      const pixels = origins.flatMap(([originX, originY], originIndex) => {
        const cluster = originIndex === 0 ? largeCluster : diagonalCluster;
        return cluster.map(([xOffset, yOffset], pixelIndex) => {
          const color = colors[(originIndex + pixelIndex) % colors.length];
          return (
            `<rect x="${originX + xOffset + 1}" y="${originY + yOffset + 1}" `
            + `width="1" height="1" fill="${color}"/>`
          );
        });
      }).join("");
      const svg = encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1424" height="863" '
        + 'viewBox="0 0 64 64" preserveAspectRatio="none">'
        + '<rect width="64" height="64" fill="#ffffff"/>'
        + pixels
        + "</svg>",
      );
      const mutated = replaceOnce(
        originalQuest,
        `src="${firstImageSource}"`,
        `src="data:image/svg+xml,${svg}"`,
        "first reusable image source",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.pixelEvidence?.dominantColorRatio <= 0.973
          && image.pixelEvidence?.structuredForegroundRatio >= 0.0195
          && image.pixelEvidence?.largestForegroundComponentRatio >= 0.005
          && image.pixelEvidence?.edgeTiles >= 8
          && image.pixelEvidence?.maxTwoDimensionalComponentArea < 28
          && image.pixelEvidence?.meaningful === false,
      )
    ),
  },
  {
    name: "inherited-opacity",
    apply: async () => {
      await fs.writeFile(
        questPath,
        injectStyle(originalQuest, "    .preview-shot-wrap { opacity: .1 !important; }"),
      );
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some((image) => image.effectiveOpacity < 0.5)
    ),
  },
  {
    name: "css-filter",
    apply: async () => {
      await fs.writeFile(
        questPath,
        injectStyle(originalQuest, "    .preview-shot { filter: blur(1px) !important; }"),
      );
    },
    assert: ({ status, report }) => (
      status !== 0 && allImageFailures(report).some((image) => image.filtered)
    ),
  },
  {
    name: "css-mask",
    apply: async () => {
      await fs.writeFile(
        questPath,
        injectStyle(
          originalQuest,
          "    .preview-shot { mask-image: linear-gradient(#000, #000) !important; }",
        ),
      );
    },
    assert: ({ status, report }) => (
      status !== 0 && allImageFailures(report).some((image) => image.masked)
    ),
  },
  {
    name: "stylesheet-individual-transform",
    apply: async () => {
      await fs.writeFile(
        questPath,
        injectStyle(originalQuest, "    img { rotate: 180deg !important; }"),
      );
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.renderedPixelMatch?.isolationComparison?.matches === true
          && image.renderedPixelMatch?.sourceComparison?.matches === false,
      )
    ),
  },
  {
    name: "object-position-rendered-blank",
    apply: async () => {
      const css = `
    .preview-shot,
    .shot {
      object-fit: none !important;
      object-position: 10000px 10000px !important;
      background: #fff !important;
    }`;
      await fs.writeFile(questPath, injectStyle(originalQuest, css));
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.renderedPixelMatch?.isolatedPixelEvidence?.meaningful === false
          || image.renderedPixelMatch?.sourceComparison?.matches === false,
      )
    ),
  },
  {
    name: "mix-blend-rendering",
    apply: async () => {
      const css = `
    .preview-shot-wrap,
    .shot-link { background: #fff !important; }
    .preview-shot,
    .shot { mix-blend-mode: difference !important; }`;
      await fs.writeFile(questPath, injectStyle(originalQuest, css));
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.renderedPixelMatch?.sourceComparison?.matches === false,
      )
    ),
  },
  {
    name: "cross-mode-content-alias",
    apply: async () => {
      const mutated = replaceOnce(
        originalQuest,
        `src="${firstHardImageSource}"`,
        `src="${firstImageSource}?hard-alias"`,
        "first Hard reusable image source",
      );
      await fs.writeFile(questPath, mutated);
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.results?.[0]?.sourceOverlap?.length === 0
      && report?.results?.[0]?.contentOverlap?.length > 0
      && report?.results?.[0]?.distinctModes === false
    ),
  },
  {
    name: "cross-mode-decoded-visual-alias",
    apply: async () => {
      const easySource = await fs.readFile(firstImagePath);
      await fs.writeFile(firstHardImagePath, addPngTextChunk(easySource));
    },
    assert: ({ status, report }) => (
      status !== 0
      && report?.results?.[0]?.contentOverlap?.length === 0
      && report?.results?.[0]?.visualOverlap?.some(
        (overlap) => overlap.decodedPixelsEqual === true,
      )
      && report?.results?.[0]?.distinctModes === false
    ),
  },
  {
    name: "offscreen-owner-pseudo-overlay",
    apply: async () => {
      const css = `
    #audit-offscreen-owner {
      position: absolute;
      left: -10000px;
      top: -10000px;
      width: 1px;
      height: 1px;
      pointer-events: none;
    }
    #audit-offscreen-owner::after {
      content: "";
      position: fixed;
      inset: 0;
      z-index: 999999;
      background: rgba(255, 255, 255, .95);
      pointer-events: none;
    }`;
      const withStyle = injectStyle(originalQuest, css);
      await fs.writeFile(
        questPath,
        injectBody(withStyle, '  <div id="audit-offscreen-owner"></div>'),
      );
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some((image) => image.unobscuredRatio < 1)
    ),
  },
  {
    name: "center-sample-pseudo-overlay",
    apply: async () => {
      const css = `
    body::after {
      content: "";
      position: fixed;
      left: calc(50vw - 50px);
      top: calc(50vh - 50px);
      width: 100px;
      height: 100px;
      z-index: 999999;
      background: rgba(255, 255, 255, .95);
      pointer-events: none;
    }`;
      await fs.writeFile(questPath, injectStyle(originalQuest, css));
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.unobscuredRatio > 0 && image.unobscuredRatio < 1,
      )
    ),
  },
  {
    name: "off-sample-band-pseudo-overlay",
    apply: async () => {
      const css = `
    .preview-shot-wrap > a,
    .shot-link { position: relative; }
    .preview-shot-wrap > a::after,
    .shot-link::after {
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      top: 7%;
      height: 4%;
      z-index: 999999;
      background: rgba(255, 255, 255, .95);
      pointer-events: none;
    }`;
      await fs.writeFile(questPath, injectStyle(originalQuest, css));
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.legacyFiveUnobscuredRatio === 1
          && image.unobscuredRatio === 1
          && image.renderedPixelMatch?.matches === false,
      )
    ),
  },
  {
    name: "offscreen-visible-pseudo-band",
    apply: async () => {
      const css = `
    #audit-visible-pseudo-owner {
      position: absolute;
      left: -10000px;
      top: -10000px;
      width: 1px;
      height: 1px;
      pointer-events: none;
    }
    #audit-visible-pseudo-owner::after {
      content: "";
      position: fixed;
      left: var(--audit-band-left, -10000px);
      top: var(--audit-band-top, -10000px);
      width: var(--audit-band-width, 1px);
      height: var(--audit-band-height, 1px);
      z-index: 999999;
      visibility: visible !important;
      opacity: 1 !important;
      background: rgba(255, 255, 255, .95);
      pointer-events: none;
    }`;
      const script = `
  <div id="audit-visible-pseudo-owner"></div>
  <script>
    (() => {
      const owner = document.querySelector("#audit-visible-pseudo-owner");
      const update = () => {
        const images = [...document.querySelectorAll(
          '[role="tabpanel"]:not([hidden]) img[data-evidence-status="reusable"]'
        )];
        const image = images
          .map((candidate) => ({ candidate, rect: candidate.getBoundingClientRect() }))
          .filter(({ rect }) => rect.bottom > 0 && rect.top < innerHeight)
          .sort((left, right) => (
            Math.abs((left.rect.top + left.rect.bottom) / 2 - innerHeight / 2)
            - Math.abs((right.rect.top + right.rect.bottom) / 2 - innerHeight / 2)
          ))[0];
        if (!image) return;
        owner.style.setProperty("--audit-band-left", image.rect.left + "px");
        owner.style.setProperty(
          "--audit-band-top",
          (image.rect.top + image.rect.height * .07) + "px"
        );
        owner.style.setProperty("--audit-band-width", image.rect.width + "px");
        owner.style.setProperty("--audit-band-height", (image.rect.height * .04) + "px");
      };
      addEventListener("scroll", update, { passive: true });
      addEventListener("resize", update, { passive: true });
      requestAnimationFrame(update);
    })();
  </script>`;
      await fs.writeFile(
        questPath,
        injectBody(injectStyle(originalQuest, css), script),
      );
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.legacyFiveUnobscuredRatio === 1
          && image.unobscuredRatio === 1
          && image.renderedPixelMatch?.isolationComparison?.matches === false,
      )
    ),
  },
  {
    name: "pseudo-box-shadow-overlay",
    apply: async () => {
      const css = `
    .preview-shot-wrap { position: relative; }
    .preview-shot-wrap::after {
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      top: 9.5%;
      height: 1px;
      z-index: 999999;
      color: transparent;
      background: transparent;
      box-shadow: 0 0 0 6px rgba(255, 255, 255, .95);
      pointer-events: none;
    }`;
      await fs.writeFile(questPath, injectStyle(originalQuest, css));
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some(
        (image) => image.renderedPixelMatch?.matches === false,
      )
    ),
  },
  {
    name: "ancestor-clipping",
    apply: async () => {
      await fs.writeFile(
        questPath,
        injectStyle(
          originalQuest,
          "    .preview-shot-wrap { height: 100px !important; overflow: hidden !important; }",
        ),
      );
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some((image) => image.clippedBy.length > 0)
    ),
  },
  {
    name: "undersized-evidence",
    apply: async () => {
      await fs.writeFile(
        questPath,
        injectStyle(originalQuest, "    .preview-shot { width: 200px !important; }"),
      );
    },
    assert: ({ status, report }) => (
      status !== 0
      && allImageFailures(report).some((image) => image.width < 640)
    ),
  },
];

const requestedMutation = process.env.MUTATION_ONLY || "";
const selectedMutations = requestedMutation
  ? mutations.filter((mutation) => mutation.name === requestedMutation)
  : mutations;
if (requestedMutation && selectedMutations.length !== 1) {
  throw new Error(`Unknown mutation: ${requestedMutation}`);
}
const mutationContractNames = mutations.map((mutation) => mutation.name);
const mutationContractSha256 = sha256(
  Buffer.from(`${JSON.stringify(mutationContractNames)}\n`),
);
const releaseEligible = Boolean(
  !requestedMutation
  && selectedMutations.length === mutationContractNames.length
);

const results = [];
try {
  for (const mutation of selectedMutations) {
    await restoreTrackedFiles();
    await fs.rm(temporaryAuditPath, { force: true });
    await mutation.apply();
    const run = await runAudit(mutation.script || auditPath);
    if (run.report) {
      const reportsOut = path.join(mutationOut, "reports");
      await fs.mkdir(reportsOut, { recursive: true });
      await fs.writeFile(
        path.join(reportsOut, `${mutation.name}.json`),
        `${JSON.stringify(run.report, null, 2)}\n`,
      );
    }
    const passed = Boolean(mutation.assert(run));
    results.push({
      name: mutation.name,
      passed,
      exit_status: run.status,
      signal: run.signal,
      audit_failed: run.report ? run.report.failed > 0 : null,
      stdout: sanitizeOutput(run.stdout.trim()),
      stderr: sanitizeOutput(run.stderr.trim()),
    });
    if (!passed) break;
  }
} finally {
  await restoreTrackedFiles();
  await fs.rm(temporaryAuditPath, { force: true });
}

const baseline = await runAudit();
const baselinePassed = Boolean(
  baseline.status === 0
  && baseline.report?.total === 1
  && baseline.report?.passed === 1
  && baseline.report?.failed === 0
);
const [
  auditScriptSource,
  mutationScriptSource,
  attestationScriptSource,
  baselineReportSource,
  baselineManifestSource,
] = await Promise.all([
  fs.readFile(auditPath),
  fs.readFile(mutationScriptPath),
  fs.readFile(attestationPath),
  fs.readFile(reportPath),
  fs.readFile(path.join(mutationOut, "audited-snapshot-manifest.json")),
]);
const summary = {
  schema: "aibast-browser-audit-mutations/1.10",
  total: selectedMutations.length,
  passed: results.filter((row) => row.passed).length,
  failed: selectedMutations.length - results.filter((row) => row.passed).length,
  baseline_restored: baselinePassed,
  mutation_names: selectedMutations.map((mutation) => mutation.name),
  release_eligible: releaseEligible,
  mutation_contract_sha256: mutationContractSha256,
  baseline_audited_inputs_sha256: baseline.report?.audited_inputs?.sha256 || null,
  execution_environment: baseline.report?.execution_environment || null,
  bindings: {
    audit_script_sha256: sha256(auditScriptSource),
    mutation_script_sha256: sha256(mutationScriptSource),
    attestation_script_sha256: sha256(attestationScriptSource),
    baseline_report_sha256: sha256(baselineReportSource),
    baseline_manifest_sha256: sha256(baselineManifestSource),
  },
  results,
};
const summaryPath = releaseEligible
  ? mutationReportPath
  : path.join(mutationOut, `partial-${requestedMutation}.json`);
await fs.writeFile(
  summaryPath,
  `${JSON.stringify(summary, null, 2)}\n`,
);
console.log(JSON.stringify({
  total: summary.total,
  passed: summary.passed,
  failed: summary.failed,
  baseline_restored: summary.baseline_restored,
}));
process.exit(summary.failed || !summary.baseline_restored ? 1 : 0);
