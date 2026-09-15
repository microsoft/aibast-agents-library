import fs from "node:fs/promises";
import { constants as fsConstants } from "node:fs";
import http from "node:http";
import path from "node:path";
import process from "node:process";
import { execFileSync } from "node:child_process";
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
const expectedWorkshops = 51;
const viewportWidths = [320, 360, 375];
const auditedPages = ["quest.html", "evidence-report.html"];
const auditScope = process.env.ACADEMY_AUDIT_SCOPE || "all";
if (!["all", "responsive", "runtime"].includes(auditScope)) {
  throw new Error(`Unknown ACADEMY_AUDIT_SCOPE: ${auditScope}`);
}
const failures = [];
let checks = 0;

function record(name, pass, detail = "") {
  checks += 1;
  if (!pass) failures.push({ name, detail });
}

async function executable(pathname) {
  if (!pathname) return false;
  try {
    await fs.access(pathname, fsConstants.X_OK);
    return true;
  } catch (_error) {
    return false;
  }
}

async function launchRequiredBrowser() {
  const candidates = [];
  if (process.env.AIBAST_CHROME_PATH) {
    candidates.push(process.env.AIBAST_CHROME_PATH);
  }
  try {
    candidates.push(chromium.executablePath());
  } catch (_error) {
    // The Playwright package can be installed without its browser payload.
  }
  candidates.push(
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  );
  const attempted = [];
  for (const candidate of [...new Set(candidates.filter(Boolean))]) {
    if (!(await executable(candidate))) continue;
    try {
      const browser = await chromium.launch({
        executablePath: candidate,
        headless: true,
      });
      return { browser, executablePath: candidate };
    } catch (error) {
      attempted.push(`${candidate}: ${error.message}`);
    }
  }
  throw new Error(
    "A Chromium-compatible browser is required; no Playwright or system "
    + `Chrome executable launched.${attempted.length ? ` ${attempted.join(" | ")}` : ""}`,
  );
}

async function courseSlugs() {
  const [catalog, registry] = await Promise.all([
    fs.readFile(path.join(root, "solutions", "catalog.json"), "utf8")
      .then(JSON.parse),
    fs.readFile(path.join(root, "registry.json"), "utf8").then(JSON.parse),
  ]);
  const registryByName = new Map(
    (registry.agents || [])
      .filter((agent) => agent?._solution)
      .map((agent) => [agent.name, agent]),
  );
  const slugs = [];
  for (const name of Object.keys(catalog.solutions || {}).sort()) {
    const agent = registryByName.get(name);
    const slug = agent?._solution?.package?.slug
      || agent?._demo?.slug
      || name.split("/").at(-1);
    if (!slug) throw new Error(`Advertised Academy course has no slug: ${name}`);
    slugs.push(slug);
  }
  const unique = [...new Set(slugs)].sort();
  if (slugs.length !== expectedWorkshops || unique.length !== expectedWorkshops) {
    throw new Error(
      `Expected ${expectedWorkshops} unique Academy courses, found ${unique.length}`,
    );
  }
  return unique;
}

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

async function startServer() {
  const resolvedRoot = path.resolve(root);
  const server = http.createServer(async (request, response) => {
    try {
      const requestUrl = new URL(request.url || "/", "http://127.0.0.1");
      const relative = decodeURIComponent(requestUrl.pathname).replace(/^\/+/, "");
      const target = path.resolve(resolvedRoot, relative || "index.html");
      if (
        target !== resolvedRoot
        && !target.startsWith(`${resolvedRoot}${path.sep}`)
      ) {
        response.writeHead(403).end("Forbidden");
        return;
      }
      const body = await fs.readFile(target);
      response.writeHead(200, {
        "content-type": mimeTypes.get(path.extname(target).toLowerCase())
          || "application/octet-stream",
        "cache-control": "no-store",
      });
      response.end(body);
    } catch (_error) {
      response.writeHead(404, {
        "content-type": "text/plain; charset=utf-8",
        "cache-control": "no-store",
      }).end("Not found");
    }
  });
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  const address = server.address();
  if (!address || typeof address === "string") {
    throw new Error("Academy audit server failed to bind");
  }
  return {
    server,
    baseUrl: `http://127.0.0.1:${address.port}`,
  };
}

async function settle(page) {
  await page.evaluate(async () => {
    if (document.fonts?.ready) {
      await Promise.race([
        document.fonts.ready,
        new Promise((resolve) => setTimeout(resolve, 1000)),
      ]);
    }
    await new Promise((resolve) => requestAnimationFrame(
      () => requestAnimationFrame(resolve),
    ));
  });
}

