"""AI-SDLC CLI — installs bundled skills, subagents, guard hooks, and the Bug Ledger MCP config."""

from __future__ import annotations

import argparse
import importlib.metadata as metadata
import importlib.resources as resources
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

AGENT_DIRS = {
    "claude": ".claude/skills",
    "cursor": ".cursor/skills",
    "windsurf": ".windsurf/skills",
    "gemini": ".gemini/skills",
}

SUBAGENT_DIRS = {"claude": ".claude/agents", "cursor": ".cursor/agents"}

HOOKS_DIR = ".claude/hooks/ai-sdlc"
SETTINGS_FILE = ".claude/settings.json"
GUARD_HOOKS = (
    ("protect_tests.py", "Edit|Write|MultiEdit|NotebookEdit"),
    ("guard_push.py", "Bash"),
)

MCP_FILES = {
    "claude": ".mcp.json",
    "cursor": ".cursor/mcp.json",
    "windsurf": ".codeium/windsurf/mcp_config.json",
    "gemini": ".gemini/settings.json",
}

BUGLEDGER = ("bugledger", {"command": "uvx", "args": ["bugledger-mcp@0.1.2"]})
UV_INSTALL_URL = "https://docs.astral.sh/uv/getting-started/installation/"
RETIRED_SKILLS = ("automate",)
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)

DIST_NAME = "ai-sdlc-kit"


def _bundled(name: str):
    bundled = resources.files("ai_sdlc") / name
    if bundled.is_dir():
        return bundled
    fallback = Path(__file__).resolve().parents[2] / name
    return fallback if fallback.is_dir() else None


def _skills_root():
    root = _bundled("skills")
    if root is None:
        raise FileNotFoundError(
            "could not locate the bundled 'skills' directory — "
            "the ai-sdlc-kit package may be installed incorrectly"
        )
    return root


def _agents_root():
    return _bundled("agents")


def _hooks_root():
    return _bundled("hooks")


def _bundled_files(root, suffix: str) -> list:
    if root is None:
        return []
    files = (p for p in root.iterdir() if p.is_file() and p.name.endswith(suffix))
    return sorted(files, key=lambda p: p.name)


def _agent_files() -> list:
    return _bundled_files(_agents_root(), ".md")


def _hook_files() -> list:
    return _bundled_files(_hooks_root(), ".py")


def _frontmatter(text: str) -> str:
    match = FRONTMATTER.match(text)
    return match.group(1) if match else ""


def _copy_tree(src, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for entry in src.iterdir():
        if entry.name == "__pycache__":
            continue
        target = dst / entry.name
        if entry.is_dir():
            _copy_tree(entry, target)
        else:
            target.write_bytes(entry.read_bytes())


def _remove_retired(skills_dir: Path, force: bool) -> None:
    for name in RETIRED_SKILLS:
        skill_md = skills_dir / name / "SKILL.md"
        if not skill_md.is_file():
            continue
        ours = rf"(?m)^name:\s*[\"']?{re.escape(name)}[\"']?\s*$"
        if not re.search(ours, _frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))):
            continue
        if force:
            shutil.rmtree(skill_md.parent)
            print(f"removed retired skill {name} (replaced by factory)")
        else:
            print(
                f"retired skill {name} found — delete {skill_md.parent} "
                "or rerun with --force (replaced by factory)"
            )


def _install_skills(agent: str, target: Path, force: bool) -> None:
    agent_dir = target / AGENT_DIRS[agent]
    installed = 0
    skipped = 0
    for skill in sorted(_skills_root().iterdir(), key=lambda p: p.name):
        if not skill.is_dir():
            continue
        dest = agent_dir / skill.name
        if dest.exists() and not force:
            print(f"skip {skill.name} (exists)")
            skipped += 1
            continue
        if dest.exists():
            shutil.rmtree(dest)
        _copy_tree(skill, dest)
        print(f"installed {skill.name}")
        installed += 1
    print(f"installed {installed}, skipped {skipped} → {agent_dir}")


def _inherit_model(text: str) -> str:
    match = FRONTMATTER.match(text)
    if not match:
        return text
    block = re.sub(r"(?m)^model:[^\r\n]*", "model: inherit", match.group(1))
    return text[: match.start(1)] + block + text[match.end(1) :]


