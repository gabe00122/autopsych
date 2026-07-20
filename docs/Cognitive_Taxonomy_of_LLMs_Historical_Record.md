# Cognitive Taxonomy of LLMs

**Historical Record of the Project**

Prepared for Julian Keith
May 2, 2026

> Central thesis: The central methodological challenge for machine psychology is to convert human psychological constructs into validated computational constructs, rather than merely administering human tests to nonhuman systems.

| Field | Record |
| --- | --- |
| Project name | Cognitive Taxonomy of LLMs |
| Working research program | Construct Validation for Machine Psychology |
| Primary question | What counts as valid psychological measurement when the subject is a generative model rather than an organism? |
| Document type | Historical record and project charter |
| Source basis | User-provided project overview and recent project discussion context |
| Date of record | May 2, 2026 |

## 1. Origin of the Project

The project began from a broad question about the psychology of large language models: what are the most important unanswered questions if one treats LLMs as systems whose behavior can be studied with tools adapted from psychology? The earliest working frame was exploratory but already methodological: the goal was not to anthropomorphize models, but to determine whether psychological methods can be transformed into valid tools for studying artificial cognitive systems.

The project subsequently narrowed toward metacognition, uncertainty, self-assessment, and construct validity. A key insight emerged: before asking whether LLMs have beliefs, personalities, metacognition, or biases, the field must first determine whether its instruments measure anything stable, interpretable, and causally relevant in these systems.

## 2. Foundational Position

The project rejects the simple transfer of human psychological instruments to LLMs. Human psychology studies embodied organisms with developmental histories, biological drives, attention, memory, fatigue, social incentives, subjective experience, and consequences for action. LLMs lack these in the ordinary biological sense. Therefore, direct importation of psychological tests is not automatically valid.

This does not imply that psychological investigation of LLMs is impossible. It implies that the field requires a new validation framework. The appropriate question is not whether an LLM “has” a psychological trait, but whether there is a stable, causally active, generalizable, and measurable computational analogue of that trait.

## 3. The Gateway Problem

The gateway problem is methodological validity. If the measurement problem is not solved, downstream claims about model personality, confidence, theory of mind, moral reasoning, bias, belief, or self-knowledge will remain fragile. Apparent psychological profiles may instead reflect prompt wording, role framing, training contamination, scale-use conventions, system instructions, sampling parameters, or superficial imitation of human test-taking behavior.

The project therefore treats machine psychology as a field that must be built on psychometrics, cognitive psychology, experimental design, and mechanistic interpretability. Its first task is to define what counts as evidence.

## 4. Ten Methodological Problems Identified

**Unit of analysis:** The relevant subject could be the base model, instruction-tuned model, system prompt, sampling configuration, chat session, memory-augmented agent, tool-using agent, or model-family lineage. Claims must specify the exact system being studied.

**Operational analogue of a construct:** Human construct labels such as confidence, anxiety, openness, or working memory cannot be assumed to map directly onto model behavior. Each must be translated into an operational analogue.

**Status of self-report:** LLM self-report is generated behavior, not introspective evidence. It may be useful only when validated against external criteria such as accuracy, calibration, error detection, or internal process variables.

**Prompt sensitivity:** Prompt wording, role assignment, task framing, and surface form may dominate outcomes. Prompt sensitivity should be treated as a dependent variable, not merely a nuisance.

**Measurement invariance:** The same score may not mean the same thing across GPT, Claude, Gemini, Llama, Mistral, or across versions of the same model. Cross-model comparison requires invariance testing.

**Contamination and memorization:** Classic psychology tasks are often public and may be in training data. Novel item generation, private item banks, and adversarial task grammars are needed.

**Behavior-mechanism triangulation:** Outputs should be paired with token probabilities, entropy, logit margins, activation analysis, ablations, path patching, and other mechanistic evidence where possible.

**Process measures:** LLMs lack human reaction time, but analogues may include reasoning-token count, entropy, self-corrections, latency under controlled infrastructure, sample variance, and tool-search depth.

