# Study 1: functional metacognitive monitoring

Status: **design encoded, stimuli not generated, not preregistered**.

Track A fully crosses 160 retained Fermi items with five elicitation conditions, six deployed model configurations from two vendors, and three repetitions. C4 and C5 are independent two-turn conversations. The shared cross-condition target is confidence that the point estimate is within one order of magnitude of truth.

Track B is a separate balanced binary design. Each model by format cell must contain exactly 50% S1 and 50% S2 trials, with 240 trials per cell and a four-point confidence response. A cell is non-estimable if Type 1 accuracy is outside 55-92% or at least 95% of confidence ratings occupy one scale point.

Final item parameters must be generated only after preregistration, stored under `data/private/`, hashed in a private timestamped OSF record, and released only after all model runs finish.

Candidate construction targets 25 template families across the five registered
domains with 10 provisional parameterizations per family. Reference benchmarks
follow the draft cross-vendor AI construction, deterministic verification, and
human source/adjudication workflow in `benchmark_validation.md`. These are
benchmarks with uncertainty, not exact known ground truth. The existing
five-family private bank is a pipeline prototype and cannot be selected for
confirmatory use.

The public draft design roster is `fermi_family_roster.json`. It currently
contains 25 deparameterized family concepts and 250 unique nonnumeric
parameterization slots. Passing its structural audit establishes only domain
balance, required metadata, eligible provisional classes, and preservation of
the preregistration boundary. It does not establish source validity, benchmark
correctness, contamination status, or P4 completion. Numerical provisional
variants remain blocked until their parent family passes the construction,
challenge, deterministic, and human-review workflow.

All Study 1 model calls are text-only and tool-disabled. Browsing, web search,
retrieval plugins, and other external tools are prohibited for every model run.
Public-search checks remain a proxy audit for public overlap and possible
training-data contamination; they are not a substitute for this collection
control.

The draft evidence requirements and rating rubric are specified in
`contamination_screening.md`. P5 remains incomplete while either search engine,
the canonical-template screen, or any final Low/Medium/High rating is pending.

The JSON schemas in this directory are the response contracts. Condition-specific nullability and cross-field checks are enforced by the parser and protocol compiler, not by silently repairing model output.

The primary inference is limited to the frozen Anthropic and OpenAI configurations. It does not establish measurement invariance across LLM vendors generally. Google and open-weight models are reserved for a separately declared external replication.
