import { randomBytes } from "node:crypto";
import { spawn } from "node:child_process";
import {
  createWriteStream,
  existsSync,
  mkdirSync,
  readFileSync,
  renameSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { createServer } from "node:http";
import { once } from "node:events";
import path from "node:path";

import { resolveFfmpegExecutable } from "./video-tools.mjs";

const MAX_BODY_BYTES = 256 * 1024;
let recordingPermissionWebContents = null;
const capturedRecordings = new WeakMap();
const lastCapturedRecordings = new WeakMap();

function errorMessage(error) {
  return String(error?.message || error);
}

function jsonResponse(response, status, body) {
  if (!response.headersSent) {
    response.writeHead(status, {
      "Cache-Control": "no-store",
      "Content-Type": "application/json; charset=utf-8",
    });
  }
  response.end(`${JSON.stringify(body)}\n`);
}

async function readJsonBody(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) {
      throw new Error("UI driver command is too large.");
    }
    chunks.push(chunk);
  }
  const value = JSON.parse(Buffer.concat(chunks).toString("utf8"));
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("UI driver command must be a JSON object.");
  }
  return value;
}

function frameTree(root) {
  const frames = [root];
  for (const child of root.frames || []) frames.push(...frameTree(child));
  return frames;
}

function brainstemFrame(window, loopbackUrl) {
  return frameTree(window.webContents.mainFrame)
    .find((frame) => loopbackUrl(frame.url));
}

