import assert from "node:assert/strict";

import { launch } from "./harness/launch.mjs";
import { frontierTest } from "./harness/test-support.mjs";

function ephemeralAgent(className, toolName) {
  return `from agents.basic_agent import BasicAgent


class ${className}(BasicAgent):
    def __init__(self):
        self.name = "${toolName}"
        self.metadata = {
            "name": self.name,
            "description": "Deterministic concurrent E2E marker.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        return "${toolName}_OK"
`;
}

function surgeonScript() {
  return {
    concurrency: 2,
    mode: "concurrent",
    sessions: [
      {
        id: "first",
        match: { prompt: "first surgeon request" },
        turns: [
          {
            tool: {
              arguments: {
                ephemeral_agent: {
                  filename: "first_probe_agent.py",
                  source: ephemeralAgent("FirstProbeAgent", "FirstProbe"),
                },
                narration: "Running the first isolated delegation",
                prompt: "FIRST_DELEGATED_PROMPT",
              },
              name: "delegate_to_brainstem",
            },
          },
          { final: "FIRST_SURGEON_REPLY" },
        ],
      },
      {
        id: "second",
        match: { prompt: "second surgeon request" },
        turns: [
          {
            tool: {
              arguments: {
                ephemeral_agent: {
                  filename: "second_probe_agent.py",
                  source: ephemeralAgent("SecondProbeAgent", "SecondProbe"),
                },
                narration: "Running the second isolated delegation",
                prompt: "SECOND_DELEGATED_PROMPT",
              },
              name: "delegate_to_brainstem",
            },
          },
          { final: "SECOND_SURGEON_REPLY" },
        ],
      },
    ],
  };
}

function modelScript() {
  return {
    steps: [
      {
        when: { lastUser: "FIRST_DELEGATED_PROMPT", stream: true },
        response: {
          delayMs: 2_000,
          text: "FIRST_BRAINSTEM_REPLY",
        },
      },
      {
        when: { lastUser: "SECOND_DELEGATED_PROMPT", stream: true },
        response: {
          delayMs: 2_000,
          text: "SECOND_BRAINSTEM_REPLY",
        },
      },
    ],
  };
}

async function runConcurrentPass(run) {
  const app = await launch({
    modelScript: modelScript(),
    scenario: `surgeon-concurrent-${run}`,
    surgeonScript: surgeonScript(),
  });
  let trace = "";
  try {
    await app.driver.run([
      {
        action: "click",
        optional: true,
        selector: "#enter",
        settleMs: 100,
      },
      {
        action: "click",
        selector: "#surgeon-tabs .surgeon-new",
        settleMs: 100,
      },
      {
        action: "click",
        selector: "#surgeon-herd-btn",
        settleMs: 100,
      },
    ], { target: "shell" });
    await app.driver.expect({
      selector: '.herd-tile[data-session-id="1"] .hcomp textarea',
      target: "shell",
    });
    await app.driver.expect({
      selector: '.herd-tile[data-session-id="2"] .hcomp textarea',
      target: "shell",
    });

    const firstSend = app.driver.run([
      {
        action: "type",
        selector: '.herd-tile[data-session-id="1"] .hcomp textarea',
        typingDelayMs: 1,
        value: "first surgeon request",
      },
      {
        action: "click",
        selector: '.herd-tile[data-session-id="1"] .hcomp button',
        settleMs: 100,
      },
    ], { target: "shell" });
    const secondSend = app.driver.run([
      {
        action: "type",
        selector: '.herd-tile[data-session-id="2"] .hcomp textarea',
        typingDelayMs: 1,
        value: "second surgeon request",
      },
      {
        action: "click",
        selector: '.herd-tile[data-session-id="2"] .hcomp button',
        settleMs: 100,
      },
    ], { target: "shell" });
    const bothLeases = app.driver.expect({
      selector: "#brainstem-beta-chat-lease",
      text: "(2)",
      timeoutMs: 30_000,
    });
    await Promise.all([firstSend, secondSend, bothLeases]);
    // Both leases being held at once is proven by the banner reaching "(2)";
    // by the time telemetry is read a fast first delegate may already have
    // released its lease, so only the bound is asserted here.
    const telemetry = await app.driver.routeTelemetry({ trace: false });
    assert.ok(
      telemetry.chat_lease_count >= 0 && telemetry.chat_lease_count <= 2,
      `lease count out of range: ${telemetry.chat_lease_count}`,
    );

    await app.driver.expect({
      selector: '.herd-tile[data-session-id="1"] .htrans',
      target: "shell",
      text: "FIRST_SURGEON_REPLY",
      timeoutMs: 60_000,
    });
    await app.driver.expect({
      selector: '.herd-tile[data-session-id="2"] .htrans',
      target: "shell",
      text: "SECOND_SURGEON_REPLY",
      timeoutMs: 60_000,
    });

    const [firstTab] = await app.driver.run([{
      action: "read",
      selector: '.herd-tile[data-session-id="1"] .htrans',
    }], { target: "shell" });
    const [secondTab] = await app.driver.run([{
      action: "read",
      selector: '.herd-tile[data-session-id="2"] .htrans',
    }], { target: "shell" });
    assert.match(firstTab.text, /FIRST_SURGEON_REPLY/);
    assert.doesNotMatch(firstTab.text, /SECOND_SURGEON_REPLY|second surgeon request/);
    assert.match(secondTab.text, /SECOND_SURGEON_REPLY/);
    assert.doesNotMatch(secondTab.text, /FIRST_SURGEON_REPLY|first surgeon request/);

    const prompts = app.model.requests.flatMap((request) => (
      request.request.messages
        .filter((message) => message.role === "user")
        .map((message) => message.content)
    ));
    assert(prompts.includes("FIRST_DELEGATED_PROMPT"));
    assert(prompts.includes("SECOND_DELEGATED_PROMPT"));
    trace = app.trace.text();
  } finally {
    await app.stop();
  }
  return trace;
}

frontierTest("concurrent Surgeon delegations keep leases and tabs isolated", async () => {
  const first = await runConcurrentPass("one");
  const second = await runConcurrentPass("two");
  assert.equal(second, first);
});
