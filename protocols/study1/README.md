# Study 1: functional metacognitive monitoring

Status: **design encoded, stimuli not generated, not preregistered**.

Track A fully crosses 160 retained Fermi items with five elicitation conditions, six deployed model configurations from two vendors, and three repetitions. C4 and C5 are independent two-turn conversations. The shared cross-condition target is confidence that the point estimate is within one order of magnitude of truth.

Track B is a separate balanced binary design. Each model by format cell must contain exactly 50% S1 and 50% S2 trials, with 240 trials per cell and a four-point confidence response. A cell is non-estimable if Type 1 accuracy is outside 55-92% or at least 95% of confidence ratings occupy one scale point.

Final item parameters must be generated only after preregistration, stored under `data/private/`, hashed in a private timestamped OSF record, and released only after all model runs finish.

The JSON schemas in this directory are the response contracts. Condition-specific nullability and cross-field checks are enforced by the parser and protocol compiler, not by silently repairing model output.

The primary inference is limited to the frozen Anthropic and OpenAI configurations. It does not establish measurement invariance across LLM vendors generally. Google and open-weight models are reserved for a separately declared external replication.