async function browserDriverCommand(command) {
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const state = window.__brainstemAiDriver ||= {};

  function ensureUi() {
    let style = document.getElementById("brainstem-ai-driver-style");
    if (!style) {
      style = document.createElement("style");
      style.id = "brainstem-ai-driver-style";
      style.textContent = `
        #brainstem-ai-driver-cursor {
          position: fixed; z-index: 2147483645; width: 28px; height: 28px;
          left: 24px; top: 24px; pointer-events: none; opacity: 0;
          filter: drop-shadow(0 2px 4px rgba(0,0,0,.65));
          transition: left .58s cubic-bezier(.22,.8,.24,1),
                      top .58s cubic-bezier(.22,.8,.24,1), opacity .16s ease;
        }
        #brainstem-ai-driver-cursor svg { width: 100%; height: 100%; display: block; }
        #brainstem-ai-driver-pulse {
          position: fixed; z-index: 2147483644; width: 14px; height: 14px;
          border: 2px solid #58a6ff; border-radius: 50%; pointer-events: none;
          opacity: 0; transform: translate(-50%,-50%) scale(.4);
        }
        #brainstem-ai-driver-pulse.go {
          animation: brainstemAiDriverPulse .62s ease-out forwards;
        }
        #brainstem-ai-driver-label {
          position: fixed; z-index: 2147483646; max-width: min(360px, 70vw);
          padding: 8px 11px; border: 1px solid #388bfd; border-radius: 8px;
          color: #e6edf3; background: rgba(13,17,23,.96);
          box-shadow: 0 8px 28px rgba(0,0,0,.45);
          font: 600 12px/1.35 ui-sans-serif, system-ui, sans-serif;
          pointer-events: none; opacity: 0; transform: translateY(4px);
          transition: opacity .16s ease, transform .16s ease;
        }
        #brainstem-ai-driver-label.show { opacity: 1; transform: translateY(0); }
        .brainstem-ai-driver-target {
          outline: 2px solid #58a6ff !important; outline-offset: 3px !important;
          transition: outline-color .18s ease;
        }
        @keyframes brainstemAiDriverPulse {
          0% { opacity: .95; transform: translate(-50%,-50%) scale(.4); }
          100% { opacity: 0; transform: translate(-50%,-50%) scale(3.2); }
        }
        @media (prefers-reduced-motion: reduce) {
          #brainstem-ai-driver-cursor { transition-duration: .08s; }
          #brainstem-ai-driver-pulse.go { animation-duration: .12s; }
        }
      `;
      document.head.appendChild(style);
    }

    let cursor = document.getElementById("brainstem-ai-driver-cursor");
    if (!cursor) {
      cursor = document.createElement("div");
      cursor.id = "brainstem-ai-driver-cursor";
      cursor.dataset.brainstemAiDriver = "true";
      cursor.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5.5 3.21V20.8c0 .45.54.67.85.35l4.86-4.86a.5.5 0 01.35-.15h6.87c.45 0 .67-.54.35-.85L6.35 2.85a.5.5 0 00-.85.36z" fill="#f0f6fc" stroke="#0d1117" stroke-width="1.5"/></svg>';
      document.body.appendChild(cursor);
    }

    let pulse = document.getElementById("brainstem-ai-driver-pulse");
    if (!pulse) {
      pulse = document.createElement("div");
      pulse.id = "brainstem-ai-driver-pulse";
      pulse.dataset.brainstemAiDriver = "true";
      document.body.appendChild(pulse);
    }

    let label = document.getElementById("brainstem-ai-driver-label");
    if (!label) {
      label = document.createElement("div");
      label.id = "brainstem-ai-driver-label";
      label.dataset.brainstemAiDriver = "true";
      document.body.appendChild(label);
    }
    return { cursor, label, pulse };
  }

  function visible(element) {
    if (!element) return false;
    const rect = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return rect.width > 0
      && rect.height > 0
      && style.display !== "none"
      && style.visibility !== "hidden"
      && Number.parseFloat(style.opacity || "1") > 0;
  }

  function normalizedText(element) {
    return String(
      element?.innerText
      || element?.getAttribute?.("aria-label")
      || element?.getAttribute?.("title")
      || element?.value
      || "",
    ).replace(/\s+/g, " ").trim();
  }

  function selectorFor(element) {
    if (element.id) return `#${CSS.escape(element.id)}`;
    const parts = [];
    let node = element;
    while (node && node !== document.body && parts.length < 5) {
      let part = node.localName;
      if (!part) break;
      const siblings = node.parentElement
        ? [...node.parentElement.children].filter((child) => child.localName === part)
        : [];
      if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(node) + 1})`;
      parts.unshift(part);
      node = node.parentElement;
    }
    return parts.join(" > ");
  }

  function findElement(step) {
    if (step.selector) {
      try {
        return document.querySelector(step.selector);
      } catch (error) {
        throw new Error(`Invalid selector ${step.selector}: ${error.message}`);
      }
    }
    const wanted = String(step.targetText || step.text || "")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();
    if (!wanted) return null;
    const candidates = [
      ...document.querySelectorAll(
        "button,a,input,textarea,select,[role='button'],[role='menuitem'],[tabindex]",
      ),
    ].filter(visible);
    return candidates.find((element) => normalizedText(element).toLowerCase() === wanted)
      || candidates.find((element) => normalizedText(element).toLowerCase().includes(wanted));
  }

  function labelText(step, fallback) {
    return String(step.label || fallback || "").trim();
  }

  async function announce(text, durationMs = 900) {
    const { label } = ensureUi();
    label.textContent = text;
    label.style.left = "50%";
    label.style.top = "18px";
    label.style.transform = "translate(-50%, 4px)";
    label.classList.add("show");
    await sleep(Math.max(120, Number(durationMs) || 900));
    label.classList.remove("show");
  }

  async function pointAt(element, text) {
    const { cursor, label } = ensureUi();
    element.scrollIntoView({ block: "center", inline: "center", behavior: "smooth" });
    await sleep(220);
    const rect = element.getBoundingClientRect();
    const x = Math.max(8, Math.min(innerWidth - 12, rect.left + rect.width / 2));
    const y = Math.max(8, Math.min(innerHeight - 12, rect.top + rect.height / 2));
    cursor.style.opacity = "1";
    cursor.style.left = `${x}px`;
    cursor.style.top = `${y}px`;
    if (text) {
      label.textContent = text;
      label.style.left = `${Math.min(innerWidth - 370, x + 22)}px`;
      label.style.top = `${Math.min(innerHeight - 54, y + 24)}px`;
      label.style.transform = "none";
      label.classList.add("show");
    }
    element.classList.add("brainstem-ai-driver-target");
    await sleep(650);
    return { x, y };
  }

  async function clickElement(element, step) {
    const description = labelText(
      step,
      `Clicking ${normalizedText(element) || selectorFor(element)}`,
    );
    const { x, y } = await pointAt(element, description);
    const { label, pulse } = ensureUi();
    pulse.style.left = `${x}px`;
    pulse.style.top = `${y}px`;
    pulse.classList.remove("go");
    void pulse.offsetWidth;
    pulse.classList.add("go");
    element.focus({ preventScroll: true });
    element.click();
    await sleep(Math.max(260, Number(step.settleMs) || 520));
    element.classList.remove("brainstem-ai-driver-target");
    label.classList.remove("show");
    return {
      clicked: selectorFor(element),
      text: normalizedText(element),
    };
  }

  function setControlValue(element, value) {
    if (element.isContentEditable) {
      element.textContent = value;
      element.dispatchEvent(new InputEvent("input", {
        bubbles: true,
        data: value,
        inputType: "insertText",
      }));
      return;
    }
    const prototype = element instanceof HTMLTextAreaElement
      ? HTMLTextAreaElement.prototype
      : element instanceof HTMLInputElement
        ? HTMLInputElement.prototype
        : null;
    const setter = prototype
      ? Object.getOwnPropertyDescriptor(prototype, "value")?.set
      : null;
    if (setter) setter.call(element, value);
    else element.value = value;
    element.dispatchEvent(new Event("input", { bubbles: true }));
  }

  async function typeInto(element, step) {
    if (
      !(
        element instanceof HTMLInputElement
        || element instanceof HTMLTextAreaElement
        || element.isContentEditable
      )
    ) {
      throw new Error("The requested UI target does not accept text.");
    }
    const value = String(step.value ?? "");
    const description = labelText(step, "Typing in the Brainstem");
    await pointAt(element, description);
    element.focus({ preventScroll: true });
    const startingValue = step.replace === false
      ? String(element.value || element.textContent || "")
      : "";
    setControlValue(element, startingValue);
    const delayMs = Math.max(0, Math.min(100, Number(step.typingDelayMs) || 18));
    let nextValue = startingValue;
    for (const character of value) {
      nextValue += character;
      setControlValue(element, nextValue);
      if (delayMs) await sleep(delayMs);
    }
    element.dispatchEvent(new Event("change", { bubbles: true }));
    await sleep(Math.max(160, Number(step.settleMs) || 300));
    element.classList.remove("brainstem-ai-driver-target");
    ensureUi().label.classList.remove("show");
    return { typed: value.length, selector: selectorFor(element) };
  }

  async function waitFor(step) {
    const timeoutMs = Math.max(100, Math.min(120000, Number(step.timeoutMs) || 10000));
    const deadline = Date.now() + timeoutMs;
    const wantedText = String(step.text || "").replace(/\s+/g, " ").trim();
    while (Date.now() < deadline) {
      let element = null;
      if (step.selector) {
        let matches;
        try {
          matches = [...document.querySelectorAll(step.selector)];
        } catch (error) {
          throw new Error(`Invalid selector ${step.selector}: ${error.message}`);
        }
        element = matches.find((candidate) => (
          visible(candidate)
          && (!wantedText || normalizedText(candidate).includes(wantedText))
        ));
      }
      const textFound = !wantedText || (
        step.selector
          ? Boolean(element)
          : document.body.innerText.replace(/\s+/g, " ").includes(wantedText)
      );
      if ((!step.selector || element) && textFound) {
        return {
          selector: element ? selectorFor(element) : null,
          text: element ? normalizedText(element) : wantedText,
        };
      }
      await sleep(100);
    }
    throw new Error(
      `Timed out waiting for ${step.selector || JSON.stringify(wantedText) || "the page"}.`,
    );
  }

  async function perform(step) {
    const action = String(step.action || "").toLowerCase();
    if (action === "set_chat_lease") {
      const input = document.getElementById("input");
      const send = document.getElementById("send");
      if (!input || !send) {
        throw new Error("The visible Brainstem chat composer is unavailable.");
      }
      if (!state.chatLeaseGuardInstalled) {
        const block = (event) => {
          if (state.chatLeaseLocked && event.isTrusted) {
            event.preventDefault();
            event.stopImmediatePropagation();
          }
        };
        send.addEventListener("click", block, true);
        input.addEventListener("keydown", (event) => {
          if (event.key === "Enter" && !event.shiftKey) block(event);
        }, true);
        state.chatLeaseGuardInstalled = true;
      }
      state.chatLeaseTokens ||= new Set();
      const leaseToken = String(step.token || "legacy");
      if (step.locked) state.chatLeaseTokens.add(leaseToken);
      else state.chatLeaseTokens.delete(leaseToken);
      state.chatLeaseLocked = state.chatLeaseTokens.size > 0;
      let banner = document.getElementById("brainstem-beta-chat-lease");
      if (!banner) {
        banner = document.createElement("div");
        banner.id = "brainstem-beta-chat-lease";
        banner.textContent = `Brain Surgeon is using this chat (${
          state.chatLeaseTokens.size
        })`;
        Object.assign(banner.style, {
          position: "fixed",
          zIndex: "2147483645",
          right: "18px",
          bottom: "72px",
          padding: "8px 11px",
          border: "1px solid rgba(88, 166, 255, .55)",
          borderRadius: "999px",
          background: "rgba(13, 17, 23, .94)",
          color: "#79c0ff",
          font: "700 11px/1 ui-sans-serif, system-ui, sans-serif",
          pointerEvents: "none",
        });
        document.body.appendChild(banner);
      }
      banner.hidden = !state.chatLeaseLocked;
      send.setAttribute(
        "aria-disabled",
        state.chatLeaseLocked ? "true" : "false",
      );
      return {
        leaseCount: state.chatLeaseTokens.size,
        locked: state.chatLeaseLocked,
      };
    }
    if (action === "surgeon_chat") {
      const panel = document.getElementById("surgeon");
      const tab = document.getElementById("surgeon-tab");
      if (!panel) throw new Error("The Brain Surgeon panel is unavailable.");
      if (!visible(panel)) {
        if (visible(tab)) {
          await clickElement(tab, {
            action: "click",
            label: "Opening GitHub Copilot Agent mode",
            settleMs: 350,
          });
        } else {
          panel.classList.add("open");
          document.body.classList.add("surgeon-open");
          await sleep(350);
        }
      }
      const input = document.getElementById("surgeon-input");
      const send = document.getElementById("surgeon-send");
      if (!visible(input) || !visible(send)) {
        throw new Error("The visible Brain Surgeon composer is unavailable.");
      }
      const baseline = document.querySelectorAll(
        "#surgeon-log .surgeon-message.assistant",
      ).length;
      const errorBaseline = document.querySelectorAll(
        "#surgeon-log .surgeon-message.error",
      ).length;
      await typeInto(input, {
        action: "type",
        value: String(step.value || step.text || ""),
        label: step.label || "Directing the Brain Surgeon",
        typingDelayMs: step.typingDelayMs ?? 5,
      });
      await clickElement(send, {
        action: "click",
        label: step.sendLabel || "Sending to GitHub Copilot",
        settleMs: 200,
      });

      const timeoutMs = Math.max(
        1000,
        Math.min(60 * 60 * 1000, Number(step.timeoutMs) || 60 * 60 * 1000),
      );
      const deadline = Date.now() + timeoutMs;
      while (Date.now() < deadline) {
        const replies = document.querySelectorAll(
          "#surgeon-log .surgeon-message.assistant",
        );
        const errors = document.querySelectorAll(
          "#surgeon-log .surgeon-message.error",
        );
        const error = errors.length > errorBaseline
          ? errors[errors.length - 1]
          : null;
        if (error && !send.disabled) {
          throw new Error(normalizedText(error));
        }
        if (replies.length > baseline && !send.disabled) {
          return {
            response: normalizedText(replies[replies.length - 1]),
          };
        }
        await sleep(150);
      }
      throw new Error("Timed out waiting for the visible Brain Surgeon reply.");
    }
    if (action === "chat") {
      const input = document.getElementById("input");
      const send = document.getElementById("send");
      if (!visible(input) || !visible(send)) {
        throw new Error("The visible Brainstem chat composer is unavailable.");
      }
      const baselineRequestId = Math.max(
        0,
        ...[...document.querySelectorAll("#chat .response-slot")]
          .map((slot) => Number(slot.dataset.requestId) || 0),
      );
      let requestId = null;
      await typeInto(input, {
        action: "type",
        value: String(step.value || step.text || ""),
        label: step.label || "Giving the Brainstem the job",
        typingDelayMs: step.typingDelayMs ?? 5,
      });
      let resolveRequestId;
      const requestCreated = new Promise((resolve) => {
        resolveRequestId = resolve;
      });
      const observer = new MutationObserver(() => {
        const created = Math.min(
          ...[...document.querySelectorAll("#chat .response-slot")]
            .map((slot) => Number(slot.dataset.requestId) || 0)
            .filter((candidate) => candidate > baselineRequestId),
        );
        if (Number.isFinite(created)) {
          observer.disconnect();
          resolveRequestId(created);
        }
      });
      observer.observe(document.getElementById("chat"), {
        childList: true,
        subtree: true,
      });
      await clickElement(send, {
        action: "click",
        label: step.sendLabel || "Sending through Brainstem chat",
        settleMs: 200,
      });
      requestId = await Promise.race([
        requestCreated,
        sleep(2000).then(() => null),
      ]);
      observer.disconnect();
      if (!Number.isFinite(requestId)) {
        throw new Error("The visible Brainstem request ID was not created.");
      }

      const timeoutMs = Math.max(
        1000,
        Math.min(60 * 60 * 1000, Number(step.timeoutMs) || 180000),
      );
      const deadline = Date.now() + timeoutMs;
      while (Date.now() < deadline) {
        const slot = document.querySelector(
          `#chat .response-slot[data-request-id="${requestId}"]`,
        );
        const reply = slot?.querySelector(
          ".msg.assistant:not(.typing-indicator):not(.stream-arriving)",
        );
        const system = slot?.querySelector(".msg.system");
        if (system) {
          throw new Error(
            normalizedText(system.querySelector(".bubble"))
            || "The visible Brainstem request failed.",
          );
        }
        if (reply) {
          const response = normalizedText(reply.querySelector(".bubble"));
          if (response) {
            return {
              requestId,
              response,
              agentLogs: normalizedText(reply.querySelector(".agent-logs")),
            };
          }
        }
        await sleep(150);
      }
      throw new Error("Timed out waiting for the visible Brainstem reply.");
    }
    if (action === "recording_status") {
      const recording = window.__brainstemBetaRecording;
      if (!recording) return { active: false };
      const track = recording.stream.getVideoTracks()[0] || null;
      return {
        active: recording.recorder.state !== "inactive",
        bytes: recording.chunks.reduce(
          (total, chunk) => total + Number(chunk.size || 0),
          0,
        ),
        chunks: recording.chunks.length,
        dataEvents: recording.dataEvents,
        error: recording.lastError,
        recorderState: recording.recorder.state,
        track: track
          ? {
              enabled: track.enabled,
              muted: track.muted,
              readyState: track.readyState,
              settings: track.getSettings(),
            }
          : null,
      };
    }
    if (action === "inspect") {
      const interactive = [
        ...document.querySelectorAll(
          "button,a,input,textarea,select,[role='button'],[role='menuitem'],[tabindex]",
        ),
      ]
        .filter((element) => visible(element) && !element.dataset.brainstemAiDriver)
        .slice(0, Math.max(1, Math.min(200, Number(step.limit) || 80)))
        .map((element) => ({
          selector: selectorFor(element),
          tag: element.localName,
          text: normalizedText(element).slice(0, 180),
          disabled: Boolean(element.disabled),
        }));
      return {
        title: document.title,
        url: location.href,
        interactive,
        text: document.body.innerText.replace(/\s+/g, " ").trim().slice(0, 4000),
      };
    }
    if (action === "read") {
      const element = step.selector ? findElement(step) : document.body;
      if (!element) {
        if (step.optional) return { skipped: true, reason: "target not found" };
        throw new Error(`UI target not found: ${step.selector || step.targetText}`);
      }
      return {
        selector: selectorFor(element),
        text: normalizedText(element).slice(0, Math.max(1, Number(step.limit) || 12000)),
      };
    }
    if (action === "wait") return waitFor(step);
    if (action === "tour" || action === "force_mode") {
      throw new Error(`Use ${action} as a top-level UI driver command, not inside run.`);
    }
    if (action === "announce") {
      await announce(String(step.text || step.label || "AI is operating the Brainstem"), step.durationMs);
      return { announced: String(step.text || step.label || "") };
    }
    if (action === "press") {
      const element = findElement(step) || document.activeElement || document.body;
      if (step.selector && !element) {
        if (step.optional) return { skipped: true, reason: "target not found" };
        throw new Error(`UI target not found: ${step.selector}`);
      }
      if (step.selector) await pointAt(element, labelText(step, `Pressing ${step.key}`));
      element.focus?.({ preventScroll: true });
      const init = {
        bubbles: true,
        cancelable: true,
        key: String(step.key || "Enter"),
        code: String(step.code || ""),
        altKey: Boolean(step.altKey),
        ctrlKey: Boolean(step.ctrlKey),
        metaKey: Boolean(step.metaKey),
        shiftKey: Boolean(step.shiftKey),
      };
      element.dispatchEvent(new KeyboardEvent("keydown", init));
      element.dispatchEvent(new KeyboardEvent("keyup", init));
      await sleep(Math.max(120, Number(step.settleMs) || 280));
      element.classList?.remove("brainstem-ai-driver-target");
      ensureUi().label.classList.remove("show");
      return { pressed: init.key, selector: selectorFor(element) };
    }

    const element = findElement(step);
    if (!element || !visible(element)) {
      if (step.optional) return { skipped: true, reason: "target not visible" };
      throw new Error(
        `Visible UI target not found: ${step.selector || step.targetText || step.text || "(unspecified)"}`,
      );
    }
    if (action === "click") return clickElement(element, step);
    if (action === "type") return typeInto(element, step);
    throw new Error(`Unsupported UI driver action: ${action || "(empty)"}`);
  }

  if (String(command.action || "").toLowerCase() === "run") {
    if (!Array.isArray(command.steps) || command.steps.length === 0) {
      throw new Error("A UI driver run requires at least one step.");
    }
    const results = [];
    for (const step of command.steps) results.push(await perform(step));
    state.lastRun = Date.now();
    return { results };
  }
  const result = await perform(command);
  state.lastRun = Date.now();
  return result;
}

