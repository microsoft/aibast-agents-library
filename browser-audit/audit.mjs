import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const auditDirectory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(
  process.env.AIBAST_REPO_ROOT
  || execFileSync(
    "git",
    ["-C", auditDirectory, "rev-parse", "--show-toplevel"],
    { encoding: "utf8" },
  ).trim(),
);
const out = process.env.AUDIT_OUT
  || auditDirectory;
const certificationOutputPaths = new Set([
  "browser-audit/audited-snapshot-manifest.json",
  "browser-audit/browser-audit.json",
  "browser-audit/browser-certification-attestation.json",
  "browser-audit/easy-contact-sheet.jpg",
  "browser-audit/hard-contact-sheet.jpg",
  "browser-audit/mutation-suite.json",
]);

function certificationInputGitStatus(rawStatus) {
  const isCertificationOutput = (candidate) => (
    certificationOutputPaths.has(candidate)
    || candidate.startsWith("browser-audit/screenshots/")
  );
  const lines = rawStatus.split("\n");
  return lines
    .filter(Boolean)
    .filter((line) => {
      const rawPath = line.slice(3);
      const candidates = rawPath
        .split(" -> ")
        .map((candidate) => candidate.replace(/^"|"$/g, ""));
      return !candidates.every(isCertificationOutput);
    })
    .map((line) => `${line}\n`)
    .join("");
}
const registrySource = await fs.readFile(path.join(root, "registry.json"));
const catalogSource = await fs.readFile(path.join(root, "solutions", "catalog.json"));
const registry = JSON.parse(registrySource.toString("utf8"));
const solutionCatalog = JSON.parse(catalogSource.toString("utf8"));
const auditedSeedContents = new Map([
  ["registry.json", registrySource],
  ["solutions/catalog.json", catalogSource],
]);
const gitSha = execFileSync(
  "git",
  ["-C", root, "rev-parse", "HEAD"],
  { encoding: "utf8" },
).trim();
const advertisedNames = Object.keys(solutionCatalog.solutions || {});
const registrySolutions = registry.agents.filter((agent) => agent?._solution);
const registryByName = new Map();
for (const agent of registrySolutions) {
  if (!agent.name || registryByName.has(agent.name)) {
    throw new Error(`Invalid or duplicate registry solution name: ${agent.name}`);
  }
  registryByName.set(agent.name, agent);
}
const catalogPackages = advertisedNames.map((name) => {
  const agent = registryByName.get(name);
  const pkg = agent?._solution?.package;
  const catalogEntry = solutionCatalog.solutions?.[name];
  if (!pkg?.slug) throw new Error(`Advertised solution has no package slug: ${name}`);
  if (!String(catalogEntry?.display_name || "").trim()) {
    throw new Error(`Advertised solution has no catalog display name: ${name}`);
  }
  const expectedQuestUrl = `solutions/${pkg.slug}/quest.html`;
  if (pkg.quest_url !== expectedQuestUrl) {
    throw new Error(`Registry quest URL mismatch for ${pkg.slug}`);
  }
  return {
    ...pkg,
    catalog_name: name,
    catalog_display_name: catalogEntry.display_name,
  };
});
const catalogSlugs = [...new Set(catalogPackages.map((pkg) => pkg.slug))].sort();
const catalogBySlug = new Map(
  catalogPackages.map((pkg) => [pkg.slug, pkg]),
);
const excludedNonAdvertised = [];
for (const [name, agent] of registryByName) {
  if (advertisedNames.includes(name)) continue;
  const slug = agent?._solution?.package?.slug;
  const relative = path.join("tests", "demo_cases", `${slug}.json`);
  const source = await fs.readFile(path.join(root, relative));
  auditedSeedContents.set(relative, source);
  const demoCase = JSON.parse(source.toString("utf8"));
  const status = String(demoCase.status || "");
  const distribution = demoCase.distribution;
  if (
    distribution?.sharepoint_advertised !== false
    || distribution?.ship_gate !== "advertise-before-ship"
  ) {
    throw new Error(`Registry-only solution lacks exclusion proof: ${slug}`);
  }
  excludedNonAdvertised.push({ slug, status });
}
const requestedSlug = process.env.AUDIT_SLUG || "";
const slugs = requestedSlug
  ? catalogSlugs.filter((slug) => slug === requestedSlug)
  : catalogSlugs;

if (advertisedNames.length !== 51 || catalogSlugs.length !== 51) {
  throw new Error(`Expected 51 catalog workshops, found ${catalogSlugs.length}`);
}
if (requestedSlug && slugs.length !== 1) {
  throw new Error(`Unknown workshop slug: ${requestedSlug}`);
}

const resolvedRoot = path.resolve(root);

function digestBuffers(contents, gateScripts) {
  const digest = createHash("sha256");
  let bytes = 0;
  for (const [relative, content] of [...contents.entries()].sort(
    ([left], [right]) => left.localeCompare(right),
  )) {
    bytes += content.length;
    digest.update(relative);
    digest.update("\0");
    digest.update(String(content.length));
    digest.update("\0");
    digest.update(content);
    digest.update("\0");
  }
  for (const [label, source] of [...gateScripts.entries()].sort(
    ([left], [right]) => left.localeCompare(right),
  )) {
    bytes += source.length;
    digest.update(label);
    digest.update("\0");
    digest.update(String(source.length));
    digest.update("\0");
    digest.update(source);
    digest.update("\0");
  }
  return {
    sha256: digest.digest("hex"),
    files: contents.size + gateScripts.size,
    bytes,
  };
}

async function readGateScripts() {
  return new Map(await Promise.all([
    ["gate:audit.mjs", fileURLToPath(import.meta.url)],
    ["gate:mutation-suite.mjs", path.join(auditDirectory, "mutation-suite.mjs")],
    ["gate:attest.mjs", path.join(auditDirectory, "attest.mjs")],
  ].map(async ([label, file]) => [label, await fs.readFile(file)])));
}

