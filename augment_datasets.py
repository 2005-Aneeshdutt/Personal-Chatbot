"""Optional synthetic paraphrases — off by default; see DATA_SOURCES.txt."""

import json
import random
import re
from typing import Dict, List


RANDOM_SEED = 42
MAX_AUG_PER_SAMPLE = 3


REPLACEMENTS = {
    "timetable": ["schedule", "time table", "class plan"],
    "schedule": ["timetable", "sched", "plan"],
    "semester": ["sem", "term"],
    "department": ["dept", "branch"],
    "examination": ["exam"],
    "exam": ["test", "examination"],
    "holiday": ["off day", "closed day"],
    "attendance": ["presence"],
    "credits": ["credit points", "cr"],
    "contact": ["details", "info"],
    "tomorrow": ["tmrw"],
    "today": ["tdy"],
}


def load(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(path: str, records: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def synonym_swap(text: str, rng: random.Random) -> str:
    result = text
    keys = list(REPLACEMENTS.keys())
    rng.shuffle(keys)
    for key in keys:
        if re.search(rf"\b{re.escape(key)}\b", result, flags=re.IGNORECASE):
            replacement = rng.choice(REPLACEMENTS[key])
            result = re.sub(
                rf"\b{re.escape(key)}\b",
                replacement,
                result,
                count=1,
                flags=re.IGNORECASE,
            )
            break
    return result


def add_typo(text: str, rng: random.Random) -> str:
    words = text.split()
    candidate_indices = [i for i, w in enumerate(words) if len(w) >= 5 and w.isalpha()]
    if not candidate_indices:
        return text
    idx = rng.choice(candidate_indices)
    word = words[idx]
    pos = rng.randint(1, len(word) - 2)
    typo = word[:pos] + word[pos + 1] + word[pos] + word[pos + 2 :]
    words[idx] = typo
    return " ".join(words)


def shorten(text: str) -> str:
    text = re.sub(r"\bplease\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bcan you\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bwhat is\b", "what's", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def augment_record(record: Dict, rng: random.Random) -> List[Dict]:
    base_query = record.get("query", "")
    variants = set()

    s1 = synonym_swap(base_query, rng)
    if s1 != base_query:
        variants.add(s1)

    s2 = add_typo(base_query, rng)
    if s2 != base_query:
        variants.add(s2)

    s3 = shorten(base_query)
    if s3 and s3 != base_query:
        variants.add(s3)

    more = synonym_swap(shorten(base_query), rng)
    if more and more != base_query:
        variants.add(more)

    augmented = []
    for query in list(variants)[:MAX_AUG_PER_SAMPLE]:
        new_record = dict(record)
        new_record["query"] = query
        new_record["augmented"] = True
        augmented.append(new_record)
    return augmented


def main() -> None:
    rng = random.Random(RANDOM_SEED)
    clean = load("benchmark_queries.json")
    stress = load("benchmark_stress.json")

    augmented_clean: List[Dict] = []
    for rec in clean:
        augmented_clean.append(rec)
        augmented_clean.extend(augment_record(rec, rng))

    augmented_stress: List[Dict] = []
    for rec in stress:
        augmented_stress.append(rec)
        augmented_stress.extend(augment_record(rec, rng))

    save("benchmark_queries_augmented.json", augmented_clean)
    save("benchmark_stress_augmented.json", augmented_stress)

    print("Created augmented datasets:")
    print(f"- benchmark_queries_augmented.json: {len(augmented_clean)}")
    print(f"- benchmark_stress_augmented.json: {len(augmented_stress)}")


if __name__ == "__main__":
    main()