async function startWindowRecording(browserWindow, command, uploadUrl) {
  const sourceId = browserWindow.getMediaSourceId();
  const maxDurationMs = Math.max(
    1000,
    Math.min(10 * 60 * 1000, Number(command.maxDurationMs) || 5 * 60 * 1000),
  );
  recordingPermissionWebContents = browserWindow.webContents;
  try {
    const source = `(${async function startRecording(options) {
      if (
        window.__brainstemBetaRecording
        && window.__brainstemBetaRecording.recorder.state !== "inactive"
      ) {
        throw new Error("The RAPP Brainstem Frontier window is already recording.");
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
          mandatory: {
            chromeMediaSource: "desktop",
            chromeMediaSourceId: options.sourceId,
            maxFrameRate: 30,
            maxHeight: 1240,
            maxWidth: 1920,
          },
        },
      });
      const mimeTypes = [
        "video/webm;codecs=vp8",
        "video/webm;codecs=vp9",
        "video/webm",
      ];
      const mimeType = mimeTypes.find((type) => MediaRecorder.isTypeSupported(type))
        || "";
      const preview = document.createElement("video");
      preview.muted = true;
      preview.playsInline = true;
      preview.srcObject = stream;
      Object.assign(preview.style, {
        position: "fixed",
        right: "0",
        bottom: "0",
        width: "2px",
        height: "2px",
        opacity: ".001",
        pointerEvents: "none",
      });
      document.body.appendChild(preview);
      await preview.play();
      const chunks = [];
      let dataEvents = 0;
      let lastError = null;
      const recorder = new MediaRecorder(
        stream,
        mimeType ? { mimeType, videoBitsPerSecond: 2_000_000 } : undefined,
      );
      const stopped = new Promise((resolve) => {
        recorder.addEventListener("stop", resolve, { once: true });
      });
      recorder.addEventListener("dataavailable", (event) => {
        dataEvents += 1;
        if (event.data?.size) chunks.push(event.data);
      });
      recorder.addEventListener("error", (event) => {
        lastError = String(event.error?.message || event.error || "MediaRecorder error");
      });
      recorder.start(500);

      let indicator = document.getElementById("brainstem-beta-recording-indicator");
      if (!indicator) {
        indicator = document.createElement("div");
        indicator.id = "brainstem-beta-recording-indicator";
        indicator.textContent = "REC  AUTOPILOT";
        Object.assign(indicator.style, {
          position: "fixed",
          zIndex: "2147483647",
          top: "14px",
          left: "50%",
          transform: "translateX(-50%)",
          padding: "7px 11px",
          border: "1px solid #ff7b72",
          borderRadius: "999px",
          background: "rgba(40, 8, 12, .94)",
          color: "#ff7b72",
          font: "700 11px/1 ui-sans-serif, system-ui, sans-serif",
          letterSpacing: ".08em",
          pointerEvents: "none",
          boxShadow: "0 6px 24px rgba(0,0,0,.4)",
        });
        document.body.appendChild(indicator);
      }
      indicator.hidden = false;

      const state = {
        autoStop: null,
        chunks,
        get dataEvents() { return dataEvents; },
        finalize: null,
        finalizePromise: null,
        indicator,
        mimeType: recorder.mimeType || mimeType || "video/webm",
        preview,
        recorder,
        get lastError() { return lastError; },
        startedAt: Date.now(),
        stopped,
        stream,
        uploadUrl: options.uploadUrl,
      };
      state.finalize = () => {
        if (state.finalizePromise) return state.finalizePromise;
        state.finalizePromise = (async () => {
          try {
            clearTimeout(state.autoStop);
            if (state.recorder.state !== "inactive") {
              state.recorder.stop();
            }
            await state.stopped;
            await new Promise((resolve) => setTimeout(resolve, 500));
            const durationMs = Date.now() - state.startedAt;
            const blob = new Blob(state.chunks, { type: state.mimeType });
            if (!blob.size) {
              throw new Error(
                `The recorded window produced an empty WebM blob from ${
                  state.chunks.length
                } chunks.`,
              );
            }
            const bytes = await blob.arrayBuffer();
            const response = await fetch(state.uploadUrl, {
              method: "POST",
              headers: {
                "Content-Type": state.mimeType,
                "X-Recording-Duration": String(durationMs),
                "X-Recording-Size": String(blob.size),
              },
              body: bytes,
            });
            const result = await response.json();
            if (!response.ok || !result?.ok) {
              throw new Error(result?.error || `Recording upload HTTP ${response.status}`);
            }
            const recording = result.recording;
            window.__brainstemBetaLastRecording = recording;
            return recording;
          } finally {
            for (const track of state.stream.getTracks()) track.stop();
            state.preview.pause();
            state.preview.srcObject = null;
            state.preview.remove();
            state.indicator.hidden = true;
            if (window.__brainstemBetaRecording === state) {
              delete window.__brainstemBetaRecording;
            }
          }
        })();
        return state.finalizePromise;
      };
      state.autoStop = setTimeout(() => {
        void state.finalize().catch(() => {
          for (const track of state.stream.getTracks()) track.stop();
          state.preview.pause();
          state.preview.srcObject = null;
          state.preview.remove();
          state.indicator.hidden = true;
        });
      }, options.maxDurationMs);
      window.__brainstemBetaRecording = state;
      return {
        maxDurationMs: options.maxDurationMs,
        mimeType: state.mimeType,
        startedAt: state.startedAt,
        track: stream.getVideoTracks()[0]?.getSettings() || null,
      };
    }.toString()})(${JSON.stringify({ sourceId, maxDurationMs, uploadUrl })})`;
    return await browserWindow.webContents.mainFrame.executeJavaScript(source, true);
  } finally {
    recordingPermissionWebContents = null;
  }
}

