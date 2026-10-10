#!/usr/bin/env python3
"""Validate every skill in the repository against the standard.

Checks the mechanical rules only. Whether a skill is any good is what review
is for.

    python scripts/validate.py            # validate everything
    python scripts/validate.py --quiet    # errors only

Exits non-zero if any check fails. Requires PyYAML (`pip install pyyaml`):
the frontmatter is parsed the way an agent parses it, so a description that
merely looks right but is not valid YAML is caught here rather than by a skill
that silently never loads.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: PyYAML is required — pip install pyyaml")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_index import CATEGORIES  # noqa: E402  (single source of truth)

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

NAME_FORMAT = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_MAX = 64
DESC_MIN, DESC_MAX = 60, 1024
TAGS_MIN, TAGS_MAX = 3, 6
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
# "see the data-modeling skill" — a boundary must point at a skill that exists.
SKILL_REF = re.compile(r"\bsee the ([a-z0-9-]+) skill\b")

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

LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)")


def check(path: Path, known: set[str]) -> list[str]:
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

    try:
        meta = yaml.safe_load(fm)
    except yaml.YAMLError as e:
        line = str(e).splitlines()[0]
        return [f"{rel}: frontmatter is not valid YAML ({line}) — quote the value or remove the `: `"]
    if not isinstance(meta, dict):
        return [f"{rel}: frontmatter is not a mapping"]

    name = meta.get("name")
    if not isinstance(name, str):
        errors.append(f"{rel}: frontmatter has no `name`")
    else:
        if name != path.parent.name:
            errors.append(f"{rel}: name `{name}` does not match directory `{path.parent.name}`")
        if not NAME_FORMAT.match(name) or len(name) > NAME_MAX:
            errors.append(f"{rel}: name `{name}` must be lowercase kebab-case, at most {NAME_MAX} chars")

    desc = meta.get("description")
    if not isinstance(desc, str):
        errors.append(f"{rel}: frontmatter has no `description`")
    else:
        desc = " ".join(desc.split())
        if len(desc) < DESC_MIN:
            errors.append(f"{rel}: description is too short to trigger reliably ({len(desc)} chars)")
        if len(desc) > DESC_MAX:
            errors.append(f"{rel}: description exceeds {DESC_MAX} chars ({len(desc)}) and will be truncated")
        if "<" in desc or ">" in desc:
            errors.append(f"{rel}: description contains `<` or `>` — an unfilled template placeholder?")
        for ref in SKILL_REF.findall(desc):
            if ref not in known:
                errors.append(f"{rel}: description points at `{ref}`, which is not a skill")
            elif ref == name:
                errors.append(f"{rel}: description points at itself as its own boundary")

    md = meta.get("metadata") if isinstance(meta.get("metadata"), dict) else {}
    parent_cat = path.parent.parent.name
    cat = md.get("category")
    if not cat:
        errors.append(f"{rel}: frontmatter has no `metadata.category`")
    elif cat != parent_cat:
        errors.append(f"{rel}: category `{cat}` does not match directory `{parent_cat}`")
    if parent_cat not in CATEGORIES:
        errors.append(f"{rel}: `{parent_cat}` is not a known category (add it to scripts/build_index.py)")

    if not SEMVER.match(str(md.get("version", ""))):
        errors.append(f"{rel}: frontmatter has no valid `metadata.version` (semver)")

    tags = md.get("tags")
    if not isinstance(tags, list) or not TAGS_MIN <= len(tags) <= TAGS_MAX:
        errors.append(f"{rel}: `metadata.tags` must be a list of {TAGS_MIN}-{TAGS_MAX} tags")
    elif bad := [x for x in tags if not isinstance(x, str) or x != x.lower()]:
        errors.append(f"{rel}: tags must be lowercase strings: {bad}")

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

    errors.extend(broken_links(path, prose))
    return errors


def broken_links(path: Path, prose: str) -> list[str]:
    rel = path.relative_to(ROOT)
    out = []
    for target in LINK_RE.findall(prose):
        target = target.split()[0]  # drop a link title: [x](path "title")
        if target.startswith("mailto:"):
            continue
        if not (path.parent / target.split("#")[0]).resolve().exists():
            out.append(f"{rel}: broken link -> {target}")
    return out


def check_docs() -> list[str]:
    """Every relative link in the non-skill Markdown must resolve too."""
    docs = [*ROOT.glob("*.md"), *ROOT.glob("docs/*.md"), *ROOT.glob("categories/*.md"),
            *ROOT.glob("examples/*.md"), *ROOT.glob("templates/*.md"), *ROOT.glob(".github/**/*.md")]
    errors = []
    for path in sorted(docs):
        if path.parent.name == "templates":
            continue  # the template is full of illustrative placeholders
        errors.extend(broken_links(path, strip_code(path.read_text(encoding="utf-8"))))
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
        name = path.parent.name
        if name in names:
            all_errors.append(
                f"duplicate skill name `{name}`: "
                f"{names[name].relative_to(ROOT)} and {path.relative_to(ROOT)}"
            )
        names[name] = path

    for path in paths:
        all_errors.extend(check(path, set(names)))
    all_errors.extend(check_docs())

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