async function inspectSurface(page) {
  return page.evaluate(() => {
    const viewport = document.documentElement.clientWidth;
    const scrollWidth = Math.max(
      document.documentElement.scrollWidth,
      document.body?.scrollWidth || 0,
    );
    const visible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== "none"
        && style.visibility !== "hidden"
        && Number(style.opacity || 1) > 0
        && rect.width > 0
        && rect.height > 0
        && element.getClientRects().length > 0;
    };
    const offenders = [...document.querySelectorAll("body *")]
      .filter(visible)
      .map((element) => {
        const rect = element.getBoundingClientRect();
        return {
          tag: element.tagName.toLowerCase(),
          id: element.id,
          className: typeof element.className === "string"
            ? element.className.slice(0, 120)
            : "",
          left: Math.round(rect.left * 10) / 10,
          right: Math.round(rect.right * 10) / 10,
          width: Math.round(rect.width * 10) / 10,
        };
      })
      .filter((row) => row.left < -1 || row.right > viewport + 1)
      .slice(0, 8);
    const academy = [...document.querySelectorAll("a[href]")]
      .some((anchor) => (
        /(?:^|\/)academy\.html(?:$|[?#])/i.test(anchor.getAttribute("href") || "")
        && /academy/i.test(anchor.textContent || "")
      ));
    const skip = document.querySelector('a.skip-link[href^="#"]');
    const target = skip
      ? document.getElementById((skip.getAttribute("href") || "").slice(1))
      : null;
    return {
      viewport,
      scrollWidth,
      overflow: Math.max(0, scrollWidth - viewport),
      offenders,
      academy,
      skip: Boolean(
        skip
        && target
        && target.getAttribute("tabindex") === "-1"
      ),
    };
  });
}

async function auditResponsiveSurfaces(browser, baseUrl, slugs) {
  const context = await browser.newContext();
  const page = await context.newPage();
  let pageErrors = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  let attempts = 0;
  for (const slug of slugs) {
    for (const filename of auditedPages) {
      for (const width of viewportWidths) {
        attempts += 1;
        pageErrors = [];
        const label = `${slug}/${filename}@${width}`;
        try {
          await page.setViewportSize({ width, height: 900 });
          const response = await page.goto(
            `${baseUrl}/solutions/${slug}/${filename}`,
            { waitUntil: "domcontentloaded", timeout: 20000 },
          );
          record(`${label} served`, Boolean(response?.ok()), `HTTP ${response?.status()}`);
          await settle(page);
          const result = await inspectSurface(page);
          record(
            `${label} document containment`,
            result.overflow === 0,
            `scrollWidth=${result.scrollWidth}, viewport=${result.viewport}, `
              + `offenders=${JSON.stringify(result.offenders)}`,
          );
          record(`${label} Academy link`, result.academy, "visible Academy navigation is required");
          record(`${label} skip link`, result.skip, "skip target must have tabindex=-1");
          record(
            `${label} uncaught errors`,
            pageErrors.length === 0,
            pageErrors.join(" | "),
          );
        } catch (error) {
          record(`${label} completed`, false, error.message);
        }
      }
    }
  }
  record(
    "all responsive surfaces audited",
    attempts === expectedWorkshops * auditedPages.length * viewportWidths.length,
    `${attempts} of ${expectedWorkshops * auditedPages.length * viewportWidths.length}`,
  );
  await context.close();
}

function pageErrorCollector(page) {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  return errors;
}

async function engineScenario(browser, baseUrl, slug, storedValue) {
  const context = await browser.newContext({ viewport: { width: 1024, height: 800 } });
  if (storedValue !== null) {
    await context.addInitScript((value) => {
      localStorage.setItem("aibast:workshop-engine", value);
    }, storedValue);
  }
  const page = await context.newPage();
  const errors = pageErrorCollector(page);
  await page.goto(
    `${baseUrl}/solutions/${slug}/quest.html`,
    { waitUntil: "domcontentloaded" },
  );
  await settle(page);
  const state = await page.evaluate(() => {
    const visible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== "none"
        && style.visibility !== "hidden"
        && rect.width > 0
        && rect.height > 0
        && element.getClientRects().length > 0;
    };
    return {
      engine: document.documentElement.dataset.workshopEngine || null,
      brainstemVisible: [...document.querySelectorAll(
        '[data-easy-lane="brainstem"]',
      )].some(visible),
      copilotVisible: [...document.querySelectorAll(
        '[data-easy-lane="copilot"]',
      )].some(visible),
    };
  });
  await context.close();
  return { ...state, errors };
}

async function profileState(page, slug) {
  return page.evaluate((workshopSlug) => {
    const raw = localStorage.getItem("aibast:achievement-profile:v1");
    const profile = raw ? JSON.parse(raw) : {};
    const workshop = profile.workshops?.[workshopSlug] || null;
    return {
      score: profile.score || 0,
      workshop,
      achievements: Object.keys(workshop?.achievements || {})
        .filter((id) => workshop.achievements[id]?.earned)
        .sort(),
    };
  }, slug);
}

