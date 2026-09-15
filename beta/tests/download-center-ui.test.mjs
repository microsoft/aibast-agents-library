import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const betaRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const page = readFileSync(path.join(betaRoot, "index.html"), "utf8").replace(
  /\r\n/g,
  "\n",
);
const downloadCenter = readFileSync(
  path.join(betaRoot, "download-center.js"),
  "utf8",
).replace(/\r\n/g, "\n");
const scripts = [...page.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((match) => match[1]);
const style = page.match(/<style>([\s\S]*?)<\/style>/)?.[1] || "";
const unsupportedWindowsArchitecture = `ARM${64}`;
const requiredThemeTokens = [
  "--cp-accent",
  "--cp-accent-fg",
  "--cp-accent-hover",
  "--cp-accent-soft",
  "--cp-bg",
  "--cp-bg-elevated",
  "--cp-border",
  "--cp-border-strong",
  "--cp-danger",
  "--cp-highlight",
  "--cp-link",
  "--cp-overlay",
  "--cp-panel",
  "--cp-panel-strong",
  "--cp-shadow",
  "--cp-sheen",
  "--cp-success",
  "--cp-surface",
  "--cp-surface-soft",
  "--cp-text",
  "--cp-text-muted",
  "--cp-text-soft",
  "--cp-warning",
];

function extractTokenBlock(css, selector) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const block = css.match(new RegExp(`${escaped}\\s*\\{([\\s\\S]*?)\\n    \\}`))?.[1] || "";
  return Object.fromEntries(
    [...block.matchAll(/(--cp-[\w-]+):\s*([^;]+);/g)].map((match) => [
      match[1],
      match[2].trim(),
    ]),
  );
}

function relativeLuminance(hex) {
  const channels = hex
    .slice(1)
    .match(/.{2}/g)
    .map((value) => Number.parseInt(value, 16) / 255)
    .map((value) =>
      value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4,
    );
  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
}

function contrastRatio(first, second) {
  const values = [relativeLuminance(first), relativeLuminance(second)];
  return (Math.max(...values) + 0.05) / (Math.min(...values) + 0.05);
}

