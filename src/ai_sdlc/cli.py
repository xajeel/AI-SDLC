"""AI-SDLC CLI — installs bundled skills into your project or home directory."""

from __future__ import annotations

import argparse
import importlib.metadata as metadata
import importlib.resources as resources
import shutil
import sys
from pathlib import Path

AGENT_DIRS = {
    "claude": ".claude/skills",
    "cursor": ".cursor/skills",
    "windsurf": ".windsurf/skills",
    "gemini": ".gemini/skills",
}

DIST_NAME = "ai-sdlc-kit"


def _skills_root():
    bundled = resources.files("ai_sdlc") / "skills"
    if bundled.is_dir():
        return bundled
    fallback = Path(__file__).resolve().parents[2] / "skills"
    if fallback.is_dir():
        return fallback
    raise FileNotFoundError(
        "could not locate the bundled 'skills' directory — "
        "the ai-sdlc-kit package may be installed incorrectly"
    )


def _copy_tree(src, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for entry in src.iterdir():
        target = dst / entry.name
        if entry.is_dir():
            _copy_tree(entry, target)
        else:
            target.write_bytes(entry.read_bytes())


def _install_for_agent(agent: str, target: Path, force: bool) -> None:
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


def _cmd_install(args: argparse.Namespace) -> int:
    target = Path.home() if args.global_ else Path(args.target)
    agents = list(AGENT_DIRS) if args.agent == "all" else [args.agent]
    for agent in agents:
        _install_for_agent(agent, target, args.force)
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    for skill in sorted(_skills_root().iterdir(), key=lambda p: p.name):
        if skill.is_dir():
            print(skill.name)
    return 0


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
        "install", help="install skills into an agent's skills directory"
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
        "--force", action="store_true", help="overwrite existing skill folders"
    )
    install_parser.set_defaults(func=_cmd_install)

    list_parser = subparsers.add_parser("list", help="list bundled skills")
    list_parser.set_defaults(func=_cmd_list)

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
