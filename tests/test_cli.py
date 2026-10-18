import json

import pytest

from ai_sdlc import cli
from ai_sdlc.cli import AGENT_DIRS, main

BUGLEDGER_ENTRY = {"command": "uvx", "args": ["bugledger-mcp@0.1.2"]}
AGENT_MD = "---\nname: {name}\ndescription: test agent\nmodel: sonnet\n---\nBody.\n"
EDIT_MATCHER = "Edit|Write|MultiEdit|NotebookEdit"


def guard_groups(hooks_dir):
    return [
        {
            "matcher": matcher,
            "hooks": [{"type": "command", "command": f'python3 "{hooks_dir}/{name}"', "timeout": 15}],
        }
        for name, matcher in (("protect_tests.py", EDIT_MATCHER), ("guard_push.py", "Bash"))
    ]


@pytest.fixture
def home(tmp_path, monkeypatch):
    path = tmp_path / "home"
    path.mkdir()
    monkeypatch.setenv("HOME", str(path))
    monkeypatch.setattr(cli.Path, "home", staticmethod(lambda: path))
    return path


@pytest.fixture
def fake_agents(tmp_path, monkeypatch):
    root = tmp_path / "bundled-agents"
    root.mkdir()
    for name in ("sdlc-builder", "sdlc-reviewer"):
        (root / f"{name}.md").write_text(AGENT_MD.format(name=name))
    monkeypatch.setattr(cli, "_agents_root", lambda: root)
    return root


def install(target, *extra):
    return main(["install", "--target", str(target), *extra])


def test_install_copies_skills(tmp_path):
    assert main(["install", "--agent", "claude", "--target", str(tmp_path)]) == 0

    skills_dir = tmp_path / ".claude" / "skills"
    installed = [p for p in skills_dir.iterdir() if p.is_dir()]
    assert len(installed) >= 7
    for skill in installed:
        assert (skill / "SKILL.md").is_file()


def test_install_all_agents(tmp_path, home):
    assert main(["install", "--agent", "all", "--target", str(tmp_path)]) == 0

    for agent, rel in AGENT_DIRS.items():
        assert (tmp_path / rel).is_dir(), f"missing skills dir for {agent}"
    for rel in (".mcp.json", ".cursor/mcp.json", ".gemini/settings.json"):
        assert "bugledger" in json.loads((tmp_path / rel).read_text())["mcpServers"]


def test_skip_without_force(tmp_path):
    main(["install", "--agent", "claude", "--target", str(tmp_path)])
    marker = tmp_path / ".claude" / "skills" / "build" / "SKILL.md"
    marker.write_text("modified-by-test")

    main(["install", "--agent", "claude", "--target", str(tmp_path)])
    assert marker.read_text() == "modified-by-test"

    main(["install", "--agent", "claude", "--target", str(tmp_path), "--force"])
    assert marker.read_text() != "modified-by-test"


def test_agents_for_claude_and_cursor(tmp_path, fake_agents, capsys):
    install(tmp_path, "--agent", "claude")
    install(tmp_path, "--agent", "cursor")
    main(["list"])

    claude = tmp_path / ".claude" / "agents" / "sdlc-builder.md"
    assert claude.read_text() == (fake_agents / "sdlc-builder.md").read_text()
    cursor = (tmp_path / ".cursor" / "agents" / "sdlc-reviewer.md").read_text()
    assert "model: inherit" in cursor and "model: sonnet" not in cursor
    out = capsys.readouterr().out
    assert "the reviewer must differ from the builder" in out
    assert "agents:\n  sdlc-builder\n  sdlc-reviewer\n" in out
    assert "hooks:\n  guard_push\n  protect_tests\n" in out


def test_mcp_json_created_without_uvx(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli.shutil, "which", lambda name: None)
    install(tmp_path)

    text = (tmp_path / ".mcp.json").read_text()
    assert json.loads(text) == {"mcpServers": {"bugledger": BUGLEDGER_ENTRY}}
    assert text.endswith("}\n") and '\n  "mcpServers"' in text
    out = capsys.readouterr().out
    assert "Bug Ledger needs uv:" in out
    assert "approve project MCP servers" in out


def test_mcp_json_merges_other_servers(tmp_path):
    other = {"command": "npx", "args": ["other-mcp"]}
    (tmp_path / ".mcp.json").write_text(json.dumps({"mcpServers": {"other": other}, "x": 1}))
    install(tmp_path)

    data = json.loads((tmp_path / ".mcp.json").read_text())
    assert data == {"mcpServers": {"other": other, "bugledger": BUGLEDGER_ENTRY}, "x": 1}


