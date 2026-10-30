# Repository maintenance evidence

The single maintenance policy is [AGENTS.md](../../AGENTS.md#research-record-maintenance).
This directory records structural work and mechanical verification.

## 2026-10-30 consolidation

- Git follows the existing `origin/main` initialization commit; the remote is
  `https://github.com/NailoongHuang/optics-project.git`.
- [Before inventory](before-inventory-2026-10-30.json) records source bytes and
  SHA-256 before consolidation, excluding the external runtime Junction.
- [Action record](reorganization-2026-10-30.json) maps 1,221 identical delivery
  copies to their canonical owners, records cache removals and review-history
  moves, and records the original delivery ZIP's hash and external location.
- Snapshot-only report sources, the PDF, and original frozen inventories remain
  in `deliverables/spin-wave-study-2026-10-21/`. Its live links now use canonical
  sources; original pre-edit bytes are under `admin/archive/`.
- Removed duplicates total approximately 830.65 MiB; removed generated caches
  total approximately 1,020.81 MiB. The original ZIP (786.46 MiB) was relocated
  intact to `C:/Users/xuanm/Desktop/optics-local-archive/2026-10-30/`.
- Distinct authored slides, required `source-before` imports, numerical arrays,
  papers, scientific exports, and review evidence are retained. Existing stable
  presentation aliases remain because builders and frozen receipts reference
  them; Git stores identical content as one object.
- `presentations/midterm/build/node_modules` is an ignored local Junction to the
  bundled runtime, not repository content. Its target was left unchanged.

## Verification

Run from the repository root:

```powershell
python admin/maintenance/check_workspace.py
python -m unittest discover -s code -v
```

The checker uses Git's tracked/indexed paths, validates local Markdown and HTML
links, and rejects tracked dependencies, credentials and files over 100 MiB.
Run it after staging new files so they are included. `--check-consolidation`
also checks the frozen 2026-10-30 preservation mapping against original hashes;
use this for that consolidation audit rather than as a requirement to freeze
all future source edits. `--check-local-archive` includes that audit and verifies
the external ZIP on the original workstation; a fresh clone does not require
that local ZIP to inspect the canonical research material.

Results are recorded in [verification-2026-10-30.json](verification-2026-10-30.json).
These checks cover repository organization and the elementary regression suite.
They do not rerun research simulations or establish new scientific results.
