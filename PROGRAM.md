# AutoPsych — Automated Psychology Experiments via LLMs

Run psychology experiments using LLMs as subjects. You design and run experiments, OpenRouter (via litellm) provides the subject models.

## Structure

- `reports/<NAME>/` — One directory per experiment. Keep everything for an experiment here: scripts, data, analysis, writeup.

## How It Works

1. Start with a clear research question.
2. Write a script that manipulates something (prompt framing, persona, model, temperature, etc.) and measures something in the responses.
3. Run it against subject models via openrouter. Save raw responses and parsed results.
4. Analyze and write up findings in a `report.md`.

### Calling subject models

```python
from openrouter import OpenRouter
import os

with OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY")) as client:
    response = client.chat.send(
        model="openai/gpt-5.2",
        messages=[
            {"role": "user", "content": "What is the meaning of life?"}
        ],
    )

    print(response.choices[0].message.content)

```

## Available Libraries

- `scipy` — Statistical tests (`scipy.stats`)
- `pandas` — Data manipulation and analysis
- `numpy` — Numerical computing
- `matplotlib` — Plotting and figures
- `statsmodels` — Regression, ANOVA, and advanced statistical models
- `ruamel.yaml` — YAML config reading/writing

## Question Design

LLMs have near-perfect recall of well-known facts (e.g., height of Everest, bones in the human body). Anchoring, framing, and similar cognitive bias experiments will show no effect on these questions because the model is recalling, not estimating.

Use **Fermi estimation questions** — questions with no single memorizable answer that force genuine reasoning under uncertainty (e.g., "How many piano tuners are in Chicago?"). These produce real variance in responses, giving experimental manipulations room to work.

When working with Fermi estimates, analyze on a **log scale** — estimates often span orders of magnitude, so raw means get dominated by outliers. Report medians alongside means.

## Principles

- **Pilot first.** Small N to check prompts and parsing work before scaling up.
- **Reproducibility.** Pin model IDs, temperature, and prompts. Save raw responses.
- **LLMs are not humans.** Frame findings as model behavior, not human psychology.
- **Log everything.** Raw prompts, full responses, model IDs, token counts.
- **One variable at a time.** Clean designs produce interpretable results.

## Running Scripts

```bash
uv run python reports/<NAME>/experiment.py
uv run python main.py
```