function walkthroughRecapChapters(mode = "baseline") {
  if (mode === "stack-churn") {
    return [
      "1 · Identity — start from one default stack",
      "2 · Compose — create a child leaf and ordered overlay",
      "3 · Prove — persistent StackChurnProof returned STACK_CHURN_READY",
      "4 · Retire — remove the role and superseded workers",
      "5 · Restore — delete temporary stacks and return to baseline",
      "6 · Promote — carry only the proven capability downstream",
    ];
  }
  if (mode === "repeat-ephemeral") {
    return [
      "1 · Identity — one caller RAPPID and one private memory anchor",
      "2 · First turn — inject, execute, and clean one temporary tool",
      "3 · Second turn — repeat the same source on the same live worker",
      "4 · Evidence — both exact request results remain in one transcript",
      "5 · Cleanup — zero leases, files, bytecode, or cache growth",
      "6 · Promotion — reusable skills stay; temporary tools disappear",
    ];
  }
  if (mode === "control-handoff") {
    return [
      "1 · Direct control — a person sends the first visible Brainstem turn",
      "2 · Repeat — a second direct turn stays in the same transcript",
      "3 · Handoff — Brain Surgeon takes control without replacing the iframe",
      "4 · Proof — all three request IDs and markers remain ordered",
      "5 · Cleanup — the delegated temporary tool disappears and the lease clears",
      "6 · Outcome — one chat surface, whichever intelligence is driving it",
    ];
  }
  return [
    "1 · Identity — one caller RAPPID and one private memory anchor",
    "2 · Composition — global + inherited + leaf + ordered overlays",
    "3 · Hotload — a single-file agent became a real tool for one turn",
    "4 · Evidence — the center Brainstem returned a testable result",
    "5 · Cleanup — the ephemeral worker disappeared automatically",
    "6 · Promotion — Frontier Brainstem → Hippocampus → Microsoft stack",
  ];
}

async function stopWindowRecording(browserWindow, command = {}) {
  const minimumDurationMs = Math.max(
    0,
    Math.min(5 * 60 * 1000, Number(command.minimumDurationMs) || 0),
  );
  const source = `(${async function stopRecording(options) {
    const state = window.__brainstemBetaRecording;
    if (state) {
      const remaining = Math.max(
        0,
        options.minimumDurationMs - (Date.now() - state.startedAt),
      );
      if (remaining) {
        let recap = document.getElementById("brainstem-beta-walkthrough-recap");
        if (!recap) {
          recap = document.createElement("div");
          recap.id = "brainstem-beta-walkthrough-recap";
          Object.assign(recap.style, {
            position: "fixed",
            zIndex: "2147483646",
            left: "50%",
            bottom: "54px",
            width: "min(760px, calc(100vw - 48px))",
            transform: "translateX(-50%)",
            padding: "18px 22px",
            border: "1px solid rgba(88, 166, 255, .55)",
            borderRadius: "16px",
            background: "rgba(13, 17, 23, .94)",
            color: "#f0f6fc",
            font: "700 18px/1.35 ui-sans-serif, system-ui, sans-serif",
            textAlign: "center",
            boxShadow: "0 18px 70px rgba(0,0,0,.58)",
            pointerEvents: "none",
          });
          document.body.appendChild(recap);
        }
        const chapters = options.chapters;
        const started = Date.now();
        const intervalMs = Math.max(
          5000,
          Math.min(12000, Math.floor(remaining / chapters.length) || 5000),
        );
        let index = 0;
        while (Date.now() - started < remaining) {
          recap.textContent = chapters[index % chapters.length];
          index += 1;
          await new Promise((resolve) => setTimeout(
            resolve,
            Math.min(intervalMs, remaining - (Date.now() - started)),
          ));
        }
        recap.remove();
      }
      return state.finalize();
    }
    const last = window.__brainstemBetaLastRecording;
    if (last) {
      delete window.__brainstemBetaLastRecording;
      return last;
    }
    throw new Error("The RAPP Brainstem Frontier window is not recording.");
  }.toString()})(${JSON.stringify({
    chapters: walkthroughRecapChapters(command.recapMode),
    minimumDurationMs,
  })})`;
  return browserWindow.webContents.mainFrame.executeJavaScript(source, true);
}