async function completeEasyCourse(page, baseUrl, slug) {
  await page.goto(
    `${baseUrl}/solutions/${slug}/quest.html`,
    { waitUntil: "domcontentloaded" },
  );
  await settle(page);
  const required = page.locator(
    '[data-checkpoint][data-achievements-path="brainstem"], '
    + '[data-checkpoint][data-achievements-path="shared"]',
  );
  const total = await required.count();
  for (let index = 0; index < total; index += 1) {
    const checkbox = required.nth(index);
    if (!(await checkbox.isChecked())) await checkbox.check();
  }
  await settle(page);
  return {
    total,
    profile: await profileState(page, slug),
  };
}

async function checkGroup(page, group) {
  const locator = page.locator(
    `[data-checkpoint][data-achievements-group="${group}"]`
    + '[data-achievements-path="brainstem"], '
    + `[data-checkpoint][data-achievements-group="${group}"]`
    + '[data-achievements-path="shared"]',
  );
  const count = await locator.count();
  for (let index = 0; index < count; index += 1) {
    const checkbox = locator.nth(index);
    if (!(await checkbox.isChecked())) await checkbox.check();
  }
  return count;
}

async function auditAchievementRuntime(browser, baseUrl, slug) {
  const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
  const page = await context.newPage();
  const errors = pageErrorCollector(page);
  await page.goto(
    `${baseUrl}/solutions/${slug}/quest.html`,
    { waitUntil: "domcontentloaded" },
  );
  await settle(page);
  const dataset = await page.evaluate(() => {
    const checkpoints = [...document.querySelectorAll(
      "[data-checkpoint][data-achievements-path]",
    )];
    return {
      count: checkpoints.length,
      exact: checkpoints.every((checkpoint) => (
        checkpoint.dataset.achievementsPath
          === checkpoint.getAttribute("data-achievements-path")
        && checkpoint.dataset.achievementsGroup
          === checkpoint.getAttribute("data-achievements-group")
        && !Object.hasOwn(checkpoint.dataset, "achievementPath")
        && !Object.hasOwn(checkpoint.dataset, "achievementGroup")
      )),
      required: checkpoints.filter((checkpoint) => (
        ["brainstem", "shared"].includes(
          checkpoint.getAttribute("data-achievements-path"),
        )
      )).length,
    };
  });
  record("achievement dataset mapping exists", dataset.count > 0, `${dataset.count} checkpoints`);
  record(
    "achievement dataset mapping is exact",
    dataset.exact,
    "data-achievements-* must map to dataset.achievements*",
  );

  for (const [group, badge] of [
    ["local-proof", "local-proof"],
    ["draft-builder", "draft-builder"],
    ["preview-proven", "preview-proven"],
  ]) {
    const groupCount = await checkGroup(page, group);
    const state = await profileState(page, slug);
    record(`${group} has required checkpoints`, groupCount > 0, `${groupCount} checkpoints`);
    record(
      `${badge} awarded by runtime`,
      state.achievements.includes(badge),
      state.achievements.join(", "),
    );
  }

  const required = page.locator(
    '[data-checkpoint][data-achievements-path="brainstem"], '
    + '[data-checkpoint][data-achievements-path="shared"]',
  );
  for (let index = 0; index < await required.count(); index += 1) {
    const checkbox = required.nth(index);
    if (!(await checkbox.isChecked())) await checkbox.check();
  }
  const complete = await profileState(page, slug);
  const progress = complete.workshop?.progress || {};
  for (const badge of [
    "local-proof",
    "draft-builder",
    "preview-proven",
    "workshop-complete",
  ]) {
    record(
      `completed Easy runtime awards ${badge}`,
      complete.achievements.includes(badge),
      complete.achievements.join(", "),
    );
  }
  record(
    "completed Easy runtime writes easyChecked",
    progress.easyChecked === dataset.required,
    `${progress.easyChecked} of ${dataset.required}`,
  );
  record(
    "completed Easy runtime writes easyTotal",
    progress.easyTotal === dataset.required,
    `${progress.easyTotal} expected ${dataset.required}`,
  );
  record(
    "completed Easy runtime writes easyComplete",
    progress.easyComplete === true,
    JSON.stringify(progress),
  );
  record("achievement runtime has no uncaught errors", errors.length === 0, errors.join(" | "));
  await context.close();
}

