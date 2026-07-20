# Study 0: AutoPsych validation

Status: **draft, not preregistered, not passed**.

Study 0 is a measurement-instrument validation, not a pilot model study. It contains four sequential layers:

1. A deterministic 500-case synthetic parser/scorer library.
2. Two blind human coders on a random 15% benchmark subsample, followed by human-AutoPsych agreement.
3. Directional replications of anchoring, framing, and confidence-accuracy dissociation across six frozen model configurations from Anthropic and OpenAI.
4. An audit against the intended-trial manifest, requiring at least 99% complete terminal records.

Before collection, add the exact prompts, item sources/generation rules, randomization seed, model freeze, OpenRouter upstream routes, decoding/reasoning policies, exclusions, and analysis scripts to the OSF preregistration. Concrete model slugs and one upstream route per model must be pinned; latest aliases, silent fallbacks, automatic rerouting, Pro modes, and multi-agent modes are not permitted. The repository rubric is machine-readable in `acceptance_rubric.json`.
