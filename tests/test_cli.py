from ai_sdlc.cli import AGENT_DIRS, main


def test_install_copies_skills(tmp_path):
    assert main(["install", "--agent", "claude", "--target", str(tmp_path)]) == 0

    skills_dir = tmp_path / ".claude" / "skills"
    installed = [p for p in skills_dir.iterdir() if p.is_dir()]
    assert len(installed) >= 7
    for skill in installed:
        assert (skill / "SKILL.md").is_file()


def test_install_all_agents(tmp_path):
    assert main(["install", "--agent", "all", "--target", str(tmp_path)]) == 0

    for agent, rel in AGENT_DIRS.items():
        assert (tmp_path / rel).is_dir(), f"missing skills dir for {agent}"


def test_skip_without_force(tmp_path):
    main(["install", "--agent", "claude", "--target", str(tmp_path)])
    marker = tmp_path / ".claude" / "skills" / "build" / "SKILL.md"
    marker.write_text("modified-by-test")

    main(["install", "--agent", "claude", "--target", str(tmp_path)])
    assert marker.read_text() == "modified-by-test"

    main(["install", "--agent", "claude", "--target", str(tmp_path), "--force"])
    assert marker.read_text() != "modified-by-test"
