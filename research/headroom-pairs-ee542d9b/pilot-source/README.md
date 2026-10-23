# Exact pre-freeze pilot sources

The pilot ran on the protocol-only checkout `9f29e7f` with uncommitted scripts.
The original outputs bind the exact script bytes by SHA-256, but those earlier
versions were initially omitted from the retained package. Standards review found
this omission before submission. These two files recover the exact hash-matching
versions; the original pilot output is preserved unchanged.

- `pair_bounds.py`: `1a1f75329df515fecaca77848c7e3338f8a1ac634eaff94069d8bbb92b29b1ce`
- `run_bounds.py`: `a70367b592471d59802c4fff68552f5d92b092b64dc8ab91ddf44dd36272ada9`

The post-pilot changes before the frozen panel added input-length/output-filename
validation and final panel count/cap assertions. They did not change pair-search
transitions, costs, queue ordering, disjoint pair selection or aggregation.

Do not execute these archived files in this directory: their original relative
root calculation assumes the normal research package path. From the repository
root, replay them in a separate disposable checkout:

```sh
git worktree add --detach ../pair-pilot-replay 9f29e7f
cp research/headroom-pairs-ee542d9b/pilot-source/pair_bounds.py research/headroom-pairs-ee542d9b/pilot-source/run_bounds.py ../pair-pilot-replay/research/headroom-pairs-ee542d9b/
python ../pair-pilot-replay/research/headroom-pairs-ee542d9b/run_bounds.py --case maze-32-32-4-n128 --limit-pairs 8 --out research/headroom-pairs-ee542d9b/pilot-replayed.json
```

This replay was performed in a detached protocol-commit checkout. Its saved
`../pilot-replayed.json` and journal match **every deterministic field** of the original
pilot, including source hashes, eight pair optima, pops, discovered states, peak
queue counts and the resulting 5991 bound. Timestamps, timings and peak RSS are
explicitly excluded; the comparison does not claim memory observations are equal.
Keep the checkout or remove it with
normal `git worktree remove` when its local evidence is no longer needed.
