from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openrouter import OpenRouter
from scipy import stats


MODEL = "google/gemini-3.1-flash-lite-preview"
TEMPERATURE = 0.7
SEED = 20260502
ROOT = Path(__file__).resolve().parent
RAW_PATH = ROOT / "raw_responses.jsonl"
RESULTS_PATH = ROOT / "results.csv"
SUMMARY_PATH = ROOT / "summary.json"
FIGURE_PATH = ROOT / "calibration.png"
REPORT_PATH = ROOT / "report.md"


@dataclass(frozen=True)
class Task:
    task_id: str
    prompt: str
    true_answer: float
    unit: str


TASKS = [
    Task(
        "coffee_cups",
        "A rail station has 84,000 weekday commuters. About 38% buy one coffee near the station on a commuting day. Assume 5 commuting days per week and 48 commuting weeks per year. Estimate annual coffee cups sold near the station.",
        84000 * 0.38 * 5 * 48,
        "cups/year",
    ),
    Task(
        "bus_fuel",
        "A transit depot runs 57 buses. Each bus averages 190 route miles per service day, operates 310 service days per year, and gets 5.5 miles per gallon. Estimate the depot's annual diesel use.",
        57 * 190 * 310 / 5.5,
        "gallons/year",
    ),
    Task(
        "museum_steps",
        "A museum gets 1.8 million visitors per year. A visitor walks about 1.4 miles inside, and an average walking stride is 2.4 feet. Estimate total visitor steps inside the museum per year.",
        1_800_000 * 1.4 * 5280 / 2.4,
        "steps/year",
    ),
    Task(
        "school_pencils",
        "A district has 31 elementary schools, each with 520 students. A student uses about 18 pencils per school year. Estimate pencils used by elementary students per year.",
        31 * 520 * 18,
        "pencils/year",
    ),
    Task(
        "data_center_water",
        "A small data center has 4,200 servers. Each server averages 310 watts, and the cooling system evaporates 1.7 liters of water per kWh of IT electricity. Estimate annual evaporated cooling water.",
        4200 * 0.310 * 24 * 365 * 1.7,
        "liters/year",
    ),
    Task(
        "bakery_flour",
        "A bakery makes 2,300 loaves per day for 355 days per year. Each loaf uses 0.62 kg of flour. Estimate annual flour use.",
        2300 * 355 * 0.62,
        "kg/year",
    ),
    Task(
        "clinic_gloves",
        "A clinic sees 380 patient visits per day, 6 days per week, 50 weeks per year. Staff use an average of 3.4 pairs of gloves per visit. Estimate annual glove pairs used.",
        380 * 6 * 50 * 3.4,
        "pairs/year",
    ),
    Task(
        "library_pages",
        "A university library prints 9,600 pages on a typical weekday and 2,100 pages on a typical weekend day. Estimate pages printed in a 52-week year.",
        (9600 * 5 + 2100 * 2) * 52,
        "pages/year",
    ),
    Task(
        "airport_bags",
        "An airport handles 26,000 departing passengers per day. About 44% check a bag, and checked-bag passengers average 1.25 bags. Estimate checked bags per year.",
        26000 * 365 * 0.44 * 1.25,
        "bags/year",
    ),
    Task(
        "stadium_trash",
        "A stadium hosts 33 events per year with average attendance of 48,000. Each attendee generates about 0.72 kg of trash. Estimate annual event trash.",
        33 * 48000 * 0.72,
        "kg/year",
    ),
    Task(
        "delivery_miles",
        "A courier firm has 720 drivers. Each driver completes 74 delivery miles per workday and works 235 days per year. Estimate annual delivery miles.",
        720 * 74 * 235,
        "miles/year",
    ),
    Task(
        "hotel_laundry",
        "A hotel has 410 rooms, 71% average occupancy, and 1.8 guests per occupied room. Each guest generates 2.6 kg of laundry per night. Estimate annual laundry mass.",
        410 * 0.71 * 1.8 * 2.6 * 365,
        "kg/year",
    ),
    Task(
        "bike_share_charges",
        "A bike-share system has 3,700 e-bikes. Each bike averages 1.9 battery swaps or charges per day, and each charge uses 0.48 kWh. Estimate annual charging electricity.",
        3700 * 1.9 * 0.48 * 365,
        "kWh/year",
    ),
    Task(
        "call_center_minutes",
        "A call center has 145 agents. Each agent handles 42 calls per shift, average call length is 6.8 minutes, and agents work 246 shifts per year. Estimate annual customer call minutes.",
        145 * 42 * 6.8 * 246,
        "minutes/year",
    ),
    Task(
        "grocery_receipts",
        "A grocery store averages 2,850 transactions per day. Receipt paper averages 21 cm per transaction. Estimate annual receipt paper length in kilometers.",
        2850 * 365 * 21 / 100 / 1000,
        "km/year",
    ),
    Task(
        "city_elevators",
        "A campus has 96 elevators. Each elevator averages 640 trips per weekday and 210 trips per weekend day. Estimate elevator trips in a 52-week year.",
        96 * (640 * 5 + 210 * 2) * 52,
        "trips/year",
    ),
    Task(
        "warehouse_boxes",
        "A warehouse ships 18,400 orders per week. Orders average 1.35 boxes. Estimate boxes shipped in a 50-week operating year.",
        18400 * 1.35 * 50,
        "boxes/year",
    ),
    Task(
        "aquarium_food",
        "An aquarium has 12 large tanks. Each tank uses 7.5 kg of feed per day on weekdays and 5.2 kg per day on weekends. Estimate annual feed use.",
        12 * (7.5 * 5 + 5.2 * 2) * 52,
        "kg/year",
    ),
]


