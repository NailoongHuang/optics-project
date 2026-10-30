"""Read-only repository link, hygiene and consolidation-preservation checks.

Run after git add so new files are included. No scientific builds are invoked.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BACKUP = ROOT / "admin/archive/2026-10-30-navigation"
MAX_BYTES = 100 * 2**20
MD_LINK = re.compile(r"!?\[[^\]\n]*\]\((<[^>]+>|[^)\n]+)\)")
TOKEN = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"\bgh[pousr]_[A-Za-z0-9]{30,}\b|"
    r"\bgithub_pat_[A-Za-z0-9_]{40,}\b|"
    r"\bsk-(?:proj-)?[A-Za-z0-9_-]{40,}\b"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(2**20), b""):
            digest.update(block)
    return digest.hexdigest()


class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs
                          if key in {"href", "src", "poster"} and value)


def links(path: Path):
    content = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".md":
        # Fenced examples are not document links.
        content = re.sub(r"(?ms)^```[^\n]*\n.*?^```[^\n]*$", "", content)
        return [m.group(1).strip().strip("<>") for m in MD_LINK.finditer(content)]
    parser = AssetParser()
    parser.feed(content)
    return parser.links


def original_copy(relative: str) -> Path:
    if relative == "README.md":
        return BACKUP / "README.md"
    if relative == "AGENTS.md":
        return BACKUP / "AGENTS.before.md"
    return BACKUP / "originals" / relative


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-consolidation", action="store_true",
                        help="Verify the frozen 2026-10-30 preservation baseline")
    parser.add_argument("--check-local-archive", action="store_true")
    args = parser.parse_args()
    names = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT).decode("utf-8").split("\0")
    tracked = {name for name in names if name}
    errors = []
    if not tracked or "admin/maintenance/check_workspace.py" not in tracked:
        errors.append("Stage repository files with git add before checking")
    hashes = {}

    def digest(path):
        key = str(path)
        if key not in hashes:
            hashes[key] = sha256(path)
        return hashes[key]

    checked_links = 0
    workstation_links = []
    captured_source_pages = []
    source_files = 0
    for name in sorted(tracked):
        path = ROOT / name
        if not path.is_file():
            errors.append(f"Tracked file is missing: {name}")
            continue
        if not path.resolve().is_relative_to(ROOT):
            errors.append(f"Tracked path resolves outside the repository: {name}")
            continue
        if path.stat().st_size > MAX_BYTES:
            errors.append(f"File exceeds 100 MiB: {name}")
        if any(part in {"node_modules", "__pycache__", ".venv", "venv"}
               for part in path.relative_to(ROOT).parts):
            errors.append(f"Tracked installed dependency or cache: {name}")
        if path.name == "deck.proto.json" or path.suffix in {".pyc", ".pyo"}:
            errors.append(f"Tracked generated cache: {name}")
        if (path.name == ".env" or path.name.startswith(".env.")
                or path.suffix.lower() in {".pem", ".key"}) and path.name != ".env.example":
            errors.append(f"Tracked private configuration: {name}")
        if path.suffix.lower() in {".md", ".txt", ".json", ".py", ".mjs", ".js",
                                   ".tex", ".html", ".csv", ".ps1", ".yml", ".yaml"}:
            content = path.read_text(encoding="utf-8-sig", errors="replace")
            if TOKEN.search(content):
                errors.append(f"Possible credential content requires review: {name}")
        # Frozen source documents retain the relative-link context they had before
        # archiving. Their exact original bytes are checked below instead.
        historical = name.startswith("admin/archive/") and name != "admin/archive/README.md"
        if historical or path.suffix.lower() not in {".md", ".html"}:
            continue
        # Downloaded paper landing pages are immutable online-source evidence,
        # with site-root URLs belonging to their declared canonical web origin.
        # They are not authored offline galleries. Hash checks still cover them.
        if path.suffix.lower() == ".html" and name.startswith("literature/"):
            content = path.read_text(encoding="utf-8-sig")
            canonical = re.search(
                r'<link\s+rel="canonical"\s+href="(https?://[^"<>]+)"', content)
            if canonical:
                captured_source_pages.append({"path": name, "origin": canonical.group(1)})
                continue
        source_files += 1
        for target in links(path):
            parts = urlsplit(target)
            if parts.scheme.lower() in {"c", "file"}:
                workstation_links.append({"source": name, "target": target})
                continue
            if parts.scheme or parts.netloc or not parts.path:
                continue
            destination = (path.parent / unquote(parts.path)).resolve()
            checked_links += 1
            if not destination.is_relative_to(ROOT):
                errors.append(f"Relative link leaves the repository: {name} -> {target}")
            else:
                rel = destination.relative_to(ROOT).as_posix()
                exists_in_git = rel in tracked or any(
                    item.startswith(rel.rstrip("/") + "/") for item in tracked)
                if not destination.exists() or not exists_in_git:
                    errors.append(f"Missing or untracked link target: {name} -> {target}")

    baseline = json.loads((HERE / "before-inventory-2026-10-30.json").read_text(encoding="utf-8"))
    record = json.loads((HERE / "reorganization-2026-10-30.json").read_text(encoding="utf-8"))
    actions = {entry["path"]: entry for entry in record["actions"]}
    preservation = Counter()
    check_preservation = args.check_consolidation or args.check_local_archive
    for entry in baseline["files"] if check_preservation else []:
        name, expected = entry["path"], entry["sha256"]
        action = actions.get(name)
        if action and action["sha256"] != expected:
            errors.append(f"Action hash differs from inventory: {name}")
            continue
        if action and action["action"] == "remove-cache":
            preservation["removed_cache"] += 1
            continue
        if action and action["action"] == "external-archive":
            if args.check_local_archive:
                archive = Path(action["destination"])
                if not archive.is_file() or digest(archive) != expected:
                    errors.append(f"External archive missing or changed: {name}")
            preservation["external_archive"] += 1
            continue
        candidate = ROOT / (action["target"] if action else name)
        # A deduplicated copy may point to a source later moved in this batch.
        rel = candidate.relative_to(ROOT).as_posix()
        if rel in actions and actions[rel]["action"] == "move":
            candidate = ROOT / actions[rel]["target"]
        if candidate.is_file() and digest(candidate) == expected:
            if candidate.relative_to(ROOT).as_posix() not in tracked:
                errors.append(f"Preserved source is not tracked: {name}")
            preservation["preserved_or_deduplicated"] += 1
        else:
            backup = original_copy(rel)
            if backup.is_file() and digest(backup) == expected:
                if backup.relative_to(ROOT).as_posix() not in tracked:
                    errors.append(f"Original backup is not tracked: {name}")
                preservation["edited_with_original_retained"] += 1
            else:
                errors.append(f"Original bytes have no recorded preserved owner: {name}")

    result = {
        "passed": not errors,
        "tracked_files": len(tracked),
        "live_documents_checked": source_files,
        "local_links_checked": checked_links,
        "workstation_links": workstation_links,
        "captured_source_pages": captured_source_pages,
        "preservation": dict(preservation),
        "consolidation_baseline_checked": check_preservation,
        "local_archive_checked": args.check_local_archive,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