function tokenContrastFailures(css) {
  const light = extractTokenBlock(css, ":root");
  const dark = extractTokenBlock(css, 'html[data-theme="dark"]');
  const checks = [
    ["light border/background", light["--cp-border"], light["--cp-bg"], 3],
    ["light strong border/surface", light["--cp-border-strong"], light["--cp-surface"], 3],
    ["light muted text/background", light["--cp-text-muted"], light["--cp-bg"], 4.5],
    ["light soft text/background", light["--cp-text-soft"], light["--cp-bg"], 4.5],
    ["light link/background", light["--cp-link"], light["--cp-bg"], 4.5],
    ["dark border/background", dark["--cp-border"], dark["--cp-bg"], 3],
    ["dark strong border/background", dark["--cp-border-strong"], dark["--cp-bg"], 3],
    ["dark muted text/background", dark["--cp-text-muted"], dark["--cp-bg"], 4.5],
    ["dark soft text/background", dark["--cp-text-soft"], dark["--cp-bg"], 4.5],
    ["dark link/background", dark["--cp-link"], dark["--cp-bg"], 4.5],
  ];
  return checks
    .filter(([, foreground, background, floor]) => {
      if (!/^#[\da-f]{6}$/i.test(foreground || "")) return true;
      if (!/^#[\da-f]{6}$/i.test(background || "")) return true;
      return contrastRatio(foreground, background) < floor;
    })
    .map(([name]) => name);
}

function removeCssBlock(source, selector) {
  const start = source.indexOf(selector);
  if (start === -1) return source;
  const openingBrace = source.indexOf("{", start);
  if (openingBrace === -1) return source;

  let depth = 0;
  for (let index = openingBrace; index < source.length; index += 1) {
    if (source[index] === "{") depth += 1;
    if (source[index] === "}") depth -= 1;
    if (depth === 0) {
      return `${source.slice(0, start)}${source.slice(index + 1)}`;
    }
  }
  return source;
}

function validateDownloadCenter(source, logic = downloadCenter) {
  const issues = [];
  const css = source.match(/<style>([\s\S]*?)<\/style>/)?.[1] || "";
  const add = (condition, issue) => {
    if (!condition) issues.push(issue);
  };

  add(
    /<main id="main-content" tabindex="-1">/.test(source),
    "skip link target must be programmatically focusable",
  );
  add(
    /class="release-chip" role="status" aria-live="polite" aria-atomic="true"/.test(source),
    "release state must be announced",
  );
  add(
    /id="platform-select" name="platform" aria-describedby="platform-help"/.test(source) &&
      /id="architecture-select"[\s\S]*?aria-describedby="platform-help"/.test(source) &&
      /id="platform-help" role="status" aria-live="polite"/.test(source),
    "platform and architecture guidance must be associated and announced",
  );
  add(
    source.includes('id="release-status">Checking Frontier release</span>') &&
      source.includes('id="release-version">Resolving</dd>') &&
      /id="download-button" type="submit" disabled/.test(source) &&
      source.includes("Checking the release and available downloads.") &&
      logic.includes('elements.status.textContent = "Checking Frontier release"'),
    "initial release state must remain truthfully unresolved",
  );
  add(
    /id="download-dialog"[\s\S]*?aria-describedby="download-dialog-description"/.test(source) &&
      /id="download-dialog-description"/.test(source),
    "dialog must have an accessible description",
  );
  add(
    /id="copy-status" class="visually-hidden" role="status" aria-live="polite"/.test(source),
    "copy confirmation must use a live status",
  );
  add(
    source.includes('id="no-js-download"') &&
      source.includes('href="frontier.ps1"') &&
      source.includes('href="frontier.sh"') &&
      /id="source-link"\s+href="https:\/\/github\.com\/microsoft\/aibast-agents-library\/tree\/main\/beta"/.test(
        source,
      ) &&
      /id="release-link-top"\s+href="https:\/\/github\.com\/microsoft\/aibast-agents-library\/releases"/.test(
        source,
      ) &&
      !/id="(?:source-link|release-link-top|release-link-bottom|windows-script|unix-script)"[^>]*href="#"/.test(
        source,
      ) &&
      !/id="panel-(?:requirements|install|additional)"[^>]*hidden/.test(source) &&
      logic.includes("setAccordionState("),
    "no-JS users must retain direct downloads, links, and visible details",
  );
  add(
    source.includes('id="recovery-panel"') &&
      source.includes('id="recovery-windows-link"') &&
      source.includes('id="recovery-unix-link"') &&
      logic.includes("showRecoveryPanel(elements, inspectionDownloads)") &&
      logic.includes("source recovery options below"),
    "API failures must expose immediate source recovery",
  );
  add(
    source.includes('id="golden-path-link"') &&
      source.includes(
        'href="https://github.com/microsoft/aibast-agents-library/blob/main/beta/GOLDEN_PATH.md"',
      ) &&
      !source.includes('href="GOLDEN_PATH.md"') &&
      logic.includes('goldenPathLink: requireElement(documentObject, "golden-path-link")') &&
      logic.includes("setFunctionalLink(elements.goldenPathLink, release.goldenPathUrl)") &&
      logic.includes("goldenPathUrl(repository, tag)"),
    "golden path link must remain Pages-safe and release-pinned",
  );
  add(
    source.includes("<span>Windows 11 x64, macOS, and Linux</span>") &&
      source.includes('<option value="windows">Windows 11 x64</option>') &&
    /<span class="os-pill" id="windows-support">Windows 11 x64<\/span>/.test(source) &&
      /<span class="platform-icon" aria-hidden="true">PS<\/span>\s*Windows 11 x64/.test(
        source,
      ) &&
    logic.includes('windows: "Windows 11 x64"') &&
    logic.includes('architectures: ["x64"]') &&
    logic.includes('(platform === "windows" && architecture !== "x64")') &&
    !new RegExp(
      `Windows 11[^"<\\n]*${unsupportedWindowsArchitecture}`,
      "i",
      ).test(source),
    "Windows support copy must remain x64-only",
  );
  add(
    source.includes("<strong>Commit-pinned source bootstraps</strong>") &&
      /Application signature and native installation verification are not claimed\s+for this preview\./.test(
        source,
      ) &&
      source.includes("Windows Defender SmartScreen warnings may still appear") &&
      /The bootstrap does not suppress\s+or remove those warnings\./.test(source) &&
      !/Verified release downloads|verified source bootstrap|same verified Frontier release|verified release commit/i.test(
        source,
      ),
    "release wording must not overclaim verification or suppress Windows warnings",
  );
  add(
    source.includes('id="source-status" class="source-status"') &&
      logic.includes('code: "SOURCE_ONLY_RELEASE"') &&
      logic.includes("This release is source-only.") &&
      !logic.includes(
        'code: "SOURCE_ONLY_RELEASE",\n        message: "This release does not publish the required binary provenance manifest."',
      ),
    "expected source-only releases must use calm explanatory status",
  );
  add(
    /id="release-files" class="release-file-list"/.test(source) &&
      logic.includes("releaseFileSummary(items)") &&
      logic.includes('entry.className = "release-file-entry"'),
    "release file summaries must pair filenames with sizes",
  );
  for (const id of ["frontier-guide-link", "security-link", "license-link"]) {
    add(
      new RegExp(`<a(?=[^>]*id="${id}")(?=[^>]*https://github\\.com/)[^>]*>`).test(source),
      `${id} must use a rendered GitHub URL`,
    );
  }
  add(
    /id="expand-all"[\s\S]*?aria-controls="panel-details panel-requirements panel-install panel-additional"[\s\S]*?aria-expanded="false"/.test(
      source,
    ),
    "expand-all state must be exposed",
  );

  for (const name of ["details", "requirements", "install", "additional"]) {
    add(
      new RegExp(
        `id="trigger-${name}"[\\s\\S]*?aria-controls="panel-${name}"[\\s\\S]*?<div[^>]*id="panel-${name}"[^>]*role="region"[^>]*aria-labelledby="trigger-${name}"`,
      ).test(source),
      `accordion ${name} must associate its trigger and region`,
    );
  }

  for (const key of ["ArrowDown", "ArrowUp", "Home", "End"]) {
    add(
      logic.includes(`case "${key}":`),
      `accordion keyboard support must include ${key}`,
    );
  }
  add(
    /trigger\.addEventListener\("keydown"/.test(logic),
    "accordion triggers must handle roving keyboard focus",
  );
  add(
    /querySelector\(\s*'input\[name="download-file"\]:checked'[\s\S]*?\.focus\(\)/.test(logic),
    "dialog must focus the selected download option",
  );
  add(
    /elements\.dialog\.addEventListener\("keydown"[\s\S]*?event\.key !== "Tab"[\s\S]*?getClientRects\(\)\.length > 0/.test(
      logic,
    ),
    "dialog must keep Tab focus within visible controls",
  );
  add(
    !logic.includes("offsetParent"),
    "visibility checks must not use offsetParent",
  );
  add(
    /elements\.expandAll\.setAttribute\("aria-expanded", String\(allOpen\)\)/.test(logic),
    "expand-all aria state must stay synchronized",
  );

  add(
    /\.brand,\s*\.context-label,\s*\.header-nav a,\s*\.resource-links a,\s*\.footer-links a\s*\{[^}]*min-height:\s*44px;/s.test(
      css,
    ),
    "compact navigation targets must be at least 44px tall",
  );
  add(
    /\.dialog-close\s*\{[^}]*width:\s*44px;[^}]*height:\s*44px;/s.test(css),
    "dialog close target must be 44px square",
  );
  add(
    /\.install-card\s*\{[^}]*min-width:\s*0;/s.test(css) &&
      /\.command\s*\{[^}]*width:\s*100%;[^}]*max-width:\s*100%;/s.test(css),
    "command cards must be allowed to shrink",
  );
  add(
    /@media \(max-width: 680px\)[\s\S]*?\.command\s*\{[^}]*white-space:\s*pre-wrap;[^}]*overflow-wrap:\s*anywhere;/s.test(
      css,
    ),
    "mobile commands must wrap without horizontal overflow",
  );
  add(
    /\.download-controls\s*\{[^}]*min-width:\s*0;/s.test(css) &&
      /select\s*\{[^}]*min-width:\s*0;[^}]*text-overflow:\s*ellipsis;/s.test(css),
    "download selectors must shrink without clipping",
  );
  add(
    /@media \(prefers-reduced-motion: reduce\)/.test(css) &&
      /scroll-behavior:\s*auto;/.test(css),
    "reduced-motion users must not receive smooth scrolling",
  );
  add(
    /:focus-visible\s*\{[^}]*outline:\s*3px solid var\(--cp-link\);/s.test(css),
    "focus indicator must use the high-contrast link token",
  );
  add(
    tokenContrastFailures(css).length === 0,
    "theme tokens must meet text and non-text contrast floors",
  );

  let nonTokenCss = removeCssBlock(css, ":root");
  nonTokenCss = removeCssBlock(nonTokenCss, 'html[data-theme="dark"]');
  add(
    !/(?:#[\da-f]{3,8}\b|rgba?\(|hsla?\()/i.test(nonTokenCss),
    "literal colors must stay inside the --cp-* token blocks",
  );

  return issues;
}

test("mandatory Clawpilot theme script and token names remain intact", () => {
  assert.ok(scripts.length >= 1);
  assert.equal(
    createHash("sha256").update(scripts[0]).digest("hex"),
    "2ac85d6a736048e9279c88c6161a28c93927621ff593e437d4fa77f3ad5b3f3f",
  );
  const lightTokens = Object.keys(extractTokenBlock(style, ":root")).sort();
  const darkTokens = Object.keys(extractTokenBlock(style, 'html[data-theme="dark"]')).sort();
  assert.deepEqual(lightTokens, requiredThemeTokens);
  assert.deepEqual(darkTokens, requiredThemeTokens);
  assert.deepEqual(tokenContrastFailures(style), []);
  assert.match(page, /<script type="module" src="download-center\.js"><\/script>/);
});

test("download center encodes the responsive accessibility contract", () => {
  assert.deepEqual(validateDownloadCenter(page), []);
});

test("download center UI checks reject representative regressions", () => {
  const mutations = [
    {
      expected: "initial release state must remain truthfully unresolved",
      source: page.replace("Checking Frontier release", "Source downloads ready"),
    },
    {
      expected: "dialog must have an accessible description",
      source: page.replace(' aria-describedby="download-dialog-description"', ""),
    },
    {
      expected: "no-JS users must retain direct downloads, links, and visible details",
      source: page.replace('id="no-js-download"', 'id="no-js-download-broken"'),
    },
    {
      expected: "mobile commands must wrap without horizontal overflow",
      source: page.replace("white-space: pre-wrap;", "white-space: pre;"),
    },
    {
      expected: "download selectors must shrink without clipping",
      source: page.replace(
        "grid-template-columns: minmax(0, 1.15fr) minmax(8.5rem, 0.85fr) auto;",
        "grid-template-columns: minmax(0, 1fr) auto;",
      ).replace("      min-width: 0;\n", ""),
    },
    {
      expected: "accordion keyboard support must include ArrowDown",
      source: page,
      logic: downloadCenter.replace('case "ArrowDown":', 'case "PageDown":'),
    },
    {
      expected: "dialog must keep Tab focus within visible controls",
      source: page,
      logic: downloadCenter.replace('event.key !== "Tab"', 'event.key !== "Enter"'),
    },
    {
      expected: "golden path link must remain Pages-safe and release-pinned",
      source: page.replace(
        'href="https://github.com/microsoft/aibast-agents-library/blob/main/beta/GOLDEN_PATH.md"',
        'href="GOLDEN_PATH.md"',
      ),
    },
    {
      expected: "Windows support copy must remain x64-only",
      source: page,
      logic: downloadCenter.replace(
        'architectures: ["x64"]',
        `architectures: ["x64", "arm${64}"]`,
      ),
    },
    {
      expected: "release wording must not overclaim verification or suppress Windows warnings",
      source: page.replace(
        "<strong>Commit-pinned source bootstraps</strong>",
        "<strong>Verified release downloads</strong>",
      ),
    },
    {
      expected: "release wording must not overclaim verification or suppress Windows warnings",
      source: page.replace(
        "Windows Defender SmartScreen warnings may still appear",
        "Windows setup is warning-free",
      ),
    },
    {
      expected: "literal colors must stay inside the --cp-* token blocks",
      source: page.replace("background: var(--cp-bg);", "background: #000;"),
    },
    {
      expected: "theme tokens must meet text and non-text contrast floors",
      source: page.replace("--cp-border: #858585;", "--cp-border: #dedede;"),
    },
    {
      expected: "accordion details must associate its trigger and region",
      source: page.replace(
        '              id="panel-details"\n              role="region"',
        '              id="panel-details"',
      ),
    },
  ];

  for (const mutation of mutations) {
    assert.ok(
      validateDownloadCenter(
        mutation.source,
        mutation.logic || downloadCenter,
      ).includes(mutation.expected),
      `mutation was not detected: ${mutation.expected}`,
    );
  }
});

test("download center UI checks are stable with CRLF source", () => {
  const crlfPage = page.replace(/\n/g, "\r\n");
  const normalizedPage = crlfPage.replace(/\r\n/g, "\n");
  assert.equal(normalizedPage, page);
  assert.deepEqual(validateDownloadCenter(normalizedPage), []);

  const mutated = normalizedPage.replace(
    "white-space: pre-wrap;",
    "white-space: pre;",
  );
  assert.ok(
    validateDownloadCenter(mutated).includes(
      "mobile commands must wrap without horizontal overflow",
    ),
  );
});

test("all inline scripts remain valid JavaScript", () => {
  for (const source of scripts) {
    assert.doesNotThrow(() => new Function(source));
  }
});
