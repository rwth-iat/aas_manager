import json
import logging
from pathlib import Path
from typing import Iterable


def find_recovery_files(recovery_dir: Path) -> dict:
    """Return {original_path: recovery_path} for all valid recovery entries."""
    result = {}
    if not recovery_dir.exists():
        return result
    for meta_file in recovery_dir.glob("*.meta.json"):
        try:
            with open(meta_file, encoding="utf-8") as f:
                meta = json.load(f)
            # resolve() so the key matches the resolved open-file paths restore
            # compares against; an unresolved symlink/'..' would miss the match.
            original = Path(meta["original_path"]).resolve()
            recovery = recovery_dir / meta["recovery_filename"]
            if recovery.exists():
                result[original] = recovery
        except Exception:
            # Corrupt/unreadable meta: skip it, but log so a user who lost
            # recovery has a diagnostic instead of silence.
            logging.warning("Skipping unreadable recovery meta file: %s", meta_file, exc_info=True)
            continue
    return result


def delete_recovery_file(recovery_path: Path) -> None:
    """Delete a recovery data file and its sidecar .meta.json."""
    recovery_path.unlink(missing_ok=True)
    (recovery_path.parent / f"{recovery_path.stem}.meta.json").unlink(missing_ok=True)


def cleanup_recovery_dir(recovery_dir: Path, keep: Iterable[Path] = ()) -> None:
    """Delete all files in the recovery dir except `keep` (and their .meta.json).

    `keep` holds recovery files of just-restored, not-yet-saved packages; the rest
    (declined, orphaned, leftover .tmp) are swept so the dir does not grow unbounded.
    """
    if not recovery_dir.exists():
        return
    keep_names = set()
    for rec in keep:
        keep_names.add(rec.name)
        keep_names.add(f"{rec.stem}.meta.json")
    for entry in recovery_dir.iterdir():
        if entry.is_file() and entry.name not in keep_names:
            entry.unlink(missing_ok=True)
