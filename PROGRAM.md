# AutoPsych Scientist Operating Manual

AutoPsych executes a fixed research protocol; it is not an autonomous question generator during confirmatory work. The Year 1 research plan, preregistrations, and frozen machine-readable protocols control the study.

## Non-negotiable sequence

1. Freeze and hash the protocol, prompts, schemas, model list, decoding policy, scoring rules, exclusions, and intended trial manifest.
2. Pass Study 0 before Study 1 confirmatory collection.
3. Preserve every intended trial, including API errors, refusals, and parse failures.
4. Analyze from the immutable raw ledger. Never hand-edit raw records.
5. Separate confirmatory outputs from exploratory analyses and disclose every deviation.

## Unit of analysis

A result is indexed to the complete system configuration, not merely a model family. Every record must identify the provider route, exact model/version if exposed, date, system and user prompts, decoding parameters, tools, memory/context state, repetition, item, condition, and retry history.

## Data integrity

- Build the intended-trial manifest before calls begin.
- Use deterministic trial IDs and SHA-256 prompt hashes.
- Store full response text before parsing.
- Invalid confidence values, reversed intervals, missing fields, and unit mismatches are failures; do not clamp or silently repair them.
- Record parse failures and refusals as outcomes. Do not drop them.
- A retry is linked to the same trial ID and reported in the terminal record.
- Keep unreleased Study 1 items in `data/private/`, which is gitignored. Publish only after collection is complete.

## Study 0 gate

AutoPsych is validated for Year 1 use only if all four preregistered criteria pass:

- synthetic parser/scorer accuracy at least 98%;
- human-AutoPsych agreement at least .90 on all primary fields;
- directional replication of at least two of three benchmark phenomena;
- run-level completeness at least 99%.

Three of four triggers remediation before Study 1. Two or fewer triggers a full pipeline audit.

## Study 1 design boundaries

- Track A and Track B are distinct designs.
- Track A uses parameterized Fermi items with supplied quantities plus one or two estimated bridge quantities.
- Track B must balance stimulus classes 50/50 within every model by format cell.
- C4 neutral reconsideration and C5 social challenge each begin from an independent C1-type first turn.
- Platform-recorded turn-1 values, not model restatements, control revision analyses.

## Statistical boundaries

Use the preregistered metrics and models. Calibration and confidence discrimination are not interchangeable. Report Brier metrics, slope/intercept, ECE, AUROC2, and first-order error separately. Cluster-bootstrap by item. Apply the registered FDR and missingness policies. Do not call a model "metacognitive" from fluent confidence language alone.

## Pilot status

The existing Gemini report is a historical pilot. It exposed ceiling effects, arithmetic-heavy items, unit errors, and weak confidence discrimination. It may motivate design choices but cannot be pooled with confirmatory Study 1 data.