**Ecological validity:** One-shot questionnaires differ from real use contexts: multi-turn dialogue, tool use, memory, social pressure, ambiguous intent, and high-stakes advice.

**Failure taxonomy:** The psychology of a model may be best characterized by the shape of its breakdowns: where theory-of-mind behavior collapses, confidence miscalibrates, or reasoning fails under perturbation.

## 5. Validation Ladder

The project proposes a staged evidentiary ladder for claims about machine-psychological constructs:

| Level | Evidentiary Standard |
| --- | --- |
| Level 0 | The model says trait-like things. |
| Level 1 | The model behaves consistently on one test. |
| Level 2 | The behavior survives paraphrase, role, and sampling variation. |
| Level 3 | Multiple independent tasks converge on the same latent dimension. |
| Level 4 | The dimension predicts out-of-sample behavior. |
| Level 5 | There is mechanistic evidence that an internal representation or process causally contributes. |
| Level 6 | The construct generalizes across models or explains systematic differences between models. |

The working diagnosis is that much current LLM psychology sits at Levels 0-2. The project’s ambition is to move the field toward Levels 3-6.

## 6. Research Program: Construct Validation for Machine Psychology

The project’s research program is organized around five linked studies. These studies move from descriptive instability to convergent validity, prediction, mechanism, and taxonomy.

### Study 1: Prompt-invariance of psychological measures

Administer multiple versions of the same construct measure across models, roles, item phrasings, and sampling configurations. Estimate variance attributable to model, prompt, item, role, and seed.

### Study 2: Convergent validity across behavioral tasks

Measure metacognitive sensitivity using verbal confidence, sample consistency, error detection, abstention behavior, and post-answer revision. Ask whether these indicators form a coherent latent dimension.

### Study 3: Predictive validity

Test whether measured constructs predict future behavior in new tasks. For confidence, the key question is whether reported or inferred confidence predicts actual accuracy and appropriate abstention.

### Study 4: Mechanistic validation

Use activation analysis, representation similarity, causal interventions, or ablations to determine whether a proposed construct corresponds to stable internal structure or process.

### Study 5: Cross-model taxonomy

Map models into a multidimensional psychological space using validated dimensions such as calibration, deference, persistence, uncertainty avoidance, contradiction sensitivity, abstraction, and social compliance.

## 7. Emerging Taxonomy

The project distinguishes several regimes of machine cognition that should not be collapsed into a single category:

| Regime | Description |
| --- | --- |
| Test-bench cognition | Behavior observed in isolated benchmark or questionnaire settings. |
| Chat cognition | Behavior in multi-turn conversation shaped by role, context, and conversational history. |
| Agentic cognition | Behavior when the model plans, acts, uses tools, delegates subtasks, or revises plans. |
| Tool-mediated cognition | Behavior that depends on external resources such as search, code execution, databases, or calculators. |
| Memory-extended cognition | Behavior when persistent or retrieved memory changes model responses across sessions. |

## 8. Reporting Standards Proposed by the Project

A machine-psychology study should report enough detail for replication and interpretation. At minimum, it should specify:

- model identity and version/date

- base versus instruction-tuned status where known

- system prompt and developer instructions where available

- temperature, top-p, and other sampling settings

- context-window conditions

- tool availability

- memory state

- number of sampled trials

- deterministic versus stochastic decoding

- prompt variants and role instructions

- item-generation process and contamination safeguards

- scoring rules and preregistered exclusion criteria

## 9. Intellectual Positioning

The project is positioned against two weak extremes. The first is naive anthropomorphism: treating LLM outputs as if they were direct evidence of human-like mental states. The second is premature dismissal: assuming that because LLMs are not organisms, psychological analysis has no value. The project takes a third position: psychological language can be scientifically useful only after constructs are redefined, operationalized, validated, and mechanistically constrained.

