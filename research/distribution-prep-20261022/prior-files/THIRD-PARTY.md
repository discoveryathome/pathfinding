# Source and data provenance

Pilot-owned Python, tests and visualization code are MIT. LaCAM3 is Keisuke
Okumura's MIT software, downloaded unchanged at the commit in research/sources.json.
Its argparse submodule remains pinned with its upstream notices. No upstream
endorsement is implied. The solver vendor checkout is ignored and reproducibly
fetched by tools/setup.sh; the published solver itself was not modified.

Maps and scenario rows are from Nathan Sturtevant's Moving AI Lab MAPF benchmark:
https://movingai.com/benchmarks/mapf/index.html . Contains information from the
Moving AI benchmarks, made available under the Open Data Commons Attribution
License 1.0: https://opendatacommons.org/licenses/by/1-0/ . Preserve those notices
with the data, derived instance descriptions and visualizations. Benchmark records
are not relicensed as pilot-owned MIT code. The database license does not override
separate rights in individual content; this package uses synthetic empty, random,
room and maze grids rather than extracted commercial game artwork.

Suggested attribution: Sturtevant, N., “Benchmarks for Grid-Based Pathfinding,”
IEEE Transactions on Computational Intelligence and AI in Games, 4(2), 144–148,
2012. Each source archive URL and SHA-256, selected member hash, scenario row and
LaCAM3 revision is recorded. Scenario octile-distance fields are NOT used as
four-connected lower bounds; the checker computes its own BFS distances.

LaCAM3 baseline: https://github.com/Kei18/lacam3
Paper: https://aamas.csc.liv.ac.uk/Proceedings/aamas2024/pdfs/p1501.pdf
Known MAPF-LNS: https://github.com/Jiaoyang-Li/MAPF-LNS
Newer preference work to compare: https://github.com/HirokiNagai-39/pibt-tiebreaking
The latter two were not installed or beaten in this trial. Neighborhood repair,
prioritized space-time A*, and proximity selection are established ideas, not
claimed novel contributions of this pilot.

Build setup initially exposed upstream tests' relative fixture paths; symlinks
under ignored build/ fix the working-directory assumptions. Assertions remain
enabled. All six upstream tests pass. The initial fixture-location failure is
retained. The pilot checker also explicitly rejects empty solutions rather than
using upstream's empty-solution feasibility convention as success.

## Round-two additions

The separately fetched PIBT preference implementation is MIT, from
https://github.com/HirokiNagai-39/pibt-tiebreaking at the commit and argparse
submodule pins in research/round2/baseline-source.json. It is based on LaCAM3; retain
all upstream notices. No upstream endorsement is implied. Its source/binaries are
not bundled in the pilot source archive.

Additional Moving AI maps and scenarios retain the same ODC Attribution License
1.0. Exact archive URLs, archive/member hashes and selected members are in
research/round2/data-sources.json. Empty-48-48 replaces a nonexistent empty-64-64
member before measurement, as recorded in the protocol.
