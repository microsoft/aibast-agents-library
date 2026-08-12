import assert from "node:assert/strict";
import {
  existsSync,
  mkdtempSync,
  rmSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import {
  BrainSurgeon,
  brainSurgeonInternals,
} from "../electron/brain-surgeon.mjs";

test("Brain Surgeon keeps the full Copilot loop and RAPP delegation tools", async () => {
  let config;
  let sendTimeout;
  const session = {
    on: () => () => {},
    sendAndWait: async (_request, timeout) => {
      sendTimeout = timeout;
      return { data: { content: "ready" } };
    },
    disconnect: async () => {},
  };
  const runtime = {
    createSession: async (value) => {
      config = value;
      return session;
    },
  };
  const surgeon = new BrainSurgeon({
    runtime,
    brainstemUrl: "http://127.0.0.1:7071",
    uiCommand: async () => ({}),
  });

  const result = await surgeon.send("hello");
  assert.equal(result.content, "ready");
  assert.equal(config.enableConfigDiscovery, true);
  assert.equal(sendTimeout, 60 * 60 * 1000);
  assert.equal(typeof config.onPermissionRequest, "function");
  assert.match(config.systemMessage.content, /real GitHub Copilot coding-agent loop/);
  assert.deepEqual(
    config.tools.map((tool) => tool.name),
    [
      "delegate_to_brainstem",
      "inspect_visible_brainstem",
      "show_rapp_identity",
      "ensure_copilot_studio_deploy_agents",
      "list_active_agent_files",
      "copilot_studio_deployment_defaults",
      "copilot_studio_auth_status",
      "start_copilot_studio_login",
      "poll_copilot_studio_login",
      "show_copilot_studio_agent_link",
      "create_agent_stack",
      "select_agent_stack",
      "remove_agent_stack",
      "install_scoped_agent",
      "list_scoped_agents",
      "remove_scoped_agent",
      "drive_visible_brainstem",
      "capture_visible_brainstem",
      "check_beta_updates",
      "clear_brainstem_chat",
      "refresh_brainstem_view",
      "start_demo_recording",
      "stop_demo_recording",
    ],
  );
});

test("temporary agent filenames are normalized safely", () => {
  assert.equal(
    brainSurgeonInternals.cleanFilename("demo.py"),
    "demo_agent.py",
  );
  assert.equal(
    brainSurgeonInternals.cleanFilename("../customer demo_agent.py"),
    "customer_demo_agent.py",
  );
  assert.throws(
    () => brainSurgeonInternals.cleanFilename("basic_agent.py"),
    /safe agent filename/,
  );
});

test("failed delegation leaves ephemeral cleanup to the beta route manager", async () => {
  const commands = [];
  const routeRequests = [];
  const surgeon = new BrainSurgeon({
    runtime: {},
    brainstemUrl: "http://127.0.0.1:7071",
    routeManager: {
      withRoute: async (options, callback) => {
        routeRequests.push(options);
        return callback({ url: "http://127.0.0.1:7081" });
      },
    },
    uiCommand: async (command) => {
      commands.push(command);
      if (command.action === "chat") throw new Error("composer unavailable");
      return {};
    },
  });

  await assert.rejects(
    surgeon.delegateToBrainstem({
      prompt: "do it",
      ephemeral_agent: {
        filename: "temporary_agent.py",
        source: "print('temporary')",
      },
    }),
    /composer unavailable/,
  );
  assert.deepEqual(routeRequests, [{
    ephemeralAgent: {
      filename: "temporary_agent.py",
      source: "print('temporary')",
    },
  }]);
  const token = commands[0].token;
  assert.match(token, /^[0-9a-f-]{36}$/);
  assert.deepEqual(commands, [
    {
      action: "set_chat_lease",
      locked: true,
      token,
    },
    {
      action: "set_chat_lease",
      locked: true,
      token,
    },
    {
      action: "wait",
      selector: "#input",
      timeoutMs: 1000,
    },
    {
      action: "chat",
      value: "do it",
      label: "Delegating this outcome to the Brainstem",
      timeoutMs: 180000,
    },
    {
      action: "set_chat_lease",
      locked: false,
      token,
    },
  ]);
});

test("concurrent delegations retain independent chat lease tokens", async () => {
  const activeTokens = new Set();
  const chatResolvers = [];
  let chatsStarted = 0;
  let resolveChatsStarted;
  const chatsReady = new Promise((resolve) => {
    resolveChatsStarted = resolve;
  });
  const surgeon = new BrainSurgeon({
    runtime: {},
    brainstemUrl: "http://127.0.0.1:7071",
    routeManager: {
      withRoute: async (_options, callback) => (
        callback({ url: "http://127.0.0.1:7081" })
      ),
      recordTelemetry: () => {},
    },
    uiCommand: async (command) => {
      if (command.action === "set_chat_lease") {
        if (command.locked) activeTokens.add(command.token);
        else activeTokens.delete(command.token);
        return {};
      }
      if (command.action === "wait") return {};
      if (command.action === "chat") {
        chatsStarted += 1;
        if (chatsStarted === 2) resolveChatsStarted();
        return new Promise((resolve) => chatResolvers.push(resolve));
      }
      return {};
    },
  });
  const request = (marker) => surgeon.delegateToBrainstem({
    prompt: marker,
    ephemeral_agent: {
      filename: `${marker}_agent.py`,
      source: `class ${marker}Agent: pass`,
    },
  });

  const first = request("first");
  const second = request("second");
  await chatsReady;
  assert.equal(activeTokens.size, 2);
  chatResolvers[0]({ response: "first" });
  await first;
  assert.equal(activeTokens.size, 1);
  chatResolvers[1]({ response: "second" });
  await second;
  assert.equal(activeTokens.size, 0);
});

test("Brain Surgeon manages nested RAPPID stacks and visibly reloads selection", async () => {
  const calls = [];
  const routeManager = {
    listScopedAgents: async (options = {}) => {
      calls.push(["list", options]);
      return { caller_rappid: "caller", stack_tree: [] };
    },
    createStack: async (options) => {
      calls.push(["create", options]);
      return { rappid: "child", name: options.name };
    },
    stackTree: () => [{ rappid: "child", name: "child", children: [] }],
    selectStack: async (options) => {
      calls.push(["select", options]);
      return {
        active_stack_rappid: options.stackRappid,
        overlay_stack_rappids: options.overlayRappids,
      };
    },
    startDefault: async () => {
      calls.push(["start"]);
      return { url: "http://127.0.0.1:7081", compositionHash: "hash" };
    },
  };
  const surgeon = new BrainSurgeon({
    runtime: {},
    brainstemUrl: "http://127.0.0.1:7071",
    routeManager,
    uiCommand: async () => ({}),
  });

  assert.equal(
    JSON.parse(await surgeon.showRappIdentity()).caller_rappid,
    "caller",
  );
  assert.equal(
    JSON.parse(await surgeon.createAgentStack({
      name: "regulated",
      parent_stack_rappid: "parent",
    })).stack.rappid,
    "child",
  );
  const selected = JSON.parse(await surgeon.selectAgentStack({
    stack_rappid: "leaf",
    overlay_stack_rappids: ["voice", "evidence"],
  }));
  assert.equal(selected.active_route.compositionHash, "hash");
  assert.deepEqual(calls, [
    ["list", {}],
    ["create", { name: "regulated", parentRappid: "parent" }],
    ["select", {
      stackRappid: "leaf",
      overlayRappids: ["voice", "evidence"],
    }],
    ["start"],
  ]);
});

test("Brain Surgeon validates and injects bundled Copilot Studio agents", async (t) => {
  const active = [];
  let restarted = 0;
  const betaHome = mkdtempSync(path.join(tmpdir(), "brain-surgeon-studio-"));
  t.after(() => rmSync(betaHome, { recursive: true, force: true }));
  const surgeon = new BrainSurgeon({
    runtime: {},
    brainstemUrl: "http://127.0.0.1:7071",
    routeManager: {
      betaHome,
      activeAgentFiles: () => active,
      installScopedAgent: async ({ filename, source }) => {
        assert.match(source, /__manifest__/);
        active.push({
          filename,
          scope: "stack:test",
          address: filename,
          source,
        });
      },
      readActiveAgent: (filename) => active.find(
        (agent) => agent.filename === filename,
      )?.source || "",
      startDefault: async () => {
        restarted += 1;
        return { url: "http://127.0.0.1:7081" };
      },
    },
    uiCommand: async () => ({}),
  });

  test("Brain Surgeon emits a clickable Copilot Studio agent link", async () => {
    const events = [];
    const surgeon = new BrainSurgeon({
      runtime: {},
      brainstemUrl: "http://127.0.0.1:7071",
      uiCommand: async () => ({}),
      onEvent: (event) => events.push(event),
    });
    const value = JSON.parse(await surgeon.showCopilotStudioAgentLink({
      environment_id: "ee67a404-325c-e726-a18a-886fe708ca0b",
      agent_id: "52670b23-8a6e-4a86-9502-7e793b127ad4",
      display_name: "RAPP News Memory One Click",
    }));
    assert.equal(
      value.url,
      "https://copilotstudio.preview.microsoft.com/environments/"
        + "ee67a404-325c-e726-a18a-886fe708ca0b/agents/"
        + "52670b23-8a6e-4a86-9502-7e793b127ad4",
    );
    assert.equal(events[0].artifact.kind, "link");
  });

  const first = JSON.parse(await surgeon.ensureCopilotStudioAgents());
  assert.deepEqual(first.injected, [
    "rar_kody_w_copilot_studio_parity_deploy_agent.py",
    "rar_kody_w_factory_agent.py",
  ]);
  assert.equal(first.active[0].version, "1.0.12");
  assert.equal(first.active[1].version, "1.0.4");
  assert.equal(first.active[0].tool_name, "CopilotStudioDeployBeta");
  assert.equal(first.active[1].tool_name, "RappCopilotStudioFactoryBeta");
  assert.equal(existsSync(first.parity_cases_path), true);
  assert.equal(existsSync(first.industry_matrix_path), true);
  assert.equal(restarted, 1);
  const second = JSON.parse(await surgeon.ensureCopilotStudioAgents());
  assert.deepEqual(second.injected, []);
  assert.equal(restarted, 1);
});

test("deployment agent validation rejects stale filenames", () => {
  assert.equal(
    brainSurgeonInternals.deploymentAgentSourceMatches(
      '__manifest__ = {"version": "9.9.9"}\nself.name = "WrongTool"',
      {
        toolName: "CopilotStudioDeployBeta",
        minimumVersion: "1.0.4",
        requiredMarker: "BETA_DRAFT_ONLY = True",
      },
    ),
    false,
  );
  assert.equal(
    brainSurgeonInternals.deploymentAgentSourceMatches(
      '__manifest__ = {"version": "1.0.12"}\n'
        + 'BETA_DRAFT_ONLY = True\nself.name = "CopilotStudioDeployBeta"',
      {
        toolName: "CopilotStudioDeployBeta",
        minimumVersion: "1.0.12",
        requiredMarker: "BETA_DRAFT_ONLY = True",
      },
    ),
    true,
  );
});
