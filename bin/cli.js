#!/usr/bin/env node
/** AI-SDLC CLI — installs bundled skills into your project or home directory. */

"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");

const AGENT_DIRS = {
  claude: ".claude/skills",
  cursor: ".cursor/skills",
  windsurf: ".windsurf/skills",
  gemini: ".gemini/skills",
};

const SKILLS_ROOT = path.join(__dirname, "..", "skills");

const HELP = `usage: ai-sdlc [--version] [-h] {install,list} ...

Install AI-SDLC skills for your coding agent.

commands:
  install              install skills into an agent's skills directory
    --agent NAME       claude | cursor | windsurf | gemini | all (default: claude)
    --target PATH      target project directory (default: current directory)
    --global           install into your home directory instead of --target
    --force            overwrite existing skill folders
  list                 list bundled skills

options:
  --version            print the version and exit
  -h, --help           show this help message and exit
`;

function fail(message) {
  console.error(`error: ${message}`);
  process.exit(1);
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

function installForAgent(agent, target, force) {
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
    fs.cpSync(path.join(SKILLS_ROOT, name), dest, { recursive: true });
    console.log(`installed ${name}`);
    installed += 1;
  }
  console.log(`installed ${installed}, skipped ${skipped} → ${agentDir}`);
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

  if (command === "list") {
    for (const name of skillNames()) console.log(name);
    return;
  }
  if (command !== "install") fail(`unknown command: ${command}`);

  const opts = { agent: "claude", target: ".", global: false, force: false };
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
    else fail(`unknown option: ${arg}`);
  }

  if (opts.agent !== "all" && !AGENT_DIRS[opts.agent]) {
    fail(`--agent must be one of: ${Object.keys(AGENT_DIRS).join(", ")}, all`);
  }

  const target = opts.global ? os.homedir() : path.resolve(opts.target);
  const agents = opts.agent === "all" ? Object.keys(AGENT_DIRS) : [opts.agent];
  for (const agent of agents) installForAgent(agent, target, opts.force);
}

main(process.argv.slice(2));