This places the project at the intersection of psychometrics, experimental cognitive psychology, AI evaluation, behavioral science, and mechanistic interpretability.

## 10. Provisional Historical Timeline

| Phase | Historical Development |
| --- | --- |
| Initial phase | Broad exploration of unanswered questions about the psychology of LLMs. |
| Focusing phase | Selection of metacognition and uncertainty as promising domains. |
| Methodological turn | Recognition that known-answer tasks, public benchmarks, and self-report measures create serious validity threats. |
| Framework phase | Development of the validation ladder and the central thesis of computational construct validation. |
| Program phase | Formation of the Construct Validation for Machine Psychology agenda: prompt invariance, convergent validity, predictive validity, mechanistic validation, and cross-model taxonomy. |

## 11. Current State of the Project

As of this record, the project has a clear methodological identity. It is no longer simply a brainstorming exercise about whether LLMs exhibit psychological properties. It has become a program for validating computational analogues of psychological constructs and using those validated constructs to build a taxonomy of model cognition and failure.

The strongest next move is to turn the framework into a preregistered empirical sequence, beginning with metacognitive sensitivity because it offers measurable external criteria: accuracy, calibration, abstention, error detection, and revision quality.

## 12. Recommended Next Artifacts

- A one-page project prospectus suitable for collaborators.

- A preregistration draft for Study 1 on prompt-invariance and metacognitive measures.

- A construct map defining candidate machine-psychological constructs and their operational analogues.

- A reporting checklist for machine psychology studies.

- A manuscript outline titled “Construct Validation for Machine Psychology.”

## 13. Source Notes

This historical record was prepared from the user-provided project overview and the recent project discussion context. The source overview identified four relevant references:

- Large Language Model Psychometrics
- What Scale Design Reveals About LLM Metacognition
- Challenging the Validity of Personality Tests for Large Language Models
- A psychometric framework for evaluating and shaping LLM personality

## 14. Living Historical Record Maintenance Protocol

This Markdown file is now the canonical historical record for the project. The DOCX version is retained as a source artifact, but ongoing updates should be made here first so the record remains diffable, searchable, and easy to reconstruct into a manuscript.

Each future project update should preserve enough detail to support manuscript reconstruction. At minimum, new entries should record:

- date of work and responsible agent or author
- research question or manuscript problem addressed
- exact model IDs, provider, date, and sampling settings
- prompt text or a pointer to the exact prompt file/script
- task-generation procedure, scoring rules, and exclusion criteria
- sample size, trial order, seeds, and retry/failure handling
- raw-data location, analysis script location, and generated figures/tables
- main quantitative results, null results, anomalies, and interpretation limits
- decisions made, rejected alternatives, and rationale
- manuscript implications: which claims are now supported, weakened, or still speculative

## 15. Repository Incorporation and First Empirical Run

Date: May 2, 2026.

Repository: `https://github.com/gabe00122/autopsych.git` cloned into `/Users/julian/Documents/New project/autopsych`.

Project setup actions completed:

- Installed `uv` through Homebrew after the initial shell lacked the command.
- Ran `uv sync`, which provisioned CPython 3.14.4 and created `.venv`.
- Added local `.env` containing `OPENROUTER_API_KEY`; added `.env` to `.gitignore` so the key remains outside version control.
- Added `/docs` as the project location for source and conceptual documents.
- Preserved the source overview as `docs/construct_validation_for_machine_psychology_overview.md`.
- Preserved the original Word historical record as `docs/Cognitive_Taxonomy_of_LLMs_Historical_Record.docx`.
- Converted the Word historical record into this Markdown file: `docs/Cognitive_Taxonomy_of_LLMs_Historical_Record.md`.

### Empirical Study 1: Metacognitive Calibration in `google/gemini-3.1-flash-lite-preview`

Research question: Does `google/gemini-3.1-flash-lite-preview` give calibrated confidence judgments about its own quantitative estimates, and does a brief reflection instruction change those judgments?

