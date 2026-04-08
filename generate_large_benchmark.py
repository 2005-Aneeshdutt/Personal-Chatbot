"""
Optional: template-generated bulk data for stress-testing only.

Default project metrics use hand-curated `benchmark_queries.json` and
`prepare_real_intent_splits.py` (Banking77) for non-synthetic evaluation.
Set USE_SYNTHETIC_BENCHMARKS=1 before `prepare_datasets.py` if you still want these files.
"""

import json
import random
from typing import Dict, List


RANDOM_SEED = 42
MIN_TOTAL_SAMPLES = 1200

DEPARTMENTS = ["CSE", "ECE", "ME", "EE", "CE", "BT"]
DEPT_LONG = {
    "CSE": "computer science",
    "ECE": "electronics",
    "ME": "mechanical",
    "EE": "electrical",
    "CE": "civil",
    "BT": "biotech",
}
SEMESTERS = [f"Semester {i}" for i in range(1, 9)]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
DATES = [
    "2026-01-26",
    "2026-08-15",
    "2026-10-02",
    "2026-12-25",
    "2026-01-01",
]


def normalize_sem(sem: str) -> str:
    return sem.replace("Semester ", "sem ")


def mk(
    query: str,
    intent: str,
    department=None,
    semester=None,
    day=None,
    date=None,
    exam_type=None,
) -> Dict:
    return {
        "query": query,
        "intent": intent,
        "entities": {
            "department": department,
            "semester": semester,
            "day": day,
            "date": date,
            "exam_type": exam_type,
        },
    }


def timetable_samples(rng: random.Random, n: int) -> List[Dict]:
    templates = [
        "What is the timetable for {dept} {sem}?",
        "Show class schedule for {dept} {sem}",
        "Classes for {dept_long} {sem} on {day}",
        "time table {dept} {sem_short} {day}",
        "{dept} {sem_short} sched pls",
    ]
    out = []
    for _ in range(n):
        dept = rng.choice(DEPARTMENTS)
        sem = rng.choice(SEMESTERS)
        day = rng.choice(DAYS)
        t = rng.choice(templates)
        q = t.format(dept=dept, dept_long=DEPT_LONG[dept], sem=sem, sem_short=normalize_sem(sem), day=day)
        expect_day = day if "{day}" in t else None
        out.append(mk(q, "timetable", department=dept, semester=sem, day=expect_day))
    return out


def exam_samples(rng: random.Random, n: int) -> List[Dict]:
    templates = [
        "When are exams for {dept} {sem}?",
        "mid sem exam date for {dept} {sem_short}",
        "end sem schedule {dept_long} {sem_short}",
        "exam timetable for {dept} {sem}",
        "final exam {dept} {sem_short} kab hai",
    ]
    out = []
    for _ in range(n):
        dept = rng.choice(DEPARTMENTS)
        sem = rng.choice(SEMESTERS)
        t = rng.choice(templates)
        q = t.format(dept=dept, dept_long=DEPT_LONG[dept], sem=sem, sem_short=normalize_sem(sem))
        exam_type = None
        if "mid" in t:
            exam_type = "mid_semester"
        elif "end" in t or "final" in t:
            exam_type = "end_semester"
        out.append(mk(q, "exam", department=dept, semester=sem, exam_type=exam_type))
    return out


def holiday_samples(rng: random.Random, n: int) -> List[Dict]:
    templates = [
        "Is {date} a holiday?",
        "holiday on {date}?",
        "college closed on {date}?",
        "is tomorrow holiday",
        "holiday details for {date}",
    ]
    out = []
    for _ in range(n):
        t = rng.choice(templates)
        date = rng.choice(DATES)
        if "tomorrow" in t:
            out.append(mk(t, "holiday"))
        else:
            out.append(mk(t.format(date=date), "holiday", date=date))
    return out


def credits_samples(rng: random.Random, n: int) -> List[Dict]:
    queries = [
        "How many credits are needed to pass?",
        "credit requirements for degree",
        "min credits to pass",
        "credits per semester?",
        "total credits for btech",
    ]
    return [mk(rng.choice(queries), "credits") for _ in range(n)]


def attendance_samples(rng: random.Random, n: int) -> List[Dict]:
    queries = [
        "minimum attendance required?",
        "attendance rules for exams",
        "attendance percentage to pass",
        "how much attendnce req",
        "attendance criteria pass",
    ]
    return [mk(rng.choice(queries), "attendance") for _ in range(n)]


def contact_samples(rng: random.Random, n: int) -> List[Dict]:
    templates = [
        "Who is HOD of {dept}?",
        "{dept} department contact details",
        "email of {dept_long} department",
        "phone for {dept} dept",
        "office location of {dept_long}",
    ]
    out = []
    for _ in range(n):
        dept = rng.choice(DEPARTMENTS)
        t = rng.choice(templates)
        out.append(mk(t.format(dept=dept, dept_long=DEPT_LONG[dept]), "contact", department=dept))
    return out


def fallback_samples(rng: random.Random, n: int) -> List[Dict]:
    queries = [
        "how to apply hostel",
        "scholarship process please",
        "tuition fee payment link",
        "placement stats last year",
        "migration certificate process",
        "clubs active this semester",
    ]
    return [mk(rng.choice(queries), "fallback") for _ in range(n)]


def typo_noise(query: str, rng: random.Random) -> str:
    words = query.split()
    if not words:
        return query
    idxs = [i for i, w in enumerate(words) if len(w) > 4]
    if not idxs:
        return query
    i = rng.choice(idxs)
    w = words[i]
    p = rng.randint(1, len(w) - 2)
    words[i] = w[:p] + w[p + 1] + w[p] + w[p + 2 :]
    return " ".join(words)


def make_stress(records: List[Dict], rng: random.Random) -> List[Dict]:
    stress = []
    for rec in records:
        new_rec = dict(rec)
        new_rec["entities"] = dict(rec["entities"])
        q = rec["query"].lower()
        q = q.replace("semester", "sem").replace("department", "dept").replace("schedule", "sched")
        if rng.random() < 0.5:
            q = typo_noise(q, rng)
        new_rec["query"] = q
        stress.append(new_rec)
    return stress


def main() -> None:
    rng = random.Random(RANDOM_SEED)

    per_intent = max(MIN_TOTAL_SAMPLES // 7, 170)
    clean = []
    clean.extend(timetable_samples(rng, per_intent))
    clean.extend(exam_samples(rng, per_intent))
    clean.extend(holiday_samples(rng, per_intent))
    clean.extend(credits_samples(rng, per_intent))
    clean.extend(attendance_samples(rng, per_intent))
    clean.extend(contact_samples(rng, per_intent))
    clean.extend(fallback_samples(rng, per_intent))

    rng.shuffle(clean)
    stress = make_stress(clean[: max(400, len(clean) // 2)], rng)

    with open("benchmark_queries_large.json", "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2)
    with open("benchmark_stress_large.json", "w", encoding="utf-8") as f:
        json.dump(stress, f, indent=2)

    print("Generated large datasets:")
    print(f"- benchmark_queries_large.json: {len(clean)}")
    print(f"- benchmark_stress_large.json: {len(stress)}")
    print(f"- total samples: {len(clean) + len(stress)}")


if __name__ == "__main__":
    main()
