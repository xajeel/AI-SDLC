#!/usr/bin/env node
/** AI-SDLC CLI — installs bundled skills, subagents, guard hooks, and the Bug Ledger MCP config. */

"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const AGENT_DIRS = {
  claude: ".claude/skills",
  cursor: ".cursor/skills",
  windsurf: ".windsurf/skills",
  gemini: ".gemini/skills",
};

const SUBAGENT_DIRS = { claude: ".claude/agents", cursor: ".cursor/agents" };

const HOOKS_DIR = ".claude/hooks/ai-sdlc";
const SETTINGS_FILE = ".claude/settings.json";
const GUARD_HOOKS = [
  ["protect_tests.py", "Edit|Write|MultiEdit|NotebookEdit"],
  ["guard_push.py", "Bash"],
];

const MCP_FILES = {
  claude: ".mcp.json",
  cursor: ".cursor/mcp.json",
  windsurf: ".codeium/windsurf/mcp_config.json",
  gemini: ".gemini/settings.json",
};

const BUGLEDGER = ["bugledger", { command: "uvx", args: ["bugledger-mcp@0.1.2"] }];
const UV_INSTALL_URL = "https://docs.astral.sh/uv/getting-started/installation/";
const RETIRED_SKILLS = ["automate"];
const FRONTMATTER = /^---\r?\n([\s\S]*?)\r?\n---/;

const SKILLS_ROOT = path.join(__dirname, "..", "skills");
const AGENTS_ROOT = path.join(__dirname, "..", "agents");
const HOOKS_ROOT = path.join(__dirname, "..", "hooks");
const STE_CHECK = path.join(SKILLS_ROOT, "plan", "scripts", "ste_check.py");

const HELP = `usage: ai-sdlc [--version] [-h] {install,list,ste-check} ...

Install AI-SDLC skills for your coding agent.

commands:
  install              install skills, subagents, guard hooks, and the Bug Ledger MCP config
    --agent NAME       claude | cursor | windsurf | gemini | all (default: claude)
    --target PATH      target project directory (default: current directory)
    --global           install into your home directory instead of --target
    --force            overwrite existing skill, agent, and hook files
    --no-bugledger     do not configure the Bug Ledger MCP server
    --no-hooks         do not install the Claude Code guard hooks
  list                 list bundled skills, agents, and hooks
  ste-check FILE...    check markdown prose against the STE writing rules

options:
  --version            print the version and exit
  -h, --help           show this help message and exit
`;

function fail(message) {
  console.error(`error: ${message}`);
  process.exit(1);
}

function isFile(file) {
  try {
    return fs.statSync(file).isFile();
  } catch {
    return false;
  }
}

function isObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function skillNames() {
  if (!fs.existsSync(SKILLS_ROOT)) {
    fail(
      "could not locate the bundled 'skills' directory — " +
        "the ai-sdlc-kit package may be installed incorrectly"
    );
  }
  return fs
    .readdirSync(SKILLS_ROOT, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function bundledFiles(root, suffix) {
  if (!fs.existsSync(root)) return [];
  return fs
    .readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith(suffix))
    .map((entry) => entry.name)
    .sort();
}

function agentFiles() {
  return bundledFiles(AGENTS_ROOT, ".md");
}

function hookFiles() {
  return bundledFiles(HOOKS_ROOT, ".py");
}

function frontmatter(text) {
  const match = FRONTMATTER.exec(text);
  return match ? match[1] : "";
}

function removeRetired(skillsDir, force) {
  for (const name of RETIRED_SKILLS) {
    const skillMd = path.join(skillsDir, name, "SKILL.md");
    if (!isFile(skillMd)) continue;
    const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const ours = new RegExp(`^name:\\s*["']?${escaped}["']?\\s*$`, "m");
    if (!ours.test(frontmatter(fs.readFileSync(skillMd, "utf8")))) continue;
    if (force) {
      fs.rmSync(path.dirname(skillMd), { recursive: true, force: true });
      console.log(`removed retired skill ${name} (replaced by factory)`);
    } else {
      console.log(
        `retired skill ${name} found — delete ${path.dirname(skillMd)} ` +
          "or rerun with --force (replaced by factory)"
      );
    }
  }
}

function installSkills(agent, target, force) {
  const agentDir = path.join(target, AGENT_DIRS[agent]);
  let installed = 0;
  let skipped = 0;
  for (const name of skillNames()) {
    const dest = path.join(agentDir, name);
    if (fs.existsSync(dest) && !force) {
      console.log(`skip ${name} (exists)`);
      skipped += 1;
      continue;
    }
    fs.rmSync(dest, { recursive: true, force: true });
    fs.cpSync(path.join(SKILLS_ROOT, name), dest, {
      recursive: true,
      filter: (src) => path.basename(src) !== "__pycache__",
    });
    console.log(`installed ${name}`);
    installed += 1;
  }
  console.log(`installed ${installed}, skipped ${skipped} → ${agentDir}`);
}

function inheritModel(text) {
  const match = FRONTMATTER.exec(text);
  if (!match) return text;
  const start = text.startsWith("---\r\n") ? 5 : 4;
  const block = match[1].replace(/^model:[^\r\n]*/gm, "model: inherit");
  return text.slice(0, start) + block + text.slice(start + match[1].length);
}

function installSubagents(agent, target, force) {
  const files = agentFiles();
  if (!SUBAGENT_DIRS[agent] || files.length === 0) return;
  const destDir = path.join(target, SUBAGENT_DIRS[agent]);
  let installed = 0;
  let skipped = 0;
  for (const file of files) {
    const name = file.slice(0, -".md".length);
    const dest = path.join(destDir, file);
    if (fs.existsSync(dest) && !force) {
      console.log(`skip agent ${name} (exists)`);
      skipped += 1;
      continue;
    }
    let data = fs.readFileSync(path.join(AGENTS_ROOT, file));
    if (agent === "cursor") data = inheritModel(data.toString("utf8"));
    fs.mkdirSync(destDir, { recursive: true });
    fs.writeFileSync(dest, data);
    console.log(`installed agent ${name}`);
    installed += 1;
  }
  console.log(`installed ${installed} agents, skipped ${skipped} → ${destDir}`);
  if (agent === "cursor") {
    console.log(
      "set a model per agent in .cursor/agents/ — the reviewer must differ from the builder"
    );
  }
}

function hookGroups(hooksDir) {
  return GUARD_HOOKS.map(([file, matcher]) => ({
    matcher,
    hooks: [{ type: "command", command: `python3 "${hooksDir}/${file}"`, timeout: 15 }],
  }));
}

function hookCommands(hooks) {
  const commands = [];
  for (const groups of Object.values(hooks)) {
    for (const group of Array.isArray(groups) ? groups : []) {
      const entries = isObject(group) ? group.hooks : null;
      for (const entry of Array.isArray(entries) ? entries : []) {
        const command = isObject(entry) ? entry.command : null;
        if (typeof command === "string") commands.push(command);
      }
    }
  }
  return commands;
}

function mergeHooks(file, hooksDir) {
  const groups = hookGroups(hooksDir);
  let data = {};
  if (fs.existsSync(file)) {
    try {
      data = JSON.parse(fs.readFileSync(file, "utf8"));
    } catch {
      data = null;
    }
    const hooks = isObject(data) ? (data.hooks === undefined ? {} : data.hooks) : null;
    const events = isObject(hooks)
      ? hooks.PreToolUse === undefined
        ? []
        : hooks.PreToolUse
      : null;
    if (!Array.isArray(events)) {
      console.log(`could not parse ${file} — left it unchanged; add this by hand:`);
      console.log(JSON.stringify({ hooks: { PreToolUse: groups } }, null, 2));
      return;
    }
  }
  const commands = hookCommands(data.hooks || {});
  const missing = groups.filter(
    (_, i) => !commands.some((command) => command.includes(`ai-sdlc/${GUARD_HOOKS[i][0]}`))
  );
  if (missing.length === 0) {
    console.log(`guard hooks already configured → ${file}`);
    return;
  }
  data.hooks = data.hooks || {};
  data.hooks.PreToolUse = data.hooks.PreToolUse || [];
  data.hooks.PreToolUse.push(...missing);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + "\n");
  console.log(`configured guard hooks → ${file}`);
}

