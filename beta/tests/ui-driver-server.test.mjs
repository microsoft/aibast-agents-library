import assert from "node:assert/strict";
import test from "node:test";

import {
  startUiDriverServer,
  uiDriverInternals,
} from "../electron/ui-driver-server.mjs";

test("visible UI driver accepts bounded user-like actions", () => {
  assert.deepEqual(
    uiDriverInternals.validateCommand({
      action: "run",
      steps: [
        { action: "announce", text: "Opening the beta menu" },
        { action: "click", selector: "#beta-app-btn" },
        { action: "type", selector: "#input", value: "hello" },
        { action: "wait", text: "done", timeoutMs: 5000 },
      ],
    }).action,
    "run",
  );
  assert.equal(
    uiDriverInternals.validateCommand({ action: "recording_status" }).action,
    "recording_status",
  );
  assert.equal(
    uiDriverInternals.validateCommand({
      action: "set_chat_lease",
      locked: true,
    }).action,
    "set_chat_lease",
  );
  assert.equal(
    uiDriverInternals.validateCommand({ action: "route_telemetry" }).action,
    "route_telemetry",
  );
});

test("visible UI driver rejects unknown and unbounded commands", () => {
  assert.throws(
    () => uiDriverInternals.validateCommand({ action: "evaluate" }),
    /Unsupported UI driver action/,
  );
  assert.throws(
    () => uiDriverInternals.validateCommand({ action: "run", steps: [] }),
    /between 1 and 40 steps/,
  );
  assert.throws(
    () => uiDriverInternals.validateCommand({
      action: "run",
      steps: Array.from({ length: 41 }, () => ({ action: "click" })),
    }),
    /between 1 and 40 steps/,
  );
});

test("visible chat waits for the stable SSE reply and has no legacy lease hooks", () => {
  const source = uiDriverInternals.browserDriverCommand.toString();
  assert.match(
    source,
    /\.msg\.assistant:not\(\.typing-indicator\):not\(\.stream-arriving\)/,
  );
  assert.match(source, /data-request-id/);
  assert.match(source, /chatLeaseLocked/);
  assert.match(source, /event\.isTrusted/);
  assert.match(source, /MutationObserver/);
  assert.match(source, /const errorBaseline = document\.querySelectorAll/);
  assert.match(source, /errors\.length > errorBaseline/);
  assert.doesNotMatch(source, /chatLeaseBypass/);
  assert.match(source, /if \(response\)/);
  assert.doesNotMatch(
    source,
    /__rappSetNextAgentLease|__rappSetNextUserGuid|agentLease|userGuid/,
  );
});

test("Brain Surgeon driver opens an existing off-canvas panel without a visible tab", () => {
  const source = uiDriverInternals.browserDriverCommand.toString();
  assert.match(source, /if \(!panel\)/);
  assert.match(source, /if \(visible\(tab\)\)/);
  assert.match(source, /panel\.classList\.add\("open"\)/);
  assert.match(source, /document\.body\.classList\.add\("surgeon-open"\)/);
});

test("synthetic cursor fades after the UI driver becomes idle", () => {
  const source = uiDriverInternals.browserDriverCommand.toString();
  assert.match(source, /const CURSOR_IDLE_HIDE_MS = 4000/);
  assert.match(source, /clearTimeout\(state\.cursorIdleTimer\)/);
  assert.match(source, /cursor\.style\.opacity = "0"/);
  assert.match(source, /cursor\.style\.top = `\$\{y\}px`;\s+wakeCursor\(cursor\)/);
});

test("walkthrough recording pads with visible recap cards, not dead air", () => {
  const source = uiDriverInternals.stopWindowRecording.toString();
  assert.match(source, /minimumDurationMs/);
  assert.match(source, /brainstem-beta-walkthrough-recap/);
  assert.match(
    uiDriverInternals.walkthroughRecapChapters("baseline").join(" "),
    /Frontier Brainstem → Hippocampus → Microsoft stack/,
  );
  assert.match(
    uiDriverInternals.walkthroughRecapChapters("stack-churn").join(" "),
    /STACK_CHURN_READY/,
  );
  assert.match(
    uiDriverInternals.walkthroughRecapChapters("control-handoff").join(" "),
    /same transcript/,
  );
});

test("long UI commands flush headers and send heartbeats", () => {
  const source = startUiDriverServer.toString();
  assert.match(source, /flushHeaders/);
  assert.match(source, /setInterval/);
  assert.match(source, /response\.write\(" "\)/);
});

test("long recordings stream to disk without base64 IPC", () => {
  const captureSource = uiDriverInternals.startCapturedWindowRecording.toString();
  const frameSource = uiDriverInternals.writeCapturedFrame.toString();
  const recorderSource = uiDriverInternals.startWindowRecording.toString();
  const serverSource = startUiDriverServer.toString();
  assert.match(frameSource, /capturePage/);
  assert.match(captureSource, /libvpx-vp9/);
  assert.match(captureSource, /image2pipe/);
  assert.match(captureSource, /framesWritten/);
  assert.match(recorderSource, /fetch\(state\.uploadUrl/);
  assert.match(recorderSource, /blob\.arrayBuffer/);
  assert.match(recorderSource, /maxHeight: 1240/);
  assert.match(recorderSource, /video\/webm;codecs=vp8/);
  assert.match(recorderSource, /preview\.play/);
  assert.match(serverSource, /\/v1\/recording-upload/);
  assert.match(serverSource, /Access-Control-Allow-Origin/);
  assert.match(serverSource, /Content-Type, X-Recording-Duration/);
  assert.match(serverSource, /createWriteStream/);
  assert.match(serverSource, /500 \* 1024 \* 1024/);
  assert.doesNotMatch(recorderSource, /FileReader|saveRecording|base64/);
});