def test_existing_bugledger_entry_kept(tmp_path, capsys):
    original = json.dumps({"mcpServers": {"bugledger": {"command": "my-ledger"}}})
    (tmp_path / ".mcp.json").write_text(original)
    install(tmp_path)

    assert (tmp_path / ".mcp.json").read_text() == original
    assert "bugledger already configured" in capsys.readouterr().out


def test_invalid_json_left_untouched(tmp_path, capsys):
    (tmp_path / ".mcp.json").write_text("{not json")
    install(tmp_path)

    assert (tmp_path / ".mcp.json").read_text() == "{not json"
    out = capsys.readouterr().out
    assert "could not parse" in out and '"bugledger-mcp@0.1.2"' in out


def test_no_bugledger_writes_nothing(tmp_path, home):
    project = tmp_path / "project"
    install(project, "--agent", "all", "--no-bugledger")

    for rel in (".mcp.json", ".cursor/mcp.json", ".gemini/settings.json"):
        assert not (project / rel).exists()
    assert not (home / ".codeium").exists()


def test_windsurf_project_mode_leaves_home_alone(tmp_path, home, capsys):
    install(tmp_path / "project", "--agent", "windsurf")

    assert list(home.iterdir()) == []
    assert "~/.codeium/windsurf/mcp_config.json" in capsys.readouterr().out


def test_global_install_mcp(home, capsys):
    main(["install", "--global", "--agent", "claude"])
    main(["install", "--global", "--agent", "windsurf"])

    settings = json.loads((home / ".claude" / "settings.json").read_text())
    hooks_dir = (home / ".claude" / "hooks" / "ai-sdlc").as_posix()
    assert settings == {"hooks": {"PreToolUse": guard_groups(hooks_dir)}}
    assert (home / ".claude" / "hooks" / "ai-sdlc" / "guard_push.py").is_file()
    assert not (home / ".claude.json").exists()
    assert not (home / ".mcp.json").exists()
    assert "claude mcp add --scope user bugledger -- uvx bugledger-mcp@0.1.2" in capsys.readouterr().out
    config = json.loads((home / ".codeium" / "windsurf" / "mcp_config.json").read_text())
    assert config["mcpServers"]["bugledger"] == BUGLEDGER_ENTRY


def test_guard_hooks_installed_without_python3(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli.shutil, "which", lambda name: None)
    install(tmp_path)

    hooks_dir = tmp_path / ".claude" / "hooks" / "ai-sdlc"
    for name in ("protect_tests.py", "guard_push.py"):
        assert (hooks_dir / name).read_bytes() == (cli._hooks_root() / name).read_bytes()
    assert sorted(p.name for p in hooks_dir.iterdir()) == ["guard_push.py", "protect_tests.py"]
    settings = tmp_path / ".claude" / "settings.json"
    text = settings.read_text()
    expected = {"hooks": {"PreToolUse": guard_groups("$CLAUDE_PROJECT_DIR/.claude/hooks/ai-sdlc")}}
    assert json.loads(text) == expected
    assert text.endswith("}\n") and '\n  "hooks"' in text
    out = capsys.readouterr().out
    assert f"configured guard hooks → {settings}" in out
    assert "guard hooks need python3 on PATH — without it they do nothing" in out


def test_guard_hooks_merge_keeps_existing_and_is_idempotent(tmp_path, capsys):
    mine = {"type": "command", "command": "python3 /opt/ai-sdlc/protect_tests.py"}
    lint = {"matcher": "Write", "hooks": [{"type": "command", "command": "lint"}]}
    stop = [{"hooks": [{"type": "command", "command": "notify"}]}]
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir()
    original = {"model": "opus", "hooks": {"PreToolUse": [lint, {"hooks": [mine]}], "Stop": stop}}
    settings.write_text(json.dumps(original))
    install(tmp_path)
    first = settings.read_text()
    install(tmp_path, "--force")

    assert settings.read_text() == first
    data = json.loads(first)
    guard_push = guard_groups("$CLAUDE_PROJECT_DIR/.claude/hooks/ai-sdlc")[1]
    pre_tool_use = [lint, {"hooks": [mine]}, guard_push]
    assert data == {"model": "opus", "hooks": {"PreToolUse": pre_tool_use, "Stop": stop}}
    out = capsys.readouterr().out
    assert out.count("configured guard hooks →") == 1
    assert f"guard hooks already configured → {settings}" in out


