"""
Laboratory Exercise No. 3 - Tasks 2-5 (section 5.12.2-5.12.5)

Runs every required dataset / hidden-layer / activation-function variant
described in the handout, prints the results, and reports the comparisons
Task 2-4 ask for ("did accuracy change? why?").
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

BASE_DATA = {
    "study_hours": [1, 2, 2, 3, 4, 5, 6, 7, 1, 3, 4, 6],
    "attendance": [55, 60, 65, 70, 75, 80, 85, 90, 50, 68, 78, 88],
    "result": [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1]
}

# Task 2 - Change the Dataset: add 5 additional students
# (keeps the handout's own example: study_hours=8, attendance=92, result=1)
NEW_STUDENTS_ADDED = {
    "study_hours": [8, 2, 5, 3, 7],
    "attendance": [92, 58, 84, 62, 95],
    "result": [1, 0, 1, 0, 1]
}

EXTENDED_DATA = {
    "study_hours": BASE_DATA["study_hours"] + NEW_STUDENTS_ADDED["study_hours"],
    "attendance": BASE_DATA["attendance"] + NEW_STUDENTS_ADDED["attendance"],
    "result": BASE_DATA["result"] + NEW_STUDENTS_ADDED["result"]
}


def run(dataset, hidden_layer_sizes, activation, label, scale=False):
    """Trains one MLPClassifier variant and returns its results."""
    df = pd.DataFrame(dataset)
    X = df[["study_hours", "attendance"]]
    y = df["result"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    if scale:
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    model = MLPClassifier(
        hidden_layer_sizes=hidden_layer_sizes,
        activation=activation,
        solver="adam",
        max_iter=1000,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)

    print(f"\n--- {label} ---")
    print(f"rows={len(df)}  hidden_layer_sizes={hidden_layer_sizes}  "
          f"activation={activation}  scaled={scale}")
    print("Actual:   ", y_test.values)
    print("Predicted:", y_pred)
    print(f"Accuracy: {accuracy:.4f}  ({accuracy * 100:.2f}%)")
    print(report)

    return {
        "label": label,
        "rows": len(df),
        "hidden_layer_sizes": hidden_layer_sizes,
        "activation": activation,
        "scaled": scale,
        "accuracy": accuracy,
        "n_test": len(y_test),
    }


results = []

# ---------------------------------------------------------------------
print("=" * 70)
print("TASK 1 BASELINE (12 students, (5,), relu) - for comparison")
print("=" * 70)
results.append(run(BASE_DATA, (5,), "relu", "Baseline: 12 students, (5,), relu"))

# ---------------------------------------------------------------------
print("\n" + "=" * 70)
print("TASK 2 - Change the Dataset (added 5 students -> 17 total)")
print("=" * 70)
print("\nAdded students:")
added_df = pd.DataFrame(NEW_STUDENTS_ADDED)
added_df["result"] = added_df["result"].map({1: "Pass", 0: "Fail"})
print(added_df.to_string(index=False))

results.append(run(EXTENDED_DATA, (5,), "relu", "Task 2: 17 students, (5,), relu"))

base_acc = results[0]["accuracy"]
ext_acc = results[-1]["accuracy"]
print(f"\nTask 2 answer -> accuracy changed from {base_acc:.4f} to {ext_acc:.4f}. "
      f"Reason: the test split grew from {results[0]['n_test']} to "
      f"{results[-1]['n_test']} samples, so each prediction now swings the "
      f"score by {100 / results[-1]['n_test']:.1f}% instead of "
      f"{100 / results[0]['n_test']:.1f}%, and the added rows shift where the "
      f"model's decision boundary needs to sit.")

# ---------------------------------------------------------------------
print("\n" + "=" * 70)
print("TASK 3 - Change the Neural Network (hidden_layer_sizes)")
print("=" * 70)

r_5 = run(EXTENDED_DATA, (5,), "relu", "Task 3a: 17 students, (5,), relu")
r_10 = run(EXTENDED_DATA, (10,), "relu", "Task 3b: 17 students, (10,), relu")
r_10_5 = run(EXTENDED_DATA, (10, 5), "relu", "Task 3c: 17 students, (10, 5), relu")
results += [r_10, r_10_5]

print(f"\nTask 3 answer -> (5,) gave {r_5['accuracy']:.4f}, (10,) gave "
      f"{r_10['accuracy']:.4f}, (10, 5) [a second hidden layer] gave "
      f"{r_10_5['accuracy']:.4f}. With only {r_5['rows']} training rows, more "
      f"neurons/layers means more parameters than the data can reliably "
      f"constrain, so accuracy does not simply go up with network size.")

# ---------------------------------------------------------------------
print("\n" + "=" * 70)
print("TASK 4 - Change the Activation Function (relu vs logistic)")
print("=" * 70)

r_relu = run(EXTENDED_DATA, (5,), "relu", "Task 4a: 17 students, (5,), relu")
r_logistic = run(EXTENDED_DATA, (5,), "logistic", "Task 4b: 17 students, (5,), logistic")
results += [r_logistic]

changed = "changed" if r_relu["accuracy"] != r_logistic["accuracy"] else "did not change"
print(f"\nTask 4 answer -> relu gave {r_relu['accuracy']:.4f}, logistic gave "
      f"{r_logistic['accuracy']:.4f}. The result {changed}, because relu and "
      f"logistic (sigmoid) shape the hidden-layer outputs differently, which "
      f"changes how the network's decision boundary is learned during "
      f"backpropagation.")

# ---------------------------------------------------------------------
print("\n" + "=" * 70)
print("TASK 5 - Test Your Own Student")
print("=" * 70)

df17 = pd.DataFrame(EXTENDED_DATA)
X17 = df17[["study_hours", "attendance"]]
y17 = df17["result"]
X17_train, X17_test, y17_train, y17_test = train_test_split(
    X17, y17, test_size=0.25, random_state=42, stratify=y17
)
final_model = MLPClassifier(
    hidden_layer_sizes=(5,), activation="relu", solver="adam",
    max_iter=1000, random_state=42
)
final_model.fit(X17_train, y17_train)

my_students = {
    "Own student (Study Hours=6, Attendance=88)": [[6, 88]],
    "Borderline student (Study Hours=3, Attendance=62)": [[3, 62]],
}
for desc, sample in my_students.items():
    pred = final_model.predict(sample)[0]
    result = "PASS" if pred == 1 else "FAIL"
    print(f"{desc} -> Prediction: {result}")

# ---------------------------------------------------------------------
print("\n" + "=" * 70)
print("APPENDIX - Feature scaling (StandardScaler), not required by the "
      "handout, included to explain the accuracy swings above")
print("=" * 70)

r_scaled_5 = run(EXTENDED_DATA, (5,), "relu", "Appendix: 17 students, (5,), relu, scaled", scale=True)
r_scaled_10 = run(EXTENDED_DATA, (10,), "relu", "Appendix: 17 students, (10,), relu, scaled", scale=True)
r_scaled_10_5 = run(EXTENDED_DATA, (10, 5), "relu", "Appendix: 17 students, (10, 5), relu, scaled", scale=True)
results += [r_scaled_5, r_scaled_10, r_scaled_10_5]

# ---------------------------------------------------------------------
print("\n" + "=" * 70)
print("SUMMARY TABLE - all variants")
print("=" * 70)
summary_df = pd.DataFrame(results)[
    ["label", "rows", "hidden_layer_sizes", "activation", "scaled", "n_test", "accuracy"]
]
print(summary_df.to_string(index=False))
