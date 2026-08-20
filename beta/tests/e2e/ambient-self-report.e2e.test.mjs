import assert from "node:assert/strict";
import {
  existsSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";

import { launch } from "./harness/launch.mjs";
import { frontierTest } from "./harness/test-support.mjs";

frontierTest("ambient self-state names a broken source agent in the next model request", async () => {
  const app = await launch({
    modelScript: {
      steps: [{
        when: {
          lastUser: "inspect your current self state",
          stream: true,
        },
        response: { text: "AMBIENT_REQUEST_CAPTURED" },
      }],
    },
    scenario: "ambient-self-report",
  });
  try {
    const brokenFilename = "ambient_broken_agent.py";
    const brokenPath = path.join(
      app.paths.grail,
      "agents",
      brokenFilename,
    );
    writeFileSync(
      brokenPath,
      "from agents.basic_agent import BasicAgent\n"
        + "class AmbientBrokenAgent(BasicAgent)\n"
        + "    pass\n",
      { mode: 0o600 },
    );
    assert.equal(existsSync(brokenPath), true);

    await app.driver.command({
      action: "chat",
      timeoutMs: 30_000,
      value: "inspect your current self state",
    });

    assert.equal(app.model.requests.length, 1);
    const request = app.model.requests[0].request;
    const systemContext = request.messages
      .filter((message) => message.role === "system")
      .map((message) => String(message.content || ""))
      .join("\n");
    assert.match(systemContext, /<system_status>/);
    assert.match(systemContext, new RegExp(brokenFilename));
    assert.match(systemContext, /SyntaxError/);
    assert.match(systemContext, /failed to load/);

    const telemetry = await app.driver.routeTelemetry({ trace: false });
    assert.equal(
      existsSync(path.join(
        telemetry.active_composition_fingerprint.agent_directory,
        brokenFilename,
      )),
      false,
      "the broken source must remain outside the executable composition",
    );
  } finally {
    await app.stop();
  }
});