def test_guard_hooks_invalid_settings_left_untouched(tmp_path, capsys):
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir()
    settings.write_text("{not json")
    install(tmp_path)

    assert settings.read_text() == "{not json"
    assert (tmp_path / ".claude" / "hooks" / "ai-sdlc" / "protect_tests.py").is_file()
    out = capsys.readouterr().out
    assert f"could not parse {settings} — left it unchanged; add this by hand:" in out
    assert '"matcher": "Bash"' in out and "ai-sdlc/guard_push.py" in out


def test_no_hooks_writes_neither_scripts_nor_settings(tmp_path):
    install(tmp_path, "--no-hooks")

    assert (tmp_path / ".claude" / "skills").is_dir()
    assert not (tmp_path / ".claude" / "hooks").exists()
    assert not (tmp_path / ".claude" / "settings.json").exists()


def test_non_claude_agent_gets_no_hooks(tmp_path, capsys):
    install(tmp_path, "--agent", "cursor")

    assert not (tmp_path / ".claude").exists()
    assert "hook" not in capsys.readouterr().out.replace(str(tmp_path), "")


@pytest.fixture
def retired(tmp_path, monkeypatch):
    """A bundle with only `factory`, plus an old `automate` skill (ours) and a user's (theirs)."""
    bundle = tmp_path / "bundle"
    (bundle / "factory").mkdir(parents=True)
    (bundle / "factory" / "SKILL.md").write_text("---\nname: factory\n---\n")
    monkeypatch.setattr(cli, "_skills_root", lambda: bundle)
    ours = tmp_path / "a" / ".claude" / "skills" / "automate"
    theirs = tmp_path / "b" / ".claude" / "skills" / "automate"
    for folder, name in ((ours, "automate"), (theirs, "my-automate")):
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(f"---\nname: {name}\n---\n")
    return ours, theirs


def test_retired_skill_kept_without_force(tmp_path, retired, capsys):
    ours, _ = retired
    install(tmp_path / "a", "--no-bugledger")

    assert (ours / "SKILL.md").is_file()
    out = capsys.readouterr().out
    assert (
        f"retired skill automate found — delete {ours} or rerun with --force (replaced by factory)"
        in out
    )
    assert "removed retired skill" not in out


def test_retired_skill_removed_with_force_only_when_ours(tmp_path, retired, capsys):
    ours, theirs = retired
    install(tmp_path / "a", "--no-bugledger", "--force")
    install(tmp_path / "b", "--no-bugledger", "--force")

    assert not ours.exists()
    assert (theirs / "SKILL.md").is_file()
    out = capsys.readouterr().out
    assert out.count("removed retired skill automate (replaced by factory)") == 1
    assert "retired skill automate found" not in out


def test_ste_check_passes_clean_sample(tmp_path):
    sample = tmp_path / "clean.md"
    sample.write_text(
        "# Title; it's ignored\n\nRun the tests. Read the output.\n\n"
        "```\ncode; it's ignored\n```\n\n| a; b | don't |\n"
    )
    assert main(["ste-check", str(sample)]) == 0


def test_ste_check_flags_long_sentence_and_semicolon(tmp_path, capsys):
    sample = tmp_path / "bad.md"
    long_sentence = " ".join(["word"] * 29) + " end."
    sample.write_text(f"# Title\n\n{long_sentence}\n\nThe file is big; the test is slow.\n")

    assert main(["ste-check", str(sample)]) == 1
    out = capsys.readouterr().out
    assert f"{sample}:3: ERROR sentence-length: sentence has 30 words (max 25)" in out
    assert f"{sample}:5: ERROR semicolon:" in out
    assert f"{sample}: 2 errors, 0 warnings" in out


def test_ste_check_skips_ascii_trace(tmp_path, capsys):
    sample = tmp_path / "trace.md"
    sample.write_text(
        "The flow is short and the pending checks run in this order\n"
        "plan → build → test → qa → ship; it's a trace, not a sentence\n"
        "├── src/\n└── tests/\n"
    )
    assert main(["ste-check", str(sample)]) == 0
    assert f"{sample}: 0 errors, 0 warnings" in capsys.readouterr().out