async function setCapturedRecordingIndicator(browserWindow, visible) {
  const source = `(${function setIndicator(show) {
    let indicator = document.getElementById("brainstem-beta-recording-indicator");
    if (!indicator) {
      indicator = document.createElement("div");
      indicator.id = "brainstem-beta-recording-indicator";
      indicator.textContent = "REC  AUTOPILOT";
      Object.assign(indicator.style, {
        position: "fixed",
        zIndex: "2147483647",
        top: "14px",
        left: "50%",
        transform: "translateX(-50%)",
        padding: "7px 11px",
        border: "1px solid #ff7b72",
        borderRadius: "999px",
        background: "rgba(40, 8, 12, .94)",
        color: "#ff7b72",
        font: "700 11px/1 ui-sans-serif, system-ui, sans-serif",
        letterSpacing: ".08em",
        pointerEvents: "none",
        boxShadow: "0 6px 24px rgba(0,0,0,.4)",
      });
      document.body.appendChild(indicator);
    }
    indicator.hidden = !show;
    return true;
  }.toString()})(${JSON.stringify(Boolean(visible))})`;
  await browserWindow.webContents.mainFrame.executeJavaScript(source, true);
}

async function showCapturedRecordingRecap(
  browserWindow,
  durationMs,
  recapMode = "baseline",
) {
  if (durationMs <= 0) return;
  const source = `(${async function showRecap(options) {
    let recap = document.getElementById("brainstem-beta-walkthrough-recap");
    if (!recap) {
      recap = document.createElement("div");
      recap.id = "brainstem-beta-walkthrough-recap";
      Object.assign(recap.style, {
        position: "fixed",
        zIndex: "2147483646",
        left: "50%",
        bottom: "54px",
        width: "min(760px, calc(100vw - 48px))",
        transform: "translateX(-50%)",
        padding: "18px 22px",
        border: "1px solid rgba(88, 166, 255, .55)",
        borderRadius: "16px",
        background: "rgba(13, 17, 23, .94)",
        color: "#f0f6fc",
        font: "700 18px/1.35 ui-sans-serif, system-ui, sans-serif",
        textAlign: "center",
        boxShadow: "0 18px 70px rgba(0,0,0,.58)",
        pointerEvents: "none",
      });
      document.body.appendChild(recap);
    }
    const chapters = options.chapters;
    const started = Date.now();
    const intervalMs = Math.max(
      5000,
      Math.min(12000, Math.floor(options.durationMs / chapters.length) || 5000),
    );
    let index = 0;
    while (Date.now() - started < options.durationMs) {
      recap.textContent = chapters[index % chapters.length];
      index += 1;
      await new Promise((resolve) => setTimeout(
        resolve,
        Math.min(intervalMs, options.durationMs - (Date.now() - started)),
      ));
    }
    recap.remove();
  }.toString()})(${JSON.stringify({
    chapters: walkthroughRecapChapters(recapMode),
    durationMs,
  })})`;
  await browserWindow.webContents.mainFrame.executeJavaScript(source, true);
}

async function writeCapturedFrame(state, browserWindow) {
  if (state.captureInFlight || state.stopping) return;
  state.captureInFlight = true;
  try {
    const image = await browserWindow.webContents.capturePage();
    if (image.isEmpty()) throw new Error("Electron captured an empty window frame.");
    const size = image.getSize();
    const frame = size.width > 1920 ? image.resize({ width: 1920 }) : image;
    const png = frame.toPNG();
    const targetFrames = Math.max(
      1,
      Math.floor((Date.now() - state.startedAt) / state.frameIntervalMs) + 1,
    );
    const copies = Math.max(1, targetFrames - state.framesWritten);
    for (let index = 0; index < copies; index += 1) {
      if (!state.process.stdin.write(png)) {
        await once(state.process.stdin, "drain");
      }
    }
    state.framesWritten += copies;
    state.lastFrame = png;
    state.lastFrameAt = Date.now();
  } catch (error) {
    state.error = errorMessage(error);
  } finally {
    state.captureInFlight = false;
  }
}

async function startCapturedWindowRecording(
  browserWindow,
  command,
  {
    env,
    publishArtifact,
    recordingDir,
  },
) {
  const existing = capturedRecordings.get(browserWindow);
  if (existing && !existing.stopping) {
    throw new Error("The RAPP Brainstem Frontier window is already recording.");
  }
  const maxDurationMs = Math.max(
    1000,
    Math.min(10 * 60 * 1000, Number(command.maxDurationMs) || 5 * 60 * 1000),
  );
  const frameRate = Math.max(
    2,
    Math.min(12, Number(command.frameRate) || 8),
  );
  const frameIntervalMs = 1000 / frameRate;
  mkdirSync(recordingDir, { recursive: true });
  const outputPath = path.join(
    recordingDir,
    `brainstem-${new Date().toISOString().replace(/[:.]/g, "-")}.webm`,
  );
  const temporaryPath = `${outputPath}.${process.pid}.tmp.webm`;
  const executable = resolveFfmpegExecutable(env);
  const child = spawn(
    executable,
    [
      "-hide_banner",
      "-loglevel",
      "error",
      "-f",
      "image2pipe",
      "-framerate",
      String(frameRate),
      "-vcodec",
      "png",
      "-i",
      "pipe:0",
      "-an",
      "-c:v",
      "libvpx-vp9",
      "-b:v",
      "1800k",
      "-deadline",
      "realtime",
      "-cpu-used",
      "5",
      "-pix_fmt",
      "yuv420p",
      "-f",
      "webm",
      "-y",
      temporaryPath,
    ],
    {
      env,
      stdio: ["pipe", "ignore", "pipe"],
      windowsHide: true,
    },
  );
  let stderr = "";
  child.stderr.on("data", (chunk) => {
    stderr = `${stderr}${chunk}`.slice(-16000);
  });
  await new Promise((resolve, reject) => {
    child.once("spawn", resolve);
    child.once("error", reject);
  });
  const closePromise = new Promise((resolve) => {
    child.once("close", (code, signal) => resolve({ code, signal }));
  });
  const state = {
    autoStop: null,
    captureInFlight: false,
    closePromise,
    error: null,
    finalizePromise: null,
    frameIntervalMs,
    frameRate,
    framesWritten: 0,
    lastFrame: null,
    lastFrameAt: null,
    maxDurationMs,
    outputPath,
    process: child,
    publishArtifact,
    startedAt: Date.now(),
    stopping: false,
    temporaryPath,
  };
  child.stdin.on("error", (error) => {
    state.error ||= errorMessage(error);
  });
  state.finalize = () => {
    if (state.finalizePromise) return state.finalizePromise;
    state.finalizePromise = (async () => {
      let completed = false;
      try {
        clearInterval(state.captureTimer);
        clearTimeout(state.autoStop);
        while (state.captureInFlight) {
          await new Promise((resolve) => setTimeout(resolve, 25));
        }
        state.stopping = true;
        const durationMs = Date.now() - state.startedAt;
        const targetFrames = Math.max(1, Math.ceil(durationMs / frameIntervalMs));
        if (state.lastFrame) {
          while (state.framesWritten < targetFrames) {
            if (!child.stdin.write(state.lastFrame)) {
              await once(child.stdin, "drain");
            }
            state.framesWritten += 1;
          }
        }
        child.stdin.end();
        const result = await Promise.race([
          state.closePromise,
          new Promise((_, reject) => setTimeout(
            () => reject(new Error("ffmpeg did not finalize within 60 seconds.")),
            60000,
          )),
        ]);
        if (result.code !== 0) {
          throw new Error(
            `ffmpeg exited with ${result.code ?? result.signal}: ${stderr.trim()}`,
          );
        }
        if (state.error) throw new Error(state.error);
        if (!existsSync(temporaryPath) || !statSync(temporaryPath).size) {
          throw new Error("ffmpeg produced an empty walkthrough recording.");
        }
        renameSync(temporaryPath, outputPath);
        const recording = {
          durationMs,
          frameRate,
          framesWritten: state.framesWritten,
          mimeType: "video/webm",
          path: outputPath,
          sizeBytes: statSync(outputPath).size,
          url: publishArtifact(outputPath, "video/webm", "recordings"),
        };
        completed = true;
        lastCapturedRecordings.set(browserWindow, recording);
        return recording;
      } finally {
        capturedRecordings.delete(browserWindow);
        await setCapturedRecordingIndicator(browserWindow, false).catch(() => {});
        if (!completed) {
          child.kill("SIGTERM");
          rmSync(temporaryPath, { force: true });
        }
      }
    })();
    return state.finalizePromise;
  };
  capturedRecordings.set(browserWindow, state);
  await setCapturedRecordingIndicator(browserWindow, true);
  await writeCapturedFrame(state, browserWindow);
  if (state.error || !state.framesWritten) {
    await state.finalize().catch(() => {});
    throw new Error(state.error || "The first walkthrough frame was not captured.");
  }
  state.captureTimer = setInterval(() => {
    void writeCapturedFrame(state, browserWindow);
  }, frameIntervalMs);
  state.autoStop = setTimeout(() => {
    void state.finalize().catch(() => {});
  }, maxDurationMs);
  return {
    encoder: "ffmpeg",
    frameRate,
    maxDurationMs,
    startedAt: state.startedAt,
  };
}