function installHooks(agent, target, force, isGlobal) {
  const files = hookFiles();
  if (agent !== "claude" || files.length === 0) return;
  const destDir = path.join(target, HOOKS_DIR);
  let installed = 0;
  let skipped = 0;
  for (const file of files) {
    const name = file.slice(0, -".py".length);
    const dest = path.join(destDir, file);
    if (fs.existsSync(dest) && !force) {
      console.log(`skip hook ${name} (exists)`);
      skipped += 1;
      continue;
    }
    fs.mkdirSync(destDir, { recursive: true });
    fs.writeFileSync(dest, fs.readFileSync(path.join(HOOKS_ROOT, file)));
    console.log(`installed hook ${name}`);
    installed += 1;
  }
  console.log(`installed ${installed} hooks, skipped ${skipped} → ${destDir}`);
  const hooksDir = isGlobal
    ? destDir.split(path.sep).join("/")
    : `$CLAUDE_PROJECT_DIR/${HOOKS_DIR}`;
  mergeHooks(path.join(target, SETTINGS_FILE), hooksDir);
  if (!onPath("python3")) {
    console.log("guard hooks need python3 on PATH — without it they do nothing");
  }
}

function snippet() {
  const [name, server] = BUGLEDGER;
  return JSON.stringify({ mcpServers: { [name]: server } }, null, 2);
}

function mergeMcp(file) {
  const [name, server] = BUGLEDGER;
  let data = {};
  if (fs.existsSync(file)) {
    try {
      data = JSON.parse(fs.readFileSync(file, "utf8"));
    } catch {
      data = null;
    }
    const servers = isObject(data)
      ? data.mcpServers === undefined
        ? {}
        : data.mcpServers
      : null;
    if (!isObject(servers)) {
      console.log(`could not parse ${file} — left it unchanged; add this by hand:`);
      console.log(snippet());
      return;
    }
    if (Object.prototype.hasOwnProperty.call(servers, name)) {
      console.log(`${name} already configured → ${file}`);
      return;
    }
  }
  data.mcpServers = data.mcpServers || {};
  data.mcpServers[name] = server;
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + "\n");
  console.log(`configured ${name} MCP → ${file}`);
}

function configureBugledger(agent, target, isGlobal) {
  const [name, server] = BUGLEDGER;
  if (agent === "claude" && isGlobal) {
    const command = [server.command, ...server.args].join(" ");
    console.log(`add Bug Ledger to Claude Code: claude mcp add --scope user ${name} -- ${command}`);
    return;
  }
  if (agent === "windsurf" && !isGlobal) {
    console.log(
      `windsurf reads MCP servers from ~/${MCP_FILES.windsurf} — ` +
        "rerun with --global, or add this by hand:"
    );
    console.log(snippet());
    return;
  }
  mergeMcp(path.join(target, MCP_FILES[agent]));
  if (agent === "claude") {
    console.log("Claude Code asks you to approve project MCP servers from .mcp.json on first use.");
  }
}

function isExecutable(file) {
  try {
    fs.accessSync(file, fs.constants.X_OK);
    return isFile(file);
  } catch {
    return false;
  }
}

function onPath(command) {
  const exts =
    process.platform === "win32" ? (process.env.PATHEXT || ".EXE;.CMD;.BAT").split(";") : [""];
  const dirs = (process.env.PATH || "").split(path.delimiter).filter(Boolean);
  return dirs.some((dir) => exts.some((ext) => isExecutable(path.join(dir, command + ext))));
}

