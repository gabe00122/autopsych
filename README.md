# AutoPsych

An experiment in using LLMs as **experiment orchestrators** — having one LLM (Claude Code/Codex, acting as the "scientist") design, run, and analyze psychology-style experiments on other LLMs (the "subjects", routed through OpenRouter).

The interesting question isn't *"do LLMs show cognitive biases?"* — it's *"can an LLM run the whole scientific loop competently?"* Hypothesis, design, pilot, scale, analyze, write up. Each experiment in `reports/` is a test of that.

## How it works

The scientist agent (Claude Code) reads [PROGRAM.md](PROGRAM.md) — its operating manual covering experiment design, question selection, statistical conventions, and reproducibility rules. It then:

1. Picks a research question.
2. Writes a script under `reports/<name>/` that manipulates one variable and measures responses.
3. Runs it against subject models via OpenRouter, saving raw responses.
4. Analyzes results and writes `reports/<name>/report.md`.

Each `reports/<name>/` directory is self-contained: code, data, analysis, writeup.

## Setup

Requires [`uv`](https://docs.astral.sh/uv/) and an [OpenRouter](https://openrouter.ai/) API key.

```bash
uv sync
export OPENROUTER_API_KEY=sk-or-...
```

## Running an experiment

```bash
uv run python reports/<name>/experiment.py
```

## Layout

- `PROGRAM.md` — the scientist agent's operating manual.
- `reports/<name>/` — one directory per experiment (script, raw data, analysis, writeup).