async function stopCapturedWindowRecording(browserWindow, command = {}) {
  const state = capturedRecordings.get(browserWindow);
  if (!state) {
    const last = lastCapturedRecordings.get(browserWindow);
    if (last) {
      lastCapturedRecordings.delete(browserWindow);
      return last;
    }
    throw new Error("The RAPP Brainstem Frontier window is not recording.");
  }
  const minimumDurationMs = Math.max(
    0,
    Math.min(5 * 60 * 1000, Number(command.minimumDurationMs) || 0),
  );
  const remaining = Math.max(
    0,
    minimumDurationMs - (Date.now() - state.startedAt),
  );
  await showCapturedRecordingRecap(
    browserWindow,
    remaining,
    command.recapMode,
  );
  return state.finalize();
}

function capturedWindowRecordingStatus(browserWindow) {
  const state = capturedRecordings.get(browserWindow);
  if (!state) return { active: false };
  return {
    active: !state.stopping,
    elapsedMs: Date.now() - state.startedAt,
    encoder: "ffmpeg",
    error: state.error,
    frameRate: state.frameRate,
    framesWritten: state.framesWritten,
    lastFrameAt: state.lastFrameAt,
    pid: state.process.pid,
  };
}

async function abortCapturedWindowRecording(browserWindow) {
  const state = capturedRecordings.get(browserWindow);
  if (!state) return;
  clearInterval(state.captureTimer);
  clearTimeout(state.autoStop);
  state.stopping = true;
  state.process.stdin.destroy();
  state.process.kill("SIGTERM");
  capturedRecordings.delete(browserWindow);
  rmSync(state.temporaryPath, { force: true });
  await setCapturedRecordingIndicator(browserWindow, false).catch(() => {});
}

function validateCommand(command) {
  const action = String(command.action || "").toLowerCase();
  const allowed = new Set([
    "announce",
    "chat",
    "click",
    "force_mode",
    "inspect",
    "press",
    "read",
    "recording_status",
    "route_telemetry",
    "refresh",
    "run",
    "screenshot",
    "start_recording",
    "set_chat_lease",
    "stop_recording",
    "surgeon_chat",
    "tour",
    "type",
    "wait",
  ]);
  if (!allowed.has(action)) {
    throw new Error(`Unsupported UI driver action: ${action || "(empty)"}`);
  }
  if (action === "run") {
    if (!Array.isArray(command.steps) || command.steps.length < 1 || command.steps.length > 40) {
      throw new Error("UI driver runs require between 1 and 40 steps.");
    }
    for (const step of command.steps) {
      const nested = validateCommand(step);
      if (nested.action === "tour" || nested.action === "force_mode") {
        throw new Error(`Use ${nested.action} as a top-level UI driver command, not inside run.`);
      }
    }
  }
  return { ...command, action };
}

// ── AI force mode ─────────────────────────────────────────────────────────
// A hidden, opt-in visual state: while an AI is driving the visible window on
// the user's behalf, the whole window's edges glow and a small tag says so.
// It is only ever lit by an explicit `force_mode` command or by a driver
// command carrying `forceMode: true`, and it fades on its own after the AI
// goes quiet, so it never lingers when a person is driving.
const FORCE_MODE_IDLE_MS = 30000;
const forceModeState = new WeakMap();

async function setForceMode(browserWindow, on, options = {}) {
  const source = `(${function forceModeOverlay(settings) {
    const STYLE_ID = "brainstem-ai-force-mode-style";
    const ID = "brainstem-ai-force-mode";
    if (!document.getElementById(STYLE_ID)) {
      const style = document.createElement("style");
      style.id = STYLE_ID;
      style.textContent = `
        #${ID} { position: fixed; inset: 0; z-index: 2147483000; pointer-events: none; }
        #${ID}[hidden] { display: none; }
        #${ID} .brainstem-ai-force-edge { position: absolute; inset: 0;
          box-shadow: inset 0 0 0 2px rgba(124,140,255,.9), inset 0 0 44px rgba(124,140,255,.30), inset 0 0 130px rgba(88,166,255,.16);
          animation: brainstem-ai-force-breathe 2.4s ease-in-out infinite; }
        #${ID} .brainstem-ai-force-tag { position: absolute; left: 50%; bottom: 14px; transform: translateX(-50%);
          display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 999px;
          border: 1px solid rgba(124,140,255,.75); background: rgba(10,12,32,.94); color: #c7ceff;
          font: 700 11px/1 ui-sans-serif, system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase;
          box-shadow: 0 6px 24px rgba(0,0,0,.45), 0 0 18px rgba(124,140,255,.35); white-space: nowrap; }
        #${ID} .brainstem-ai-force-dot { width: 8px; height: 8px; border-radius: 50%; background: #9aa6ff;
          box-shadow: 0 0 0 3px rgba(154,166,255,.25); animation: brainstem-ai-force-pulse 1.6s ease-in-out infinite; }
        @keyframes brainstem-ai-force-breathe { 0%,100% { opacity: .55; } 50% { opacity: 1; } }
        @keyframes brainstem-ai-force-pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.35); } }
        @media (prefers-reduced-motion: reduce) {
          #${ID} .brainstem-ai-force-edge, #${ID} .brainstem-ai-force-dot { animation: none; }
        }`;
      document.head.appendChild(style);
    }
    let overlay = document.getElementById(ID);
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = ID;
      overlay.dataset.brainstemAiDriver = "true";
      overlay.setAttribute("role", "status");
      overlay.setAttribute("aria-live", "polite");
      overlay.innerHTML = '<div class="brainstem-ai-force-edge"></div>'
        + '<div class="brainstem-ai-force-tag"><span class="brainstem-ai-force-dot"></span><span class="brainstem-ai-force-text"></span></div>';
      document.body.appendChild(overlay);
    }
    overlay.querySelector(".brainstem-ai-force-text").textContent = String(
      settings.label || "AI force mode · an AI is driving this Brainstem — you're watching",
    ).slice(0, 120);
    overlay.hidden = !settings.on;
    return { forceMode: Boolean(settings.on) };
  }.toString()})(${JSON.stringify({ on: Boolean(on), label: options.label || "" })})`;
  const result = await browserWindow.webContents.mainFrame.executeJavaScript(source, true);
  const state = forceModeState.get(browserWindow) || {};
  clearTimeout(state.timer);
  state.on = Boolean(on);
  state.timer = null;
  forceModeState.set(browserWindow, state);
  return result;
}

