# Study 1 reference-benchmark validation

Status: **draft procedure, not preregistered**.

Study 1 uses **reference benchmarks**, not known ground truth. Exact real-world
totals are unavailable for many Fermi estimands, so agreement between two
researchers or two models is evidence of reproducibility, not proof of truth.

## Candidate-bank structure

The target bank contains 25 template families spanning the five registered
domains, with 10 provisional parameterizations per family. Benchmark evidence
is assembled and reviewed at the family level; deterministic code propagates an
approved formula and bridge-quantity ranges to its parameterized candidates.
The template family is recorded for every item so retention and analysis can be
balanced by domain and family.

The existing five-family candidate bank is a pipeline prototype and is not
eligible for confirmatory selection under this procedure.

The draft roster in `fermi_family_roster.json` reserves ten nonnumeric
parameterization slots for each of 25 proposed families. Roster validation is a
design-cardinality check only. A slot is not a candidate item, and no family in
the roster is eligible for numerical propagation until its benchmark packet is
approved under the workflow below.

## Benchmark classes

- **A — externally checkable:** a suitable observed aggregate is available for
  an out-of-sample back-check.
- **B — constructed and triangulated:** no exact aggregate is available, but
  the estimand, formula, and consequential bridge quantities are supported by
  defensible independent evidence.
- **C — speculative:** the benchmark depends materially on inaccessible,
  circular, arbitrary, or weakly sourced assumptions. Class C is excluded.

## Family-level workflow

1. **AI construction.** A model creates a family packet containing the precise
   estimand, formula, units, bridge quantities, primary-source candidates,
   reference ranges, benchmark point and interval, sensitivity analysis, and
   any available external back-check. It sees provisional templates only.
2. **Blind cross-vendor challenge.** A model from a different vendor receives
   the packet without the constructor's inclusion verdict. It independently
   recomputes the benchmark, checks the sources, identifies omitted variables,
   attempts to falsify the estimand and interval, and recommends A, B, or C.
3. **Deterministic checks.** Code verifies units, arithmetic, interval ordering,
   sensitivity calculations, source fields, and consistent propagation to all
   parameterized candidates. Model agreement cannot waive these checks.
4. **Human source and construct review.** A human verifies the primary evidence,
   estimand, exclusions, and benchmark class for every retained family. Humans
   do not independently solve every parameterized item.
5. **Human adjudication and audit.** A second human adjudicates every AI
   disagreement, every proposed Class C or otherwise high-risk family, and a
   preregistered random sample of AI agreements. The sampling fraction and seed
   must be frozen before review begins.

## Wolfram Alpha instrument

The official Wolfram Alpha website or API is used as a logged family-level
computational cross-check. The Wolfram GPT in the ChatGPT GPT Store and other
LLM wrappers are prohibited for this role.

Permitted uses are arithmetic and unit verification, component-quantity
cross-checks, and comparison with an externally observed aggregate. Wolfram
Alpha is not a primary source, does not replace source triangulation, cannot
independently confer Class A status, and does not count as either AI reviewer.

Each use records the exact query, date and time, access method, input
interpretation, assumptions, returned value and units, displayed source or
attribution information, and result link. Results are treated as time-varying
instrument outputs. They are preserved only to the extent authorized by the
applicable license or written agreement.

Only provisional family-level components and deparameterized templates may be
queried. Final confirmatory stems, numerical parameters, and complete benchmark
packets are never sent to Wolfram Alpha. Final arithmetic is reproduced locally.
Written correspondence received on 2026-07-26, in reply to a request for
logged manual API cross-checks, documents a non-commercial allowance of up to
2,000 queries per month and the project's no-cache/no-training commitment. It
supports individual researcher-initiated manual API queries within that scope;
automated bulk querying remains out of scope. The correspondence is retained in
the controlled record. Any use remains within the documented allowance, and
final stems, numerical parameters, and complete benchmark packets remain
prohibited inputs. Rate-limit detail, retention detail, and attribution or
publication conditions remain to be recorded if supplied.

## Acceptance rules

A family can generate retained candidates only when:

- its packet is complete and bound to source snapshots or stable source IDs;
- the two AI roles used different vendors and their outputs are preserved;
- all consequential bridge quantities are triangulated, or a documented reason
  explains why one authoritative source is sufficient;
- deterministic checks pass and unresolved discrepancies are absent;
- any Wolfram Alpha cross-check is fully logged and licensing-compliant;
- human source/construct review is signed; and
- the final adjudicated class is A or B.

Candidate variants remain ineligible if they are arithmetic-only, fail the
contamination screen, fail family-balance requirements, or inherit an unresolved
family review. Reference-benchmark uncertainty must be carried into sensitivity
analyses rather than hidden behind a single point value.

## Exposure and preregistration boundary

The construction and review models may see provisional deparameterized
templates and source packets, but they must not see final confirmatory stems or
numerical parameters. After the Study 1 preregistration is filed, final
parameters are generated mechanically from approved family specifications,
privately archived, and hashed. Study models remain text-only and tool-disabled
during collection.
