// Builds one SKILL.md in the browser from the public skill files a path names.
// Nothing the visitor typed is used; only their chosen path and area name.
(function (root) {
  "use strict";
  const LIBRARY = "https://microsoft.github.io/aibast-agents-library/";
  const body = text => text.replace(/^---\n[\s\S]*?\n---\n+/, "").trim();
  function assembleSkill({route, areaName, skills}) {
    const names = Object.keys(skills);
    const lines = [
      "---",
      "name: aibast-my-" + route.id,
      "description: A personal AIBAST skill for one path: " + route.label +
        ". Built from the public AIBAST Agents Library skills " + names.join(", ") + ".",
      "---",
      "",
      "# My AIBAST skill: " + route.label,
      "",
      "This file was put together on the AIBAST Agents Library paths page from",
      "public library skills. The everyday starting point is still the one",
      "AIBAST link: " + LIBRARY + "skills/aibast/SKILL.md",
      "",
      "## About this person",
      "",
      "- Path: " + route.label,
    ];
    if (areaName) lines.push("- Area they chose: " + areaName);
    lines.push(
      "",
      "## How to use this file",
      "",
      "Ask which of these the person needs, in this order: " +
        names.map((name, i) => (i + 1) + ". " + name).join("; ") + ".",
      "Run that part exactly as written below. When it finishes, offer the next",
      "part in one line, with \"or stop here\". Each part's own rules apply while",
      "it runs. When a part says to end with a line \"and nothing else\", that",
      "ends that part only: you still add the next-part line, every time.",
    );
    names.forEach((name, i) => {
      const next = names[i + 1];
      lines.push("", "<!-- " + name + " -->", "", "## Part: " + name, "",
        body(skills[name]).replace(/^(#+) /gm, "#$1 "), "",
        "### When this part ends", "",
        "After this part's last line, always add this exact line: \"" +
          (next ? "Next: " + next + ", or stop here." : "This path is done.") + "\"");
    });
    lines.push("", "## After each part", "",
      "When a part finishes, add one last line offering the next part in the",
      "order above, with \"or stop here\". Do this even when the part said to",
      "end with its own line. After the last part, say the path is done.");
    return lines.join("\n") + "\n";
  }
  root.AIBASTMySkill = {assembleSkill};
})(typeof window !== "undefined" ? window : globalThis);
