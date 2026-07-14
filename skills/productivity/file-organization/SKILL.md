---
name: file-organization
description: Use when organizing, deduplicating, or cleaning up files. Covers safe classification and renaming, finding true duplicates, reclaiming space, and never destroying data during a cleanup.
metadata:
  category: productivity
  version: 1.0.0
  tags: [files, organization, deduplication, cleanup, automation]
---

# File Organization

## Purpose

Bring order to a directory without losing anything. Every file-organization task has one hard requirement that overrides all others: nothing is destroyed, and every action is reversible.

## When to Use

- Organizing a directory of accumulated files.
- Finding and removing duplicates.
- Reclaiming disk space.
- Applying a consistent naming convention.
- Sorting downloads, documents, or media.

## Capabilities

- Classification by type, content, and date.
- True duplicate detection by content hash.
- Consistent renaming.
- Space analysis.
- Safe, reversible operations.

## Inputs

- The directory, and how large it actually is.
- The organizing principle: by type, by date, by project.
- What must not be touched.

## Outputs

- A plan, shown before anything is executed.
- The reorganization, performed reversibly.
- A report of what changed.

## Workflow

1. **Survey first** — Count, size, types, and the largest items. Never act on a directory you have not looked at.
2. **Propose a plan and show it** — What will move where, what will be renamed, what will be deleted. This is shown, and confirmed, before anything happens.
3. **Detect duplicates by content, not by name** — Hash the files. Two files with the same name are frequently different; two files with different names are frequently identical.
4. **Move, do not delete** — Duplicates and junk go to a quarantine directory, not to oblivion. Delete only after the user has confirmed, and preferably never.
5. **Preserve the metadata** — Modification times carry information. Do not destroy them by copying carelessly.
6. **Report what happened** — With a way to undo it.

## Best Practices

- Never delete. Move to a quarantine directory and let the user delete it themselves once they are satisfied. A cleanup that destroys one needed file has failed regardless of how much space it reclaimed.
- Hash before declaring a duplicate. Filename matching produces false positives (two different `invoice.pdf`) and false negatives (`report.pdf` and `report (1).pdf` that are identical).
- Hash cheaply: compare sizes first, then hash only the files whose sizes match. Hashing a 200 GB directory in full is slow and almost entirely wasted.
- Dry-run everything. Show the plan, and require confirmation for anything destructive.
- Preserve the original name somewhere — in a manifest, if not in the filename. Renaming without a record is irreversible in practice.
- Watch for hard links and symlinks. "Deleting a duplicate" that is a hard link frees nothing and may break something.

## Examples

**Duplicate detection that is correct and fast:**

```python
import hashlib
from collections import defaultdict
from pathlib import Path

def find_duplicates(root: Path) -> dict[str, list[Path]]:
    """Two passes. Size first — cheap. Hash only the size collisions."""
    by_size: dict[int, list[Path]] = defaultdict(list)

    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink():
            by_size[path.stat().st_size].append(path)

    # Only files with an identical size can be identical. Everything else is
    # excluded without reading a byte.
    candidates = [paths for paths in by_size.values() if len(paths) > 1]

    by_hash: dict[str, list[Path]] = defaultdict(list)
    for group in candidates:
        for path in group:
            by_hash[_hash(path)].append(path)

    return {h: paths for h, paths in by_hash.items() if len(paths) > 1}


def _hash(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.blake2b(digest_size=16)
    with path.open("rb") as f:
        while data := f.read(chunk):
            h.update(data)
    return h.hexdigest()
```

**A plan shown before anything is done:**

```text
Survey of ~/Downloads:
  2,847 files, 41.2 GB

  Duplicates (identical content) : 312 files, 8.4 GB reclaimable
  Installers (.dmg, .pkg, .exe)  : 89 files, 14.1 GB — all older than 6 months
  Screenshots                    : 1,204 files, 2.1 GB
  Documents (pdf, docx)          : 418 files
  Archives (.zip, .tar.gz)       : 203 files, 9.8 GB

PLAN — nothing is deleted. Everything is moved, and a manifest records the
original location of every file.

  1. Duplicates -> ~/Downloads/_quarantine/duplicates/
     The most recently modified copy of each set stays where it is.
     312 files, 8.4 GB.

  2. Installers older than 6 months -> ~/Downloads/_quarantine/installers/
     89 files, 14.1 GB.

  3. Screenshots -> ~/Downloads/Screenshots/YYYY-MM/
     Organized by capture date (from EXIF where available, mtime otherwise).

  4. Documents -> ~/Downloads/Documents/
  5. Archives  -> left in place (they may be needed; too risky to move blind).

  Manifest written to ~/Downloads/_quarantine/manifest.json.
  To undo everything:  python restore.py manifest.json

Proceed? [y/N]
```

## Notes

- The size-then-hash approach is not an optimization detail; on a large directory it is the difference between a task that finishes in seconds and one that reads every byte on the disk.
- The quarantine directory plus a manifest is what makes a cleanup safe. The user gets the space back the moment they empty it, and until then nothing is lost.
- BLAKE2 is faster than SHA-256 and entirely adequate for duplicate detection, where you are not defending against an adversary constructing collisions.
