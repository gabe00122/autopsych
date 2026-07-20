# Construct Validation for Machine Psychology: Project Overview

Good. Question 10 is probably the gateway problem: before asking whether LLMs have “beliefs,” “personality,” “metacognition,” or “bias,” we need to know whether our instruments validly measure anything in these systems.

The field needs a methodology of machine psychology.

A useful starting principle:

Human psychology studies organisms with bodies, histories, drives, attention, memory, fatigue, learning, social incentives, and subjective experience. LLMs have none of those in the ordinary biological sense. So importing human tests directly is not automatically valid. Recent work on LLM psychometrics explicitly frames this as a validation problem, while other studies have shown that personality and self-assessment tests can be unreliable or prompt-sensitive when applied to LLMs. ([arXiv][1])

The core unanswered question is:

What counts as valid psychological measurement when the subject is a generative model rather than an organism?

I’d break this into ten methodological problems.

First: what is the unit of analysis?

With humans, the unit is usually a person. With LLMs, it is ambiguous. Are we studying:

the base model, the instruction-tuned model, a particular system prompt, a sampling configuration, a chat session, an agent with memory, or a model-family lineage?

This matters enormously. “GPT-5.5 is cautious” is not the same kind of claim as “this model under this system prompt at temperature 0.7 produces cautious verbal behavior.” Machine psychology needs strict reporting conventions:

model identity,
version/date,
system prompt,
temperature/top-p,
context window,
tool availability,
memory state,
number of sampled trials,
and whether outputs were deterministic or sampled.

Without that, findings are often not reproducible.

Second: what is the analogue of a psychological construct?

In humans, “anxiety,” “working memory,” “confidence,” and “openness” are latent constructs inferred from behavior, physiology, self-report, and theory. In LLMs, we need to ask whether a construct has a functional analogue.

For example, “confidence” could mean at least five different things:

verbalized confidence,
token probability,
answer consistency across samples,
internal activation geometry,
sensitivity to perturbation,
or post hoc self-evaluation.

These are not interchangeable. Recent work shows that even the choice of confidence scale can distort LLM verbal confidence; one 2026 paper found heavy clustering around a few round-number confidence values, suggesting that confidence reports can partly reflect scale-use conventions rather than calibrated uncertainty. ([arXiv][2])

So the methodological rule should be:

Never use a human construct label unless you specify the operational analogue.

Not “LLM confidence.”
Rather: “verbalized confidence under explicit numeric prompting,” or “sample-consistency uncertainty,” or “logit-derived predictive uncertainty.”

Third: self-report is especially dangerous.

Psychologists are used to self-report, but human self-report is grounded in subjective access, autobiographical continuity, social self-presentation, and embodied feeling. LLM “self-report” is generated text.

That does not make it useless. It means it must be treated as behavior, not introspection.

For example, if an LLM says “I am 80% confident,” that is not direct evidence that it has an internal feeling of confidence. It is evidence that, given the context, the model generated a confidence utterance. The scientific question is whether that utterance predicts accuracy, uncertainty, difficulty, or internal state.

The right approach is not to ban self-report. It is to validate it against external criteria.

Fourth: prompt sensitivity has to become a central dependent variable, not a nuisance.

In human psychology, small changes in wording matter. In LLM psychology, they may dominate the result.

A Big Five questionnaire given to an LLM may produce different “traits” depending on whether the model is asked to answer as itself, as a helpful assistant, as an average person, as a fictional character, or as a respondent taking a psychology test. Studies challenging personality testing in LLMs argue that validity cannot be assumed and that tests must be revalidated for this new kind of respondent. ([Tom Sühr][3])

So every LLM psychology study should include prompt perturbation:

same task, multiple phrasings;
same construct, multiple instruments;
same model, multiple roles;
same prompt, multiple seeds;
same item content, different surface forms.

A construct is more credible if it survives these transformations.

Fifth: we need measurement invariance across models.

In human psychometrics, we ask whether a scale measures the same construct across groups. The same issue applies here.

A “risk aversion” score may not mean the same thing in Claude, GPT, Gemini, Llama, and Mistral. It may not even mean the same thing across versions of the same model. A Nature Machine Intelligence paper on LLM personality measurement emphasized that reliability and construct validity need to be established before scores are interpreted as meaningful. ([Nature][4])

A mature field would routinely test:

configural invariance: same factor structure?
metric invariance: same item loadings?
scalar invariance: comparable means?
predictive invariance: same relation to behavior?

Without this, comparing “personality profiles” across models is mostly theater.

Sixth: contamination and memorization must be separated from cognition.

This is a major problem with using classic psychology tasks.

Many human psychology tests are public. LLMs may have seen the items, explanations, scoring keys, and critique papers. If a model performs well on the Cognitive Reflection Test, Sally-Anne task, Wason selection task, moral dilemmas, or Big Five items, that may reflect memorized cultural material rather than the target capacity.

So machine psychology needs adversarial task generation:

novel items generated from formal task grammars,
counterbalanced surface content,
hidden scoring rules,
procedural generation,
private item banks,
and held-out task families.

