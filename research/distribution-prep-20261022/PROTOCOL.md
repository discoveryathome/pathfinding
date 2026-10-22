# Distribution preparation baseline protocol

Author-run, exposed-data calibration. Pinned MAPF-LNS2 commit
1369823985a15944f9a339226d521f61605a6d17, upstream defaults, six-second internal
deadline, seeds 419 and 503, compared with pinned LaCAM3 under the same requested
deadline on three exposed cases: first lexicographic round-two empty, room and
maze cases. Randomize method order with seed 221042. Retain every timeout/failure.
Use a 30-second external kill limit; record elapsed and child CPU separately.

Important qualification: LNS optimizes SOC and LaCAM optimizes SOL. Re-score both
under the same checker and report SOC, SOL and makespan, but do not present this
as a matched-internal-objective algorithm ranking. The requested time limits also
do not guarantee equal actual CPU. Record objective mismatch and overruns explicitly.
Only exact verified nondominated witnesses may enter the current archive.

Add an obstacle-distance lower bound strengthened by a greedy matching of disjoint
agent pairs forced to collide along every individually shortest trajectory within
32 steps. Every matched pair requires at least one extra SOL/SOC unit; disjoint
pairs make these penalties additive. The matching need not be maximum. Validate
against exact two-agent search on small controls. A bound gap is an upper bound
on possible improvement, not a promise of attainable improvement.

Source and dependency licenses remain separate; LNS2 is research-licensed and
optional. Do not vendor its code or binaries in the pilot release.