async function auditStorageDenial(browser, baseUrl, slug) {
  const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
  await context.addInitScript(() => {
    const denied = () => {
      throw new DOMException("Storage denied by Academy audit", "SecurityError");
    };
    for (const method of ["getItem", "setItem", "removeItem", "clear"]) {
      Object.defineProperty(Storage.prototype, method, {
        configurable: true,
        value: denied,
      });
    }
  });
  const page = await context.newPage();
  const errors = pageErrorCollector(page);
  await page.goto(
    `${baseUrl}/solutions/${slug}/quest.html`,
    { waitUntil: "domcontentloaded" },
  );
  await settle(page);
  const before = await page.evaluate(() => {
    const visible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== "none"
        && style.visibility !== "hidden"
        && rect.width > 0
        && rect.height > 0
        && element.getClientRects().length > 0;
    };
    return {
      engine: document.documentElement.dataset.workshopEngine || null,
      easyPanelVisible: visible(document.querySelector('[data-path="easy"]')),
      visibleEasyLanes: [...document.querySelectorAll("[data-easy-lane]")]
        .filter(visible).length,
    };
  });
  record(
    "storage denial defaults visual engine to brainstem",
    before.engine === "brainstem",
    String(before.engine),
  );
  record(
    "storage denial keeps Easy content visible",
    before.easyPanelVisible && before.visibleEasyLanes > 0,
    JSON.stringify(before),
  );

  const visibleCheckboxes = page.locator("[data-checkpoint]:visible");
  const count = await visibleCheckboxes.count();
  let checked = false;
  if (count > 0) {
    try {
      await visibleCheckboxes.first().check();
      checked = await visibleCheckboxes.first().isChecked();
    } catch (error) {
      record("storage-denied checkbox interaction", false, error.message);
    }
  }
  const after = await page.evaluate(() => {
    const status = [...document.querySelectorAll('[role="status"], [aria-live]')]
      .map((element) => {
        const style = getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        return {
          text: (element.textContent || "").trim(),
          visible: style.display !== "none"
            && style.visibility !== "hidden"
            && rect.width >= 0
            && rect.height >= 0,
        };
      })
      .find((row) => (
        row.visible
        && /storage|persist|not saved|in memory|this (?:tab|session)/i.test(row.text)
      ));
    return {
      progress: document.getElementById("achievement-progress-label")?.textContent || "",
      persistence: status?.text || "",
    };
  });
  record("storage-denied checkbox remains usable", count > 0 && checked, `${count} candidates`);
  record(
    "storage denial retains in-memory progress",
    /^[1-9]\d*\s+of\s+/i.test(after.progress),
    after.progress,
  );
  record(
    "storage denial is visibly announced",
    Boolean(after.persistence),
    after.persistence,
  );
  record("storage denial has no uncaught errors", errors.length === 0, errors.join(" | "));
  await context.close();
}

async function auditManualTransition(browser, baseUrl, slug) {
  const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
  const page = await context.newPage();
  const errors = pageErrorCollector(page);
  await page.goto(
    `${baseUrl}/solutions/${slug}/quest.html`,
    { waitUntil: "domcontentloaded" },
  );
  const seed = await page.evaluate((workshopSlug) => {
    const checkpoints = [...document.querySelectorAll(
      '[data-checkpoint][data-achievements-path="brainstem"], '
      + '[data-checkpoint][data-achievements-path="shared"]',
    )];
    const progress = Object.fromEntries(
      checkpoints.map((checkpoint) => [checkpoint.dataset.checkpoint, true]),
    );
    const achievements = Object.fromEntries(
      [
        "started",
        "local-proof",
        "draft-builder",
        "preview-proven",
        "workshop-complete",
      ].map((id) => [id, { earned: true, earnedAt: null }]),
    );
    localStorage.setItem("aibast:workshop-engine", "brainstem");
    localStorage.setItem(
      `aibast:${workshopSlug}:quest-progress`,
      JSON.stringify(progress),
    );
    localStorage.setItem(`aibast:${workshopSlug}:quest-mode`, "easy");
    localStorage.removeItem(`aibast:${workshopSlug}:manual-progress`);
    localStorage.setItem(
      "aibast:achievement-profile:v1",
      JSON.stringify({
        score: 100,
        workshops: {
          [workshopSlug]: {
            slug: workshopSlug,
            mode: "easy",
            progress: {
              easyChecked: checkpoints.length,
              easyTotal: checkpoints.length,
              hardChecked: 0,
              hardTotal: 0,
              easyComplete: true,
              hardComplete: false,
              updatedAt: null,
            },
            achievements,
          },
        },
        updatedAt: null,
      }),
    );
    return { easyTotal: checkpoints.length };
  }, slug);
  await page.reload({ waitUntil: "domcontentloaded" });
  await settle(page);
  const before = await page.evaluate((workshopSlug) => {
    const profile = JSON.parse(
      localStorage.getItem("aibast:achievement-profile:v1") || "{}",
    );
    return {
      workshop: profile.workshops?.[workshopSlug] || null,
      hardRaw: localStorage.getItem(`aibast:${workshopSlug}:manual-progress`),
    };
  }, slug);
  record(
    "zero Hard progress is not persisted at startup",
    before.hardRaw === null,
    String(before.hardRaw),
  );
  record(
    "Easy-complete profile survives startup",
    before.workshop?.mode === "easy"
      && before.workshop?.progress?.easyComplete === true
      && before.workshop?.progress?.easyChecked === seed.easyTotal,
    JSON.stringify(before.workshop),
  );

  await page.locator('[role="tab"][data-mode="hard"]').click();
  await settle(page);
  const opened = await page.evaluate((workshopSlug) => {
    const profile = JSON.parse(
      localStorage.getItem("aibast:achievement-profile:v1") || "{}",
    );
    return {
      workshop: profile.workshops?.[workshopSlug] || null,
      hardRaw: localStorage.getItem(`aibast:${workshopSlug}:manual-progress`),
    };
  }, slug);
  record(
    "opening Manual does not change achievement mode",
    opened.workshop?.mode === "easy",
    JSON.stringify(opened.workshop),
  );
  record(
    "opening Manual preserves Easy completion",
    opened.workshop?.progress?.easyComplete === true
      && opened.workshop?.progress?.hardChecked === 0
      && opened.workshop?.progress?.hardComplete === false,
    JSON.stringify(opened.workshop?.progress),
  );
  record(
    "opening Manual does not create Hard persistence",
    opened.hardRaw === null,
    String(opened.hardRaw),
  );

  const firstHard = page.locator(
    '[data-path="hard"] .complete[data-step]',
  ).first();
  await firstHard.check();
  await settle(page);
  const advanced = await page.evaluate((workshopSlug) => {
    const profile = JSON.parse(
      localStorage.getItem("aibast:achievement-profile:v1") || "{}",
    );
    const hard = JSON.parse(
      localStorage.getItem(`aibast:${workshopSlug}:manual-progress`) || "[]",
    );
    return {
      workshop: profile.workshops?.[workshopSlug] || null,
      hard,
    };
  }, slug);
  record(
    "first real Hard check switches achievement mode",
    advanced.workshop?.mode === "hard",
    JSON.stringify(advanced.workshop),
  );
  record(
    "first real Hard check persists progress",
    advanced.workshop?.progress?.hardChecked === 1
      && advanced.workshop?.progress?.hardTotal > 0
      && advanced.workshop?.progress?.easyComplete === true
      && advanced.hard.length === 1,
    JSON.stringify(advanced),
  );
  record("Manual transition has no uncaught errors", errors.length === 0, errors.join(" | "));
  await context.close();
}

