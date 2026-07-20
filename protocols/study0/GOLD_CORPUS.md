# Gold validation corpus

`gold_cases.jsonl` is the independent reference corpus for parser and scorer
validation. It is hand-authored: the validator reads its expected values but
never generates or derives them from AutoPsych implementation code.

Each line identifies the production response schema to apply, raw model text,
and the expected parse status. Valid cases additionally assert parsed values
and JSON recovery behavior. Score cases assert normalized estimates, error
metrics, and expected scoring failures.

The current seed corpus establishes coverage across all four production
response contracts. Expand it to the 500-case preregistration target using a
reviewed coverage matrix; do not overwrite its expected values from observed
validator output. New cases require a second reviewer and a corpus-hash update.

## Expansion target

| Response contract | Target cases | Seed cases | Primary coverage |
| --- | ---: | ---: | --- |
| Study 0 response | 100 | 10 | required fields, enum/null handling, refusals, recovery |
| Study 1 Track A | 220 | 9 | numeric coercion, intervals, units, scoring, malformed output |
| Study 1 Track B | 100 | 5 | binary choice and four-point confidence bounds |
| Study 1 revision | 80 | 4 | original/revised values, confidence, decision constraints |
| **Total** | **500** | **28** | |

The 28 seed cases are a development baseline, not evidence that the 500-case
Study 0 Layer A acceptance criterion has passed.
