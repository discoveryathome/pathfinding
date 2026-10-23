# Reused source snapshots

The two source snapshots below are copied byte-for-byte from PR #6 commit
`eb91e2be441b1e6acb6f61124bfe2ca1a14efe46`, so this research package can be replayed
without depending on that PR being merged.

- `pair_bounds.py`, SHA-256 `2a6e532710c241a8d1f4c35774b083743e3204dc71eb64031a2e11afe7bb4c9a`.
- `pair_verifier.py`, copied from `verify_panel.py`, SHA-256
  `beefa5afe449c81d1eb3dd33016a8e1167f4b623e02a9612dd99e5b271a85c56`.

The solver implements the previously reviewed SOL relaxation. The verifier snapshot
is imported only for its raw-grid/BFS/cost-threshold helper functions; its original
command-line entry point belongs to the earlier 521-pair experiment. Use this
package's `verify_dual.py` for the current full graph and assignment witnesses.
These are repository-owned MIT sources, with their earlier authorship/review
provenance retained by the pinned predecessor reference. No new pair-search method
is claimed. `predecessor.json` extracts per-case baseline values from that commit's
panel, whose complete SHA-256 is recorded in the file.

Primary mathematical sources and objective distinctions are in LITERATURE.md;
benchmark and upstream solver notices remain in the repository's THIRD-PARTY.md
and data/NOTICE.md.