async function captureAuditedInputs() {
  const contents = new Map(auditedSeedContents);
  const discoverFetchedResources = (html) => {
    const resources = new Set();
    const add = (value) => {
      const candidate = String(value || "").trim();
      if (
        !candidate
        || candidate.startsWith("#")
        || /^(?:data:|https?:|\/\/|javascript:|mailto:|tel:)/i.test(candidate)
      ) {
        return;
      }
      resources.add(candidate.split(/[?#]/, 1)[0]);
    };
    for (const match of html.matchAll(
      /<(img|script|iframe|source|video|audio|track|embed|object|input|link)\b[^>]*>/gi,
    )) {
      const tag = match[1].toLowerCase();
      const markup = match[0];
      for (const attribute of markup.matchAll(
        /\b(src|poster|data|href|srcset)="([^"]+)"/gi,
      )) {
        const name = attribute[1].toLowerCase();
        if (name === "href" && tag !== "link") continue;
        if (name === "srcset") {
          for (const entry of attribute[2].split(",")) {
            add(entry.trim().split(/\s+/, 1)[0]);
          }
        } else {
          add(attribute[2]);
        }
      }
    }
    for (const styleBlock of html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)) {
      for (const match of styleBlock[1].matchAll(
        /url\(\s*(['"]?)([^'")]+)\1\s*\)/gi,
      )) {
        add(match[2]);
      }
    }
    return resources;
  };
  for (const slug of catalogSlugs) {
    const packageRoot = path.join(root, "solutions", slug);
    const questPath = path.join(packageRoot, "quest.html");
    const questRelative = path.relative(root, questPath);
    const deploymentRelative = path.join("solutions", slug, "deployment.json");
    const [questSource, deploymentSource] = await Promise.all([
      fs.readFile(questPath),
      fs.readFile(path.join(root, deploymentRelative)),
    ]);
    contents.set(questRelative, questSource);
    contents.set(deploymentRelative, deploymentSource);
    const quest = questSource.toString("utf8");
    for (const source of discoverFetchedResources(quest)) {
      const target = path.resolve(packageRoot, source);
      if (target.startsWith(`${resolvedRoot}${path.sep}`)) {
        const relative = path.relative(root, target);
        if (!contents.has(relative)) {
          contents.set(relative, await fs.readFile(target));
        }
      }
    }
  }
  const gateScripts = await readGateScripts();
  const summary = digestBuffers(contents, gateScripts);
  const manifest = [
    ...[...contents.entries()].map(([relative, content]) => ({
      path: relative,
      bytes: content.length,
      sha256: createHash("sha256").update(content).digest("hex"),
    })),
    ...[...gateScripts.entries()].map(([label, source]) => ({
      path: label,
      bytes: source.length,
      sha256: createHash("sha256").update(source).digest("hex"),
    })),
  ].sort((left, right) => left.path.localeCompare(right.path));
  const manifestJson = `${JSON.stringify({
    schema: "aibast-browser-audit-snapshot/1.0",
    aggregate_sha256: summary.sha256,
    files: summary.files,
    bytes: summary.bytes,
    entries: manifest,
  }, null, 2)}\n`;
  return {
    contents,
    relativePaths: [...contents.keys()].sort(),
    manifestJson,
    manifestSha256: createHash("sha256").update(manifestJson).digest("hex"),
    summary,
  };
}

async function digestCurrentAuditedInputs(relativePaths) {
  const contents = new Map();
  const errors = [];
  for (const relative of relativePaths) {
    try {
      contents.set(relative, await fs.readFile(path.join(root, relative)));
    } catch (error) {
      errors.push(`${relative}: ${error.code || error.message}`);
      contents.set(relative, Buffer.from(`AUDIT_READ_ERROR:${error.code || error.message}`));
    }
  }
  let gateScripts;
  try {
    gateScripts = await readGateScripts();
  } catch (error) {
    errors.push(`gate scripts: ${error.code || error.message}`);
    gateScripts = new Map([
      ["gate:read-error", Buffer.from(`AUDIT_READ_ERROR:${error.code || error.message}`)],
    ]);
  }
  return {
    ...digestBuffers(contents, gateScripts),
    errors,
  };
}

const auditedInputSnapshot = await captureAuditedInputs();
const auditedInputs = auditedInputSnapshot.summary;
const auditedInputContents = auditedInputSnapshot.contents;
const initialCurrentInputs = await digestCurrentAuditedInputs(
  auditedInputSnapshot.relativePaths,
);
if (
  initialCurrentInputs.errors.length
  || initialCurrentInputs.sha256 !== auditedInputs.sha256
) {
  throw new Error("Audited inputs changed while the immutable snapshot was created");
}
const gitStatus = certificationInputGitStatus(execFileSync(
  "git",
  ["-C", root, "status", "--porcelain=v1"],
  { encoding: "utf8" },
));
const gitStatusSha256 = createHash("sha256").update(gitStatus).digest("hex");

const mimeTypes = new Map([
  [".css", "text/css; charset=utf-8"],
  [".gif", "image/gif"],
  [".html", "text/html; charset=utf-8"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".md", "text/markdown; charset=utf-8"],
  [".png", "image/png"],
  [".svg", "image/svg+xml"],
  [".zip", "application/zip"],
]);
const rejectedSnapshotRequests = new Set();
const server = http.createServer(async (request, response) => {
  try {
    const requestUrl = new URL(request.url || "/", "http://127.0.0.1");
    const relative = decodeURIComponent(requestUrl.pathname).replace(/^\/+/, "");
    let target = path.resolve(resolvedRoot, relative || "index.html");
    if (target !== resolvedRoot && !target.startsWith(`${resolvedRoot}${path.sep}`)) {
      response.writeHead(403).end("Forbidden");
      return;
    }
    let relativeTarget = path.relative(resolvedRoot, target);
    let body = auditedInputContents.get(relativeTarget);
    if (!body) {
      rejectedSnapshotRequests.add(relativeTarget);
      response.writeHead(409, {
        "content-type": "text/plain; charset=utf-8",
        "cache-control": "no-store",
      }).end("Resource is outside the immutable browser-audit snapshot");
      return;
    }
    response.writeHead(200, {
      "content-type": mimeTypes.get(path.extname(target).toLowerCase())
        || "application/octet-stream",
      "cache-control": "no-store",
      "x-aibast-audit-sha": gitSha,
      "x-aibast-audit-inputs": auditedInputs.sha256,
    });
    if (request.method !== "HEAD") response.end(body);
    else response.end();
  } catch (_error) {
    response.writeHead(404).end("Not found");
  }
});
await new Promise((resolve, reject) => {
  server.once("error", reject);
  server.listen(0, "127.0.0.1", resolve);
});
const address = server.address();
if (!address || typeof address === "string") throw new Error("Audit server failed to bind");
const baseUrl = `http://127.0.0.1:${address.port}`;

const inventorySignature = (rows) => JSON.stringify(rows.map((row) => ({
  rawSrc: row.rawSrc,
  canonicalPath: row.canonicalPath,
  alt: row.alt,
  status: row.status,
  mode: row.mode,
  checkpointId: row.checkpointId,
  srcset: row.srcset,
  sizes: row.sizes,
  pictureSources: row.pictureSources,
})));

function visualIdentityOverlap(easyImages, hardImages) {
  const overlaps = [];
  for (const easyImage of easyImages) {
    for (const hardImage of hardImages) {
      const easyPixels = easyImage.pixelEvidence;
      const hardPixels = hardImage.pixelEvidence;
      const easyVector = easyPixels?.perceptualRgbBase64
        ? Buffer.from(easyPixels.perceptualRgbBase64, "base64")
        : Buffer.alloc(0);
      const hardVector = hardPixels?.perceptualRgbBase64
        ? Buffer.from(hardPixels.perceptualRgbBase64, "base64")
        : Buffer.alloc(0);
      let meanRgbDelta = 255;
      let maximumRgbDelta = 255;
      if (easyVector.length === 768 && hardVector.length === 768) {
        let totalDelta = 0;
        maximumRgbDelta = 0;
        for (let index = 0; index < easyVector.length; index += 1) {
          const delta = Math.abs(easyVector[index] - hardVector[index]);
          totalDelta += delta;
          maximumRgbDelta = Math.max(maximumRgbDelta, delta);
        }
        meanRgbDelta = totalDelta / easyVector.length;
      }
      const decodedPixelsEqual = Boolean(
        easyPixels?.decodedPixelSha256
        && easyPixels.decodedPixelSha256 === hardPixels?.decodedPixelSha256
      );
      const perceptuallyEquivalent = Boolean(
        meanRgbDelta <= 0.1
        && maximumRgbDelta <= 2
      );
      if (!decodedPixelsEqual && !perceptuallyEquivalent) continue;
      overlaps.push({
        easy: easyImage.rawSrc,
        hard: hardImage.rawSrc,
        decodedPixelsEqual,
        meanRgbDelta,
        maximumRgbDelta,
      });
    }
  }
  return overlaps;
}

async function expectedQuestImageInventory(page, slug) {
  const relative = path.join("solutions", slug, "quest.html");
  const source = auditedInputContents.get(relative).toString("utf8");
  const parsed = await page.evaluate(({ html, expectedSlug }) => {
    const documentSnapshot = new DOMParser().parseFromString(html, "text/html");
    const rows = [...documentSnapshot.querySelectorAll("img")].map((image) => {
      const panel = image.closest('[role="tabpanel"][data-path]');
      const rawSrc = String(image.getAttribute("src") || "").trim();
      let canonicalPath = "";
      try {
        const resolved = new URL(
          rawSrc,
          `http://immutable.invalid/solutions/${expectedSlug}/quest.html`,
        );
        if (resolved.origin === "http://immutable.invalid") {
          canonicalPath = resolved.pathname;
        }
      } catch (_error) {
        canonicalPath = "";
      }
      const filename = canonicalPath.split("/").pop() || "";
      const picture = image.closest("picture");
      return {
        rawSrc,
        canonicalPath,
        alt: String(image.getAttribute("alt") || "").trim(),
        status: image.getAttribute("data-evidence-status"),
        mode: panel?.getAttribute("data-path") || "",
        checkpointId: String(
          image.getAttribute("data-evidence-id")
          || filename.replace(/\.[^.]+$/, ""),
        ).trim(),
        srcset: String(image.getAttribute("srcset") || "").trim(),
        sizes: String(image.getAttribute("sizes") || "").trim(),
        pictureSources: picture
          ? [...picture.querySelectorAll("source")].map((source) => ({
            srcset: String(source.getAttribute("srcset") || "").trim(),
            sizes: String(source.getAttribute("sizes") || "").trim(),
            media: String(source.getAttribute("media") || "").trim(),
            type: String(source.getAttribute("type") || "").trim(),
          }))
          : [],
      };
    });
    return rows;
  }, { html: source, expectedSlug: slug });
  const rows = parsed.map((row) => {
    const sourceRelative = decodeURIComponent(row.canonicalPath).replace(/^\/+/, "");
    const content = auditedInputContents.get(sourceRelative);
    return {
      ...row,
      sourceRelative,
      sha256: content
        ? createHash("sha256").update(content).digest("hex")
        : null,
    };
  });
  const checkpointKeys = rows.map((row) => `${row.mode}:${row.checkpointId}`);
  return {
    rows,
    valid: rows.length > 0
      && new Set(checkpointKeys).size === checkpointKeys.length
      && rows.every((row) => (
        Boolean(row.rawSrc)
        && Boolean(row.sha256)
        && row.status === "reusable"
        && ["easy", "hard"].includes(row.mode)
        && row.alt.length >= 8
        && !/^(?:image|photo|screenshot|evidence)$/i.test(row.alt)
        && row.checkpointId.length >= 3
        && row.canonicalPath.startsWith(`/solutions/${slug}/`)
        && row.srcset === ""
        && row.sizes === ""
        && row.pictureSources.length === 0
      )),
  };
}

async function captureCleanSourceScreenshot(sourcePage, spec, sourceUrl) {
  await sourcePage.setViewportSize({
    width: spec.viewportWidth,
    height: spec.viewportHeight,
  });
  await sourcePage.setContent(
    "<!doctype html><html><head><style>"
    + "html,body{margin:0;padding:0;background:transparent;overflow:hidden}"
    + "#source{all:initial!important;position:fixed!important;display:block!important;"
    + "box-sizing:border-box!important;margin:0!important;padding:0!important;"
    + "opacity:1!important;visibility:visible!important;object-fit:fill!important;"
    + "object-position:50% 50%!important;filter:none!important;"
    + "backdrop-filter:none!important;mix-blend-mode:normal!important;"
    + "transform:none!important;rotate:none!important;scale:none!important;"
    + "translate:none!important;perspective:none!important;clip-path:none!important;"
    + "mask:none!important;-webkit-mask:none!important;background:transparent!important;"
    + "content-visibility:visible!important;contain:none!important;isolation:isolate!important;"
    + "will-change:auto!important}"
    + "</style></head><body><img id=\"source\" alt=\"\"></body></html>",
    { waitUntil: "domcontentloaded" },
  );
  await sourcePage.evaluate(async ({ sourceSpec, url }) => {
    const image = document.querySelector("#source");
    const set = (property, value) => {
      image.style.setProperty(property, value, "important");
    };
    set("left", `${sourceSpec.left}px`);
    set("top", `${sourceSpec.top}px`);
    set("width", `${sourceSpec.width}px`);
    set("height", `${sourceSpec.height}px`);
    set("border-top", sourceSpec.borderTop);
    set("border-right", sourceSpec.borderRight);
    set("border-bottom", sourceSpec.borderBottom);
    set("border-left", sourceSpec.borderLeft);
    set("border-radius", sourceSpec.borderRadius);
    set("image-rendering", sourceSpec.imageRendering);
    image.src = url;
    await image.decode();
    if (!image.naturalWidth || !image.naturalHeight) {
      throw new Error("Immutable source image decoded without dimensions");
    }
  }, { sourceSpec: spec, url: sourceUrl });
  return (
    await sourcePage.locator("#source").screenshot({
      animations: "disabled",
      caret: "hide",
    })
  ).toString("base64");
}

async function inspectModeImages(page, sourcePage, mode, expectedRows) {
  const images = page.locator(
    `[data-path="${mode}"] img[data-evidence-status="reusable"]`,
  );
  const count = await images.count();
  const rows = [];
  for (let index = 0; index < count; index += 1) {
    const image = images.nth(index);
    const expected = expectedRows[index] || null;
    const liveDescriptor = await image.evaluate((element) => {
      const rawSrc = String(element.getAttribute("src") || "").trim();
      const resolved = new URL(rawSrc, document.baseURI);
      const panel = element.closest('[role="tabpanel"][data-path]');
      const filename = resolved.pathname.split("/").pop() || "";
      const currentSource = element.currentSrc
        ? new URL(element.currentSrc, document.baseURI)
        : resolved;
      const picture = element.closest("picture");
      return {
        rawSrc,
        canonicalPath: resolved.pathname,
        currentSrcCanonicalPath: currentSource.pathname,
        alt: String(element.getAttribute("alt") || "").trim(),
        status: element.getAttribute("data-evidence-status"),
        mode: panel?.getAttribute("data-path") || "",
        checkpointId: String(
          element.getAttribute("data-evidence-id")
          || filename.replace(/\.[^.]+$/, ""),
        ).trim(),
        srcset: String(element.getAttribute("srcset") || "").trim(),
        sizes: String(element.getAttribute("sizes") || "").trim(),
        pictureSources: picture
          ? [...picture.querySelectorAll("source")].map((source) => ({
            srcset: String(source.getAttribute("srcset") || "").trim(),
            sizes: String(source.getAttribute("sizes") || "").trim(),
            media: String(source.getAttribute("media") || "").trim(),
            type: String(source.getAttribute("type") || "").trim(),
          }))
          : [],
      };
    });
    const visible = await image.isVisible();
    let loadError = null;
    if (visible) {
      await image.evaluate((element) => {
        element.scrollIntoView({
          block: "center",
          inline: "center",
          behavior: "auto",
        });
      });
      await page.waitForTimeout(50);
      try {
        await image.evaluate((element) => new Promise((resolve, reject) => {
          const timer = setTimeout(
            () => reject(new Error(`Image load timed out: ${element.getAttribute("src")}`)),
            10000,
          );
          const finish = (callback) => {
            clearTimeout(timer);
            callback();
          };
          if (element.complete) {
            finish(
              element.naturalWidth > 0
                ? resolve
                : () => reject(new Error(`Image failed: ${element.getAttribute("src")}`)),
            );
            return;
          }
          element.addEventListener("load", () => finish(resolve), { once: true });
          element.addEventListener(
            "error",
            () => finish(
              () => reject(new Error(`Image failed: ${element.getAttribute("src")}`)),
            ),
            { once: true },
          );
        }));
      } catch (error) {
        loadError = String(error);
      }
      await image.evaluate((element) => {
        element.scrollIntoView({
          block: "center",
          inline: "center",
          behavior: "auto",
        });
      });
      await page.waitForTimeout(25);
    }
    let renderedScreenshot = "";
    let isolatedScreenshot = "";
    let sourceScreenshot = "";
    if (visible) {
      const sourceSpec = await image.evaluate((element) => {
        const rect = element.getBoundingClientRect();
        const computed = getComputedStyle(element);
        return {
          left: rect.left,
          top: rect.top,
          width: rect.width,
          height: rect.height,
          viewportWidth: innerWidth,
          viewportHeight: innerHeight,
          borderTop: computed.borderTop,
          borderRight: computed.borderRight,
          borderBottom: computed.borderBottom,
          borderLeft: computed.borderLeft,
          borderRadius: computed.borderRadius,
          imageRendering: computed.imageRendering,
        };
      });
      renderedScreenshot = (
        await image.screenshot({ animations: "disabled", caret: "hide" })
      ).toString("base64");
      await image.evaluate((element) => {
        const stateKey = "__aibastAuditVisualIsolation";
        if (window[stateKey]) throw new Error("Visual isolation state already exists");
        const styleRecords = [];
        const attributeRecords = [];
        const attribute = "data-aibast-audit-isolate";
        const candidates = [
          document.documentElement,
          document.body,
          ...document.body.querySelectorAll("*"),
        ].filter(Boolean);
        for (const candidate of candidates) {
          const related = candidate === element
            || candidate.contains(element)
            || element.contains(candidate);
          if (related) {
            attributeRecords.push({
              candidate,
              original: candidate.getAttribute(attribute),
            });
            candidate.setAttribute(attribute, "");
            continue;
          }
          styleRecords.push({
            candidate,
            value: candidate.style.getPropertyValue("opacity"),
            priority: candidate.style.getPropertyPriority("opacity"),
          });
          candidate.style.setProperty("opacity", "0", "important");
        }
        const pseudoStyle = document.createElement("style");
        pseudoStyle.textContent = `
          [${attribute}]::before,
          [${attribute}]::after {
            visibility: hidden !important;
            opacity: 0 !important;
            color: transparent !important;
            background: none !important;
            border-color: transparent !important;
            outline: none !important;
            box-shadow: none !important;
            text-shadow: none !important;
          }
        `;
        document.head.appendChild(pseudoStyle);
        window[stateKey] = {
          attribute,
          attributeRecords,
          pseudoStyle,
          styleRecords,
        };
      });
      try {
        isolatedScreenshot = (
          await image.screenshot({ animations: "disabled", caret: "hide" })
        ).toString("base64");
        if (expected?.canonicalPath) {
          sourceScreenshot = await captureCleanSourceScreenshot(
            sourcePage,
            sourceSpec,
            `${baseUrl}${expected.canonicalPath}`,
          );
        }
      } finally {
        await page.evaluate(() => {
          const stateKey = "__aibastAuditVisualIsolation";
          const state = window[stateKey];
          if (!state) return;
          state.pseudoStyle.remove();
          for (const record of state.attributeRecords) {
            if (record.original === null) {
              record.candidate.removeAttribute(state.attribute);
            } else {
              record.candidate.setAttribute(state.attribute, record.original);
            }
          }
          for (const record of state.styleRecords) {
            if (record.value) {
              record.candidate.style.setProperty(
                "opacity",
                record.value,
                record.priority,
              );
            } else {
              record.candidate.style.removeProperty("opacity");
            }
          }
          delete window[stateKey];
        });
      }
    }
    const row = await image.evaluate(async (element, screenshots) => {
      const filterOpacity = (value) => {
        let opacity = 1;
        for (const match of String(value || "").matchAll(/opacity\(([^)]+)\)/g)) {
          const raw = match[1].trim();
          const parsed = raw.endsWith("%")
            ? Number.parseFloat(raw) / 100
            : Number.parseFloat(raw);
          if (Number.isFinite(parsed)) opacity *= parsed;
        }
        return opacity;
      };
      const visuallyMasked = (computed) => (
        (computed.maskImage && computed.maskImage !== "none")
        || (computed.webkitMaskImage && computed.webkitMaskImage !== "none")
        || (computed.clipPath && computed.clipPath !== "none")
        || computed.contentVisibility === "hidden"
      );
      const rect = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      const container = element.closest(
        ".preview-case, .learn-step, .preview-shot-wrap, article, section",
      ) || element.parentElement;
      const containerRect = container.getBoundingClientRect();
      const clippedBy = [];
      let effectiveOpacity = Number.parseFloat(style.opacity || "1");
      let effectiveFilterOpacity = filterOpacity(style.filter);
      let filtered = Boolean(style.filter && style.filter !== "none");
      let masked = visuallyMasked(style);
      let ancestorsVisible = true;
      let parent = element.parentElement;
      while (parent) {
        const parentStyle = getComputedStyle(parent);
        const parentRect = parent.getBoundingClientRect();
        effectiveOpacity *= Number.parseFloat(parentStyle.opacity || "1");
        effectiveFilterOpacity *= filterOpacity(parentStyle.filter);
        filtered ||= Boolean(parentStyle.filter && parentStyle.filter !== "none");
        masked ||= visuallyMasked(parentStyle);
        if (
          parentStyle.display === "none"
          || parentStyle.visibility === "hidden"
          || parent.hidden
        ) {
          ancestorsVisible = false;
        }
        const clipsX = ["hidden", "clip", "auto", "scroll"].includes(
          parentStyle.overflowX,
        );
        const clipsY = ["hidden", "clip", "auto", "scroll"].includes(
          parentStyle.overflowY,
        );
        if (
          (clipsX && (rect.left < parentRect.left - 1 || rect.right > parentRect.right + 1))
          || (clipsY && (rect.top < parentRect.top - 1 || rect.bottom > parentRect.bottom + 1))
        ) {
          clippedBy.push(
            `${parent.tagName.toLowerCase()}.${[...parent.classList].join(".")}`,
          );
        }
        if (parent === document.documentElement) break;
        parent = parent.parentElement;
      }
      const toPoint = ([xRatio, yRatio]) => [
        Math.min(innerWidth - 1, Math.max(0, rect.left + rect.width * xRatio)),
        Math.min(innerHeight - 1, Math.max(0, rect.top + rect.height * yRatio)),
      ];
      const legacyFivePoints = [
        [0.5, 0.5],
        [0.2, 0.2],
        [0.8, 0.2],
        [0.2, 0.8],
        [0.8, 0.8],
      ].map(toPoint);
      const sampleRatios = Array.from(
        { length: 11 },
        (_value, index) => 0.05 + (index * 0.09),
      );
      const points = sampleRatios.flatMap((yRatio) => (
        sampleRatios.map((xRatio) => toPoint([xRatio, yRatio]))
      ));
      const allCandidates = [...document.querySelectorAll("*")]
        .filter((candidate) => candidate !== element);
      const overlappingCandidates = allCandidates
        .filter((candidate) => {
          const candidateRect = candidate.getBoundingClientRect();
          return candidateRect.right > rect.left
            && candidateRect.left < rect.right
            && candidateRect.bottom > rect.top
            && candidateRect.top < rect.bottom;
        });
      const pointerOverrides = overlappingCandidates
        .filter((candidate) => {
          const candidateStyle = getComputedStyle(candidate);
          return candidateStyle.pointerEvents === "none"
            && candidateStyle.display !== "none"
            && candidateStyle.visibility !== "hidden"
            && Number.parseFloat(candidateStyle.opacity || "1") > 0.05;
        })
        .map((candidate) => ({
          candidate,
          value: candidate.style.getPropertyValue("pointer-events"),
          priority: candidate.style.getPropertyPriority("pointer-events"),
        }));
      for (const override of pointerOverrides) {
        override.candidate.style.setProperty("pointer-events", "auto", "important");
      }
      const colorAlpha = (value) => {
        if (!value || value === "transparent") return 0;
        const rgba = value.match(
          /rgba?\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+(?:\s*,\s*([\d.]+))?\s*\)/,
        );
        if (!rgba) return 1;
        return rgba[1] === undefined ? 1 : Number.parseFloat(rgba[1]);
      };
      const pseudoPainted = (computed) => {
        const content = String(computed.content || "");
        const hasContent = !["", "none", "normal"].includes(content);
        const hasBackground = (
          colorAlpha(computed.backgroundColor) > 0.05
          || computed.backgroundImage !== "none"
        );
        const hasBorder = [
          ["Top", computed.borderTopWidth, computed.borderTopColor],
          ["Right", computed.borderRightWidth, computed.borderRightColor],
          ["Bottom", computed.borderBottomWidth, computed.borderBottomColor],
          ["Left", computed.borderLeftWidth, computed.borderLeftColor],
        ].some(([_side, width, color]) => (
          Number.parseFloat(width || "0") > 0
          && colorAlpha(color) > 0.05
        ));
        const hasOutline = (
          computed.outlineStyle !== "none"
          && Number.parseFloat(computed.outlineWidth || "0") > 0
          && colorAlpha(computed.outlineColor) > 0.05
        );
        const hasShadow = Boolean(
          computed.boxShadow && computed.boxShadow !== "none",
        );
        return computed.display !== "none"
          && computed.visibility !== "hidden"
          && Number.parseFloat(computed.opacity || "1") > 0.05
          && (
            hasBackground
            || hasBorder
            || hasOutline
            || hasShadow
            || (hasContent && colorAlpha(computed.color) > 0.05)
          );
      };
      const pseudoOverrides = [];
      const pseudoRules = [];
      for (const [candidateIndex, candidate] of allCandidates.entries()) {
        for (const pseudo of ["::before", "::after"]) {
          const computed = getComputedStyle(candidate, pseudo);
          if (!pseudoPainted(computed) || computed.pointerEvents !== "none") continue;
          const pseudoName = pseudo.slice(2);
          const attribute = `data-audit-pseudo-${candidateIndex}-${pseudoName}`;
          const original = candidate.getAttribute(attribute);
          candidate.setAttribute(attribute, "");
          pseudoOverrides.push({ candidate, attribute, original });
          pseudoRules.push(
            `[${attribute}]${pseudo}{pointer-events:auto!important;}`,
          );
        }
      }
      const pseudoStyle = document.createElement("style");
      pseudoStyle.textContent = pseudoRules.join("\n");
      document.head.appendChild(pseudoStyle);
      const related = (candidate) => Boolean(
        candidate
        && (
          candidate === element
          || element.contains(candidate)
        )
      );
      let unobscuredPoints;
      let legacyFiveUnobscuredPoints;
      try {
        const pointIsUnobscured = ([x, y]) => {
          const stack = document.elementsFromPoint(x, y);
          const topVisible = stack.find((candidate) => {
            const candidateStyle = getComputedStyle(candidate);
            return candidateStyle.display !== "none"
              && candidateStyle.visibility !== "hidden"
              && Number.parseFloat(candidateStyle.opacity || "1") > 0.05;
          });
          return related(topVisible);
        };
        unobscuredPoints = points.filter(pointIsUnobscured).length;
        legacyFiveUnobscuredPoints = legacyFivePoints
          .filter(pointIsUnobscured)
          .length;
      } finally {
        pseudoStyle.remove();
        for (const override of pseudoOverrides) {
          if (override.original === null) {
            override.candidate.removeAttribute(override.attribute);
          } else {
            override.candidate.setAttribute(
              override.attribute,
              override.original,
            );
          }
        }
        for (const override of pointerOverrides) {
          if (override.value) {
            override.candidate.style.setProperty(
              "pointer-events",
              override.value,
              override.priority,
            );
          } else {
            override.candidate.style.removeProperty("pointer-events");
          }
        }
      }
      const unobscuredRatio = points.length
        ? unobscuredPoints / points.length
        : 0;
      const legacyFiveUnobscuredRatio = legacyFivePoints.length
        ? legacyFiveUnobscuredPoints / legacyFivePoints.length
        : 0;
      const pixelEvidence = await (async () => {
        try {
          const sampleSize = 64;
          const totalPixels = sampleSize * sampleSize;
          const canvas = document.createElement("canvas");
          canvas.width = sampleSize;
          canvas.height = sampleSize;
          const context = canvas.getContext("2d", { willReadFrequently: true });
          if (!context) throw new Error("2D canvas unavailable");
          context.drawImage(element, 0, 0, sampleSize, sampleSize);
          const pixels = context.getImageData(0, 0, sampleSize, sampleSize).data;
          let opaquePixels = 0;
          let lumaSum = 0;
          let lumaSquaredSum = 0;
          let minLuma = 255;
          let maxLuma = 0;
          const quantizedColors = new Set();
          const colorBuckets = new Map();
          const lumaValues = new Float32Array(totalPixels);
          const tileGrid = 4;
          const tileSize = sampleSize / tileGrid;
          const tiles = Array.from(
            { length: tileGrid * tileGrid },
            () => ({
              opaquePixels: 0,
              minLuma: 255,
              maxLuma: 0,
              colors: new Set(),
            }),
          );
          for (let offset = 0; offset < pixels.length; offset += 4) {
            const alpha = pixels[offset + 3];
            if (alpha <= 16) continue;
            const pixelIndex = offset / 4;
            const x = pixelIndex % sampleSize;
            const y = Math.floor(pixelIndex / sampleSize);
            const red = pixels[offset];
            const green = pixels[offset + 1];
            const blue = pixels[offset + 2];
            const luma = (0.2126 * red) + (0.7152 * green) + (0.0722 * blue);
            lumaValues[pixelIndex] = luma;
            opaquePixels += 1;
            lumaSum += luma;
            lumaSquaredSum += luma * luma;
            minLuma = Math.min(minLuma, luma);
            maxLuma = Math.max(maxLuma, luma);
            quantizedColors.add(
              `${red >> 5}:${green >> 5}:${blue >> 5}:${alpha >> 6}`,
            );
            const colorBucket = `${red >> 5}:${green >> 5}:${blue >> 5}`;
            colorBuckets.set(
              colorBucket,
              (colorBuckets.get(colorBucket) || 0) + 1,
            );
            const tileX = Math.min(tileGrid - 1, Math.floor(x / tileSize));
            const tileY = Math.min(tileGrid - 1, Math.floor(y / tileSize));
            const tile = tiles[(tileY * tileGrid) + tileX];
            tile.opaquePixels += 1;
            tile.minLuma = Math.min(tile.minLuma, luma);
            tile.maxLuma = Math.max(tile.maxLuma, luma);
            tile.colors.add(`${red >> 5}:${green >> 5}:${blue >> 5}`);
          }
          const opaqueRatio = opaquePixels / totalPixels;
          const averageLuma = opaquePixels ? lumaSum / opaquePixels : 0;
          const variance = opaquePixels
            ? Math.max(0, (lumaSquaredSum / opaquePixels) - (averageLuma ** 2))
            : 0;
          const lumaStdDev = Math.sqrt(variance);
          const lumaRange = opaquePixels ? maxLuma - minLuma : 0;
          const tilePixels = tileSize * tileSize;
          const detailedTiles = tiles.filter((tile) => (
            tile.opaquePixels / tilePixels >= 0.8
            && tile.colors.size >= 4
            && tile.maxLuma - tile.minLuma >= 8
          )).length;
          const [dominantBucket = "0:0:0", dominantPixels = 0] = [
            ...colorBuckets.entries(),
          ].sort((left, right) => right[1] - left[1])[0] || [];
          const dominantCenter = dominantBucket
            .split(":")
            .map((component) => (Number(component) * 32) + 16);
          const foregroundCounts = Array(tileGrid * tileGrid).fill(0);
          const foregroundMask = new Uint8Array(totalPixels);
          let foregroundPixels = 0;
          for (let offset = 0; offset < pixels.length; offset += 4) {
            const alpha = pixels[offset + 3];
            if (alpha <= 16) continue;
            const red = pixels[offset];
            const green = pixels[offset + 1];
            const blue = pixels[offset + 2];
            const distance = Math.abs(red - dominantCenter[0])
              + Math.abs(green - dominantCenter[1])
              + Math.abs(blue - dominantCenter[2]);
            if (distance < 48) continue;
            foregroundPixels += 1;
            const pixelIndex = offset / 4;
            foregroundMask[pixelIndex] = 1;
            const x = pixelIndex % sampleSize;
            const y = Math.floor(pixelIndex / sampleSize);
            const tileX = Math.min(tileGrid - 1, Math.floor(x / tileSize));
            const tileY = Math.min(tileGrid - 1, Math.floor(y / tileSize));
            foregroundCounts[(tileY * tileGrid) + tileX] += 1;
          }
          const foregroundTileIndexes = foregroundCounts
            .map((count, tileIndex) => ({ count, tileIndex }))
            .filter(({ count }) => count >= 4);
          const foregroundRows = new Set(
            foregroundTileIndexes.map(({ tileIndex }) => Math.floor(tileIndex / tileGrid)),
          ).size;
          const foregroundColumns = new Set(
            foregroundTileIndexes.map(({ tileIndex }) => tileIndex % tileGrid),
          ).size;
          const foregroundRatio = foregroundPixels / totalPixels;
          const visitedForeground = new Uint8Array(totalPixels);
          const structuredTileIndexes = new Set();
          let structuredForegroundPixels = 0;
          let structuredComponents = 0;
          let largestForegroundComponent = 0;
          let maxTwoDimensionalComponentArea = 0;
          for (let start = 0; start < totalPixels; start += 1) {
            if (!foregroundMask[start] || visitedForeground[start]) continue;
            const stack = [start];
            const component = [];
            visitedForeground[start] = 1;
            while (stack.length) {
              const pixelIndex = stack.pop();
              component.push(pixelIndex);
              const x = pixelIndex % sampleSize;
              const y = Math.floor(pixelIndex / sampleSize);
              for (let yOffset = -1; yOffset <= 1; yOffset += 1) {
                for (let xOffset = -1; xOffset <= 1; xOffset += 1) {
                  if (xOffset === 0 && yOffset === 0) continue;
                  const neighborX = x + xOffset;
                  const neighborY = y + yOffset;
                  if (
                    neighborX < 0
                    || neighborX >= sampleSize
                    || neighborY < 0
                    || neighborY >= sampleSize
                  ) continue;
                  const neighbor = (neighborY * sampleSize) + neighborX;
                  if (!foregroundMask[neighbor] || visitedForeground[neighbor]) continue;
                  visitedForeground[neighbor] = 1;
                  stack.push(neighbor);
                }
              }
            }
            largestForegroundComponent = Math.max(
              largestForegroundComponent,
              component.length,
            );
            if (component.length < 4) continue;
            let minComponentX = sampleSize;
            let maxComponentX = -1;
            let minComponentY = sampleSize;
            let maxComponentY = -1;
            for (const pixelIndex of component) {
              const x = pixelIndex % sampleSize;
              const y = Math.floor(pixelIndex / sampleSize);
              minComponentX = Math.min(minComponentX, x);
              maxComponentX = Math.max(maxComponentX, x);
              minComponentY = Math.min(minComponentY, y);
              maxComponentY = Math.max(maxComponentY, y);
            }
            const componentWidth = maxComponentX - minComponentX + 1;
            const componentHeight = maxComponentY - minComponentY + 1;
            if (componentWidth >= 4 && componentHeight >= 4) {
              maxTwoDimensionalComponentArea = Math.max(
                maxTwoDimensionalComponentArea,
                componentWidth * componentHeight,
              );
            }
            structuredComponents += 1;
            structuredForegroundPixels += component.length;
            for (const pixelIndex of component) {
              const x = pixelIndex % sampleSize;
              const y = Math.floor(pixelIndex / sampleSize);
              const tileX = Math.min(tileGrid - 1, Math.floor(x / tileSize));
              const tileY = Math.min(tileGrid - 1, Math.floor(y / tileSize));
              structuredTileIndexes.add((tileY * tileGrid) + tileX);
            }
          }
          const structuredForegroundRatio = structuredForegroundPixels / totalPixels;
          const largestForegroundComponentRatio = (
            largestForegroundComponent / totalPixels
          );
          const edgeCounts = Array(tileGrid * tileGrid).fill(0);
          let edgePixels = 0;
          for (let y = 0; y < sampleSize; y += 1) {
            for (let x = 0; x < sampleSize; x += 1) {
              const pixelIndex = (y * sampleSize) + x;
              if (pixels[(pixelIndex * 4) + 3] <= 16) continue;
              let edgeDelta = 0;
              if (
                x < sampleSize - 1
                && pixels[((pixelIndex + 1) * 4) + 3] > 16
              ) {
                edgeDelta = Math.max(
                  edgeDelta,
                  Math.abs(lumaValues[pixelIndex] - lumaValues[pixelIndex + 1]),
                );
              }
              if (
                y < sampleSize - 1
                && pixels[((pixelIndex + sampleSize) * 4) + 3] > 16
              ) {
                edgeDelta = Math.max(
                  edgeDelta,
                  Math.abs(
                    lumaValues[pixelIndex]
                    - lumaValues[pixelIndex + sampleSize],
                  ),
                );
              }
              if (edgeDelta < 12) continue;
              edgePixels += 1;
              const tileX = Math.min(tileGrid - 1, Math.floor(x / tileSize));
              const tileY = Math.min(tileGrid - 1, Math.floor(y / tileSize));
              edgeCounts[(tileY * tileGrid) + tileX] += 1;
            }
          }
          const edgeTileIndexes = edgeCounts
            .map((count, tileIndex) => ({ count, tileIndex }))
            .filter(({ count }) => count >= 3);
          const edgeRows = new Set(
            edgeTileIndexes.map(({ tileIndex }) => Math.floor(tileIndex / tileGrid)),
          ).size;
          const edgeColumns = new Set(
            edgeTileIndexes.map(({ tileIndex }) => tileIndex % tileGrid),
          ).size;
          const edgeRatio = edgePixels / totalPixels;
          const perceptualLuma = [];
          const perceptualGrid = 8;
          const perceptualTileSize = sampleSize / perceptualGrid;
          for (let tileY = 0; tileY < perceptualGrid; tileY += 1) {
            for (let tileX = 0; tileX < perceptualGrid; tileX += 1) {
              let tileLuma = 0;
              for (
                let y = tileY * perceptualTileSize;
                y < (tileY + 1) * perceptualTileSize;
                y += 1
              ) {
                for (
                  let x = tileX * perceptualTileSize;
                  x < (tileX + 1) * perceptualTileSize;
                  x += 1
                ) {
                  tileLuma += lumaValues[(y * sampleSize) + x];
                }
              }
              perceptualLuma.push(
                Math.round(tileLuma / (perceptualTileSize ** 2)),
              );
            }
          }
          const rgbGrid = 16;
          const rgbTileSize = sampleSize / rgbGrid;
          const perceptualRgb = new Uint8Array(rgbGrid * rgbGrid * 3);
          let rgbOffset = 0;
          for (let tileY = 0; tileY < rgbGrid; tileY += 1) {
            for (let tileX = 0; tileX < rgbGrid; tileX += 1) {
              let redSum = 0;
              let greenSum = 0;
              let blueSum = 0;
              for (
                let y = tileY * rgbTileSize;
                y < (tileY + 1) * rgbTileSize;
                y += 1
              ) {
                for (
                  let x = tileX * rgbTileSize;
                  x < (tileX + 1) * rgbTileSize;
                  x += 1
                ) {
                  const offset = ((y * sampleSize) + x) * 4;
                  redSum += pixels[offset];
                  greenSum += pixels[offset + 1];
                  blueSum += pixels[offset + 2];
                }
              }
              const divisor = rgbTileSize ** 2;
              perceptualRgb[rgbOffset] = Math.round(redSum / divisor);
              perceptualRgb[rgbOffset + 1] = Math.round(greenSum / divisor);
              perceptualRgb[rgbOffset + 2] = Math.round(blueSum / divisor);
              rgbOffset += 3;
            }
          }
          let perceptualRgbBinary = "";
          for (const value of perceptualRgb) {
            perceptualRgbBinary += String.fromCharCode(value);
          }
          const decodedPixelSha256 = Array.from(new Uint8Array(
            await crypto.subtle.digest("SHA-256", pixels),
          )).map((value) => value.toString(16).padStart(2, "0")).join("");
          return {
            readable: true,
            sampleSize,
            opaqueRatio,
            quantizedColors: quantizedColors.size,
            lumaStdDev,
            lumaRange,
            detailedTiles,
            totalTiles: tiles.length,
            dominantColorRatio: opaquePixels ? dominantPixels / opaquePixels : 1,
            foregroundRatio,
            foregroundTiles: foregroundTileIndexes.length,
            foregroundRows,
            foregroundColumns,
            structuredForegroundRatio,
            structuredComponents,
            structuredTiles: structuredTileIndexes.size,
            largestForegroundComponentRatio,
            maxTwoDimensionalComponentArea,
            edgeRatio,
            edgeTiles: edgeTileIndexes.length,
            edgeRows,
            edgeColumns,
            decodedPixelSha256,
            perceptualLuma,
            perceptualRgbBase64: btoa(perceptualRgbBinary),
            meaningful: Boolean(
              opaqueRatio >= 0.8
              && quantizedColors.size >= 8
              && lumaStdDev >= 1
              && lumaRange >= 8
              && detailedTiles >= 3
              && foregroundRatio >= 0.024
              && foregroundTileIndexes.length >= 5
              && foregroundRows >= 2
              && foregroundColumns >= 4
              && structuredForegroundRatio >= 0.0195
              && largestForegroundComponentRatio >= 0.005
              && (
                maxTwoDimensionalComponentArea >= 28
                || (
                  structuredForegroundRatio >= 0.05
                  && largestForegroundComponentRatio >= 0.01
                )
              )
              && (opaquePixels ? dominantPixels / opaquePixels : 1) <= 0.973
              && edgeRatio >= 0.05
              && edgeTileIndexes.length >= 8
              && edgeRows >= 3
              && edgeColumns >= 4
            ),
          };
        } catch (error) {
          return {
            readable: false,
            meaningful: false,
            error: String(error),
          };
        }
      })();
      const renderedPixelMatch = await (async () => {
        if (!screenshots.rendered || !screenshots.isolated || !screenshots.source) {
          return {
            readable: false,
            matches: false,
            error: "Rendered, isolated, or source screenshot unavailable",
          };
        }
        try {
          const decodeScreenshot = (base64, label) => new Promise(
            (resolve, reject) => {
              const screenshot = new Image();
              screenshot.addEventListener(
                "load",
                () => resolve(screenshot),
                { once: true },
              );
              screenshot.addEventListener(
                "error",
                () => reject(new Error(`${label} screenshot failed to decode`)),
                { once: true },
              );
              screenshot.src = `data:image/png;base64,${base64}`;
            },
          );
          const [renderedImage, isolatedImage, sourceImage] = await Promise.all([
            decodeScreenshot(screenshots.rendered, "Rendered"),
            decodeScreenshot(screenshots.isolated, "Isolated"),
            decodeScreenshot(screenshots.source, "Source"),
          ]);
          const width = renderedImage.naturalWidth;
          const height = renderedImage.naturalHeight;
          if (!width || !height) throw new Error("Rendered screenshot is empty");
          if (
            isolatedImage.naturalWidth !== width
            || isolatedImage.naturalHeight !== height
            || sourceImage.naturalWidth !== width
            || sourceImage.naturalHeight !== height
          ) {
            return {
              readable: true,
              width,
              height,
              isolatedWidth: isolatedImage.naturalWidth,
              isolatedHeight: isolatedImage.naturalHeight,
              sourceWidth: sourceImage.naturalWidth,
              sourceHeight: sourceImage.naturalHeight,
              matches: false,
              error: "Rendered, isolated, and source screenshot dimensions differ",
            };
          }
          const imagePixels = (image, targetWidth = width, targetHeight = height) => {
            const canvas = document.createElement("canvas");
            canvas.width = targetWidth;
            canvas.height = targetHeight;
            const context = canvas.getContext("2d", { willReadFrequently: true });
            if (!context) throw new Error("2D canvas unavailable");
            context.drawImage(image, 0, 0, targetWidth, targetHeight);
            return context.getImageData(0, 0, targetWidth, targetHeight).data;
          };
          const compare = (
            leftImage,
            rightImage,
            maximumChangedRatio = 0.0001,
            maximumMeanDelta = 0.05,
          ) => {
            const leftPixels = imagePixels(leftImage);
            const rightPixels = imagePixels(rightImage);
            let comparedPixels = 0;
            let changedPixels = 0;
            let totalDelta = 0;
            let maximumDelta = 0;
            for (let offset = 0; offset < leftPixels.length; offset += 4) {
              const delta = Math.max(
                Math.abs(leftPixels[offset] - rightPixels[offset]),
                Math.abs(leftPixels[offset + 1] - rightPixels[offset + 1]),
                Math.abs(leftPixels[offset + 2] - rightPixels[offset + 2]),
                Math.abs(leftPixels[offset + 3] - rightPixels[offset + 3]),
              );
              comparedPixels += 1;
              totalDelta += delta;
              maximumDelta = Math.max(maximumDelta, delta);
              if (delta > 2) changedPixels += 1;
            }
            const changedRatio = comparedPixels
              ? changedPixels / comparedPixels
              : 1;
            const meanDelta = comparedPixels
              ? totalDelta / comparedPixels
              : 255;
            return {
              comparedPixels,
              changedRatio,
              meanDelta,
              maximumDelta,
              matches: Boolean(
                changedRatio <= maximumChangedRatio
                && meanDelta <= maximumMeanDelta
              ),
            };
          };
          const analyzeRenderedContent = (image) => {
            const sampleSize = 64;
            const totalPixels = sampleSize * sampleSize;
            const pixels = imagePixels(image, sampleSize, sampleSize);
            let opaquePixels = 0;
            let lumaSum = 0;
            let lumaSquaredSum = 0;
            let minLuma = 255;
            let maxLuma = 0;
            const quantizedColors = new Set();
            const colorBuckets = new Map();
            const lumaValues = new Float32Array(totalPixels);
            const tileGrid = 4;
            const tileSize = sampleSize / tileGrid;
            const tiles = Array.from(
              { length: tileGrid * tileGrid },
              () => ({
                opaquePixels: 0,
                minLuma: 255,
                maxLuma: 0,
                colors: new Set(),
              }),
            );
            for (let offset = 0; offset < pixels.length; offset += 4) {
              const alpha = pixels[offset + 3];
              if (alpha <= 16) continue;
              const pixelIndex = offset / 4;
              const x = pixelIndex % sampleSize;
              const y = Math.floor(pixelIndex / sampleSize);
              const red = pixels[offset];
              const green = pixels[offset + 1];
              const blue = pixels[offset + 2];
              const luma = (0.2126 * red) + (0.7152 * green) + (0.0722 * blue);
              lumaValues[pixelIndex] = luma;
              opaquePixels += 1;
              lumaSum += luma;
              lumaSquaredSum += luma * luma;
              minLuma = Math.min(minLuma, luma);
              maxLuma = Math.max(maxLuma, luma);
              quantizedColors.add(
                `${red >> 5}:${green >> 5}:${blue >> 5}:${alpha >> 6}`,
              );
              const colorBucket = `${red >> 5}:${green >> 5}:${blue >> 5}`;
              colorBuckets.set(
                colorBucket,
                (colorBuckets.get(colorBucket) || 0) + 1,
              );
              const tileX = Math.min(tileGrid - 1, Math.floor(x / tileSize));
              const tileY = Math.min(tileGrid - 1, Math.floor(y / tileSize));
              const tile = tiles[(tileY * tileGrid) + tileX];
              tile.opaquePixels += 1;
              tile.minLuma = Math.min(tile.minLuma, luma);
              tile.maxLuma = Math.max(tile.maxLuma, luma);
              tile.colors.add(`${red >> 5}:${green >> 5}:${blue >> 5}`);
            }
            const opaqueRatio = opaquePixels / totalPixels;
            const averageLuma = opaquePixels ? lumaSum / opaquePixels : 0;
            const variance = opaquePixels
              ? Math.max(0, (lumaSquaredSum / opaquePixels) - (averageLuma ** 2))
              : 0;
            const lumaStdDev = Math.sqrt(variance);
            const lumaRange = opaquePixels ? maxLuma - minLuma : 0;
            const tilePixels = tileSize * tileSize;
            const detailedTiles = tiles.filter((tile) => (
              tile.opaquePixels / tilePixels >= 0.8
              && tile.colors.size >= 4
              && tile.maxLuma - tile.minLuma >= 8
            )).length;
            const [dominantBucket = "0:0:0", dominantPixels = 0] = [
              ...colorBuckets.entries(),
            ].sort((left, right) => right[1] - left[1])[0] || [];
            const dominantCenter = dominantBucket
              .split(":")
              .map((component) => (Number(component) * 32) + 16);
            const foregroundCounts = Array(tileGrid * tileGrid).fill(0);
            const foregroundMask = new Uint8Array(totalPixels);
            let foregroundPixels = 0;
            for (let offset = 0; offset < pixels.length; offset += 4) {
              const alpha = pixels[offset + 3];
              if (alpha <= 16) continue;
              const red = pixels[offset];
              const green = pixels[offset + 1];
              const blue = pixels[offset + 2];
              const distance = Math.abs(red - dominantCenter[0])
                + Math.abs(green - dominantCenter[1])
                + Math.abs(blue - dominantCenter[2]);
              if (distance < 48) continue;
              foregroundPixels += 1;
              const pixelIndex = offset / 4;
              foregroundMask[pixelIndex] = 1;
              const x = pixelIndex % sampleSize;
              const y = Math.floor(pixelIndex / sampleSize);
              const tileX = Math.min(tileGrid - 1, Math.floor(x / tileSize));
              const tileY = Math.min(tileGrid - 1, Math.floor(y / tileSize));
              foregroundCounts[(tileY * tileGrid) + tileX] += 1;
            }
            const foregroundTileIndexes = foregroundCounts
              .map((count, tileIndex) => ({ count, tileIndex }))
              .filter(({ count }) => count >= 4);
            const foregroundRows = new Set(
              foregroundTileIndexes.map(({ tileIndex }) => Math.floor(tileIndex / tileGrid)),
            ).size;
            const foregroundColumns = new Set(
              foregroundTileIndexes.map(({ tileIndex }) => tileIndex % tileGrid),
            ).size;
            const foregroundRatio = foregroundPixels / totalPixels;
            const visitedForeground = new Uint8Array(totalPixels);
            const structuredTileIndexes = new Set();
            let structuredForegroundPixels = 0;
            let structuredComponents = 0;
            let largestForegroundComponent = 0;
            let maxTwoDimensionalComponentArea = 0;
            for (let start = 0; start < totalPixels; start += 1) {
              if (!foregroundMask[start] || visitedForeground[start]) continue;
              const stack = [start];
              const component = [];
              visitedForeground[start] = 1;
              while (stack.length) {
                const pixelIndex = stack.pop();
                component.push(pixelIndex);
                const x = pixelIndex % sampleSize;
                const y = Math.floor(pixelIndex / sampleSize);
                for (let yOffset = -1; yOffset <= 1; yOffset += 1) {
                  for (let xOffset = -1; xOffset <= 1; xOffset += 1) {
                    if (xOffset === 0 && yOffset === 0) continue;
                    const neighborX = x + xOffset;
                    const neighborY = y + yOffset;
                    if (
                      neighborX < 0
                      || neighborX >= sampleSize
                      || neighborY < 0
                      || neighborY >= sampleSize
                    ) continue;
                    const neighbor = (neighborY * sampleSize) + neighborX;
                    if (!foregroundMask[neighbor] || visitedForeground[neighbor]) continue;
                    visitedForeground[neighbor] = 1;
                    stack.push(neighbor);
                  }
                }
              }
              largestForegroundComponent = Math.max(
                largestForegroundComponent,
                component.length,
              );
              if (component.length < 4) continue;
              let minComponentX = sampleSize;
              let maxComponentX = -1;
              let minComponentY = sampleSize;
              let maxComponentY = -1;
              for (const pixelIndex of component) {
                const x = pixelIndex % sampleSize;
                const y = Math.floor(pixelIndex / sampleSize);
                minComponentX = Math.min(minComponentX, x);
                maxComponentX = Math.max(maxComponentX, x);
                minComponentY = Math.min(minComponentY, y);
                maxComponentY = Math.max(maxComponentY, y);
              }
              const componentWidth = maxComponentX - minComponentX + 1;
              const componentHeight = maxComponentY - minComponentY + 1;
              if (componentWidth >= 4 && componentHeight >= 4) {
                maxTwoDimensionalComponentArea = Math.max(
                  maxTwoDimensionalComponentArea,
                  componentWidth * componentHeight,
                );
              }
              structuredComponents += 1;
              structuredForegroundPixels += component.length;
              for (const pixelIndex of component) {
                const x = pixelIndex % sampleSize;
                const y = Math.floor(pixelIndex / sampleSize);
                const tileX = Math.min(tileGrid - 1, Math.floor(x / tileSize));
                const tileY = Math.min(tileGrid - 1, Math.floor(y / tileSize));
                structuredTileIndexes.add((tileY * tileGrid) + tileX);
              }
            }
            const structuredForegroundRatio = structuredForegroundPixels / totalPixels;
            const largestForegroundComponentRatio = (
              largestForegroundComponent / totalPixels
            );
            const edgeCounts = Array(tileGrid * tileGrid).fill(0);
            let edgePixels = 0;
            for (let y = 0; y < sampleSize; y += 1) {
              for (let x = 0; x < sampleSize; x += 1) {
                const pixelIndex = (y * sampleSize) + x;
                if (pixels[(pixelIndex * 4) + 3] <= 16) continue;
                let edgeDelta = 0;
                if (
                  x < sampleSize - 1
                  && pixels[((pixelIndex + 1) * 4) + 3] > 16
                ) {
                  edgeDelta = Math.max(
                    edgeDelta,
                    Math.abs(lumaValues[pixelIndex] - lumaValues[pixelIndex + 1]),
                  );
                }
                if (
                  y < sampleSize - 1
                  && pixels[((pixelIndex + sampleSize) * 4) + 3] > 16
                ) {
                  edgeDelta = Math.max(
                    edgeDelta,
                    Math.abs(
                      lumaValues[pixelIndex]
                      - lumaValues[pixelIndex + sampleSize],
                    ),
                  );
                }
                if (edgeDelta < 12) continue;
                edgePixels += 1;
                const tileX = Math.min(tileGrid - 1, Math.floor(x / tileSize));
                const tileY = Math.min(tileGrid - 1, Math.floor(y / tileSize));
                edgeCounts[(tileY * tileGrid) + tileX] += 1;
              }
            }
            const edgeTileIndexes = edgeCounts
              .map((count, tileIndex) => ({ count, tileIndex }))
              .filter(({ count }) => count >= 3);
            const edgeRows = new Set(
              edgeTileIndexes.map(({ tileIndex }) => Math.floor(tileIndex / tileGrid)),
            ).size;
            const edgeColumns = new Set(
              edgeTileIndexes.map(({ tileIndex }) => tileIndex % tileGrid),
            ).size;
            const edgeRatio = edgePixels / totalPixels;
            return {
              sampleSize,
              opaqueRatio,
              quantizedColors: quantizedColors.size,
              lumaStdDev,
              lumaRange,
              detailedTiles,
              totalTiles: tiles.length,
              dominantColorRatio: opaquePixels ? dominantPixels / opaquePixels : 1,
              foregroundRatio,
              foregroundTiles: foregroundTileIndexes.length,
              foregroundRows,
              foregroundColumns,
              structuredForegroundRatio,
              structuredComponents,
              structuredTiles: structuredTileIndexes.size,
              largestForegroundComponentRatio,
              maxTwoDimensionalComponentArea,
              edgeRatio,
              edgeTiles: edgeTileIndexes.length,
              edgeRows,
              edgeColumns,
              meaningful: Boolean(
                opaqueRatio >= 0.8
                && quantizedColors.size >= 8
                && lumaStdDev >= 1
                && lumaRange >= 8
                && detailedTiles >= 3
                && foregroundRatio >= 0.024
                && foregroundTileIndexes.length >= 5
                && foregroundRows >= 2
                && foregroundColumns >= 4
                && structuredForegroundRatio >= 0.0195
                && largestForegroundComponentRatio >= 0.005
                && (
                  maxTwoDimensionalComponentArea >= 28
                  || (
                    structuredForegroundRatio >= 0.05
                    && largestForegroundComponentRatio >= 0.01
                  )
                )
                && (opaquePixels ? dominantPixels / opaquePixels : 1) <= 0.973
                && edgeRatio >= 0.05
                && edgeTileIndexes.length >= 8
                && edgeRows >= 3
                && edgeColumns >= 4
              ),
            };
          };
          const isolationComparison = compare(renderedImage, isolatedImage);
          const sourceComparison = compare(
            isolatedImage,
            sourceImage,
            0.02,
            0.2,
          );
          const isolatedPixelEvidence = analyzeRenderedContent(isolatedImage);
          return {
            readable: true,
            width,
            height,
            comparedPixels: isolationComparison.comparedPixels,
            changedRatio: isolationComparison.changedRatio,
            meanDelta: isolationComparison.meanDelta,
            maximumDelta: isolationComparison.maximumDelta,
            isolationComparison,
            sourceComparison,
            isolatedPixelEvidence,
            matches: Boolean(
              isolationComparison.matches
              && sourceComparison.matches
              && isolatedPixelEvidence.meaningful
            ),
          };
        } catch (error) {
          return {
            readable: false,
            matches: false,
            error: String(error),
          };
        }
      })();
      const visibleWidth = Math.max(
        0,
        Math.min(rect.right, innerWidth) - Math.max(rect.left, 0),
      );
      const visibleHeight = Math.max(
        0,
        Math.min(rect.bottom, innerHeight) - Math.max(rect.top, 0),
      );
      const viewportCoverage = rect.width && rect.height
        ? (visibleWidth * visibleHeight) / (rect.width * rect.height)
        : 0;
      return {
        src: element.getAttribute("src"),
        alt: element.getAttribute("alt"),
        visible: rect.width > 0
          && rect.height > 0
          && style.visibility !== "hidden"
          && style.display !== "none"
          && Number.parseFloat(style.opacity || "1") > 0.05
          && ancestorsVisible
          && effectiveOpacity > 0.05
          && effectiveFilterOpacity > 0.05
          && !masked,
        opacity: Number.parseFloat(style.opacity || "1"),
        effectiveOpacity,
        effectiveFilterOpacity,
        filtered,
        masked,
        ancestorsVisible,
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        top: Math.round(rect.top),
        bottom: Math.round(rect.bottom),
        viewportHeight: innerHeight,
        containerWidth: Math.round(containerRect.width),
        ratio: containerRect.width ? rect.width / containerRect.width : 0,
        viewportRatio: innerWidth ? rect.width / innerWidth : 0,
        naturalWidth: element.naturalWidth,
        naturalHeight: element.naturalHeight,
        broken: element.complete && element.naturalWidth === 0,
        viewportCoverage,
        inViewport: viewportCoverage >= 0.9,
        pixelEvidence,
        renderedPixelMatch,
        unobscuredSamples: points.length,
        unobscuredRatio,
        legacyFiveUnobscuredRatio,
        unobscured: unobscuredPoints === points.length,
        clippedBy,
      };
    }, {
      rendered: renderedScreenshot,
      isolated: isolatedScreenshot,
      source: sourceScreenshot,
    });
    rows.push({
      ...row,
      rawSrc: liveDescriptor.rawSrc,
      canonicalPath: liveDescriptor.canonicalPath,
      currentSrcCanonicalPath: liveDescriptor.currentSrcCanonicalPath,
      status: liveDescriptor.status,
      mode: liveDescriptor.mode,
      checkpointId: liveDescriptor.checkpointId,
      srcset: liveDescriptor.srcset,
      sizes: liveDescriptor.sizes,
      pictureSources: liveDescriptor.pictureSources,
      loadError,
      sourceSha256: expected?.sha256 || null,
      inventoryIdentity: Boolean(
        expected
        && inventorySignature([liveDescriptor]) === inventorySignature([expected])
        && liveDescriptor.currentSrcCanonicalPath === expected.canonicalPath
      ),
    });
  }
  return rows;
}

async function modeSnapshot(page, mode, images) {
  return page.evaluate(({ expectedMode, inspectedImages }) => {
    const visible = (element) => {
      if (!element) return false;
      const rect = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      return rect.width > 0
        && rect.height > 0
        && style.visibility !== "hidden"
        && style.display !== "none"
        && Number.parseFloat(style.opacity || "1") > 0.05;
    };
    const panels = [...document.querySelectorAll('[role="tabpanel"][data-path]')];
    const visiblePanels = panels.filter(visible);
    const path = document.querySelector(
      `[role="tabpanel"][data-path="${expectedMode}"]`,
    );
    const opposite = document.querySelector(
      `[role="tabpanel"][data-path="${expectedMode === "easy" ? "hard" : "easy"}"]`,
    );
    const renderedDescendant = (element) => {
      const rect = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      return rect.width > 0
        && rect.height > 0
        && style.display !== "none"
        && style.visibility !== "hidden"
        && Number.parseFloat(style.opacity || "1") > 0.05;
    };
    const oppositeRenderedDescendants = opposite
      ? [...opposite.querySelectorAll("*")].filter(renderedDescendant)
      : [];
    const oppositeHitTargets = oppositeRenderedDescendants.filter((element) => {
      const rect = element.getBoundingClientRect();
      const x = Math.min(innerWidth - 1, Math.max(0, rect.left + rect.width / 2));
      const y = Math.min(innerHeight - 1, Math.max(0, rect.top + rect.height / 2));
      return document.elementsFromPoint(x, y).some(
        (candidate) => candidate === element || element.contains(candidate),
      );
    });
    const oppositeSuppressed = Boolean(
      opposite
      && opposite.hidden
      && getComputedStyle(opposite).display === "none"
      && oppositeRenderedDescendants.length === 0
      && oppositeHitTargets.length === 0
    );
    const selectedTab = document.querySelector(
      `[role="tab"][data-mode="${expectedMode}"][aria-selected="true"]`,
    );
    const semanticAnchor = expectedMode === "easy"
      ? path?.querySelector("#easy-step-4")
      : path?.querySelector(".hard-overview");
    return {
      activeMode: document.querySelector("[data-mode].active")?.getAttribute("data-mode"),
      selectedTabs: [...document.querySelectorAll('[role="tab"][aria-selected="true"]')]
        .map((element) => element.getAttribute("data-mode")),
      visiblePaths: [...document.querySelectorAll("[data-path]")]
        .filter(visible)
        .map((element) => element.getAttribute("data-path")),
      targetHidden: Boolean(path?.hidden),
      oppositeHidden: oppositeSuppressed,
      oppositeComputedDisplay: opposite ? getComputedStyle(opposite).display : null,
      oppositeRenderedDescendants: oppositeRenderedDescendants.length,
      oppositeHitTargets: oppositeHitTargets.length,
      semanticAnchor: visible(semanticAnchor),
      tabSemantics: Boolean(
        panels.length === 2
        && visiblePanels.length === 1
        && visiblePanels[0] === path
        && oppositeSuppressed
        && selectedTab
        && selectedTab.getAttribute("aria-controls") === path?.id
        && path?.getAttribute("aria-labelledby") === selectedTab.id
      ),
      images: inspectedImages,
      horizontalOverflow: Math.max(
        0,
        document.documentElement.scrollWidth - document.documentElement.clientWidth,
      ),
    };
  }, { expectedMode: mode, inspectedImages: images });
}

async function inspectQuestImageInventory(page) {
  return page.evaluate(() => {
    const rows = [...document.querySelectorAll("img")].map((image) => {
      const panel = image.closest('[role="tabpanel"][data-path]');
      const rawSrc = String(image.getAttribute("src") || "").trim();
      let canonicalPath = "";
      try {
        canonicalPath = new URL(rawSrc, document.baseURI).pathname;
      } catch (_error) {
        canonicalPath = "";
      }
      const filename = canonicalPath.split("/").pop() || "";
      const currentSource = image.currentSrc
        ? new URL(image.currentSrc, document.baseURI)
        : null;
      const picture = image.closest("picture");
      return {
        rawSrc,
        canonicalPath,
        currentSrcCanonicalPath: currentSource?.pathname || "",
        alt: String(image.getAttribute("alt") || "").trim(),
        status: image.getAttribute("data-evidence-status"),
        mode: panel?.getAttribute("data-path") || "",
        checkpointId: String(
          image.getAttribute("data-evidence-id")
          || filename.replace(/\.[^.]+$/, ""),
        ).trim(),
        srcset: String(image.getAttribute("srcset") || "").trim(),
        sizes: String(image.getAttribute("sizes") || "").trim(),
        pictureSources: picture
          ? [...picture.querySelectorAll("source")].map((source) => ({
            srcset: String(source.getAttribute("srcset") || "").trim(),
            sizes: String(source.getAttribute("sizes") || "").trim(),
            media: String(source.getAttribute("media") || "").trim(),
            type: String(source.getAttribute("type") || "").trim(),
          }))
          : [],
      };
    });
    return {
      rows,
      valid: rows.length > 0 && rows.every((row) => (
        Boolean(row.rawSrc)
        && Boolean(row.canonicalPath)
        && row.status === "reusable"
        && ["easy", "hard"].includes(row.mode)
        && row.alt.length >= 8
        && !/^(?:image|photo|screenshot|evidence)$/i.test(row.alt)
        && row.checkpointId.length >= 3
        && row.srcset === ""
        && row.sizes === ""
        && row.pictureSources.length === 0
      )),
    };
  });
}

async function captureContext(image, destination, relative) {
  const section = image.locator(
    "xpath=ancestor::*[self::article or self::section][1]",
  );
  const target = (await section.count()) ? section : image;
  const source = await target.screenshot();
  const artifact = {
    path: relative,
    bytes: source.length,
    sha256: createHash("sha256").update(source).digest("hex"),
  };
  await fs.writeFile(destination, source);
  return artifact;
}

async function fileArtifact(relative) {
  try {
    const source = await fs.readFile(path.join(out, relative));
    return {
      path: relative,
      bytes: source.length,
      sha256: createHash("sha256").update(source).digest("hex"),
    };
  } catch (error) {
    return {
      path: relative,
      bytes: 0,
      sha256: null,
      error: error.code || String(error),
    };
  }
}

async function buildContactSheet(context, mode, workshopSlugs) {
  const cards = await Promise.all(workshopSlugs.map(async (slug) => {
    const relative = `screenshots/${slug}-${mode}.png`;
    const source = await fs.readFile(path.join(out, relative));
    return {
      slug,
      source: `data:image/png;base64,${source.toString("base64")}`,
    };
  }));
  const page = await context.newPage();
  await page.setViewportSize({ width: 1500, height: 900 });
  await page.setContent(`<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * { box-sizing: border-box; }
    html, body { margin: 0; width: 1500px; background: #f3f2f1; }
    main { display: grid; grid-template-columns: repeat(3, 500px); }
    article {
      width: 500px;
      height: 350px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      overflow: hidden;
    }
    img {
      display: block;
      max-width: 480px;
      max-height: 300px;
      object-fit: contain;
    }
    p {
      margin: 0;
      height: 26px;
      color: #1b1a19;
      font: 16px/26px Arial, sans-serif;
      text-align: center;
    }
  </style>
</head>
<body>
  <main>
    ${cards.map(({ slug, source }) => (
    `<article><img src="${source}" alt=""><p>${slug}</p></article>`
  )).join("")}
  </main>
</body>
</html>`, { waitUntil: "load" });
  await page.evaluate(() => Promise.all(
    [...document.images].map((image) => image.decode()),
  ));
  const source = await page.screenshot({
    fullPage: true,
    type: "jpeg",
    quality: 92,
  });
  await page.close();
  const relative = `${mode}-contact-sheet.jpg`;
  const artifact = {
    path: relative,
    bytes: source.length,
    sha256: createHash("sha256").update(source).digest("hex"),
  };
  await fs.writeFile(path.join(out, relative), source);
  return artifact;
}

await fs.mkdir(path.join(out, "screenshots"), { recursive: true });
const browser = await chromium.launch({ headless: true });
const browserVersion = browser.version();
const rejectedExternalRequests = new Set();
const rejectedWebSocketRequests = new Set();
const auditContext = await browser.newContext({
  viewport: { width: 1440, height: 1000 },
  serviceWorkers: "block",
});
await auditContext.addInitScript(() => {
  const attempts = [];
  Object.defineProperty(window, "__aibastAuditServiceWorkerAttempts", {
    configurable: false,
    get: () => attempts.map((attempt) => ({ ...attempt })),
  });
  const recordAttempt = (scriptURL, options) => {
    attempts.push({
      scriptURL: String(scriptURL),
      scope: String(options?.scope || ""),
      type: String(options?.type || "classic"),
    });
  };
  const container = navigator.serviceWorker;
  if (!container) {
    const blockedContainer = Object.freeze({
      register(scriptURL, options) {
        recordAttempt(scriptURL, options);
        return Promise.reject(new DOMException(
          "Service workers are blocked by the browser audit",
          "SecurityError",
        ));
      },
    });
    Object.defineProperty(navigator, "serviceWorker", {
      configurable: false,
      get: () => blockedContainer,
    });
    return;
  }
  const originalRegister = container.register.bind(container);
  Object.defineProperty(container, "register", {
    configurable: false,
    writable: false,
    value(scriptURL, options) {
      recordAttempt(scriptURL, options);
      return originalRegister(scriptURL, options);
    },
  });
});
await auditContext.route("**/*", async (route) => {
  const requestUrl = new URL(route.request().url());
  if (
    ["about:", "blob:", "data:"].includes(requestUrl.protocol)
    || requestUrl.origin === baseUrl
  ) {
    await route.continue();
    return;
  }
  rejectedExternalRequests.add(requestUrl.href);
  await route.abort("blockedbyclient");
});
await auditContext.routeWebSocket(/.*/, async (webSocket) => {
  rejectedWebSocketRequests.add(webSocket.url());
  await webSocket.close({
    code: 1008,
    reason: "Browser audit blocks all WebSocket connections",
  });
});
const sourcePage = await auditContext.newPage();
const results = [];

for (const slug of slugs) {
  const page = await auditContext.newPage();
  await page.setViewportSize({ width: 1440, height: 1000 });
  const errors = [];
  const easyScreenshotRelative = `screenshots/${slug}-easy.png`;
  const hardScreenshotRelative = `screenshots/${slug}-hard.png`;
  await Promise.all([
    fs.rm(path.join(out, easyScreenshotRelative), { force: true }),
    fs.rm(path.join(out, hardScreenshotRelative), { force: true }),
  ]);
  const expectedPath = `/solutions/${slug}/quest.html`;
  const expectedQuestInventory = await expectedQuestImageInventory(page, slug);
  const expectedEasyRows = expectedQuestInventory.rows.filter(
    (row) => row.mode === "easy",
  );
  const expectedHardRows = expectedQuestInventory.rows.filter(
    (row) => row.mode === "hard",
  );
  const deploymentRelative = path.join("solutions", slug, "deployment.json");
  const deployment = JSON.parse(
    auditedInputContents.get(deploymentRelative).toString("utf8"),
  );
  const expectedTitle = deployment.display_name;
  const catalogRecord = catalogBySlug.get(slug);
  const catalogIdentity = Boolean(
    catalogRecord
    && catalogRecord.catalog_display_name === expectedTitle
    && catalogRecord.catalog_name === deployment.name
  );
  page.on("pageerror", (error) => errors.push(String(error)));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  const response = await page.goto(
    `${baseUrl}${expectedPath}`,
    { waitUntil: "networkidle" },
  );
  await page.evaluate(() => {
    document.documentElement.style.scrollBehavior = "auto";
    document.body.style.scrollBehavior = "auto";
  });
  const responseHeaders = response?.headers() || {};
  const provenance = Boolean(
    responseHeaders["x-aibast-audit-sha"] === gitSha
    && responseHeaders["x-aibast-audit-inputs"] === auditedInputs.sha256
    && new URL(page.url()).pathname === expectedPath
  );
  const identity = await page.evaluate(
    ({ expectedSlug, title }) => ({
      slug: document.body.dataset.workshopSlug === expectedSlug,
      title: document.querySelector("main h1")?.textContent?.trim() === title,
    }),
    { expectedSlug: slug, title: expectedTitle },
  );
  const mission = await page.locator("body").innerText().then((text) => text.includes(
    "Turn motivated, open-minded, non-technical sales professionals into AI superheroes",
  ));
  const questImageInventory = await inspectQuestImageInventory(page);
  const questInventoryMatches = Boolean(
    expectedQuestInventory.valid
    && questImageInventory.valid
    && inventorySignature(questImageInventory.rows)
      === inventorySignature(expectedQuestInventory.rows)
  );
  const referenceOnly = await page.locator(
    'img[data-evidence-status="reference-only"]',
  ).count();

  const easyTab = page.getByRole("tab", { name: "Easy", exact: true });
  await easyTab.click();
  await page.waitForFunction((mode) => {
    const selected = [...document.querySelectorAll('[role="tab"][aria-selected="true"]')]
      .map((element) => element.getAttribute("data-mode"));
    return document.querySelector(`[data-mode="${mode}"]`)?.classList.contains("active")
      && selected.length === 1
      && selected[0] === mode
      && document.querySelector(`[data-path="${mode}"]`)?.hidden === false
      && document.querySelector(`[data-path="${mode === "easy" ? "hard" : "easy"}"]`)?.hidden;
  }, "easy");
  const easyImages = await inspectModeImages(
    page,
    sourcePage,
    "easy",
    expectedEasyRows,
  );
  const easy = await modeSnapshot(page, "easy", easyImages);
  const desktopEasyInventory = await inspectQuestImageInventory(page);
  const easyImage = page.locator(
    '[data-path="easy"] img[data-evidence-status="reusable"]',
  ).first();
  const easyFallback = page.locator(
    '[data-path="easy"] .withheld-checkpoint',
  ).first();
  let easyCaptureArtifact = null;
  if (easyImages.length) {
    await easyImage.scrollIntoViewIfNeeded();
    easyCaptureArtifact = await captureContext(
      easyImage,
      path.join(out, easyScreenshotRelative),
      easyScreenshotRelative,
    );
  } else if (await easyFallback.count()) {
    await easyFallback.scrollIntoViewIfNeeded();
    easyCaptureArtifact = await captureContext(
      easyFallback,
      path.join(out, easyScreenshotRelative),
      easyScreenshotRelative,
    );
  }

  const hardTab = page.getByRole("tab", { name: "Hard", exact: true });
  await hardTab.click();
  await page.waitForFunction((mode) => {
    const selected = [...document.querySelectorAll('[role="tab"][aria-selected="true"]')]
      .map((element) => element.getAttribute("data-mode"));
    return document.querySelector(`[data-mode="${mode}"]`)?.classList.contains("active")
      && selected.length === 1
      && selected[0] === mode
      && document.querySelector(`[data-path="${mode}"]`)?.hidden === false
      && document.querySelector(`[data-path="${mode === "easy" ? "hard" : "easy"}"]`)?.hidden;
  }, "hard");
  const hardImages = await inspectModeImages(
    page,
    sourcePage,
    "hard",
    expectedHardRows,
  );
  const hard = await modeSnapshot(page, "hard", hardImages);
  const desktopHardInventory = await inspectQuestImageInventory(page);
  const hardImage = page.locator(
    '[data-path="hard"] img[data-evidence-status="reusable"]',
  ).first();
  let hardCaptureArtifact = null;
  if (hardImages.length) {
    await hardImage.scrollIntoViewIfNeeded();
    hardCaptureArtifact = await captureContext(
      hardImage,
      path.join(out, hardScreenshotRelative),
      hardScreenshotRelative,
    );
  }

  const easySources = easy.images.map((image) => image.rawSrc);
  const hardSources = hard.images.map((image) => image.rawSrc);
  const sourceOverlap = easySources.filter((source) => hardSources.includes(source));
  const easyContentHashes = easy.images.map((image) => image.sourceSha256);
  const hardContentHashes = hard.images.map((image) => image.sourceSha256);
  const contentOverlap = easyContentHashes.filter(
    (sha256) => sha256 && hardContentHashes.includes(sha256),
  );
  const visualOverlap = visualIdentityOverlap(easy.images, hard.images);
  const inspectedInventory = [...easy.images, ...hard.images];
  const completeImageInventory = Boolean(
    questInventoryMatches
    && inventorySignature(inspectedInventory)
      === inventorySignature(expectedQuestInventory.rows)
    && inspectedInventory.every((image) => image.inventoryIdentity)
  );
  const distinctModes = Boolean(
    easy.activeMode === "easy"
    && hard.activeMode === "hard"
    && easy.selectedTabs.length === 1
    && easy.selectedTabs[0] === "easy"
    && hard.selectedTabs.length === 1
    && hard.selectedTabs[0] === "hard"
    && easy.visiblePaths.length === 1
    && easy.visiblePaths[0] === "easy"
    && hard.visiblePaths.length === 1
    && hard.visiblePaths[0] === "hard"
    && !easy.targetHidden
    && !hard.targetHidden
    && easy.oppositeHidden
    && hard.oppositeHidden
    && easy.semanticAnchor
    && hard.semanticAnchor
    && easy.tabSemantics
    && hard.tabSemantics
    && (easySources.length > 0 || expectedEasyRows.length === 0)
    && hardSources.length > 0
    && sourceOverlap.length === 0
    && contentOverlap.length === 0
    && visualOverlap.length === 0
  );

  await page.setViewportSize({ width: 390, height: 844 });
  await easyTab.click();
  await page.waitForFunction(() => (
    document.querySelector('[data-mode="easy"][aria-selected="true"]')
    && document.querySelector('[data-path="easy"]')?.hidden === false
    && document.querySelector('[data-path="hard"]')?.hidden
  ));
  const mobileEasyImages = await inspectModeImages(
    page,
    sourcePage,
    "easy",
    expectedEasyRows,
  );
  const mobileEasy = await modeSnapshot(page, "easy", mobileEasyImages);
  const mobileEasyInventory = await inspectQuestImageInventory(page);
  await hardTab.click();
  await page.waitForFunction(() => (
    document.querySelector('[data-mode="hard"][aria-selected="true"]')
    && document.querySelector('[data-path="hard"]')?.hidden === false
    && document.querySelector('[data-path="easy"]')?.hidden
  ));
  const mobileHardImages = await inspectModeImages(
    page,
    sourcePage,
    "hard",
    expectedHardRows,
  );
  const mobileHard = await modeSnapshot(page, "hard", mobileHardImages);
  const mobileHardInventory = await inspectQuestImageInventory(page);

  const desktopRows = [...easy.images, ...hard.images];
  const desktopImageFailures = desktopRows.filter((image) => (
    !image.inventoryIdentity
    || Boolean(image.loadError)
    || !image.visible
    || !image.ancestorsVisible
    || image.effectiveOpacity < 0.5
    || image.effectiveFilterOpacity < 0.5
    || image.filtered
    || image.masked
    || image.broken
    || image.naturalWidth === 0
    || !image.pixelEvidence?.meaningful
    || !image.renderedPixelMatch?.matches
    || image.width < 640
    || image.height < 250
    || image.ratio < 0.85
    || image.viewportRatio < 0.4
    || image.viewportCoverage < 0.9
    || !image.unobscured
    || image.clippedBy.length > 0
  ));
  const mobileRows = [...mobileEasy.images, ...mobileHard.images];
  const mobileImageFailures = mobileRows.filter((image) => (
    !image.inventoryIdentity
    || Boolean(image.loadError)
    || !image.visible
    || !image.ancestorsVisible
    || image.effectiveOpacity < 0.5
    || image.effectiveFilterOpacity < 0.5
    || image.filtered
    || image.masked
    || image.broken
    || image.naturalWidth === 0
    || !image.pixelEvidence?.meaningful
    || !image.renderedPixelMatch?.matches
    || image.width < 280
    || image.height < 120
    || image.ratio < 0.85
    || image.viewportRatio < 0.72
    || image.viewportCoverage < 0.9
    || !image.unobscured
    || image.clippedBy.length > 0
  ));
  const mobileEasySources = mobileEasy.images.map((image) => image.rawSrc);
  const mobileHardSources = mobileHard.images.map((image) => image.rawSrc);
  const inventoryStable = Boolean(
    inventorySignature(easy.images) === inventorySignature(mobileEasy.images)
    && inventorySignature(hard.images) === inventorySignature(mobileHard.images)
    && JSON.stringify(easyContentHashes)
      === JSON.stringify(mobileEasy.images.map((image) => image.sourceSha256))
    && JSON.stringify(hardContentHashes)
      === JSON.stringify(mobileHard.images.map((image) => image.sourceSha256))
  );
  const expectedInventorySignature = inventorySignature(expectedQuestInventory.rows);
  const dynamicImageInventory = [
    desktopEasyInventory,
    desktopHardInventory,
    mobileEasyInventory,
    mobileHardInventory,
  ].every((inventory) => (
    inventory.valid
    && inventorySignature(inventory.rows) === expectedInventorySignature
  ));
  const serviceWorkerAttempts = await page.evaluate(
    () => window.__aibastAuditServiceWorkerAttempts || [],
  );
  const screenshotArtifacts = [
    easyCaptureArtifact || {
      path: easyScreenshotRelative,
      bytes: 0,
      sha256: null,
      error: "Easy screenshot was not captured",
    },
    hardCaptureArtifact || {
      path: hardScreenshotRelative,
      bytes: 0,
      sha256: null,
      error: "Hard screenshot was not captured",
    },
  ];
  const writtenScreenshotArtifacts = await Promise.all([
    fileArtifact(easyScreenshotRelative),
    fileArtifact(hardScreenshotRelative),
  ]);
  const screenshotsBound = screenshotArtifacts.every(
    (artifact) => artifact.bytes > 0
      && typeof artifact.sha256 === "string"
      && artifact.sha256.length === 64,
  ) && JSON.stringify(screenshotArtifacts)
    === JSON.stringify(writtenScreenshotArtifacts);
  const passed = Boolean(
    response?.ok()
    && provenance
    && catalogIdentity
    && identity.slug
    && identity.title
    && mission
    && completeImageInventory
    && referenceOnly === 0
    && distinctModes
    && mobileEasy.tabSemantics
    && mobileHard.tabSemantics
    && mobileEasy.semanticAnchor
    && mobileHard.semanticAnchor
    && inventoryStable
    && dynamicImageInventory
    && desktopImageFailures.length === 0
    && mobileImageFailures.length === 0
    && easy.horizontalOverflow <= 4
    && hard.horizontalOverflow <= 4
    && mobileEasy.horizontalOverflow <= 4
    && mobileHard.horizontalOverflow <= 4
    && serviceWorkerAttempts.length === 0
    && screenshotsBound
    && errors.length === 0
  );
  results.push({
    slug,
    passed,
    status: response?.status(),
    provenance,
    catalogIdentity,
    identity,
    mission,
    expectedQuestInventory,
    questImageInventory,
    questInventoryMatches,
    completeImageInventory,
    dynamicImageInventory,
    serviceWorkerAttempts,
    screenshotArtifacts,
    writtenScreenshotArtifacts,
    screenshotsBound,
    referenceOnly,
    easy,
    hard,
    mobileEasy,
    mobileHard,
    distinctModes,
    inventoryStable,
    sourceOverlap,
    contentOverlap,
    visualOverlap,
    desktopImageFailures,
    mobileImageFailures,
    errors,
    capturedEasy: Boolean(easyCaptureArtifact),
    capturedHard: Boolean(hardImages.length),
  });
  await page.close();
}

const contactSheetArtifacts = await Promise.all([
  buildContactSheet(auditContext, "easy", slugs),
  buildContactSheet(auditContext, "hard", slugs),
]);
await sourcePage.close();
const observedServiceWorkers = auditContext.serviceWorkers()
  .map((worker) => worker.url())
  .sort();
await auditContext.close();
await browser.close();
await new Promise((resolve) => server.close(resolve));
const finalAuditedInputs = await digestCurrentAuditedInputs(
  auditedInputSnapshot.relativePaths,
);
const auditedInputsUnchanged = Boolean(
  finalAuditedInputs.errors.length === 0
  && finalAuditedInputs.files === auditedInputs.files
  && finalAuditedInputs.bytes === auditedInputs.bytes
  && finalAuditedInputs.sha256 === auditedInputs.sha256
);
const immutableSnapshotComplete = Boolean(
  rejectedSnapshotRequests.size === 0
  && rejectedExternalRequests.size === 0
  && rejectedWebSocketRequests.size === 0
  && observedServiceWorkers.length === 0
);
if (!auditedInputsUnchanged || !immutableSnapshotComplete) {
  for (const result of results) {
    result.passed = false;
    result.provenance = false;
    if (!auditedInputsUnchanged) {
      result.errors.push("Audited inputs changed during the browser audit");
    }
    if (!immutableSnapshotComplete) {
      result.errors.push("A browser request escaped the immutable audit snapshot");
    }
  }
}
const report = {
  schema: "aibast-browser-visual-audit/4.8",
  repository: "microsoft/aibast-agents-library",
  repository_root: ".",
  git_sha: gitSha,
  git_dirty: Boolean(gitStatus.trim()),
  git_status_sha256: gitStatusSha256,
  audited_inputs: auditedInputs,
  final_audited_inputs: finalAuditedInputs,
  audited_inputs_unchanged: auditedInputsUnchanged,
  certification_basis: "immutable byte snapshot, immutable static evidence inventory, stylesheet-free source render, and content-addressed gate scripts",
  snapshot_manifest: {
    path: "audited-snapshot-manifest.json",
    sha256: auditedInputSnapshot.manifestSha256,
  },
  immutable_snapshot_complete: immutableSnapshotComplete,
  rejected_snapshot_requests: [...rejectedSnapshotRequests].sort(),
  rejected_external_requests: [...rejectedExternalRequests].sort(),
  rejected_websocket_requests: [...rejectedWebSocketRequests].sort(),
  service_workers_policy: "block",
  observed_service_workers: observedServiceWorkers,
  registry_urls_verified: true,
  advertised_total: catalogSlugs.length,
  excluded_non_advertised: excludedNonAdvertised,
  server_base: "immutable-local-http",
  execution_environment: {
    node: process.version,
    platform: process.platform,
    arch: process.arch,
    chromium: browserVersion,
  },
  total: results.length,
  passed: results.filter((row) => row.passed).length,
  failed: results.filter((row) => !row.passed).length,
  screenshot_artifacts: results.flatMap((row) => row.screenshotArtifacts),
  contact_sheet_artifacts: contactSheetArtifacts,
  results,
};
await fs.writeFile(
  path.join(out, "audited-snapshot-manifest.json"),
  auditedInputSnapshot.manifestJson,
);
await fs.writeFile(
  path.join(out, "browser-audit.json"),
  `${JSON.stringify(report, null, 2)}\n`,
);
console.log(JSON.stringify({
  total: report.total,
  passed: report.passed,
  failed: report.failed,
  failures: results.filter((row) => !row.passed).map((row) => row.slug),
}));
process.exit(report.failed ? 1 : 0);
