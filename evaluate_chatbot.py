import argparse
import json
from collections import Counter
from typing import Dict, List, Optional, Tuple

from entity_extractor import EntityExtractor
from intent_detector import IntentDetector


DEFAULT_BENCHMARK_FILES = [
    "data_splits/test_clean.json",
    "data_splits/test_stress.json",
]
ENTITY_FIELDS = ["department", "semester", "day", "date", "exam_type"]


def _safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _normalize_expected_intent(intent: str) -> Optional[str]:
    if intent == "fallback":
        return None
    return intent


def _f1_from_counts(tp: int, fp: int, fn: int) -> float:
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def evaluate_intents(
    samples: List[Dict], detector: IntentDetector
) -> Tuple[Dict[str, float], Dict[str, Dict[str, int]]]:
    labels = sorted({s["intent"] for s in samples})
    confusion: Dict[str, Dict[str, int]] = {
        label: {pred: 0 for pred in labels} for label in labels
    }

    total = len(samples)
    correct = 0
    fallback_total = 0
    fallback_triggered = 0

    for sample in samples:
        expected_label = sample["intent"]
        expected_intent = _normalize_expected_intent(expected_label)

        predicted_intent, _ = detector.detect_intent(sample["query"])

        predicted_label = predicted_intent if predicted_intent is not None else "fallback"
        confusion[expected_label][predicted_label] += 1

        if predicted_label == expected_label:
            correct += 1

        if expected_label == "fallback":
            fallback_total += 1
            if predicted_label == "fallback":
                fallback_triggered += 1

    per_class_f1: Dict[str, float] = {}
    for label in labels:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in labels if other != label)
        fn = sum(confusion[label][other] for other in labels if other != label)
        per_class_f1[label] = _f1_from_counts(tp, fp, fn)

    macro_f1 = _safe_div(sum(per_class_f1.values()), len(per_class_f1))

    metrics = {
        "samples": total,
        "intent_accuracy": _safe_div(correct, total),
        "intent_macro_f1": macro_f1,
        "fallback_recall": _safe_div(fallback_triggered, fallback_total),
        "fallback_trigger_rate": _safe_div(
            sum(1 for s in samples if _normalize_expected_intent(s["intent"]) is None), total
        ),
    }
    return metrics, confusion


def evaluate_entities(samples: List[Dict], extractor: EntityExtractor) -> Dict[str, float]:
    evaluated_samples = [s for s in samples if s["intent"] != "fallback"]
    sample_count = len(evaluated_samples)

    field_correct = Counter()
    field_total = Counter()
    exact_match = 0
    tp = fp = fn = 0

    for sample in evaluated_samples:
        expected = sample.get("entities", {})
        predicted = extractor.extract_all(sample["query"])

        all_match = True
        for field in ENTITY_FIELDS:
            gold = expected.get(field)
            pred = predicted.get(field)
            field_total[field] += 1
            if gold == pred:
                field_correct[field] += 1
            else:
                all_match = False

            if gold is not None and pred is not None:
                if gold == pred:
                    tp += 1
                else:
                    fp += 1
                    fn += 1
            elif gold is None and pred is not None:
                fp += 1
            elif gold is not None and pred is None:
                fn += 1

        if all_match:
            exact_match += 1

    micro_precision = _safe_div(tp, tp + fp)
    micro_recall = _safe_div(tp, tp + fn)
    micro_f1 = _f1_from_counts(tp, fp, fn)

    results = {
        "entity_exact_match_accuracy": _safe_div(exact_match, sample_count),
        "entity_micro_precision": micro_precision,
        "entity_micro_recall": micro_recall,
        "entity_micro_f1": micro_f1,
    }
    for field in ENTITY_FIELDS:
        results[f"{field}_accuracy"] = _safe_div(field_correct[field], field_total[field])

    return results


def print_metrics(title: str, metrics: Dict[str, float]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for key, value in metrics.items():
        if key == "samples":
            print(f"{key}: {int(value)}")
        else:
            print(f"{key}: {value * 100:.2f}%")


def _evaluate_dataset(samples: List[Dict]) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, Dict[str, int]]]:
    detector = IntentDetector()
    extractor = EntityExtractor()
    intent_metrics, confusion = evaluate_intents(samples, detector)
    entity_metrics = evaluate_entities(samples, extractor)
    return intent_metrics, entity_metrics, confusion


def _write_markdown_report(
    output_path: str, dataset_results: List[Tuple[str, Dict[str, float], Dict[str, float]]]
) -> None:
    lines = [
        "# Chatbot Evaluation Report",
        "",
        "Intent confidence threshold: uses `IntentDetector.min_confidence`.",
        "",
        "| Dataset | Samples | Intent Accuracy | Macro F1 | Entity Micro F1 | Entity Exact Match |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for dataset_name, intent_metrics, entity_metrics in dataset_results:
        lines.append(
            "| "
            + f"{dataset_name} | "
            + f"{int(intent_metrics['samples'])} | "
            + f"{intent_metrics['intent_accuracy'] * 100:.2f}% | "
            + f"{intent_metrics['intent_macro_f1'] * 100:.2f}% | "
            + f"{entity_metrics['entity_micro_f1'] * 100:.2f}% | "
            + f"{entity_metrics['entity_exact_match_accuracy'] * 100:.2f}% |"
        )
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate chatbot intent/entity quality.")
    parser.add_argument(
        "--files",
        nargs="+",
        default=DEFAULT_BENCHMARK_FILES,
        help="Benchmark JSON files to evaluate.",
    )
    parser.add_argument(
        "--report",
        default="metrics_report.md",
        help="Markdown report output path.",
    )
    args = parser.parse_args()

    dataset_results: List[Tuple[str, Dict[str, float], Dict[str, float]]] = []

    for benchmark_file in args.files:
        with open(benchmark_file, "r", encoding="utf-8") as f:
            samples = json.load(f)

        intent_metrics, entity_metrics, confusion = _evaluate_dataset(samples)
        dataset_results.append((benchmark_file, intent_metrics, entity_metrics))

        print(f"\n=== Dataset: {benchmark_file} ===")
        print_metrics("Intent Metrics", intent_metrics)
        print_metrics("Entity Metrics", entity_metrics)

        print("\nConfusion Matrix (rows=expected, cols=predicted)")
        labels = list(confusion.keys())
        print("expected\\predicted\t" + "\t".join(labels))
        for expected in labels:
            row = [str(confusion[expected][pred]) for pred in labels]
            print(f"{expected}\t" + "\t".join(row))

    _write_markdown_report(args.report, dataset_results)
    print(f"\nSaved report: {args.report}")


if __name__ == "__main__":
    main()
