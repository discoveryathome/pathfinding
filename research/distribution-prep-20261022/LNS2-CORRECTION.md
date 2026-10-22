# Configuration correction before the second comparison

The first default run is preserved in lns2-comparison/. Inspection of driver.cpp
and LNS.cpp shows maxIterations defaults to zero, preventing improvement after
initial feasibility. Its 0.36–1.27 second runs were not six seconds of optimization.

The second comparison changes only maxIterations to 1,000,000 so the six-second
deadline can govern improvement. Same cases, seeds, methods and verification.
This is a configuration repair on exposed cases, not an unseen confirmation or
parameter search. Internal objective mismatch (LNS2 SOC versus LaCAM3 SOL) remains
and prevents a matched-objective superiority claim. Both raw passes are retained.