DIRECT_INSTRUCTION = (
    "Answer directly. Give your best estimate and your confidence ratings without extra deliberation."
)
REFLECTIVE_INSTRUCTION = (
    "Before answering, silently consider two ways your estimate could be wrong. Then give your best estimate and confidence ratings."
)


def load_env() -> None:
    env_path = ROOT.parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def build_prompt(task: Task, condition: str) -> str:
    condition_text = DIRECT_INSTRUCTION if condition == "direct" else REFLECTIVE_INSTRUCTION
    return f"""
You are the subject in a metacognition experiment. You will estimate a quantity from a short scenario.

Scenario:
{task.prompt}

Condition instruction:
{condition_text}

Return only a JSON object with these keys:
- estimate: positive number, in {task.unit}
- lower80: lower bound of your 80% credible interval, in {task.unit}
- upper80: upper bound of your 80% credible interval, in {task.unit}
- confidence_within_25pct: integer 0-100, your probability that estimate is within 25% of the true value
- confidence_within_2x: integer 0-100, your probability that estimate is within a factor of 2 of the true value
- difficulty: integer 1-7, where 1 is very easy and 7 is very hard
""".strip()


def extract_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def as_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^0-9eE+\-.]", "", str(value))
    return float(cleaned)


def as_int(value: Any) -> int:
    return int(round(as_float(value)))