function armForceModeIdle(browserWindow, idleMs = FORCE_MODE_IDLE_MS) {
  const state = forceModeState.get(browserWindow);
  if (!state?.on) return;
  clearTimeout(state.timer);
  state.timer = setTimeout(() => {
    setForceMode(browserWindow, false).catch(() => {});
  }, Math.max(1000, Math.min(10 * 60 * 1000, Number(idleMs) || FORCE_MODE_IDLE_MS)));
  state.timer.unref?.();
}

function forceModeStatus(browserWindow) {
  return { forceMode: Boolean(forceModeState.get(browserWindow)?.on) };
}

// ── Show Mode click-through (tour) ────────────────────────────────────────
// Drives the Show Mode click-through preview that lives in the shell window
// (ui/show-mode-tour.js) so an AI can walk it, pause on a step, and capture
// evidence exactly as a person clicking Next would see it.
async function runTourCommand(browserWindow, command) {
  const source = `(${async function tourCommand(cmd) {
    const tour = window.rappShowModeTour;
    if (!tour) return { available: false, error: "Show Mode click-through is not loaded in this window." };
    const value = String(cmd.value || "status").toLowerCase();
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const indexOf = (ref) => {
      if (ref === undefined || ref === null || ref === "") return -1;
      const asNumber = Number(ref);
      if (Number.isInteger(asNumber) && asNumber >= 0 && asNumber < tour.steps.length) return asNumber;
      return tour.steps.indexOf(String(ref));
    };
    if (value === "start") tour.start(0);
    else if (value === "next") tour.running ? tour.next() : tour.start(0);
    else if (value === "prev") tour.prev();
    else if (value === "stop") tour.stop();
    else if (value === "goto") {
      const index = indexOf(cmd.step);
      if (index < 0) return { available: true, error: `Unknown tour step ${cmd.step}`, steps: tour.steps };
      tour.start(index);
    } else if (value !== "status") {
      return { available: true, error: `Unsupported tour command ${value}`, steps: tour.steps };
    }
    if (value !== "status") {
      await sleep(Math.max(0, Math.min(5000, Number(cmd.settleMs) || 750)));
      // Let the compositor commit the new step before anyone captures the page.
      await Promise.race([
        new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))),
        sleep(400),
      ]);
    }
    return {
      available: true,
      running: Boolean(tour.running),
      step: tour.step || null,
      index: tour.steps.indexOf(tour.step),
      total: tour.steps.length,
      steps: tour.steps,
    };
  }.toString()})(${JSON.stringify(command)})`;
  const value = String(command.value || "status").toLowerCase();
  if (value !== "status") {
    // The click-through is a presentation: keep painting while it runs so
    // captures reflect the current step, and surface the window without
    // stealing keyboard focus from wherever the person is typing.
    try {
      browserWindow.webContents.setBackgroundThrottling(value !== "stop");
      if (value !== "stop" && !browserWindow.isFocused()) {
        if (browserWindow.isMinimized()) browserWindow.restore();
        browserWindow.moveTop?.();
      }
    } catch {
      // best effort
    }
  }
  return browserWindow.webContents.mainFrame.executeJavaScript(source, true);
}

function writeMetadata(metadataPath, metadata) {
  mkdirSync(path.dirname(metadataPath), { recursive: true });
  const temporaryPath = `${metadataPath}.${process.pid}.tmp`;
  writeFileSync(temporaryPath, `${JSON.stringify(metadata, null, 2)}\n`, {
    mode: 0o600,
  });
  renameSync(temporaryPath, metadataPath);
}

function removeOwnedMetadata(metadataPath, token) {
  try {
    const current = JSON.parse(readFileSync(metadataPath, "utf8"));
    if (current.token === token && current.pid === process.pid) {
      rmSync(metadataPath, { force: true });
    }
  } catch {
    // A missing or replaced metadata file belongs to no cleanup action here.
  }
}

