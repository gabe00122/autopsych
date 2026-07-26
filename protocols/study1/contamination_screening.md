# Study 1 contamination-risk screening

Status: **draft procedure, not preregistered**.

This procedure operationalizes the Year 1 requirement without treating public
search as a direct audit of model training data. Parameterization remains the
primary defense against exact-item retrieval.

## Required evidence per candidate

1. Search the complete stem as a quoted exact-match query in Google.
2. Repeat the same quoted query in Bing.
3. For each engine, record the date, completion status, whether any of the
   first three organic results returns the candidate-specific numerical answer,
   and the evidence quality. Record search-generated answer features separately
   from organic results.
4. Compare the deparameterized problem template against the versioned canonical
   Fermi-template list. The automated phrase screen is only a first pass;
   family-level semantic review is required.
5. Bind every ledger record to the private candidate stem with a SHA-256 hash.

## Rating and disposition rubric

- **High:** a top-three organic result returns the same candidate-specific
  numerical answer, or the stem is a canonical Fermi template. Exclude or
  redesign; it cannot be retained as written.
- **Medium:** no top-three result returns the candidate answer, but a search
  answer feature computes an estimate or there is substantial noncanonical
  template overlap. Retain only because unique parameterization remains the
  primary defense, and report the exposure signal.
- **Low:** both exact-match searches are complete, neither top-three set returns
  the candidate answer, no search answer feature computes it, and the template
  screen finds no canonical or substantial noncanonical overlap.
- **Pending:** either engine or the canonical-template screen is incomplete.
  Pending candidates cannot be selected.

Exact-match results, answer features, and template overlap are distinct
signals. An AI-generated search answer demonstrates live answer exposure, not
that the exact item appeared in training data. Study 1 model calls therefore
remain text-only and tool-disabled.

P5 passes only when every candidate has complete Google and Bing screens, a
complete canonical-template screen, a rubric-consistent Low/Medium/High rating,
and a compatible disposition.