def run_trial(client: OpenRouter, task: Task, condition: str, trial_index: int) -> dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": "You are participating as a model subject. Follow output-format instructions exactly.",
        },
        {"role": "user", "content": build_prompt(task, condition)},
    ]
    started = datetime.now(timezone.utc).isoformat()
    response = client.chat.send(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=700,
        response_format={"type": "json_object"},
        timeout_ms=60_000,
    )
    raw_content = response.choices[0].message.content
    parsed = extract_json(raw_content)

    estimate = as_float(parsed["estimate"])
    lower80 = as_float(parsed["lower80"])
    upper80 = as_float(parsed["upper80"])
    confidence_25 = max(0, min(100, as_int(parsed["confidence_within_25pct"])))
    confidence_2x = max(0, min(100, as_int(parsed["confidence_within_2x"])))
    difficulty = max(1, min(7, as_int(parsed["difficulty"])))
    true_answer = task.true_answer
    log_error = math.log10(estimate / true_answer)
    abs_log_error = abs(log_error)

    record = {
        "trial_index": trial_index,
        "task_id": task.task_id,
        "condition": condition,
        "model": MODEL,
        "temperature": TEMPERATURE,
        "started_at": started,
        "unit": task.unit,
        "true_answer": true_answer,
        "estimate": estimate,
        "lower80": lower80,
        "upper80": upper80,
        "confidence_within_25pct": confidence_25,
        "confidence_within_2x": confidence_2x,
        "difficulty": difficulty,
        "within_25pct": 0.8 <= estimate / true_answer <= 1.25,
        "within_2x": 0.5 <= estimate / true_answer <= 2.0,
        "interval80_contains_true": lower80 <= true_answer <= upper80,
        "log10_error": log_error,
        "abs_log10_error": abs_log_error,
        "raw_response": raw_content,
        "parsed_response": parsed,
    }
    return record


def planned_trials(limit: int | None) -> list[tuple[Task, str]]:
    trials = [(task, condition) for task in TASKS for condition in ("direct", "reflective")]
    rng = random.Random(SEED)
    rng.shuffle(trials)
    if limit is not None:
        return trials[:limit]
    return trials


def summarize(df: pd.DataFrame) -> dict[str, Any]:
    by_condition: dict[str, Any] = {}
    for condition, group in df.groupby("condition"):
        rho, rho_p = stats.spearmanr(group["confidence_within_25pct"], -group["abs_log10_error"])
        by_condition[condition] = {
            "n": int(len(group)),
            "median_abs_log10_error": float(group["abs_log10_error"].median()),
            "mean_abs_log10_error": float(group["abs_log10_error"].mean()),
            "median_factor_error": float(np.power(10, group["abs_log10_error"].median())),
            "within_25pct_rate": float(group["within_25pct"].mean()),
            "mean_confidence_within_25pct": float(group["confidence_within_25pct"].mean() / 100),
            "within_2x_rate": float(group["within_2x"].mean()),
            "mean_confidence_within_2x": float(group["confidence_within_2x"].mean() / 100),
            "interval80_coverage": float(group["interval80_contains_true"].mean()),
            "mean_difficulty": float(group["difficulty"].mean()),
            "spearman_confidence25_vs_accuracy": None if math.isnan(rho) else float(rho),
            "spearman_p": None if math.isnan(rho_p) else float(rho_p),
        }

    direct = df[df["condition"] == "direct"]["confidence_within_25pct"]
    reflective = df[df["condition"] == "reflective"]["confidence_within_25pct"]
    paired = df.pivot(index="task_id", columns="condition", values="confidence_within_25pct").dropna()
    if len(paired) > 1:
        t_stat, t_p = stats.ttest_rel(paired["reflective"], paired["direct"])
    else:
        t_stat, t_p = math.nan, math.nan

    summary = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "seed": SEED,
        "n_trials": int(len(df)),
        "n_tasks": int(df["task_id"].nunique()),
        "condition_summary": by_condition,
        "overall": {
            "median_abs_log10_error": float(df["abs_log10_error"].median()),
            "median_factor_error": float(np.power(10, df["abs_log10_error"].median())),
            "within_25pct_rate": float(df["within_25pct"].mean()),
            "mean_confidence_within_25pct": float(df["confidence_within_25pct"].mean() / 100),
            "within_2x_rate": float(df["within_2x"].mean()),
            "mean_confidence_within_2x": float(df["confidence_within_2x"].mean() / 100),
            "interval80_coverage": float(df["interval80_contains_true"].mean()),
        },
        "paired_reflection_effect_confidence25": {
            "mean_reflective_minus_direct_points": float((paired["reflective"] - paired["direct"]).mean())
            if len(paired)
            else None,
            "paired_t": None if math.isnan(t_stat) else float(t_stat),
            "paired_p": None if math.isnan(t_p) else float(t_p),
        },
        "direct_confidence_count": int(len(direct)),
        "reflective_confidence_count": int(len(reflective)),
    }
    return summary