export async function startUiDriverServer({
  window,
  brainstemHome,
  brainstemRuntimeFingerprint = null,
  loopbackUrl,
  env = process.env,
  routeTelemetry = () => null,
  runtimeFingerprint = null,
} = {}) {
  if (!window || typeof loopbackUrl !== "function") {
    throw new Error("The UI driver requires a BrowserWindow and loopback URL guard.");
  }
  const betaHome = env.BRAINSTEM_BETA_HOME
    || path.join(brainstemHome, "beta-launcher");
  const metadataPath = env.BRAINSTEM_BETA_UI_DRIVER_FILE
    || path.join(betaHome, "ui-driver.json");
  const captureDir = path.join(betaHome, "captures");
  const recordingDir = path.join(betaHome, "recordings");
  const token = randomBytes(32).toString("hex");
  const artifactToken = randomBytes(32).toString("hex");
  const artifacts = new Map();
  const sockets = new Set();
  let stopping = false;

  function publishArtifact(filePath, contentType, kind) {
    if (!existsSync(filePath)) {
      throw new Error(`UI driver artifact is missing: ${filePath}`);
    }
    const artifactId = randomBytes(18).toString("base64url");
    artifacts.set(artifactId, {
      contentType,
      kind,
      path: filePath,
      createdAt: Date.now(),
    });
    while (artifacts.size > 100) {
      artifacts.delete(artifacts.keys().next().value);
    }
    const address = server.address();
    if (!address || typeof address === "string") {
      throw new Error("The UI driver artifact server is unavailable.");
    }
    return `http://127.0.0.1:${address.port}/v1/${kind}/${artifactId}`
      + `?token=${encodeURIComponent(artifactToken)}`;
  }

  async function captureEvidence() {
    mkdirSync(captureDir, { recursive: true });
    const image = await window.webContents.capturePage();
    const outputPath = path.join(
      captureDir,
      `brainstem-${new Date().toISOString().replace(/[:.]/g, "-")}.png`,
    );
    writeFileSync(outputPath, image.toPNG(), { mode: 0o600 });
    const preview = image.getSize().width > 1280
      ? image.resize({ width: 1280 })
      : image;
    const frame = brainstemFrame(window, loopbackUrl);
    const visibleText = frame
      ? await frame.executeJavaScript(
          "document.body.innerText.replace(/\\s+/g, ' ').trim().slice(0, 12000)",
          true,
        )
      : "";
    return {
      captureUrl: publishArtifact(outputPath, "image/png", "captures"),
      dataUrl: `data:image/jpeg;base64,${preview.toJPEG(72).toString("base64")}`,
      path: outputPath,
      size: image.getSize(),
      visibleText,
    };
  }

  const server = createServer(async (request, response) => {
    if (stopping) {
      jsonResponse(response, 503, { ok: false, error: "UI driver is shutting down." });
      return;
    }
    const requestUrl = new URL(request.url || "/", "http://127.0.0.1");
    if (
      request.method === "OPTIONS"
      && requestUrl.pathname === "/v1/recording-upload"
    ) {
      if (requestUrl.searchParams.get("token") !== artifactToken) {
        jsonResponse(response, 401, { ok: false, error: "Unauthorized." });
        return;
      }
      response.writeHead(204, {
        "Access-Control-Allow-Headers": "Content-Type, X-Recording-Duration, X-Recording-Size",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Private-Network": "true",
        "Access-Control-Max-Age": "600",
        "Cache-Control": "no-store",
      });
      response.end();
      return;
    }
    if (
      request.method === "POST"
      && requestUrl.pathname === "/v1/recording-upload"
    ) {
      response.setHeader("Access-Control-Allow-Origin", "*");
      if (requestUrl.searchParams.get("token") !== artifactToken) {
        jsonResponse(response, 401, { ok: false, error: "Unauthorized." });
        return;
      }
      const mimeType = String(request.headers["content-type"] || "")
        .split(";", 1)[0];
      if (mimeType !== "video/webm") {
        jsonResponse(response, 415, {
          ok: false,
          error: "The recording upload must be video/webm.",
        });
        return;
      }
      mkdirSync(recordingDir, { recursive: true });
      const outputPath = path.join(
        recordingDir,
        `brainstem-${new Date().toISOString().replace(/[:.]/g, "-")}.webm`,
      );
      const temporaryPath = `${outputPath}.${process.pid}.tmp`;
      const output = createWriteStream(temporaryPath, { mode: 0o600 });
      let size = 0;
      try {
        for await (const chunk of request) {
          size += chunk.length;
          if (size > 500 * 1024 * 1024) {
            throw new Error("The recorded window exceeds 500 MB.");
          }
          if (!output.write(chunk)) await once(output, "drain");
        }
        output.end();
        await once(output, "finish");
        if (!size) {
          throw new Error(
            `The recorded window is empty (renderer reported ${
              request.headers["x-recording-size"] || "unknown"
            } bytes).`,
          );
        }
        renameSync(temporaryPath, outputPath);
        const durationMs = Number(request.headers["x-recording-duration"]) || null;
        jsonResponse(response, 200, {
          ok: true,
          recording: {
            durationMs,
            mimeType,
            path: outputPath,
            sizeBytes: size,
            url: publishArtifact(outputPath, mimeType, "recordings"),
          },
        });
      } catch (error) {
        output.destroy();
        rmSync(temporaryPath, { force: true });
        jsonResponse(response, 400, {
          ok: false,
          error: errorMessage(error),
        });
      }
      return;
    }
    const artifactMatch = requestUrl.pathname.match(
      /^\/v1\/(captures|recordings)\/([A-Za-z0-9_-]+)$/,
    );
    if (request.method === "GET" && artifactMatch) {
      const artifact = artifacts.get(artifactMatch[2]);
      if (
        requestUrl.searchParams.get("token") !== artifactToken
        || !artifact
        || artifact.kind !== artifactMatch[1]
        || !existsSync(artifact.path)
      ) {
        jsonResponse(response, 404, { ok: false, error: "Artifact not found." });
        return;
      }
      const body = readFileSync(artifact.path);
      response.writeHead(200, {
        "Cache-Control": "no-store",
        "Content-Length": body.length,
        "Content-Type": artifact.contentType,
      });
      server.on("connection", (socket) => {
        sockets.add(socket);
        socket.once("close", () => sockets.delete(socket));
      });
      response.end(body);
      return;
    }

    if (request.method !== "POST" || requestUrl.pathname !== "/v1/command") {
      jsonResponse(response, 404, { ok: false, error: "Not found." });
      return;
    }
    if (request.headers.authorization !== `Bearer ${token}`) {
      jsonResponse(response, 401, { ok: false, error: "Unauthorized." });
      return;
    }

    let heartbeat = null;
    try {
      const command = validateCommand(await readJsonBody(request));
      response.writeHead(200, {
        "Cache-Control": "no-store",
        "Content-Type": "application/json; charset=utf-8",
      });
      response.flushHeaders();
      heartbeat = setInterval(() => {
        if (!response.writableEnded) response.write(" ");
      }, 15000);
      if (command.forceMode === true) {
        await setForceMode(window, true, { label: command.forceLabel });
      }
      if (command.action === "force_mode") {
        const wanted = String(command.value || "status").toLowerCase();
        if (wanted === "on") await setForceMode(window, true, { label: command.label });
        else if (wanted === "off") await setForceMode(window, false);
        else if (wanted !== "status") {
          throw new Error(`Unsupported force_mode value: ${wanted}`);
        }
        if (wanted === "on") armForceModeIdle(window, command.idleMs);
        jsonResponse(response, 200, { ok: true, result: forceModeStatus(window) });
        return;
      }
      if (command.action === "tour") {
        const result = await runTourCommand(window, command);
        armForceModeIdle(window, command.idleMs);
        jsonResponse(response, 200, { ok: true, result });
        return;
      }
      if (
        command.action === "recording_status"
        && capturedRecordings.has(window)
      ) {
        jsonResponse(response, 200, {
          ok: true,
          result: capturedWindowRecordingStatus(window),
        });
        return;
      }
      if (command.action === "route_telemetry") {
        const navigationCount = await window.webContents.mainFrame
          .executeJavaScript(
            "Number(window.__brainstemBetaNavigationCount || 0)",
            true,
          );
        const activeFrame = brainstemFrame(window, loopbackUrl);
        const chatLeaseCount = activeFrame
          ? await activeFrame.executeJavaScript(
              "Number(window.__brainstemAiDriver?.chatLeaseTokens?.size || 0)",
              true,
            )
          : null;
        jsonResponse(response, 200, {
          ok: true,
          result: {
            ...routeTelemetry(),
            chat_lease_count: chatLeaseCount,
            navigation_count: navigationCount,
          },
        });
        return;
      }
      if (command.action === "refresh") {
        const frame = brainstemFrame(window, loopbackUrl);
        if (!frame) {
          throw new Error("The live Brainstem frontend is not loaded yet.");
        }
        await frame.executeJavaScript(
          "setTimeout(() => location.reload(), 25); true",
          true,
        );
        jsonResponse(response, 200, {
          ok: true,
          result: { refreshing: true },
        });
        return;
      }
      if (command.action === "start_recording") {
        let result;
        try {
          result = await startCapturedWindowRecording(window, command, {
            env,
            publishArtifact,
            recordingDir,
          });
        } catch (captureError) {
          const address = server.address();
          if (!address || typeof address === "string") {
            throw captureError;
          }
          const uploadUrl = `http://127.0.0.1:${address.port}/v1/recording-upload`
            + `?token=${encodeURIComponent(artifactToken)}`;
          result = await startWindowRecording(window, command, uploadUrl);
          result.fallback = errorMessage(captureError);
        }
        jsonResponse(response, 200, { ok: true, result });
        return;
      }
      if (command.action === "stop_recording") {
        const recording = (
          capturedRecordings.has(window)
          || lastCapturedRecordings.has(window)
        )
          ? await stopCapturedWindowRecording(window, command)
          : await stopWindowRecording(window, command);
        jsonResponse(response, 200, {
          ok: true,
          result: {
            recording,
            screenshot: await captureEvidence(),
          },
        });
        return;
      }
      if (command.action === "screenshot") {
        jsonResponse(response, 200, {
          ok: true,
          result: await captureEvidence(),
        });
        return;
      }

      const target = command.target === "shell"
        ? window.webContents.mainFrame
        : brainstemFrame(window, loopbackUrl);
      if (!target) {
        throw new Error("The live Brainstem frontend is not loaded yet.");
      }
      const source = `(${browserDriverCommand.toString()})(${JSON.stringify(command)})`;
      const result = await target.executeJavaScript(source, true);
      armForceModeIdle(window, command.idleMs);
      jsonResponse(response, 200, { ok: true, result });
    } catch (error) {
      jsonResponse(response, 400, { ok: false, error: errorMessage(error) });
    } finally {
      if (heartbeat) clearInterval(heartbeat);
    }
  });

  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  const address = server.address();
  if (!address || typeof address === "string") {
    server.close();
    throw new Error("The UI driver could not allocate a loopback port.");
  }

  writeMetadata(metadataPath, {
    version: 1,
    host: "127.0.0.1",
    port: address.port,
    token,
    pid: process.pid,
    brainstemRuntimeFingerprint,
    runtimeFingerprint,
    startedAt: new Date().toISOString(),
  });

  return {
    metadataPath,
    publishArtifact,
    async stop() {
      stopping = true;
      await abortCapturedWindowRecording(window);
      const closed = new Promise((resolve) => server.close(resolve));
      for (const socket of sockets) socket.destroy();
      server.closeAllConnections?.();
      await Promise.race([
        closed,
        new Promise((resolve) => setTimeout(resolve, 2000)),
      ]);
      removeOwnedMetadata(metadataPath, token);
    },
  };
}

export const uiDriverInternals = {
  browserDriverCommand,
  forceModeStatus,
  runTourCommand,
  setForceMode,
  startCapturedWindowRecording,
  startWindowRecording,
  stopCapturedWindowRecording,
  stopWindowRecording,
  validateCommand,
  walkthroughRecapChapters,
  writeCapturedFrame,
};

export function allowsUiDriverMediaPermission(webContents, permission) {
  return permission === "media" && webContents === recordingPermissionWebContents;
}