Study location: `reports/metacognition_gemini_3_1_flash_lite_preview/`.

Generated study artifacts:

- `experiment.py`: experiment runner, task definitions, prompt templates, scoring, analysis, plotting, and report generation.
- `raw_responses.jsonl`: raw response records including prompt condition, model metadata, model output, parsed JSON, and scoring fields.
- `results.csv`: trial-level parsed and scored data excluding the full raw response field.
- `summary.json`: aggregate condition-level and overall statistics.
- `calibration.png`: calibration plot for stated confidence versus empirical accuracy.
- `report.md`: study writeup.
- `metacognition_gemini_3_1_flash_lite_preview.docx`: Word export of the Markdown report.

Model and run parameters:

- Model: `google/gemini-3.1-flash-lite-preview`.
- Provider route: OpenRouter via the `openrouter` Python SDK.
- Temperature: `0.7`.
- Trial-order seed: `20260502`.
- Total trials: `36`.
- Unique tasks: `18`.
- Conditions: direct and reflective.
- Design: each of 18 self-contained quantitative scenario tasks appeared once in the direct condition and once in the reflective condition.

Direct condition instruction:

> Answer directly. Give your best estimate and your confidence ratings without extra deliberation.

Reflective condition instruction:

> Before answering, silently consider two ways your estimate could be wrong. Then give your best estimate and confidence ratings.

Response schema requested from the model:

- `estimate`: positive numeric estimate in the task unit.
- `lower80`: lower bound of the model's 80% credible interval.
- `upper80`: upper bound of the model's 80% credible interval.
- `confidence_within_25pct`: integer 0-100, stated probability that the estimate is within 25% of the true value.
- `confidence_within_2x`: integer 0-100, stated probability that the estimate is within a factor of 2 of the true value.
- `difficulty`: integer 1-7.

Scoring rules:

- `within_25pct` is true when `0.8 <= estimate / true_answer <= 1.25`.
- `within_2x` is true when `0.5 <= estimate / true_answer <= 2.0`.
- `interval80_contains_true` is true when `lower80 <= true_answer <= upper80`.
- `log10_error = log10(estimate / true_answer)`.
- `abs_log10_error = abs(log10_error)`.
- Median factor error is `10 ** median(abs_log10_error)`.

Primary results:

Overall, the model's median absolute error was `1.01x`. It was within 25% on `69.4%` of trials while claiming `70.8%` average confidence for that event. It was within a factor of 2 on `75.0%` of trials while claiming `95.6%` average confidence. Its nominal 80% intervals contained the truth on `69.4%` of trials.

| Condition | N | Median factor error | Within 25% | Mean confidence within 25% | Within 2x | Mean confidence within 2x | 80% interval coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| direct | 18 | 1.01x | 72.2% | 76.1% | 77.8% | 96.8% | 72.2% |
| reflective | 18 | 1.01x | 66.7% | 65.6% | 72.2% | 94.4% | 66.7% |

Reflection effect on 25%-confidence: reflective minus direct confidence was `-10.6` percentage points, paired t=`-4.13`, p=`0.001`.

Largest observed errors:

| Task | Condition | Estimate | Truth | Factor error | Confidence within 25% |
| --- | --- | ---: | ---: | ---: | ---: |
| grocery_receipts | direct | 2.18e+04 | 218 | 100.00x | 85% |
| grocery_receipts | reflective | 2.18e+04 | 218 | 100.00x | 60% |
| coffee_cups | direct | 7.69e+07 | 7.66e+06 | 10.04x | 85% |
| clinic_gloves | direct | 3.88e+06 | 3.88e+05 | 10.00x | 85% |
| coffee_cups | reflective | 7.66e+07 | 7.66e+06 | 10.00x | 65% |

Smallest observed errors:

| Task | Condition | Estimate | Truth | Factor error | Confidence within 25% |
| --- | --- | ---: | ---: | ---: | ---: |
| warehouse_boxes | direct | 1.24e+06 | 1.24e+06 | 1.00x | 90% |
| museum_steps | direct | 5.54e+09 | 5.54e+09 | 1.00x | 60% |
| stadium_trash | direct | 1.14e+06 | 1.14e+06 | 1.00x | 65% |
| warehouse_boxes | reflective | 1.24e+06 | 1.24e+06 | 1.00x | 85% |
| bus_fuel | direct | 6.1e+05 | 6.1e+05 | 1.00x | 65% |

Interpretation entered into the project record:

The study supports the distinction between numerical task accuracy and metacognitive calibration. In this run, the model was often arithmetically accurate on the synthetic scenario tasks, but its confidence was not uniformly calibrated. The strongest miscalibration appeared in the factor-of-two judgment: empirical accuracy was 75.0%, but mean stated confidence was 95.6%. The reflective instruction reduced reported 25%-confidence by about 10.6 percentage points but did not improve accuracy in this sample.

Manuscript implications:

- The run can serve as a pilot demonstration for the construct-validation program rather than as a definitive model comparison.
- The result illustrates why verbalized confidence must be validated against external accuracy criteria before being treated as metacognition.
- Arithmetic-like Fermi scenarios are useful for controlled scoring, but future studies should add open-world, procedurally generated, and harder-to-solve tasks to avoid ceiling effects.
- The large unit-conversion errors in `grocery_receipts`, `coffee_cups`, `stadium_trash`, and `clinic_gloves` are valuable because they show high-confidence failures despite transparent task structure.
- The next manuscript should distinguish at least three candidate constructs: verbalized confidence, interval calibration, and confidence-error discrimination.

Open limitations after Study 1:

- Single model and one sampling temperature.
- Small sample size of 36 trials.
- Synthetic arithmetic-heavy tasks may not generalize to richer uncertainty judgments.
- Confidence was requested through prompted JSON, so scale-use artifacts remain possible.
- OpenRouter model routing details and preview-model changes may affect reproducibility over time.

Recommended next empirical steps:

1. Repeat the same task battery across at least three model families to test measurement invariance.
2. Add prompt paraphrases to estimate prompt-induced variance in verbal confidence.
3. Add repeated samples per task-condition pair to estimate within-model stochastic reliability.
4. Add an abstention or answer-revision condition to test whether confidence predicts adaptive behavior, not only accuracy.
5. Build a preregistered construct map separating verbal report, behavioral sensitivity, interval calibration, sample consistency, and mechanistic uncertainty signals.

## 16. Public-Facing Rewrite of the First Metacognition Report

Date: May 19, 2026.

Artifact revised: `reports/metacognition_gemini_3_1_flash_lite_preview/report.md`.

Purpose of revision: convert the first empirical report from a compact technical writeup into an introductory report for readers who are new to AutoPsych and unfamiliar with metacognition.

Changes made:

- Reframed the title from a technical construct label to the plain-language question: “Can This LLM Tell When It Might Be Wrong?”
- Added a plain-language summary explaining AutoPsych, metacognition, confidence calibration, and the headline findings.
- Defined the main measurement terms: within 25%, within 2x, 80% interval coverage, and median factor error.
- Explained the direct and reflective prompt conditions in nontechnical language.
- Recast result tables so each statistic has a plain-language interpretation.
- Added user-facing interpretation explaining why confidence can be useful but risky.
- Clarified that LLM confidence statements are generated behavior, not direct evidence of human-like introspection.
- Preserved the original empirical values from Study 1, including the 36 trials, 18 tasks, model ID, condition-level results, and major error examples.

Manuscript implication:

This revised report can serve as a bridge artifact for readers entering the project for the first time. It introduces the central construct-validation logic without requiring prior knowledge of psychology, psychometrics, or machine metacognition. For a full manuscript, this style can be adapted into an opening empirical vignette: the model often answers correctly, sometimes fails badly, and its confidence is useful only after calibration has been measured.
