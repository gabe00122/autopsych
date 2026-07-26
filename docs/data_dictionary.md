# AutoPsych data dictionary

## Intended-trial manifest

The manifest is created before collection and includes the run ID, protocol ID, preregistration URL, creation timestamp, intended count, ordered trial IDs, a hash of the full trial specification, and every trial specification.

A trial specification contains:

- experiment/study, item, condition, and repetition;
- gateway, pinned upstream provider route, requested concrete model ID, and vendor;
- complete message list and SHA-256 prompt hash;
- response schema;
- provider-specific sampling/decoding parameters;
- item metadata needed for scoring, without secrets in public manifests.

## Terminal trial record

Each intended trial receives exactly one terminal record. Required fields include:

- run/trial IDs and schema version;
- item, condition, repetition, gateway, pinned and returned upstream provider, requested model, and returned version;
- start/completion timestamps;
- full messages, prompt hash, and decoding parameters;
- attempt count, status code, request ID, seed/fingerprint where exposed, and token usage;
- full raw response;
- parse status (`valid`, `invalid`, `refusal`, or `api_error`), parse errors, and parsed values;
- scoring results and any scoring error;
- terminal API error if no response was obtained.

API errors, refusals, and parse failures are data. They are never represented by a missing row.

## Private reference-benchmark family packet

Each template family has one private packet containing the family ID, domain,
estimand, formula, units, bridge quantities, primary-source references and
snapshots, benchmark point and interval, sensitivity results, optional external
back-check, benchmark class (A/B/C), constructor output, blind cross-vendor
challenge, deterministic-check result, human source/construct sign-off, and any
adjudication record. When used, the Wolfram Alpha instrument record includes
the exact query, timestamp, official website/API access method, input
interpretation, assumptions, result and units, displayed attribution/source
information, result link, and licensing basis for retention. Candidate records reference the family ID and inherit only
an approved A or B packet. Final numerical stems are absent until after
preregistration.

The current prototype candidate JSON uses the legacy field names
`ground_truth_point` and `plausible_truth_interval`. Until the replacement
family schema is frozen, those fields are interpreted as the reference-
benchmark point and interval; they must not be described as exact known truth.

## Private contamination ledger

Each candidate has one private contamination record containing the candidate
ID and stem SHA-256, exact-match Google and Bing screen status, search date,
top-three answer judgment, evidence quality, search-answer-feature flag,
canonical-template result, final Low/Medium/High or Pending rating, rationale,
and disposition. Search-generated answers are recorded separately from organic
top-three results. A candidate with any pending screen cannot be selected.

## Release tiers

- `data/private/`: embargoed item parameters and private OSF hashes; never commit during collection.
- `runs/`: local raw manifests and ledgers; gitignored because they may contain embargoed prompts or provider metadata.
- `protocols/`: public frozen rules, schemas, and preregistration materials.
- `reports/`: derived outputs and pilot history, not raw protocol authority.