def _install_subagents(agent: str, target: Path, force: bool) -> None:
    files = _agent_files()
    if agent not in SUBAGENT_DIRS or not files:
        return
    dest_dir = target / SUBAGENT_DIRS[agent]
    installed = 0
    skipped = 0
    for src in files:
        name = src.name[: -len(".md")]
        dest = dest_dir / src.name
        if dest.exists() and not force:
            print(f"skip agent {name} (exists)")
            skipped += 1
            continue
        data = src.read_bytes()
        if agent == "cursor":
            data = _inherit_model(data.decode("utf-8")).encode("utf-8")
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        print(f"installed agent {name}")
        installed += 1
    print(f"installed {installed} agents, skipped {skipped} → {dest_dir}")
    if agent == "cursor":
        print("set a model per agent in .cursor/agents/ — the reviewer must differ from the builder")


def _hook_groups(hooks_dir: str) -> list:
    return [
        {
            "matcher": matcher,
            "hooks": [{"type": "command", "command": f'python3 "{hooks_dir}/{name}"', "timeout": 15}],
        }
        for name, matcher in GUARD_HOOKS
    ]


def _hook_commands(hooks: dict) -> list:
    commands = []
    for groups in hooks.values():
        for group in groups if isinstance(groups, list) else []:
            entries = group.get("hooks") if isinstance(group, dict) else None
            for entry in entries if isinstance(entries, list) else []:
                command = entry.get("command") if isinstance(entry, dict) else None
                if isinstance(command, str):
                    commands.append(command)
    return commands


def _merge_hooks(path: Path, hooks_dir: str) -> None:
    groups = _hook_groups(hooks_dir)
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            data = None
        hooks = data.get("hooks", {}) if isinstance(data, dict) else None
        events = hooks.get("PreToolUse", []) if isinstance(hooks, dict) else None
        if not isinstance(events, list):
            print(f"could not parse {path} — left it unchanged; add this by hand:")
            print(json.dumps({"hooks": {"PreToolUse": groups}}, indent=2, ensure_ascii=False))
            return
    commands = _hook_commands(data.get("hooks", {}))
    missing = [
        group
        for group, (name, _) in zip(groups, GUARD_HOOKS)
        if not any(f"ai-sdlc/{name}" in command for command in commands)
    ]
    if not missing:
        print(f"guard hooks already configured → {path}")
        return
    data.setdefault("hooks", {}).setdefault("PreToolUse", []).extend(missing)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"configured guard hooks → {path}")


def _install_hooks(agent: str, target: Path, force: bool, is_global: bool) -> None:
    files = _hook_files()
    if agent != "claude" or not files:
        return
    dest_dir = target / HOOKS_DIR
    installed = 0
    skipped = 0
    for src in files:
        name = src.name[: -len(".py")]
        dest = dest_dir / src.name
        if dest.exists() and not force:
            print(f"skip hook {name} (exists)")
            skipped += 1
            continue
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(src.read_bytes())
        print(f"installed hook {name}")
        installed += 1
    print(f"installed {installed} hooks, skipped {skipped} → {dest_dir}")
    hooks_dir = dest_dir.as_posix() if is_global else f"$CLAUDE_PROJECT_DIR/{HOOKS_DIR}"
    _merge_hooks(target / SETTINGS_FILE, hooks_dir)
    if shutil.which("python3") is None:
        print("guard hooks need python3 on PATH — without it they do nothing")


def _snippet() -> str:
    name, server = BUGLEDGER
    return json.dumps({"mcpServers": {name: server}}, indent=2)


def _merge_mcp(path: Path) -> None:
    name, server = BUGLEDGER
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            data = None
        servers = data.get("mcpServers", {}) if isinstance(data, dict) else None
        if not isinstance(servers, dict):
            print(f"could not parse {path} — left it unchanged; add this by hand:")
            print(_snippet())
            return
        if name in servers:
            print(f"{name} already configured → {path}")
            return
    data.setdefault("mcpServers", {})[name] = server
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"configured {name} MCP → {path}")


