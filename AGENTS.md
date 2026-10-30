# Repository Agent Instructions

## Purpose and startup

This is the optics spin-wave research workspace. Start at [README.md](README.md),
then read the owning topic's README and the sources relevant to the request.
Keep maintained instructions in English and preserve source material in its
original language. User-facing explanations default to Chinese.

The active research authority and the linked personal agreements below retain
their scope. A plan, an old authorization, or an existing runner does not
authorize a new research computation.

## Research Record Maintenance

This section is the single repository-wide maintenance policy, adapted from
`GR_lensing-main/AGENTS.md#research-record-maintenance` on 2026-10-30.

### Single owners and entry points

- Root `README.md` is the navigation entry, not a second scientific task board.
- `research/<topic>/README.md` owns that topic's current scope, status, open
  questions, next actions, and links to evidence. Update it when these change.
- Existing `progress.md` is dated history. Plans explain intended methods and
  dependencies; neither duplicates the live status maintained in the README.
- `presentations/midterm/README.md` owns presentation release and editing routes;
  `code/README.md` owns the elementary solver's model and test contract.
- `admin/maintenance/` contains repository maintenance evidence. It does not
  maintain scientific progress. Personal agreements and profile remain owned
  by the linked personal setup, without repository copies.

### Placement and continuity

Use the owning topic's `discussions/`, `derivations/`, `tests/`, and `drafts/`
for new topic records when they contain real material. Continue using existing
`theory/`, `experiments/`, and dated literature directories where executable
paths, provenance, or frozen manifests already depend on them. Create no empty
category directories merely to match a template.

Keep reusable teaching code in `code/`, derivation notes and editable TeX in
`Note/`, cited source papers in `literature/`, scientific exports with their
scripts and data in `figures/`, and presentation sources in `presentations/`.
`deliverables/` holds distinct reports and export metadata, without another
maintained copy of the entire repository. Put retired navigation and review
history in `admin/archive/`; link it from the owning entry when useful.

1. Find the existing topic and update it. Record dates and changed assumptions
   inside that file. A conversation or follow-up does not require a new file.
2. Create a file only for a distinct topic, reproducible experiment, or separate
   deliverable with its own source. Keep living filenames stable.
3. Preserve supervisor statements, human edits, source versions, failed tests,
   negative results, and superseding corrections. Distinguish proposals,
   algebra checks, numerical observations, and established findings.
4. A request to record an idea updates its topic record; it does not start an
   experiment, add a competing plan, or update global memory.
5. Before moving or deleting, inspect callers and provenance. Remove duplicates
   only after byte comparison. Keep distinct authored versions and scientific
   inputs. Record old-to-new paths and SHA-256 for structural consolidation.
6. Keep frozen manifests and evidence unchanged. Document relocation separately;
   update live links and callers together. Back up changed configuration once
   per coherent revision. Avoid whole-workspace snapshots for routine edits.
7. `admin/maintenance/check_workspace.py` checks tracked links, preservation,
   repository hygiene, and size boundaries. Run it after structural changes.
   Its checks do not establish scientific correctness or visual quality.

### Computation and artifact scope

Keep user-editable reports, images, TeX, PDFs, and other deliverables on Windows.
New substantive research simulations and their environments belong in Ubuntu/WSL;
record their Linux paths and export results to the owning Windows topic. Existing
Windows research records retain provenance. Elementary non-QNM teaching examples
may stay on Windows. Do not rerun simulations for directory maintenance.

Chapter edits, builds, and delivery are scoped to the named chapter or section;
check runner side effects before use. Preserve other chapters and global PDFs.
Substantial teaching changes follow their applicable teaching/review workflow.

### Git and publication

- Preserve upstream history and human changes; do not force-push or rewrite it.
- Commit source, inspectable deliverables, scientific inputs, and verification
  metadata. Ignore runtime Junctions, installed dependencies, caches, temporary
  serializers, local configuration, and credentials. Do not ignore the entire
  presentation `build/`: it contains authored source and required imports.
- Keep exact file bytes across checkout: `.gitattributes` disables newline
  conversion so recorded scientific hashes remain valid.
- Inspect the actual staged diff and run the checker before committing. Reuse
  the existing elementary regression suite when checking code availability.
  Run only checks needed for the requested change.
- Push to the configured remote only within the user's requested scope. Verify
  the remote branch SHA and a clean working tree after a push.

<!-- local-context-bridge:start -->
## Local personal context

Before the first substantive response, read the current personal working
agreements at [C:/Users/xuanm/.codex/AGENTS.md](C:/Users/xuanm/.codex/AGENTS.md), subject to the current
instruction hierarchy and explicit user requests. That file owns conversational
defaults; this project's artifact language and technical rules retain their scope.

Before personalized work, read [PROFILE.md](C:/Users/xuanm/.codex/personal-setup/PROFILE.md).
For relevant reusable lessons read [MEMORY.md](C:/Users/xuanm/.codex/personal-setup/MEMORY.md).
Prefer these current sources over partial or stale chat-memory summaries.
Keep one maintained profile; do not copy biography or mutable progress here.
Recheck current project state in its own sources. If a referenced file is
unavailable, report that gap instead of inventing details or claiming synchronization.
Reading local files does not update ChatGPT account memory or settings.
<!-- local-context-bridge:end -->

## Spin-wave space-time wave-packet research

Before planning, resuming, or redirecting this topic, read the canonical
[supervisor guidance](research/spin-wave-spacetime-wavepackets/teacher-dialogue.md)
and the current [paper research plan](research/spin-wave-spacetime-wavepackets/paper-research-plan.md).
The user explicitly designated the supplied supervisor conversation as this
project's enduring research authority on 2026-10-21. Preserve its original text
and keep the work centered on frequency–wavevector correlations, spin-wave
space-time wave-packet construction, and literature-grounded paper development.
Record later guidance and justified revisions separately. A plan does not
authorize research execution; check the current user request before running it.
