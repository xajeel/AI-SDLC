#!/usr/bin/env python3
"""ai-sdlc PreToolUse hook: stop the builder from editing tester-owned tests.

Protected files are those listed in the `## Tests` section of any
.sdlc/specs/*/spec.md. Protection is on while .sdlc/.stage says `build`, or
whenever the hook fires inside the sdlc-builder subagent. The sdlc-tester
subagent is always allowed. Any unexpected input or error -> allow (exit 0).
"""
import glob
import json
import os
import re
import sys

BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
FILE_LIKE = re.compile(r"[\w.-]+\.[A-Za-z0-9]{1,10}$")
LABEL = re.compile(r"^\W*(plan|files|covers)\W*:", re.IGNORECASE)


def agent_name(data):
    agent = data.get("agent_type") or ""
    return agent.rsplit(":", 1)[-1] if isinstance(agent, str) else ""


def find_root(start):
    path = os.path.realpath(start)
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    while True:
        if os.path.isdir(os.path.join(path, ".sdlc")):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent


def stage_is_build(root):
    try:
        with open(os.path.join(root, ".sdlc", ".stage"), encoding="utf-8") as fh:
            words = fh.read().split()
    except OSError:
        return False
    return bool(words) and words[0].lower() == "build"


def path_token(line):
    match = BULLET.match(line)
    if not match:
        return None
    token = match.group(1).split()[0].strip("`*'\",;")
    token = token.split("::", 1)[0]
    token = re.sub(r":\d+(?::\d+)?$", "", token)
    if token.endswith("/") or "/" in token or FILE_LIKE.match(token):
        return token
    return None


def tests_tokens(lines):
    """Path tokens from `## Tests` bullets; only those under `Files:` when that label exists."""
    all_tokens, file_tokens = [], []
    in_tests = has_files = in_files = False
    for line in lines + ["## end"]:
        if line.startswith("## "):
            in_tests = line[3:].strip().lower().startswith("tests")
            in_files = False
            continue
        if not in_tests:
            continue
        label = LABEL.match(line)
        if label:
            in_files = label.group(1).lower() == "files"
            has_files = has_files or in_files
            continue
        token = path_token(line)
        if token:
            (file_tokens if in_files else all_tokens).append(token)
    return file_tokens if has_files else all_tokens + file_tokens


def protected_paths(root):
    paths = set()
    for spec in glob.glob(os.path.join(root, ".sdlc", "specs", "*", "spec.md")):
        try:
            with open(spec, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for token in tests_tokens(lines):
            full = os.path.realpath(os.path.join(root, token))
            paths.add((full, token.endswith("/") or os.path.isdir(full)))
    return paths


def main():
    data = json.load(sys.stdin)
    if not isinstance(data, dict):
        return 0
    agent = agent_name(data)
    if agent == "sdlc-tester":
        return 0
    tool_input = data.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(target, str) or not target:
        return 0
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    target = os.path.realpath(os.path.join(cwd, os.path.expanduser(target)))

    roots = []
    for start in (os.path.dirname(target), cwd, os.environ.get("CLAUDE_PROJECT_DIR")):
        root = find_root(start) if start else None
        if root and root not in roots:
            roots.append(root)

    for root in roots:
        if agent != "sdlc-builder" and not stage_is_build(root):
            continue
        for path, is_dir in protected_paths(root):
            if target == path or (is_dir and target.startswith(path + os.sep)):
                rel = os.path.relpath(target, root)
                sys.stderr.write(
                    "Blocked by ai-sdlc protect_tests: {} is a tester-owned test "
                    "(listed in a spec's ## Tests section) and build may not edit it. "
                    "File a test challenge for /test instead: the test file and name, "
                    "why it is wrong, and the spec line it contradicts.\n".format(rel)
                )
                return 2
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        code = 0
    sys.exit(code)