def _configure_bugledger(agent: str, target: Path, is_global: bool) -> None:
    name, server = BUGLEDGER
    if agent == "claude" and is_global:
        command = " ".join([server["command"], *server["args"]])
        print(f"add Bug Ledger to Claude Code: claude mcp add --scope user {name} -- {command}")
        return
    if agent == "windsurf" and not is_global:
        print(
            f"windsurf reads MCP servers from ~/{MCP_FILES['windsurf']} — "
            "rerun with --global, or add this by hand:"
        )
        print(_snippet())
        return
    _merge_mcp(target / MCP_FILES[agent])
    if agent == "claude":
        print("Claude Code asks you to approve project MCP servers from .mcp.json on first use.")


def _cmd_install(args: argparse.Namespace) -> int:
    target = Path.home() if args.global_ else Path(args.target)
    agents = list(AGENT_DIRS) if args.agent == "all" else [args.agent]
    for agent in agents:
        _remove_retired(target / AGENT_DIRS[agent], args.force)
        _install_skills(agent, target, args.force)
        _install_subagents(agent, target, args.force)
        if not args.no_hooks:
            _install_hooks(agent, target, args.force, args.global_)
        if not args.no_bugledger:
            _configure_bugledger(agent, target, args.global_)
    if not args.no_bugledger and shutil.which("uvx") is None:
        print(f"Bug Ledger needs uv: {UV_INSTALL_URL}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    for skill in sorted(_skills_root().iterdir(), key=lambda p: p.name):
        if skill.is_dir():
            print(skill.name)
    agents = _agent_files()
    if agents:
        print("agents:")
        for agent in agents:
            print(f"  {agent.name[: -len('.md')]}")
    hooks = _hook_files()
    if hooks:
        print("hooks:")
        for hook in hooks:
            print(f"  {hook.name[: -len('.py')]}")
    return 0


def _cmd_ste_check(args: argparse.Namespace) -> int:
    script = _skills_root() / "plan" / "scripts" / "ste_check.py"
    if not script.is_file():
        raise FileNotFoundError("could not locate the bundled STE checker (plan/scripts/ste_check.py)")
    spec = importlib.util.spec_from_file_location("ai_sdlc_ste_check", str(script))
    module = importlib.util.module_from_spec(spec)
    write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = write_bytecode
    return module.main(args.files)


def _version() -> str:
    try:
        return metadata.version(DIST_NAME)
    except metadata.PackageNotFoundError:
        return "0.0.0-dev"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-sdlc", description="Install AI-SDLC skills for your coding agent."
    )
    parser.add_argument("--version", action="store_true", help="print the version and exit")

    subparsers = parser.add_subparsers(dest="command")

    install_parser = subparsers.add_parser(
        "install", help="install skills, subagents, guard hooks, and the Bug Ledger MCP config"
    )
    install_parser.add_argument(
        "--agent",
        choices=[*AGENT_DIRS, "all"],
        default="claude",
        help="which agent to install skills for (default: claude)",
    )
    install_parser.add_argument(
        "--target", default=".", help="target project directory (default: current directory)"
    )
    install_parser.add_argument(
        "--global",
        dest="global_",
        action="store_true",
        help="install into your home directory instead of --target",
    )
    install_parser.add_argument(
        "--force", action="store_true", help="overwrite existing skill, agent, and hook files"
    )
    install_parser.add_argument(
        "--no-bugledger",
        action="store_true",
        help="do not configure the Bug Ledger MCP server",
    )
    install_parser.add_argument(
        "--no-hooks",
        action="store_true",
        help="do not install the Claude Code guard hooks",
    )
    install_parser.set_defaults(func=_cmd_install)

    list_parser = subparsers.add_parser("list", help="list bundled skills, agents, and hooks")
    list_parser.set_defaults(func=_cmd_list)

    ste_parser = subparsers.add_parser(
        "ste-check", help="check markdown prose against the STE writing rules"
    )
    ste_parser.add_argument("files", nargs="+", metavar="FILE")
    ste_parser.set_defaults(func=_cmd_ste_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(_version())
        return 0

    if not getattr(args, "command", None):
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
