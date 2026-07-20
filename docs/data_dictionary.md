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

## Release tiers

- `data/private/`: embargoed item parameters and private OSF hashes; never commit during collection.
- `runs/`: local raw manifests and ledgers; gitignored because they may contain embargoed prompts or provider metadata.
- `protocols/`: public frozen rules, schemas, and preregistration materials.
- `reports/`: derived outputs and pilot history, not raw protocol authority.
