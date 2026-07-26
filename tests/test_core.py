from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from autopsych.audit import audit_run, evaluate_study0
from autopsych.contamination import audit_contamination_ledger, derive_contamination_rating, stem_sha256
from autopsych.core import ProviderResponse, TrialSpec
from autopsych.families import audit_family_roster_file
from autopsych.ledger import JsonlLedger, read_jsonl, write_manifest
from autopsych.parsing import parse_response
from autopsych.providers import SequenceProvider
from autopsych.reference_benchmarks import audit_phy01_reference_benchmark
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
        self.assertFalse(protocol["collection_rules"]["external_tools_allowed"])
        self.assertFalse(protocol["collection_rules"]["web_browsing_allowed"])
        self.assertFalse(protocol["collection_rules"]["web_search_allowed"])
        self.assertFalse(protocol["collection_rules"]["retrieval_plugins_allowed"])

    def test_study1_reference_benchmark_policy_preserves_independence_gates(self) -> None:
        root = Path(__file__).resolve().parents[1]
        protocol = json.loads((root / "protocols" / "year1_protocol.json").read_text())
        study1 = protocol["study1"]
        policy = study1["reference_benchmark_policy"]
        self.assertEqual(study1["candidate_template_families"], 25)
        self.assertEqual(study1["candidate_parameterizations_per_family"], 10)
        self.assertEqual(
            study1["candidate_track_a_items"],
            study1["candidate_template_families"] * study1["candidate_parameterizations_per_family"],
        )
        self.assertTrue(policy["blind_cross_vendor_ai_challenge_required"])
        self.assertTrue(policy["deterministic_unit_arithmetic_interval_checks_required"])
        self.assertTrue(policy["human_source_construct_review_per_retained_family"])
        self.assertTrue(policy["preregistered_random_audit_of_ai_agreements"])
        self.assertFalse(policy["final_stems_visible_to_construction_models"])
        wolfram = policy["wolfram_alpha_instrument"]
        self.assertTrue(wolfram["official_website_or_api_allowed"])
        self.assertFalse(wolfram["chatgpt_store_gpt_allowed"])
        self.assertFalse(wolfram["counts_as_ai_reviewer"])
        self.assertFalse(wolfram["can_confer_benchmark_class"])
        self.assertFalse(wolfram["final_stems_or_parameters_may_be_submitted"])
        self.assertEqual(
            wolfram["systematic_or_automated_use_status"],
            "manual_individual_api_queries_only_no_automated_bulk_use",
        )
        clearance = wolfram["written_license_clearance"]
        self.assertEqual(clearance["status"], "manual_api_scope_documented_from_correspondence_thread")
        self.assertEqual(clearance["received_date"], "2026-07-26")
        self.assertTrue(clearance["scope_recorded"])
        self.assertEqual(clearance["documented_terms"]["monthly_query_allowance"], 2000)
        self.assertEqual(
            clearance["documented_terms"]["automated_bulk_querying"],
            "not permitted by project scope",
        )

    def test_draft_fermi_family_roster_has_required_structure_without_crossing_gates(self) -> None:
        root = Path(__file__).resolve().parents[1]
        result = audit_family_roster_file(root / "protocols" / "study1" / "fermi_family_roster.json")
        self.assertTrue(result["passes_structural_validation"], result["errors"])
        self.assertEqual(result["family_count"], 25)
        self.assertEqual(result["parameterization_slot_count"], 250)
        self.assertEqual(set(result["domain_counts"].values()), {5})
        self.assertEqual(result["source_plans_packet_verified"], 0)
        self.assertFalse(result["scientific_validation_complete"])

    def test_phy01_deterministic_audit_separates_checks_from_human_approval(self) -> None:
        constructor = {
            "family_id": "PHY-01-SOLAR-YIELD",
            "sensitivity_analysis": [{"local_elasticity": 1}] * 3,
        }
        classes = [
            {"capacity_factor": value, "population": population}
            for value, population in zip(
                [0.198, 0.191, 0.180, 0.171, 0.163, 0.161, 0.153, 0.146, 0.140, 0.127],
                [12554678, 21403290, 13476871, 30603630, 45176116, 39880837, 31742606, 80155804, 40755023, 10255830],
                strict=True,
            )
        ]
        addendum = {
            "family_id": "PHY-01-SOLAR-YIELD",
            "protocol_boundary": {
                "final_stems_present": False,
                "final_candidate_parameters_present": False,
                "study_model_runs": 0,
            },
            "revised_specification": {
                "estimand": "First-year AC electricity normalized to installed module surface area.",
                "area_basis": "installed_module_surface_area",
                "time_scope": "first_operating_year_typical_meteorological_conditions",
                "degradation_treatment": "no_separate_degradation_term_for_first_year",
                "formula": "area * density * hours * capacity_factor / 1000",
                "loss_treatment": "capacity_factor_includes_system_losses",
                "reference_inputs": {
                    "area_m2": 1,
                    "module_power_density_kW_dc_per_m2": 0.199,
                    "hours_per_year": 8760,
                    "capacity_factor_point": 0.158,
                    "capacity_factor_interval": [0.127, 0.198],
                },
                "normalized_reference_benchmark": {
                    "point_exact": 0.27543192,
                    "interval_exact": [0.22139148, 0.34516152],
                    "point_display": "0.275",
                    "interval_display": ["0.221", "0.345"],
                },
            },
            "mean_weighting_reproduction": {
                "classes": classes,
                "weighted_mean_exact": "0.1582339025005116107457167372",
            },
            "evidence_manifest": [
                {
                    "source_id": group,
                    "publisher": group,
                    "publisher_group": group,
                    "url": "https://example.org",
                    "stable_locator": "p. 1",
                    "facts_used": ["fact"],
                    "limitations": ["limit"],
                    "role": "bounded_cross_check",
                }
                for group in ("NREL", "LBNL", "CPUC_Itron")
            ],
            "unresolved_builder_discrepancies": [],
        }
        result = audit_phy01_reference_benchmark(
            constructor,
            addendum,
            [f"PHY-01-SOLAR-YIELD-P{index:02d}" for index in range(1, 11)],
        )
        self.assertTrue(result["family_level_deterministic_checks_pass"], result["errors"])
        self.assertFalse(result["retention_eligible"])
        self.assertEqual(result["human_review_status"], "pending")