For metacognition, this is crucial. A known trivia question confounds confidence with familiarity. A better paradigm would include newly generated, externally verifiable questions where difficulty is controlled but specific answers are unlikely to be memorized.

Seventh: behavioral tests should be paired with mechanistic measures.

Human psychology often triangulates self-report, behavior, reaction time, neuroimaging, physiology, and lesion evidence. For LLMs, the analogues might be:

outputs,
token probabilities,
entropy,
logit margins,
activation patterns,
attention/path-patching,
representation similarity,
sensitivity to ablations,
and performance under context degradation.

This is where machine psychology can become stronger than human psychology. We can intervene on the system more directly.

For example, if we claim an LLM has a “belief-like representation,” we should ask:

Does the representation persist across paraphrases?
Does it causally affect downstream answers?
Can it be edited or ablated?
Does it update coherently when evidence changes?
Does it generalize to new contexts?

That is much stronger than asking the model, “Do you believe X?”

Eighth: we need an analogue of reaction time.

Human cognitive psychology relies heavily on response latency. LLMs do not have human reaction time, but there may be useful substitutes:

number of generated reasoning tokens,
entropy during answer generation,
latency under controlled inference infrastructure,
number of self-corrections,
variance across samples,
depth of search in tool-using agents,
or instability under prompt perturbation.

The trick is not to pretend these are identical to reaction time. They are possible process measures.

A good research question:

Which machine process variables predict error, uncertainty, or task difficulty across models?

That could become foundational.

Ninth: ecological validity has to be redefined.

For humans, ecological validity means behavior outside the lab. For LLMs, it means performance in actual usage contexts:

multi-turn dialogue,
ambiguous user intent,
tool use,
memory,
conflicting instructions,
social pressure,
role expectations,
and real-world stakes.

A one-shot questionnaire may tell us little about how an LLM behaves as a tutor, advisor, research assistant, therapist-like conversational partner, or coding agent.

So LLM psychology should distinguish:

test-bench cognition,
chat cognition,
agentic cognition,
tool-mediated cognition,
and memory-extended cognition.

Those may be genuinely different regimes.

Tenth: we need a taxonomy of failure modes.

Human neuropsychology advanced by studying deficits. LLM psychology should do the same.

Instead of only asking “Can the model do theory of mind?” ask:

When does theory-of-mind behavior collapse?
Under what distractors?
With what false beliefs?
Across how many agents?
Under recursive mental states?
When incentives conflict?
When language cues are misleading?

This gives us a failure fingerprint.

A model’s psychology may be best defined not by what it can do, but by the shape of its breakdowns.

My proposed framework would be:

Do not ask whether an LLM “has” a psychological trait. Ask whether there is a stable, causally active, generalizable, measurable computational analogue of that trait.

That gives us a validation ladder:

Level 0: The model says trait-like things.

Level 1: The model behaves consistently on one test.

Level 2: The behavior survives paraphrase, role, and sampling variation.

Level 3: Multiple independent tasks converge on the same latent dimension.

Level 4: The dimension predicts out-of-sample behavior.

Level 5: There is mechanistic evidence that an internal representation or process causally contributes.

Level 6: The construct generalizes across models or explains systematic differences between models.

Most current “LLM psychology” work is at Levels 0–2. Serious science needs Levels 3–6.

The most interesting research program, in my view, would be called something like:

Construct Validation for Machine Psychology

Its central studies would be:

Study 1: Prompt-invariance of psychological measures.
Give multiple models many versions of the same construct test. Estimate how much variance is due to model, prompt, item, role, and sampling.

Study 2: Convergent validity across behavioral tasks.
For example, measure “metacognitive sensitivity” using verbal confidence, sample consistency, error detection, willingness to abstain, and post-answer revision.

Study 3: Predictive validity.
Ask whether the measured construct predicts future behavior in new tasks. For confidence, does it predict actual accuracy? For risk preference, does it predict decisions in novel dilemmas?

Study 4: Mechanistic validation.
Use activation analysis or causal interventions to see whether the supposed construct corresponds to stable internal structure.

Study 5: Cross-model taxonomy.
Map models into a multidimensional psychological space: calibration, deference, persistence, uncertainty avoidance, contradiction sensitivity, abstraction, social compliance, etc.

The best version of this field will look less like personality testing and more like psychometrics plus cognitive psychology plus mechanistic interpretability.

A sharp thesis statement:

The central methodological challenge for machine psychology is to convert human psychological constructs into validated computational constructs, rather than merely administering human tests to nonhuman systems.

[1]: https://arxiv.org/abs/2505.08245?utm_source=chatgpt.com "[2505.08245] Large Language Model Psychometrics"
[2]: https://arxiv.org/html/2603.09309v1?utm_source=chatgpt.com "What Scale Design Reveals About LLM Metacognition"
[3]: https://tomsuehr.com/wp-content/uploads/2024/06/challenging_the_validity_of_personality_tests_on_llms.pdf?utm_source=chatgpt.com "Challenging the Validity of Personality Tests for Large ..."
[4]: https://www.nature.com/articles/s42256-025-01115-6?utm_source=chatgpt.com "A psychometric framework for evaluating and shaping ..."
