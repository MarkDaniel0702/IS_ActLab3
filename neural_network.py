"""
Laboratory Exercise No. 3: Building and Training a Neural Network for
Classification Using Python (scikit-learn, MLPClassifier)

Loads student data from a CSV file (study_hours, attendance, result),
validates and checks the data, trains an MLPClassifier, evaluates it,
and predicts outcomes for new students.

Usage:
    python neural_network.py [path_to_csv]

If no path is given, students_500.csv is used by default.
"""

import sys
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

REQUIRED_COLUMNS = ["study_hours", "attendance", "result"]
INPUT_FEATURES = ["study_hours", "attendance"]
TARGET_COLUMN = "result"
DEFAULT_CSV = "students_500.csv"


# ---------------------------------------------------------------------------
# 1. Data loading
# ---------------------------------------------------------------------------
def load_dataset(csv_path):
    """Reads the dataset from a CSV file, exiting with a clear message if
    the file is missing, empty, or cannot be parsed."""
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        sys.exit(f"Error: could not find CSV file '{csv_path}'.")
    except pd.errors.EmptyDataError:
        sys.exit(f"Error: CSV file '{csv_path}' is empty.")
    except pd.errors.ParserError as e:
        sys.exit(f"Error: CSV file '{csv_path}' is malformed ({e}).")

    if df.empty:
        sys.exit(f"Error: CSV file '{csv_path}' contains no rows.")

    return df


def validate_columns(df, csv_path):
    """Confirms the dataset has the columns the model needs before doing
    anything else with it."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        sys.exit(
            f"Error: '{csv_path}' is missing required column(s): {missing}. "
            f"Expected columns: {REQUIRED_COLUMNS}"
        )


# ---------------------------------------------------------------------------
# 2. Data quality checks
# ---------------------------------------------------------------------------
def check_data_quality(df, csv_path, expected_rows=None):
    """Runs a set of sanity checks on the dataset and prints a summary.
    Nothing here stops execution (except missing values, which would break
    training) -- issues are reported so the user can inspect the data."""
    print(f"\n--- Data Quality Report: {csv_path} ---")
    print(f"Rows: {len(df)}")

    if expected_rows is not None and len(df) != expected_rows:
        print(f"Warning: expected {expected_rows} rows, found {len(df)}.")

    missing_count = df[REQUIRED_COLUMNS].isna().sum().sum()
    print(f"Missing values: {missing_count}")
    if missing_count > 0:
        df.dropna(subset=REQUIRED_COLUMNS, inplace=True)
        print(f"  -> Dropped rows with missing values. {len(df)} rows remain.")

    duplicate_rows = df.duplicated().sum()
    print(f"Duplicate rows: {duplicate_rows}")
    if duplicate_rows > 0:
        df.drop_duplicates(inplace=True)
        print(f"  -> Dropped duplicate rows. {len(df)} rows remain.")

    invalid_attendance = df[(df["attendance"] < 0) | (df["attendance"] > 100)]
    print(f"Invalid attendance values (outside 0-100): {len(invalid_attendance)}")

    invalid_hours = df[(df["study_hours"] < 0) | (df["study_hours"] > 24)]
    print(f"Invalid study_hours values (outside 0-24): {len(invalid_hours)}")

    # Near-identical input combinations: round to a coarse resolution and
    # look for repeats -- these add little learning value and can indicate
    # noisy or copy-pasted data.
    rounded = df[INPUT_FEATURES].round({"study_hours": 1, "attendance": 0})
    near_duplicates = rounded.duplicated().sum()
    print(f"Near-identical study_hours/attendance combinations: {near_duplicates}")

    print("\nSummary statistics:")
    print(df[REQUIRED_COLUMNS].describe())
    print(f"Result distribution:\n{df[TARGET_COLUMN].value_counts()}")
    print("--- End of Data Quality Report ---\n")

    return df


# ---------------------------------------------------------------------------
# 3. Preprocessing
# ---------------------------------------------------------------------------
def preprocess_data(df):
    """Separates inputs/target and scales the input features so both
    features contribute proportionally during training (attendance ranges
    0-100 while study_hours ranges 0-10, so scaling matters)."""
    X = df[INPUT_FEATURES]
    y = df[TARGET_COLUMN]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler


# ---------------------------------------------------------------------------
# 4. Training
# ---------------------------------------------------------------------------
def train_model(X_train, y_train):
    """Creates and trains the MLPClassifier."""
    model = MLPClassifier(
        hidden_layer_sizes=(5,),
        activation="relu",
        solver="adam",
        max_iter=1000,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model


# ---------------------------------------------------------------------------
# 5. Evaluation
# ---------------------------------------------------------------------------
def evaluate_model(model, X_test, y_test):
    """Predicts on the held-out test set and prints accuracy metrics."""
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print("\nActual:   ", y_test.values.tolist())
    print("Predicted:", y_pred.tolist())
    print(f"\nAccuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    return y_pred


# ---------------------------------------------------------------------------
# 6. Prediction
# ---------------------------------------------------------------------------
def predict_students(model, scaler, students):
    """Predicts Pass/Fail for a list of [study_hours, attendance] pairs.
    Inputs are scaled with the same scaler fitted on the training data."""
    students_scaled = scaler.transform(students)
    predictions = model.predict(students_scaled)

    print("\nPredictions:")
    for i, (student, prediction) in enumerate(zip(students, predictions)):
        result = "PASS" if prediction == 1 else "FAIL"
        print(
            f"Student {i + 1} - Study Hours: {student[0]}, "
            f"Attendance: {student[1]}% -> Prediction: {result}"
        )
    return predictions


# ---------------------------------------------------------------------------
# 7. Visualization
# ---------------------------------------------------------------------------
def visualize_dataset(df, csv_path):
    """Saves a scatter plot of study_hours vs. attendance, colored by
    result, named after the source CSV so runs don't overwrite each other."""
    dataset_label = csv_path.rsplit(".", 1)[0].replace("/", "_").replace("\\", "_")
    output_path = f"outputs/dataset_scatter_{dataset_label}.png"

    colors = ["red" if r == 0 else "green" for r in df["result"]]
    plt.figure(figsize=(6, 5))
    plt.scatter(df["study_hours"], df["attendance"], c=colors, s=40, edgecolors="black", alpha=0.7)
    plt.xlabel("Study Hours")
    plt.ylabel("Attendance (%)")
    plt.title(f"Student Dataset: {csv_path}\n(green = Pass, red = Fail)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved dataset visualization to {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV

    df = load_dataset(csv_path)
    validate_columns(df, csv_path)
    df = check_data_quality(df, csv_path)

    X, y, scaler = preprocess_data(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)

    new_students = [
        [5, 10],
        [6, 0],
        [4, 75],
        [5, 82],
        [0, 100]
    ]
    predict_students(model, scaler, new_students)

    visualize_dataset(df, csv_path)


if __name__ == "__main__":
    main()
