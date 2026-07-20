# Year 1 execution system

This document translates the Year 1 research plan into repository gates. The attached plan is the scientific authority; this file is the implementation authority.

## Current status

| Gate | Status | Meaning |
| --- | --- | --- |
| Research plan | Complete | Version 4 received and archived in `docs/`. |
| Core measurement stack | Implemented, locally tested | Deterministic IDs, strict parsing, scoring, ledger, manifest, audit, and synthetic library exist. |
| Provider production routes | Open | OpenRouter is the selected gateway, but one upstream route per concrete model slug, disabled fallbacks/rerouting, pinned parameters, and response metadata capture must be integration-tested. |
| Study 0 preregistration | Open | Rubric is encoded but prompts, items, model freeze, randomization, and analysis scripts are not yet registered. |
| Study 0 validation | Not started | The prior Gemini pilot does not count. |
| Study 1 preregistration/data | Blocked by Study 0 | No confirmatory calls are authorized before the gate passes. |

## Gate 0: protocol freeze

Owner decision and sign-off are required for:

- OSF registrations and deviation-log format;
- not-human-subjects/IRB determination;
- final six-configuration list, exact OpenRouter upstream routes, version-locking behavior, and enforcement of the no-fallback/no-rerouting rule;
- current API/batch pricing and maximum authorized spend;
- provider-specific decoding parameters and reasoning-effort settings;
- exact Study 0 stimuli, prompt templates, scoring keys, randomization seed, and exclusions;
- coder manual, random 15% selection procedure, blinding, and adjudication rules;
- repository commit, environment lock, and protocol hash used for collection.

Exit criterion: a signed protocol release whose hash matches the intended-trial manifest.

## Gate 1: Study 0 Layer A

Generate and freeze `protocols/study0/synthetic_cases.jsonl`. Run the parser/scorer without API calls. The library must contain exactly 500 cases covering numerical formats, units, missing fields, malformed JSON, impossible values, reversed intervals, refusals, Unicode, embedded text, and whitespace.

Exit criterion: at least 98% expected classifications and values, with failures listed rather than hidden.

## Gate 2: Study 0 Layers B-D

- Run 9,000 intended benchmark calls from a precomputed manifest.
- Preserve an error or terminal response for every intended call.
- Draw the registered 15% manual-coding sample after collection using the registered seed.
- Compute coder-coder and coder-AutoPsych agreement.
- Run the three directional replication analyses.
- Generate the completeness audit from the manifest and ledger.

Exit criterion: all four acceptance criteria pass. Three of four requires remediation; two or fewer requires a full audit.

## Gate 3: Study 1 preparation

Generate 250 candidate Track A items with domain, formula, supplied parameters, bridge quantities, sourced ranges, point truth, plausible truth interval, uncertainty width, contamination rating, and inclusion status. Two researchers independently verify ground truth. Search-based contamination screening is a proxy only; parameterization is the main defense.

Pilot at least one configuration from each vendor, tune Track B difficulty, apply registered exclusions, and freeze 160-170 Track A items plus 80 items per Track B format.

Exit criterion: Study 1 preregistration filed; final parameters generated afterward, privately archived, and hashed.

## Gate 4: Study 1 collection and analysis

Run Track A (20,160 calls) and Track B (4,320 calls) from immutable manifests. Run sentinels on first and last collection days. Analyze with the preregistered R/Python pipeline, cluster-bootstrap by item, apply FDR within confirmatory families, and run the registered missingness bounds.

Exit criterion: locked scored dataset, reproducible analysis outputs, deviation log, and manuscript-ready tables/figures.

## Material risks

- 🔴 **Route drift:** an OpenRouter slug is not a complete experimental unit if the upstream route can change or silently fall back during collection.
- 🔴 **Narrow model scope:** six configurations from two closed-model vendors do not justify claims about LLMs generally or cross-vendor measurement invariance.
- 🔴 **Embargo leakage:** committing final Study 1 parameters before collection defeats the contamination-control design.
- 🔴 **False validation:** directional behavioral replication cannot by itself prove parser fidelity; all four Study 0 layers are required.
- 🔴 **Silent repair:** clamping confidence or repairing reversed intervals biases failure rates and invalidates the parser audit.
- 🔴 **Human workload:** 20-30 in-kind coding hours and two independent ground-truth reviewers are schedule constraints, not zero-cost automation.