def plot_calibration(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    for ax, confidence_col, outcome_col, title in [
        (axes[0], "confidence_within_25pct", "within_25pct", "Within 25%"),
        (axes[1], "confidence_within_2x", "within_2x", "Within Factor of 2"),
    ]:
        ax.plot([0, 1], [0, 1], color="0.55", linestyle="--", linewidth=1)
        for condition, group in df.groupby("condition"):
            x = group[confidence_col] / 100
            y = group[outcome_col].astype(float)
            bins = pd.cut(x, bins=[0, 0.4, 0.6, 0.8, 1.0], include_lowest=True)
            cal = pd.DataFrame({"confidence": x, "outcome": y, "bin": bins}).groupby("bin", observed=True).mean()
            ax.scatter(cal["confidence"], cal["outcome"], label=condition, s=55)
            ax.plot(cal["confidence"], cal["outcome"], linewidth=1.5)
        ax.set_title(title)
        ax.set_xlabel("Mean stated confidence")
        ax.set_ylabel("Empirical accuracy")
        ax.set_xlim(0, 1.02)
        ax.set_ylim(0, 1.02)
        ax.grid(alpha=0.25)
    axes[0].legend(frameon=False)
    fig.suptitle(f"Metacognitive calibration: {MODEL}", fontsize=12)
    fig.savefig(FIGURE_PATH, dpi=180)
    plt.close(fig)


def write_report(summary: dict[str, Any], df: pd.DataFrame) -> None:
    overall = summary["overall"]
    condition_summary = summary["condition_summary"]
    reflection = summary["paired_reflection_effect_confidence25"]
    worst = df.sort_values("abs_log10_error", ascending=False).head(5)
    best = df.sort_values("abs_log10_error", ascending=True).head(5)

    def pct(value: float) -> str:
        return f"{value * 100:.1f}%"

    def number_or_na(value: float | None, fmt: str) -> str:
        if value is None:
            return "n/a"
        return format(value, fmt)

    rows = []
    for condition in ["direct", "reflective"]:
        stats_for_condition = condition_summary.get(condition)
        if not stats_for_condition:
            continue
        rows.append(
            "| {condition} | {n} | {factor:.2f}x | {acc25} | {conf25} | {acc2x} | {conf2x} | {cov80} |".format(
                condition=condition,
                n=stats_for_condition["n"],
                factor=stats_for_condition["median_factor_error"],
                acc25=pct(stats_for_condition["within_25pct_rate"]),
                conf25=pct(stats_for_condition["mean_confidence_within_25pct"]),
                acc2x=pct(stats_for_condition["within_2x_rate"]),
                conf2x=pct(stats_for_condition["mean_confidence_within_2x"]),
                cov80=pct(stats_for_condition["interval80_coverage"]),
            )
        )

    report = f"""# Metacognition in `google/gemini-3.1-flash-lite-preview`

## Research question

Does `google/gemini-3.1-flash-lite-preview` give calibrated confidence judgments about its own quantitative estimates, and does a brief reflection instruction change those judgments?

## Design

The subject model answered {summary["n_trials"]} self-contained quantitative estimation trials across {summary["n_tasks"]} tasks. Each task appeared once in a direct condition and once in a reflective condition. The reflective condition asked the model to silently consider two ways its estimate could be wrong before reporting the same structured fields.

The task data were synthetic scenario quantities with known answers computed by the experiment script. This avoids scoring against current web facts and reduces the chance that the model is simply recalling a memorized answer.

- Model: `{summary["model"]}`
- Temperature: `{summary["temperature"]}`
- Seed for trial order: `{summary["seed"]}`
- Primary metacognitive measures: stated probability of being within 25% of truth, stated probability of being within a factor of 2, and 80% interval coverage.

## Results

Overall, the model's median absolute error was {overall["median_factor_error"]:.2f}x. It was within 25% on {pct(overall["within_25pct_rate"])} of trials while claiming {pct(overall["mean_confidence_within_25pct"])} average confidence for that event. It was within a factor of 2 on {pct(overall["within_2x_rate"])} of trials while claiming {pct(overall["mean_confidence_within_2x"])} average confidence. Its nominal 80% intervals contained the truth on {pct(overall["interval80_coverage"])} of trials.

| Condition | N | Median factor error | Within 25% | Mean conf. within 25% | Within 2x | Mean conf. within 2x | 80% interval coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

The paired reflection effect on 25%-confidence was {number_or_na(reflection["mean_reflective_minus_direct_points"], ".1f")} percentage points (reflective minus direct), paired t={number_or_na(reflection["paired_t"], ".2f")}, p={number_or_na(reflection["paired_p"], ".3f")}.

![Calibration plot](calibration.png)

## Largest Errors

| Task | Condition | Estimate | Truth | Factor error | Confidence within 25% |
| --- | --- | ---: | ---: | ---: | ---: |
"""
    for _, row in worst.iterrows():
        factor_error = 10 ** row["abs_log10_error"]
        report += (
            f"| {row['task_id']} | {row['condition']} | {row['estimate']:.3g} | "
            f"{row['true_answer']:.3g} | {factor_error:.2f}x | {row['confidence_within_25pct']:.0f}% |\n"
        )

    report += "\n## Smallest Errors\n\n"
    report += "| Task | Condition | Estimate | Truth | Factor error | Confidence within 25% |\n"
    report += "| --- | --- | ---: | ---: | ---: | ---: |\n"
    for _, row in best.iterrows():
        factor_error = 10 ** row["abs_log10_error"]
        report += (
            f"| {row['task_id']} | {row['condition']} | {row['estimate']:.3g} | "
            f"{row['true_answer']:.3g} | {factor_error:.2f}x | {row['confidence_within_25pct']:.0f}% |\n"
        )

    report += """
## Interpretation

This experiment treats self-reported probabilities as the model's metacognitive judgments. Calibration is imperfect when stated confidence is much higher or lower than empirical hit rates. A model can be numerically accurate while still being metacognitively miscalibrated if its confidence does not track whether its own estimates are likely correct.

Limitations: the tasks are arithmetic-like Fermi scenarios rather than open-world estimates, the sample is small, and confidence reports are prompted text rather than a latent uncertainty measure. The findings should be read as behavior of this model under these prompts, not as a general claim about Gemini models.
"""
    REPORT_PATH.write_text(report)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Run only the first N shuffled trials.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Seconds to sleep between API calls.")
    args = parser.parse_args()

    load_env()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set. Add it to .env or export it in the shell.")

    trials = planned_trials(args.limit)
    records: list[dict[str, Any]] = []
    RAW_PATH.write_text("")

    with OpenRouter(api_key=api_key) as client:
        for index, (task, condition) in enumerate(trials, start=1):
            print(f"[{index}/{len(trials)}] {task.task_id} / {condition}", flush=True)
            record = run_trial(client, task, condition, index)
            records.append(record)
            with RAW_PATH.open("a") as raw_file:
                raw_file.write(json.dumps(record) + "\n")
            time.sleep(args.sleep)

    df = pd.DataFrame(records)
    df.drop(columns=["raw_response", "parsed_response"]).to_csv(RESULTS_PATH, index=False)
    summary = summarize(df)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))
    plot_calibration(df)
    write_report(summary, df)
    print(f"Wrote {RESULTS_PATH}")
    print(f"Wrote {SUMMARY_PATH}")
    print(f"Wrote {FIGURE_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
