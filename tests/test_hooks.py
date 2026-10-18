import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parents[1] / "hooks"
ENV = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR" and not k.startswith("GIT_")}
SPEC = """# Spec

## Tests — owned by /test · read-only for /build
Plan:
- empty input — catches: a crash on an empty list
- tests/plan_only.py::test_x — catches: a plan line, not a tester-owned file
Files:
- tests/x.py — 5 tests · red · sha256 abc123

## Acceptance
- src/app.py returns the total
"""


def run(hook, payload):
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    proc = subprocess.run(
        [sys.executable, str(HOOKS / hook)], input=stdin, text=True, capture_output=True, env=ENV
    )
    return proc.returncode


@pytest.fixture
def project(tmp_path):
    spec = tmp_path / ".sdlc" / "specs" / "totals" / "spec.md"
    spec.parent.mkdir(parents=True)
    spec.write_text(SPEC)
    return tmp_path


def edit(project, path, stage=None, agent=None):
    if stage:
        (project / ".sdlc" / ".stage").write_text(stage + "\n")
    data = {"tool_name": "Edit", "cwd": str(project), "tool_input": {"file_path": str(project / path)}}
    if agent:
        data["agent_type"] = agent
    return run("protect_tests.py", data)


@pytest.fixture
def repo(tmp_path):
    if shutil.which("git") is None:
        pytest.skip("git is not installed")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, env=ENV)

    def on(branch):
        ref = "refs/heads/" + branch
        subprocess.run(["git", "symbolic-ref", "HEAD", ref], cwd=tmp_path, check=True, env=ENV)
        return tmp_path

    return on


def push(command, cwd):
    return run("guard_push.py", {"tool_name": "Bash", "cwd": str(cwd), "tool_input": {"command": command}})


@pytest.mark.parametrize(
    "agent, stage, path, code",
    [
        ("sdlc-builder", "test totals", "tests/x.py", 2),
        ("sdlc-tester", "build totals", "tests/x.py", 0),
        (None, "build totals", "tests/x.py", 2),
        (None, "test totals", "tests/x.py", 0),
        (None, "build totals", "src/app.py", 0),
    ],
)
def test_protect_tests_by_agent_and_stage(project, agent, stage, path, code):
    assert edit(project, path, stage, agent) == code


def test_protect_tests_reads_only_the_files_list(project):
    assert edit(project, "tests/x.py", "build totals") == 2
    assert edit(project, "tests/plan_only.py", "build totals") == 0


@pytest.mark.parametrize("hook", ["protect_tests.py", "guard_push.py"])
def test_hooks_allow_invalid_json(hook):
    assert run(hook, "{not json") == 0


@pytest.mark.parametrize(
    "command, code",
    [
        ("git push origin feat/x", 0),
        ("git push origin main", 2),
        ("git push -f origin feat/x", 2),
        ("bash -c 'git push origin main'", 2),
        ("git push origin integration", 2),
        ("git push origin $(git branch --show-current) --force", 2),
        ("git push --repo origin main", 2),
        ("git push --repo=origin main", 2),
        ("git push --repo origin feat/x", 0),
    ],
)
def test_guard_push_commands(tmp_path, command, code):
    assert push(command, tmp_path) == code


@pytest.mark.parametrize("branch, code", [("main", 2), ("feat/x", 0)])
def test_guard_push_bare_push_checks_current_branch(repo, branch, code):
    assert push("git push", repo(branch)) == code


@pytest.mark.parametrize("branch, code", [("main", 2), ("feat/x", 0)])
def test_guard_push_unexpanded_refspec_checks_current_branch(repo, branch, code):
    assert push("git push origin $(git branch --show-current)", repo(branch)) == code
