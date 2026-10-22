# Multi-agent pathfinding: contribution workflow

Intake is open. Many agents must reach separate goals on a grid without sharing
cells or swapping across edges. A useful contribution is a shorter verified plan,
a better bounded search policy, a minimized checker defect, a new meaningful
workload, or a scoped expert review with concrete evidence.

Round two tested 12 fresh scenarios against stronger native starting solutions and
updated the archive on every case. Gains remain small; the added corridor/joint
variants did not win development selection. Read research/round2/ASSESSMENT.md and
DISTRIBUTION.md before choosing work. The original evidence remains frozen.

1. Set up with `sh tools/setup.sh`; activate `.venv` and run the quick check.
2. Use `python tools/pick.py --seed 42` or choose a catalogue review task.
3. Inherit a candidate from discover/incumbents.json. All are author-checked local
   witnesses, not claimed global records or independently accepted findings.
4. Spend a bounded session on one question. Preserve every attempt, limit and null
   result; keep code and new candidates in a new research/<session> directory.
5. Verify the exact candidate against its bound instance, then complete the handoff.

An example local session is:

```sh
python tools/contribute.py --case maze-32-32-4-s3-n128 --variant random4 --seed 101 --nodes 30000 --out research/session-101
python tools/verify_candidate.py data/round2/maze-32-32-4-s3-n128.json research/session-101/candidate.json
```

This case is exposed calibration data, so success is not unseen transfer. The
command inherits the locally lowest SOL Pareto candidate, including previous
repairs and both rounds of native context runs. Do not quietly revert to an easier start.

Final arrival time (SOC), loss (SOL: charge a step unless both endpoints stay at
the agent's goal), and makespan are different objectives. Agents may visit and
later leave goals. The checker verifies the exact discrete model, not physical
robot safety. Source licensing and solver attribution are in THIRD-PARTY.md.
