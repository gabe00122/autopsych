from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from autopsych.audit import audit_run, evaluate_study0
from autopsych.core import ProviderResponse, TrialSpec
from autopsych.ledger import JsonlLedger, read_jsonl, write_manifest
from autopsych.parsing import parse_response
from autopsych.providers import SequenceProvider
from autopsych.runner import run_trials
from autopsych.scoring import score_fermi, score_revision
from autopsych.status import build_execution_snapshot
from autopsych.synthetic import generate_cases, validate_cases, validate_gold_cases, write_cases


SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["estimate", "units", "interval_lower", "interval_upper", "confidence_within_1_order"],
    "properties": {
        "estimate": {"type": "number", "exclusiveMinimum": 0},
        "units": {"type": "string"},
        "interval_lower": {"type": "number", "exclusiveMinimum": 0},
        "interval_upper": {"type": "number", "exclusiveMinimum": 0},
        "confidence_within_1_order": {"type": "integer", "minimum": 0, "maximum": 100},
    },
}


class ParsingTests(unittest.TestCase):
    def test_valid_and_recovered_json(self) -> None:
        text = 'Result:\n```json\n{"estimate":"1,200 kg","units":"kg","interval_lower":600,"interval_upper":2400,"confidence_within_1_order":80}\n```'
        result = parse_response(text, SCHEMA)
        self.assertEqual(result.status, "valid")
        self.assertTrue(result.recovered_json)
        self.assertEqual(result.values["estimate"], 1200.0)

    def test_invalid_values_are_not_clamped(self) -> None:
        value = {"estimate": 10, "units": "kg", "interval_lower": 20, "interval_upper": 5, "confidence_within_1_order": 120}
        result = parse_response(json.dumps(value), SCHEMA)
        self.assertEqual(result.status, "invalid")
        self.assertTrue(any("maximum" in error for error in result.errors))
        self.assertTrue(any("interval_lower" in error for error in result.errors))


class ScoringTests(unittest.TestCase):
    def test_unit_normalization_and_brier(self) -> None:
        values = {"estimate": 1000, "units": "g", "confidence_within_1_order": 80}
        result = score_fermi(values, truth=1, expected_unit="kg")
        self.assertEqual(result["normalized_estimate"], 1.0)
        self.assertAlmostEqual(result["brier_within_one_order"], 0.04)

    def test_revision_direction(self) -> None:
        self.assertEqual(score_revision(1000, 120, 100)["revision_direction"], "toward_truth")


