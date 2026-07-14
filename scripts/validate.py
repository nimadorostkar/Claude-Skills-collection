#!/usr/bin/env python3
"""Validate every skill in the repository against the standard.

Checks the mechanical rules only. Whether a skill is any good is what review
is for.

    python scripts/validate.py            # validate everything
    python scripts/validate.py --quiet    # errors only

Exits non-zero if any check fails.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

SECTIONS = [
    "Purpose",
    "When to Use",
    "Capabilities",
    "Inputs",
    "Outputs",
    "Workflow",
    "Best Practices",
    "Examples",
    "Notes",
]

CATEGORIES = {
    "languages", "development", "backend", "frontend", "mobile",
    "devops", "data", "security", "testing", "ai", "agent-tooling",
    "finance", "documents", "design", "writing", "productivity", "business",
}

FORBIDDEN = [
    (re.compile(r"\bTODO\b|\bFIXME\b|\bXXX\b"), "placeholder marker"),
    (re.compile(r"\badapted from\b|\bbased on the\b.*\brepo\b|\boriginal author\b", re.I),
     "attribution"),
    (re.compile(r"\bcoming soon\b|\bto be written\b|\bplaceholder text\b|\bTBD\b", re.I),
     "unfinished text"),
]

FENCE_RE = re.compile(r"^```.*?^```", re.M | re.S)


def strip_code(text: str) -> str:
    """Remove fenced code blocks. Their contents are illustrative — a `##` inside
    a Markdown example is not a section, and a relative link inside one is not a
    link the repository has to resolve."""
    return FENCE_RE.sub("", text)

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF←-⇿⬀-⯿]"
)

NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.M)
DESC_RE = re.compile(r"^description:\s*(.+?)(?=^\w+:)", re.M | re.S)
CAT_RE = re.compile(r"^\s+category:\s*(\S+)\s*$", re.M)
VER_RE = re.compile(r"^\s+version:\s*(\d+\.\d+\.\d+)\s*$", re.M)
LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)")


def check(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)

    # --- frontmatter -------------------------------------------------------
    if not text.startswith("---\n"):
        return [f"{rel}: missing YAML frontmatter"]

    try:
        _, fm, body = text.split("---", 2)
    except ValueError:
        return [f"{rel}: malformed frontmatter delimiters"]

    name_m = NAME_RE.search(fm)
    if not name_m:
        errors.append(f"{rel}: frontmatter has no `name`")
    elif name_m.group(1) != path.parent.name:
        errors.append(
            f"{rel}: name `{name_m.group(1)}` does not match directory `{path.parent.name}`"
        )

    desc_m = DESC_RE.search(fm)
    if not desc_m:
        errors.append(f"{rel}: frontmatter has no `description`")
    else:
        desc = " ".join(desc_m.group(1).split())
        if len(desc) < 60:
            errors.append(f"{rel}: description is too short to trigger reliably ({len(desc)} chars)")

    cat_m = CAT_RE.search(fm)
    parent_cat = path.parent.parent.name
    if not cat_m:
        errors.append(f"{rel}: frontmatter has no `metadata.category`")
    elif cat_m.group(1) != parent_cat:
        errors.append(
            f"{rel}: category `{cat_m.group(1)}` does not match directory `{parent_cat}`"
        )
    if parent_cat not in CATEGORIES:
        errors.append(f"{rel}: `{parent_cat}` is not a known category")

    if not VER_RE.search(fm):
        errors.append(f"{rel}: frontmatter has no valid `metadata.version` (semver)")

    prose = strip_code(body)

    # --- sections ----------------------------------------------------------
    found = re.findall(r"^## (.+)$", prose, re.M)
    if found != SECTIONS:
        missing = [s for s in SECTIONS if s not in found]
        extra = [s for s in found if s not in SECTIONS]
        if missing:
            errors.append(f"{rel}: missing section(s): {', '.join(missing)}")
        if extra:
            errors.append(f"{rel}: unexpected section(s): {', '.join(extra)}")
        if not missing and not extra:
            errors.append(f"{rel}: sections are out of order")

    if not re.search(r"^# .+$", prose, re.M):
        errors.append(f"{rel}: no H1 title")

    # --- content rules -----------------------------------------------------
    for pattern, label in FORBIDDEN:
        if m := pattern.search(prose):
            errors.append(f"{rel}: contains {label}: {m.group(0)!r}")

    if m := EMOJI.search(prose):
        errors.append(f"{rel}: contains emoji: {m.group(0)!r}")

    # --- links -------------------------------------------------------------
    for target in LINK_RE.findall(prose):
        resolved = (path.parent / target.split("#")[0]).resolve()
        if not resolved.exists():
            errors.append(f"{rel}: broken link -> {target}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    paths = sorted(SKILLS.glob("*/*/SKILL.md"))
    if not paths:
        print("error: no skills found", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    names: dict[str, Path] = {}

    for path in paths:
        all_errors.extend(check(path))
        if m := NAME_RE.search(path.read_text(encoding="utf-8")):
            name = m.group(1)
            if name in names:
                all_errors.append(
                    f"duplicate skill name `{name}`: "
                    f"{names[name].relative_to(ROOT)} and {path.relative_to(ROOT)}"
                )
            names[name] = path

    if all_errors:
        for e in all_errors:
            print(f"FAIL  {e}", file=sys.stderr)
        print(f"\n{len(all_errors)} error(s) across {len(paths)} skills", file=sys.stderr)
        return 1

    if not args.quiet:
        by_cat: dict[str, int] = {}
        for p in paths:
            by_cat[p.parent.parent.name] = by_cat.get(p.parent.parent.name, 0) + 1
        for cat in sorted(by_cat):
            print(f"  {cat:<15} {by_cat[cat]:>3}")
        print(f"\nOK  {len(paths)} skills, {len(by_cat)} categories, 0 errors")

    return 0


if __name__ == "__main__":
    sys.exit(main())