async function auditAcademyManualResumeLifecycle(browser, baseUrl, slug) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.addInitScript(() => {
    localStorage.setItem("aibast:workshop-engine", "brainstem");
  });
  const questPage = await context.newPage();
  const questErrors = pageErrorCollector(questPage);
  const easy = await completeEasyCourse(questPage, baseUrl, slug);
  record(
    "Manual resume lifecycle starts from real Easy completion",
    easy.total > 0
      && easy.profile.workshop?.progress?.easyComplete === true,
    JSON.stringify(easy),
  );

  const manualPage = await context.newPage();
  const manualErrors = pageErrorCollector(manualPage);
  await manualPage.goto(
    `${baseUrl}/solutions/${slug}/manual-tutorial.html`,
    { waitUntil: "domcontentloaded" },
  );
  await settle(manualPage);
  const manualBoxes = manualPage.locator(".complete[data-step]");
  const manualTotal = await manualBoxes.count();
  if (manualTotal > 0) await manualBoxes.first().check();
  await settle(manualPage);
  const manualProgress = await profileState(manualPage, slug);
  record(
    "standalone Manual step creates real Hard progress",
    manualTotal > 1
      && manualProgress.workshop?.mode === "hard"
      && manualProgress.workshop?.progress?.hardChecked === 1
      && manualProgress.workshop?.progress?.hardTotal === manualTotal
      && manualProgress.workshop?.progress?.easyComplete === true,
    JSON.stringify({ manualTotal, manualProgress }),
  );

  const academyPage = await context.newPage();
  const academyErrors = pageErrorCollector(academyPage);
  await academyPage.goto(`${baseUrl}/academy.html`, {
    waitUntil: "domcontentloaded",
  });
  await academyPage.waitForFunction(() => (
    document.getElementById("courseGrid")?.getAttribute("aria-busy") === "false"
  ));
  await settle(academyPage);
  const academy = await academyPage.evaluate((workshopSlug) => {
    const describe = (anchor) => {
      if (!anchor) return null;
      const url = new URL(anchor.href, document.baseURI);
      return {
        text: (anchor.textContent || "").trim(),
        pathname: url.pathname,
        hash: url.hash,
      };
    };
    const activeTitle = [...document.querySelectorAll(
      "#activeCourseList a[data-course-link]",
    )].find((anchor) => anchor.dataset.courseLink === workshopSlug);
    const completedTitle = [...document.querySelectorAll(
      "#completedCourseList a[data-course-link]",
    )].find((anchor) => anchor.dataset.courseLink === workshopSlug);
    const activeItem = activeTitle?.closest(".learning-course") || null;
    const catalogTitle = [...document.querySelectorAll(
      "#courseGrid .course-card h3 a[data-course-link]",
    )].find((anchor) => anchor.dataset.courseLink === workshopSlug);
    const catalogCard = catalogTitle?.closest(".course-card") || null;
    return {
      activeListed: Boolean(activeTitle),
      completedListed: Boolean(completedTitle),
      activeAction: describe(activeItem?.querySelector("a.button")),
      catalogAction: describe(
        catalogCard?.querySelector(".course-actions a.button.primary"),
      ),
      continueAction: describe(document.getElementById("continueAction")),
    };
  }, slug);
  const expectedPath = `/solutions/${slug}/manual-tutorial.html`;
  const isResumeManual = (action) => (
    action?.text === "Resume Manual"
    && action.pathname === expectedPath
    && action.hash === "#resume"
  );
  record(
    "Academy classifies Easy-complete Manual progress as Active",
    academy.activeListed && !academy.completedListed,
    JSON.stringify(academy),
  );
  record(
    "Academy Active list action is Resume Manual",
    isResumeManual(academy.activeAction),
    JSON.stringify(academy.activeAction),
  );
  record(
    "Academy primary actions resume standalone Manual",
    isResumeManual(academy.catalogAction)
      && isResumeManual(academy.continueAction),
    JSON.stringify({
      catalog: academy.catalogAction,
      continue: academy.continueAction,
    }),
  );

  let followed = false;
  let resumeState = null;
  if (isResumeManual(academy.continueAction)) {
    await Promise.all([
      academyPage.waitForURL(
        (url) => (
          url.pathname === expectedPath
          && url.hash.startsWith("#resume")
        ),
      ),
      academyPage.locator("#continueAction").click(),
    ]);
    await settle(academyPage);
    followed = true;
    resumeState = await academyPage.evaluate(() => {
      const boxes = [...document.querySelectorAll(".complete[data-step]")];
      const next = boxes.find((box) => !box.checked) || null;
      return {
        total: boxes.length,
        firstChecked: boxes[0]?.checked === true,
        nextStep: next?.dataset.step || null,
        focusedStep: document.activeElement?.dataset?.step || null,
        focused: document.activeElement === next,
      };
    });
  }
  record(
    "Academy Resume Manual action follows manual-tutorial.html#resume",
    followed,
    JSON.stringify(academy.continueAction),
  );
  record(
    "Academy Resume Manual focuses the next standalone step",
    resumeState?.total === manualTotal
      && resumeState?.firstChecked === true
      && resumeState?.nextStep === "2"
      && resumeState?.focusedStep === "2"
      && resumeState?.focused === true,
    JSON.stringify(resumeState),
  );
  record(
    "Academy Manual resume lifecycle has no uncaught errors",
    [...questErrors, ...manualErrors, ...academyErrors].length === 0,
    [...questErrors, ...manualErrors, ...academyErrors].join(" | "),
  );
  await context.close();
}

