"""
Generates three synthetic student-performance datasets (100, 500, and
1,000 records) used by neural_network.py.

Each dataset is produced independently (different random seed) using the
SAME generation rule, so the 500- and 1,000-record files are not just the
100-record file copied/extended -- they are fresh samples from the same
underlying distribution.

Columns:
    study_hours - hours studied per day (0-10, nearest 0.5)
    attendance  - class attendance percentage (30-100, nearest 0.1)
    result      - 1 = Pass, 0 = Fail, derived from a weighted combination
                  of study_hours and attendance plus a small amount of
                  noise (so the relationship is logical but not perfectly
                  deterministic).
"""

import numpy as np
import pandas as pd

# Weights used to turn (study_hours, attendance) into a pass/fail score.
# Study hours matter slightly more than attendance, but both count.
HOURS_WEIGHT = 0.55
ATTENDANCE_WEIGHT = 0.45
PASS_THRESHOLD = 0.6
NOISE_STD = 0.05  # small noise so the boundary isn't perfectly sharp

HOURS_RANGE = (0.0, 10.0)
ATTENDANCE_RANGE = (30.0, 100.0)


def compute_result(study_hours, attendance, rng):
    """Turns study_hours/attendance into a 0/1 result using a fixed,
    understandable rule: a weighted score compared to a threshold, with
    a small amount of random noise so the data isn't perfectly clean."""
    normalized_hours = study_hours / HOURS_RANGE[1]
    normalized_attendance = attendance / 100.0
    score = HOURS_WEIGHT * normalized_hours + ATTENDANCE_WEIGHT * normalized_attendance
    noisy_score = score + rng.normal(0, NOISE_STD)
    return 1 if noisy_score >= PASS_THRESHOLD else 0


def generate_dataset(n_records, seed):
    """Generates n_records unique, realistic (study_hours, attendance, result)
    rows using rejection sampling to guarantee no duplicate or overly
    similar input combinations."""
    rng = np.random.default_rng(seed)
    seen_combinations = set()
    rows = []

    max_attempts = n_records * 200
    attempts = 0

    while len(rows) < n_records and attempts < max_attempts:
        attempts += 1

        # Sample from a bell-shaped distribution so most students cluster
        # around typical values, with fewer students at the extremes.
        study_hours = rng.normal(loc=5.0, scale=2.2)
        study_hours = np.clip(study_hours, *HOURS_RANGE)
        study_hours = round(study_hours * 2) / 2  # nearest 0.5

        attendance = rng.normal(loc=78.0, scale=14.0)
        attendance = np.clip(attendance, *ATTENDANCE_RANGE)
        attendance = round(attendance, 1)  # nearest 0.1%

        # Reject near-duplicate input combinations (rounded to the same
        # resolution we store) to keep every row meaningfully distinct.
        combo_key = (study_hours, attendance)
        if combo_key in seen_combinations:
            continue
        seen_combinations.add(combo_key)

        result = compute_result(study_hours, attendance, rng)
        rows.append((study_hours, attendance, result))

    if len(rows) < n_records:
        raise RuntimeError(
            f"Could not generate {n_records} unique rows "
            f"(only got {len(rows)}) -- widen the sampling ranges."
        )

    df = pd.DataFrame(rows, columns=["study_hours", "attendance", "result"])
    return df


def main():
    dataset_sizes = {
        "students_100.csv": (100, 100),
        "students_500.csv": (500, 500),
        "students_1000.csv": (1000, 1000),
    }

    for filename, (n_records, seed) in dataset_sizes.items():
        df = generate_dataset(n_records, seed)
        df.to_csv(filename, index=False)

        pass_rate = df["result"].mean() * 100
        print(
            f"{filename}: {len(df)} rows written "
            f"(pass rate {pass_rate:.1f}%, "
            f"study_hours [{df['study_hours'].min()}-{df['study_hours'].max()}], "
            f"attendance [{df['attendance'].min()}-{df['attendance'].max()}])"
        )


if __name__ == "__main__":
    main()