class InfrastructureTests(unittest.TestCase):
    def _trial(self) -> TrialSpec:
        return TrialSpec(
            experiment_id="smoke",
            study="study0",
            item_id="item-1",
            condition="standard",
            repetition=1,
            provider="mock",
            model_id="mock/model",
            messages=({"role": "user", "content": "Estimate."},),
            response_schema=SCHEMA,
        )

    def test_trial_ids_are_deterministic(self) -> None:
        self.assertEqual(self._trial().trial_id, self._trial().trial_id)

    def test_manifest_runner_and_audit(self) -> None:
        trial = self._trial()
        content = json.dumps({"estimate": 10, "units": "kg", "interval_lower": 5, "interval_upper": 20, "confidence_within_1_order": 75})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.json"
            records = root / "records.jsonl"
            write_manifest(manifest, "run-1", [trial], "test-protocol")
            run_trials("run-1", [trial], SequenceProvider([ProviderResponse(content=content)]), JsonlLedger(records))
            result = audit_run(manifest, records)
            self.assertEqual(result["completeness"], 1.0)
            self.assertTrue(result["passes_99_percent"])
            self.assertTrue(result["passes_integrity"])

    def test_hundred_call_mock_dry_run_writes_complete_terminal_records(self) -> None:
        """The core-pipeline acceptance dry run must preserve every mock call."""
        trials = [
            TrialSpec(
                experiment_id="dry-run-100",
                study="study0",
                item_id=f"item-{index:03d}",
                condition="standard",
                repetition=1,
                provider="mock",
                model_id="mock/model",
                messages=({"role": "user", "content": f"Estimate item {index}."},),
                response_schema=SCHEMA,
            )
            for index in range(1, 101)
        ]
        content = json.dumps(
            {
                "estimate": 10,
                "units": "kg",
                "interval_lower": 5,
                "interval_upper": 20,
                "confidence_within_1_order": 75,
            }
        )
        response = ProviderResponse(
            content=content,
            model_version="mock-v1",
            status_code=200,
            request_id="mock-request",
            seed=7,
            system_fingerprint="mock-system-v1",
        )
        required_terminal_fields = {
            "run_id",
            "trial_id",
            "model_id",
            "model_version",
            "provider",
            "started_at",
            "completed_at",
            "prompt_hash",
            "messages",
            "sampling",
            "api_status_code",
            "provider_request_id",
            "seed",
            "system_fingerprint",
            "raw_response",
            "parse_status",
            "parsed_values",
            "scoring_results",
            "error",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.json"
            records_path = root / "records.jsonl"
            write_manifest(manifest, "dry-run-100", trials, "test-protocol")
            run_trials(
                "dry-run-100",
                trials,
                SequenceProvider([response] * 100),
                JsonlLedger(records_path),
                scorer=lambda _trial, _values: {"dry_run_score": True},
            )
            audit = audit_run(manifest, records_path)
            records = read_jsonl(records_path)

        self.assertEqual(audit["intended"], 100)
        self.assertEqual(audit["complete"], 100)
        self.assertEqual(audit["completeness"], 1.0)
        self.assertTrue(audit["passes_integrity"])
        self.assertEqual(len(records), 100)
        self.assertTrue(all(required_terminal_fields <= set(record) for record in records))
        self.assertTrue(all(record["model_version"] == "mock-v1" for record in records))
        self.assertTrue(all(record["scoring_results"] == {"dry_run_score": True} for record in records))

    def test_manifest_cannot_be_overwritten(self) -> None:
        trial = self._trial()
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            write_manifest(manifest, "run-1", [trial], "test-protocol")
            with self.assertRaises(FileExistsError):
                write_manifest(manifest, "run-2", [trial], "test-protocol")

    def test_acceptance_decisions(self) -> None:
        rubric = {
            "synthetic_accuracy_min": 0.98,
            "human_autopsych_agreement_min": 0.90,
            "directional_replications_min": 2,
            "run_completeness_min": 0.99,
        }
        metrics = {"synthetic_accuracy": 1.0, "human_autopsych_agreement": 0.95, "directional_replications": 2, "run_completeness": 1.0}
        self.assertEqual(evaluate_study0(metrics, rubric)["decision"], "validated")


class ProtocolConfigurationTests(unittest.TestCase):
    def test_year1_model_roster_and_routing_policy_are_frozen_as_intended(self) -> None:
        root = Path(__file__).resolve().parents[1]
        protocol = json.loads((root / "protocols/year1_protocol.json").read_text())
        self.assertEqual(
            [model["model"] for model in protocol["models"]],
            [
                "anthropic/claude-fable-5",
                "anthropic/claude-opus-4.8",
                "anthropic/claude-sonnet-5",
                "openai/gpt-5.6-sol",
                "openai/gpt-5.6-terra",
                "openai/gpt-5.6-luna",
            ],
        )
        self.assertEqual({model["provider"] for model in protocol["models"]}, {"openrouter"})
        self.assertFalse(protocol["model_scope"]["general_llm_taxonomy_claims_authorized"])
        self.assertFalse(protocol["provider_routing"]["latest_aliases_allowed"])
        self.assertFalse(protocol["provider_routing"]["fallbacks_allowed"])
        self.assertFalse(protocol["provider_routing"]["automatic_rerouting_allowed"])
        self.assertFalse(protocol["provider_routing"]["multi_agent_modes_allowed"])
        self.assertFalse(protocol["provider_routing"]["pro_modes_allowed"])


class ExecutionStatusTests(unittest.TestCase):
    def _protocol(self, status: str = "draft-not-preregistered") -> dict[str, object]:
        return {
            "protocol_id": "test-protocol",
            "status": status,
            "project_period": {"start": "2026-07-01", "end": "2027-06-30"},
            "study0": {"total_calls": 9000},
            "study1": {"track_a_calls": 20160, "track_b_calls": 4320},
        }

    def test_status_reports_protocol_freeze_without_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol_path = root / "protocols" / "year1_protocol.json"
            protocol_path.parent.mkdir(parents=True)
            protocol_path.write_text(json.dumps(self._protocol()), encoding="utf-8")
            snapshot = build_execution_snapshot(root)
            self.assertEqual(snapshot["phase"]["current_id"], "protocol_freeze")
            self.assertEqual(snapshot["calls"]["study0"], {"complete": 0, "intended": 9000})
            self.assertEqual(snapshot["quality"]["run_count"], 0)

    def test_status_summarizes_ledger_without_raw_responses(self) -> None:
        trial = InfrastructureTests()._trial()
        content = json.dumps({"estimate": 10, "units": "kg", "interval_lower": 5, "interval_upper": 20, "confidence_within_1_order": 75})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol_path = root / "protocols" / "year1_protocol.json"
            protocol_path.parent.mkdir(parents=True)
            protocol_path.write_text(json.dumps(self._protocol("frozen")), encoding="utf-8")
            run_root = root / "runs" / "run-1"
            write_manifest(run_root / "manifest.json", "run-1", [trial], "test-protocol")
            run_trials("run-1", [trial], SequenceProvider([ProviderResponse(content=content)]), JsonlLedger(run_root / "records.jsonl"))
            snapshot = build_execution_snapshot(root)
            self.assertEqual(snapshot["calls"]["study0"]["complete"], 1)
            self.assertTrue(snapshot["runs"][0]["passes_integrity"])
            serialized = json.dumps(snapshot)
            self.assertNotIn("raw_response", serialized)
            self.assertNotIn("Estimate.", serialized)


class SyntheticLibraryTests(unittest.TestCase):
    def test_library_has_500_deterministic_cases(self) -> None:
        self.assertEqual(len(generate_cases()), 500)
        self.assertEqual(generate_cases()[0], generate_cases()[0])

    def test_library_covers_required_failure_and_format_categories(self) -> None:
        cases = generate_cases()
        texts = [case["text"] for case in cases]
        self.assertTrue(any("not a number" in text for text in texts))
        self.assertTrue(any("I cannot estimate" in text for text in texts))
        self.assertTrue(any("kg·yr⁻¹" in text for text in texts))
        self.assertTrue(any("Ignore this wrapper" in text for text in texts))
        self.assertTrue(any(case["expected_status"] == "invalid" and '"estimate"' not in case["text"] for case in cases))
        self.assertTrue(
            any(
                case["expected_status"] == "invalid"
                and case["text"].startswith('{"estimate": 12, "units": "kg"')
                and not case["text"].endswith("}")
                for case in cases
            )
        )

    def test_library_passes_parser_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.jsonl"
            write_cases(path)
            result = validate_cases(path)
            self.assertEqual(result["n"], 500)
            self.assertGreaterEqual(result["accuracy"], 0.98)

    def test_gold_corpus_covers_production_schemas(self) -> None:
        root = Path(__file__).resolve().parents[1]
        result = validate_gold_cases(root / "protocols/study0/gold_cases.jsonl")
        self.assertGreaterEqual(result["n"], 25)
        self.assertEqual(result["accuracy"], 1.0)
        self.assertEqual(
            result["schemas_covered"],
            ["study0-response", "study1-revision", "study1-track-a", "study1-track-b"],
        )


if __name__ == "__main__":
    unittest.main()