async function auditQuestStandaloneManualRefresh(browser, baseUrl, slug) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.addInitScript(() => {
    localStorage.setItem("aibast:workshop-engine", "brainstem");
  });
  const questPage = await context.newPage();
  const questErrors = pageErrorCollector(questPage);
  const easy = await completeEasyCourse(questPage, baseUrl, slug);
  record(
    "cross-tab Manual refresh starts Easy-complete",
    easy.total > 0
      && easy.profile.workshop?.progress?.easyComplete === true,
    JSON.stringify(easy),
  );
  const before = easy.profile;

  await questPage.locator('[role="tab"][data-mode="hard"]').click();
  await settle(questPage);
  const initial = await questPage.evaluate(() => {
    const boxes = [...document.querySelectorAll(
      '[data-path="hard"] .complete[data-step]',
    )];
    return {
      total: boxes.length,
      checked: boxes.filter((box) => box.checked).length,
      label: document.getElementById("hard-progress-label")?.textContent?.trim()
        || "",
    };
  });
  record(
    "embedded Manual initial display uses actual step total",
    initial.total > 1
      && initial.checked === 0
      && initial.label === `0 of ${initial.total} complete`
      && initial.label !== "0 of 0 complete",
    JSON.stringify(initial),
  );

  const manualPage = await context.newPage();
  const manualErrors = pageErrorCollector(manualPage);
  await manualPage.goto(
    `${baseUrl}/solutions/${slug}/manual-tutorial.html`,
    { waitUntil: "domcontentloaded" },
  );
  await settle(manualPage);
  const standaloneTotal = await manualPage.locator(
    ".complete[data-step]",
  ).count();
  if (standaloneTotal > 0) {
    await manualPage.locator('.complete[data-step="1"]').check();
  }
  await settle(manualPage);
  const standalone = await manualPage.evaluate((workshopSlug) => {
    const profile = JSON.parse(
      globalThis.aibastWorkshopStorage.getItem(
        "aibast:achievement-profile:v1",
      ) || "{}",
    );
    return {
      label: document.getElementById("progress-label")?.textContent?.trim() || "",
      workshop: profile.workshops?.[workshopSlug] || null,
      score: profile.score || 0,
      achievements: Object.keys(
        profile.workshops?.[workshopSlug]?.achievements || {},
      ).filter(
        (id) => profile.workshops[workshopSlug].achievements[id]?.earned,
      ).sort(),
    };
  }, slug);
  record(
    "standalone Manual tab persists exactly step 1",
    standaloneTotal === initial.total
      && standalone.label === `1 of ${standaloneTotal} complete`
      && standalone.workshop?.progress?.hardChecked === 1
      && standalone.workshop?.progress?.hardTotal === standaloneTotal,
    JSON.stringify(standalone),
  );
  record(
    "standalone Manual step preserves Easy completion without duplicate awards",
    standalone.workshop?.progress?.easyComplete === true
      && standalone.score === before.score
      && JSON.stringify(standalone.achievements)
        === JSON.stringify(before.achievements),
    JSON.stringify({ before, standalone }),
  );

  await manualPage.close();
  await questPage.bringToFront();
  await questPage.evaluate(() => {
    window.dispatchEvent(new Event("focus"));
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await settle(questPage);
  const refreshed = await questPage.evaluate((workshopSlug) => {
    const boxes = [...document.querySelectorAll(
      '[data-path="hard"] .complete[data-step]',
    )];
    const profile = JSON.parse(
      globalThis.aibastWorkshopStorage.getItem(
        "aibast:achievement-profile:v1",
      ) || "{}",
    );
    const workshop = profile.workshops?.[workshopSlug] || null;
    return {
      total: boxes.length,
      checked: boxes.filter((box) => box.checked).length,
      firstChecked: boxes[0]?.checked === true,
      label: document.getElementById("hard-progress-label")?.textContent?.trim()
        || "",
      workshop,
      score: profile.score || 0,
      achievements: Object.keys(workshop?.achievements || {})
        .filter((id) => workshop.achievements[id]?.earned)
        .sort(),
    };
  }, slug);
  record(
    "quest refreshes embedded Manual checkbox and progress on return",
    refreshed.total === initial.total
      && refreshed.checked === 1
      && refreshed.firstChecked === true
      && refreshed.label === `1 of ${initial.total} complete`,
    JSON.stringify(refreshed),
  );
  record(
    "quest cross-tab refresh preserves Easy completion and award identity",
    refreshed.workshop?.progress?.easyComplete === true
      && refreshed.score === before.score
      && JSON.stringify(refreshed.achievements)
        === JSON.stringify(before.achievements),
    JSON.stringify({ before, refreshed }),
  );
  record(
    "quest standalone Manual refresh has no uncaught errors",
    [...questErrors, ...manualErrors].length === 0,
    [...questErrors, ...manualErrors].join(" | "),
  );
  await context.close();
}

async function auditResume(browser, baseUrl, slug) {
  const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
  await context.addInitScript((workshopSlug) => {
    localStorage.setItem("aibast:workshop-engine", "brainstem");
    localStorage.removeItem("aibast:achievement-profile:v1");
    localStorage.removeItem(`aibast:${workshopSlug}:quest-progress`);
    localStorage.removeItem(`aibast:${workshopSlug}:manual-progress`);
  }, slug);
  const page = await context.newPage();
  const errors = pageErrorCollector(page);
  await page.goto(
    `${baseUrl}/solutions/${slug}/quest.html#resume`,
    { waitUntil: "domcontentloaded" },
  );
  await settle(page);
  const state = await page.evaluate((workshopSlug) => {
    const candidates = [...document.querySelectorAll(
      '[data-checkpoint][data-achievements-path="brainstem"], '
      + '[data-checkpoint][data-achievements-path="shared"]',
    )];
    const incomplete = candidates.find((checkbox) => !checkbox.checked) || null;
    const active = document.activeElement;
    const focused = Boolean(
      incomplete
      && (
        active === incomplete
        || incomplete.closest(".learn-step, .step, .checkpoint")?.contains(active)
      )
    );
    const raw = localStorage.getItem("aibast:achievement-profile:v1");
    const profile = raw ? JSON.parse(raw) : {};
    const achievements = profile.workshops?.[workshopSlug]?.achievements || {};
    return {
      candidateCount: candidates.length,
      focused,
      incompleteChecked: incomplete?.checked ?? null,
      earned: Object.keys(achievements).filter((id) => achievements[id]?.earned),
    };
  }, slug);
  record("#resume has an incomplete Easy target", state.candidateCount > 0, String(state.candidateCount));
  record("#resume focuses the incomplete target", state.focused, JSON.stringify(state));
  record(
    "#resume does not complete or award its target",
    state.incompleteChecked === false && state.earned.length === 0,
    JSON.stringify(state),
  );
  record("#resume has no uncaught errors", errors.length === 0, errors.join(" | "));
  await context.close();
}

async function selectedTabState(page) {
  return page.evaluate(() => {
    const tabs = [...document.querySelectorAll('[role="tab"]')];
    const selected = tabs.find((tab) => tab.getAttribute("aria-selected") === "true");
    const panel = selected
      ? document.getElementById(selected.getAttribute("aria-controls"))
      : null;
    return {
      tabs: tabs.map((tab) => ({
        mode: tab.dataset.mode,
        selected: tab.getAttribute("aria-selected"),
        tabIndex: tab.tabIndex,
      })),
      selected: selected?.dataset.mode || null,
      focused: document.activeElement?.dataset?.mode || null,
      panelVisible: Boolean(panel && !panel.hidden),
    };
  });
}

async function auditTabs(browser, baseUrl, slug) {
  const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
  await context.addInitScript(() => {
    localStorage.setItem("aibast:workshop-engine", "brainstem");
  });
  const page = await context.newPage();
  const errors = pageErrorCollector(page);
  await page.goto(
    `${baseUrl}/solutions/${slug}/quest.html`,
    { waitUntil: "domcontentloaded" },
  );
  const easy = page.locator('[role="tab"][data-mode="easy"]');
  await easy.focus();
  const initial = await selectedTabState(page);
  record(
    "mode tabs start with roving tabindex",
    initial.selected === "easy"
      && initial.tabs.find((tab) => tab.mode === "easy")?.tabIndex === 0
      && initial.tabs.find((tab) => tab.mode === "hard")?.tabIndex === -1,
    JSON.stringify(initial),
  );
  for (const [key, expected] of [
    ["End", "hard"],
    ["Home", "easy"],
    ["ArrowRight", "hard"],
    ["ArrowLeft", "easy"],
  ]) {
    await page.locator(`[role="tab"][data-mode="${expected === "easy" ? "hard" : "easy"}"]`)
      .press(key);
    const state = await selectedTabState(page);
    record(
      `mode tabs support ${key}`,
      state.selected === expected
        && state.focused === expected
        && state.panelVisible,
      JSON.stringify(state),
    );
  }
  record("mode tabs have no uncaught errors", errors.length === 0, errors.join(" | "));
  await context.close();
}

async function auditRepresentativeRuntime(browser, baseUrl, slugs) {
  const slug = slugs.includes("account-intelligence")
    ? "account-intelligence"
    : slugs[0];
  for (const [storedValue, expected] of [
    [null, "brainstem"],
    ["brainstem", "brainstem"],
    ["invalid", "brainstem"],
    ["copilot", "copilot"],
  ]) {
    const state = await engineScenario(browser, baseUrl, slug, storedValue);
    record(
      `visual engine ${String(storedValue)} -> ${expected}`,
      state.engine === expected
        && state.brainstemVisible === (expected === "brainstem")
        && state.copilotVisible === (expected === "copilot"),
      JSON.stringify(state),
    );
    record(
      `visual engine ${String(storedValue)} has no uncaught errors`,
      state.errors.length === 0,
      state.errors.join(" | "),
    );
  }
  await auditAchievementRuntime(browser, baseUrl, slug);
  await auditStorageDenial(browser, baseUrl, slug);
  await auditManualTransition(browser, baseUrl, slug);
  await auditAcademyManualResumeLifecycle(browser, baseUrl, slug);
  await auditQuestStandaloneManualRefresh(browser, baseUrl, slug);
  await auditResume(browser, baseUrl, slug);
  await auditTabs(browser, baseUrl, slug);
}

let server;
let browser;
try {
  const slugs = await courseSlugs();
  const serving = await startServer();
  server = serving.server;
  const launched = await launchRequiredBrowser();
  browser = launched.browser;
  console.log(`Academy browser: ${launched.executablePath}`);
  if (auditScope !== "runtime") {
    await auditResponsiveSurfaces(browser, serving.baseUrl, slugs);
  }
  if (auditScope !== "responsive") {
    await auditRepresentativeRuntime(browser, serving.baseUrl, slugs);
  }
} catch (error) {
  record("academy audit crashed", false, error.stack || error.message);
} finally {
  if (browser) await browser.close();
  if (server) {
    await new Promise((resolve) => server.close(resolve));
  }
}

console.log(
  `Academy course browser audit: ${checks - failures.length}/${checks} checks passed; `
  + `${failures.length} failed`,
);
for (const failure of failures.slice(0, 100)) {
  console.error(`FAIL ${failure.name}${failure.detail ? ` — ${failure.detail}` : ""}`);
}
if (failures.length > 100) {
  console.error(`FAIL ... ${failures.length - 100} additional failures omitted`);
}
process.exitCode = failures.length === 0 ? 0 : 1;
