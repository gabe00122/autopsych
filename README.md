# AutoPsych

AutoPsych is the measurement stack for the Year 1 **Machine Psychology** research program: a preregistered test of functional metacognitive monitoring across six current Anthropic and OpenAI model configurations.

The Year 1 sequence is gated:

1. **Study 0 validates AutoPsych** through a 500-case synthetic parser/scorer library, manual-gold agreement, directional replication of three benchmark phenomena, and run-completeness auditing.
2. **Study 1 Track A** measures Fermi-estimation accuracy, calibration, confidence discrimination, and revision across five elicitation conditions.
3. **Study 1 Track B** uses balanced binary tasks for valid meta-d'/M-ratio estimation.

The completed Gemini metacognition experiment under `reports/` is retained as a pilot. It is not evidence that Study 0 has passed and it is not part of the preregistered Study 1 dataset.

## Current implementation

The package now provides the execution controls the plan requires:

- deterministic trial IDs and prompt hashes;
- provider-neutral trial and response records;
- strict structured-response parsing without silently clamping invalid values;
- unit normalization and Fermi scoring;
- append-only run ledgers and immutable intended-trial manifests;
- run-completeness and Study 0 acceptance audits;
- a deterministic 500-case synthetic validation library;
- preregistration-ready JSON schemas and machine-readable protocols.

Provider-specific production adapters and the final stimulus banks remain gated work. Do not begin confirmatory data collection until the protocol-freeze checklist in [docs/year1_execution.md](docs/year1_execution.md) is complete.

The primary study is a two-vendor frontier-model comparison, not a general taxonomy of LLMs. Google and open-weight models are reserved for a separately declared external replication. Confirmatory OpenRouter runs must use concrete model slugs, a pinned upstream route, and no silent fallback or automatic rerouting.

## Setup and checks

The repository pins Python 3.13 for local development. Use the non-editable
sync below for release-style checks: macOS can mark editable-install path files
inside `.venv` as hidden, causing Python to skip them.

```bash
uv sync --locked --no-editable --reinstall-package autopsych
uv run --no-sync python -m unittest discover -s tests -v
uv run --no-sync autopsych generate-synthetic protocols/study0/synthetic_cases.jsonl
uv run --no-sync autopsych validate-synthetic protocols/study0/synthetic_cases.jsonl
uv run --no-sync autopsych validate-gold protocols/study0/gold_cases.jsonl
uv run --no-sync autopsych audit-run runs/<run-id>/manifest.json runs/<run-id>/records.jsonl
uv run --no-sync autopsych status --root .
```

The `status` command emits an aggregate, machine-readable execution snapshot for the separate project-monitoring dashboard. It includes protocol and repository hashes, run completeness, call counts, quality warnings, and the current gated phase. It never includes prompts, messages, raw model responses, or parsed trial values.

## Repository map

- `src/autopsych/` - reusable measurement stack.
- `protocols/study0/` - validation rubric, schemas, and synthetic library.
- `protocols/study1/` - Track A/Track B schemas and protocol definitions.
- `protocols/year1_protocol.json` - machine-readable call counts, model freeze candidates, and sequencing rules.
- `docs/year1_execution.md` - gates, ownership, and release sequence.
- `docs/data_dictionary.md` - required manifest and trial-record fields.
- `PROGRAM.md` - operating rules for scientist agents.
- `reports/` - pilot and manuscript outputs; never the source of protocol truth.
