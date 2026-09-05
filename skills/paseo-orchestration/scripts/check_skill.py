"""Check this skill's packaging, not live agent behavior. Stdlib only."""

from pathlib import Path
import re


def check(root: Path) -> None:
    text = (root / "SKILL.md").read_text()
    assert text.startswith("---\n"), "Missing frontmatter"
    frontmatter, body = text[4:].split("\n---\n", 1)
    fields = dict(line.split(": ", 1) for line in frontmatter.splitlines())
    assert fields["name"] == root.name
    assert 0 < len(fields["description"]) <= 60
    assert fields["description"].endswith(".")
    assert "disable-model-invocation" not in fields
    for heading in ("When to use", "Prerequisites", "Procedure", "Pitfalls", "Verification"):
        assert f"## {heading}\n" in body, f"Missing section: {heading}"
    for document in root.rglob("*.md"):
        content = document.read_text()
        assert "/home/pj/" not in content, f"Machine-local path: {document}"
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (document.parent / target.split("#", 1)[0]).resolve()
            assert resolved.is_relative_to(root.resolve()), f"Escaping link: {target}"
            assert resolved.is_file(), f"Missing link: {target}"
    for name in ("references/hermes.md", "references/verification.md", "templates/worker-brief.md"):
        assert (root / name).is_file(), f"Missing artifact: {name}"


if __name__ == "__main__":
    check(Path(__file__).resolve().parents[1])
    print("PASS: frontmatter, activation metadata, sections, local links, and portable paths")
    print("Live profile routing, callbacks, and cross-machine behavior are not tested here.")