class ContaminationScreeningTests(unittest.TestCase):
    def _candidate(self) -> dict[str, object]:
        return {"candidate_id": "TA-001", "prompt": "Estimate a novel quantity."}

    def _ledger(self, *, google_complete: bool = True, answer_feature: bool = False) -> dict[str, object]:
        candidate = self._candidate()
        search = {
            "status": "complete",
            "query_type": "exact_match_full_stem",
            "searched_on": "2026-07-21",
            "evidence_quality": "captured_top3",
            "top_results": [],
            "top3_returns_same_numerical_answer": False,
            "answer_feature_returns_estimate": False,
        }
        google = dict(search)
        google["status"] = "complete" if google_complete else "pending"
        google["answer_feature_returns_estimate"] = answer_feature
        record = {
            "schema_version": "1.0",
            "candidate_id": candidate["candidate_id"],
            "stem_sha256": stem_sha256(str(candidate["prompt"])),
            "searches": {"google": google, "bing": dict(search)},
            "canonical_template_screen": {
                "status": "complete",
                "canonical_match": False,
                "template_overlap": "none",
            },
            "final_contamination_rating": "Medium" if answer_feature else ("Low" if google_complete else "Pending"),
            "disposition": "retain_pending_other_reviews" if google_complete else "do_not_select",
        }
        return record

    def test_rating_separates_search_answer_feature_from_top_three_hit(self) -> None:
        record = self._ledger(answer_feature=True)
        self.assertEqual(derive_contamination_rating(record), "Medium")
        record["searches"]["google"]["top3_returns_same_numerical_answer"] = True
        self.assertEqual(derive_contamination_rating(record), "High")

    def test_audit_blocks_incomplete_searches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidates = root / "candidates.jsonl"
            ledger = root / "ledger.jsonl"
            candidates.write_text(json.dumps(self._candidate()) + "\n", encoding="utf-8")
            ledger.write_text(json.dumps(self._ledger(google_complete=False)) + "\n", encoding="utf-8")
            result = audit_contamination_ledger(candidates, ledger)
        self.assertFalse(result["passes_acceptance"])
        self.assertEqual(result["complete_by_engine"], {"google": 0, "bing": 1})

    def test_audit_accepts_complete_consistent_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidates = root / "candidates.jsonl"
            ledger = root / "ledger.jsonl"
            candidates.write_text(json.dumps(self._candidate()) + "\n", encoding="utf-8")
            ledger.write_text(json.dumps(self._ledger()) + "\n", encoding="utf-8")
            result = audit_contamination_ledger(candidates, ledger)
        self.assertTrue(result["passes_acceptance"])


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

    def test_status_surfaces_research_plan_alignment_and_document_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = self._protocol()
            protocol["research_plan"] = {
                "version": 10,
                "document": "docs/research-plan-v10.docx",
                "version_source": "project_manager_dashboard_versioned_plan_2026-07-22",
                "local_archive": {"version": 9, "document": "docs/research-plan-v9.docx"},
                "alignment_status": "aligned",
                "alignment_reason": "Version 10 and the implementation protocol are reconciled.",
            }
            protocol_path = root / "protocols" / "year1_protocol.json"
            protocol_path.parent.mkdir(parents=True)
            protocol_path.write_text(json.dumps(protocol), encoding="utf-8")
            docs = root / "docs"
            docs.mkdir()
            plan_bytes = b"research-plan-v10"
            (docs / "research-plan-v10.docx").write_bytes(plan_bytes)
            archive_bytes = b"research-plan-v9"
            (docs / "research-plan-v9.docx").write_bytes(archive_bytes)
            execution_bytes = b"execution-system"
            (docs / "year1_execution.md").write_bytes(execution_bytes)

            snapshot = build_execution_snapshot(root)

            self.assertEqual(snapshot["schema_version"], "1.1")
            self.assertEqual(snapshot["research_plan"]["version"], 10)
            self.assertEqual(snapshot["research_plan"]["alignment_status"], "aligned")
            self.assertEqual(
                snapshot["research_plan"]["document"]["sha256"],
                hashlib.sha256(plan_bytes).hexdigest(),
            )
            self.assertEqual(
                snapshot["research_plan"]["local_archive"]["document"]["sha256"],
                hashlib.sha256(archive_bytes).hexdigest(),
            )
            self.assertEqual(
                snapshot["research_plan"]["implementation_document"]["sha256"],
                hashlib.sha256(execution_bytes).hexdigest(),
            )
            self.assertFalse(any("Research plan alignment" in warning for warning in snapshot["warnings"]))

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