function findPython() {
  for (const command of ["python3", "python"]) {
    const probe = spawnSync(command, ["-c", "import sys; sys.exit(sys.version_info[0] != 3)"], {
      stdio: "ignore",
    });
    if (!probe.error && probe.status === 0) return command;
  }
  return null;
}

function steCheck(files) {
  if (files.length === 0) {
    console.error("usage: ai-sdlc ste-check [-h] FILE [FILE ...]");
    console.error("ai-sdlc ste-check: error: the following arguments are required: FILE");
    process.exit(2);
  }
  if (!isFile(STE_CHECK)) {
    fail("could not locate the bundled STE checker (plan/scripts/ste_check.py)");
  }
  const python = findPython();
  if (!python) {
    console.error(
      "ste-check needs Python 3 — the plan skill self-checks against skills/plan/ste.md instead"
    );
    process.exit(2);
  }
  const result = spawnSync(python, [STE_CHECK, ...files], { stdio: "inherit" });
  process.exit(result.status === null ? 1 : result.status);
}

function listBundled() {
  for (const name of skillNames()) console.log(name);
  const agents = agentFiles();
  if (agents.length > 0) {
    console.log("agents:");
    for (const file of agents) console.log(`  ${file.slice(0, -".md".length)}`);
  }
  const hooks = hookFiles();
  if (hooks.length > 0) {
    console.log("hooks:");
    for (const file of hooks) console.log(`  ${file.slice(0, -".py".length)}`);
  }
}

function parseInstall(rest) {
  const opts = {
    agent: "claude",
    target: ".",
    global: false,
    force: false,
    bugledger: true,
    hooks: true,
  };
  while (rest.length) {
    let arg = rest.shift();
    let inline = null;
    const eq = arg.indexOf("=");
    if (arg.startsWith("--") && eq !== -1) {
      inline = arg.slice(eq + 1);
      arg = arg.slice(0, eq);
    }
    const value = () => {
      const v = inline !== null ? inline : rest.shift();
      if (v === undefined) fail(`${arg} needs a value`);
      return v;
    };
    if (arg === "--agent") opts.agent = value();
    else if (arg === "--target") opts.target = value();
    else if (arg === "--global") opts.global = true;
    else if (arg === "--force") opts.force = true;
    else if (arg === "--no-bugledger") opts.bugledger = false;
    else if (arg === "--no-hooks") opts.hooks = false;
    else fail(`unknown option: ${arg}`);
  }
  if (opts.agent !== "all" && !AGENT_DIRS[opts.agent]) {
    fail(`--agent must be one of: ${Object.keys(AGENT_DIRS).join(", ")}, all`);
  }
  return opts;
}

function install(rest) {
  const opts = parseInstall(rest);
  const target = opts.global ? os.homedir() : path.resolve(opts.target);
  const agents = opts.agent === "all" ? Object.keys(AGENT_DIRS) : [opts.agent];
  for (const agent of agents) {
    removeRetired(path.join(target, AGENT_DIRS[agent]), opts.force);
    installSkills(agent, target, opts.force);
    installSubagents(agent, target, opts.force);
    if (opts.hooks) installHooks(agent, target, opts.force, opts.global);
    if (opts.bugledger) configureBugledger(agent, target, opts.global);
  }
  if (opts.bugledger && !onPath("uvx")) {
    console.log(`Bug Ledger needs uv: ${UV_INSTALL_URL}`);
  }
}

function main(argv) {
  if (argv.length === 0) {
    process.stdout.write(HELP);
    process.exit(1);
  }
  if (argv.includes("-h") || argv.includes("--help")) {
    process.stdout.write(HELP);
    process.exit(0);
  }
  if (argv.includes("--version")) {
    console.log(require("../package.json").version);
    process.exit(0);
  }

  const [command, ...rest] = argv;

  if (command === "list") return listBundled();
  if (command === "ste-check") return steCheck(rest);
  if (command !== "install") fail(`unknown command: ${command}`);
  install(rest);
}

main(process.argv.slice(2));
