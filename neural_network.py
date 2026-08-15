"""
Laboratory Exercise No. 3: Building and Training a Neural Network for
Classification Using Python (scikit-learn, MLPClassifier)
"""

import warnings
warnings.filterwarnings("ignore")

# 5.1 Import the Libraries
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report

# 5.2 Create the Dataset
data = {
    "study_hours": [1, 2, 2, 3, 4, 5, 6, 7, 1, 3, 4, 6],
    "attendance": [55, 60, 65, 70, 75, 80, 85, 90, 50, 68, 78, 88],
    "result": [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1]
}
# 0 = Fail, 1 = Pass

df = pd.DataFrame(data)

print("Dataset:")
print(df)

# 5.3 Separate Inputs and Outputs
X = df[["study_hours", "attendance"]]
y = df["result"]

# 5.4 Split the Dataset (75% Training / 25% Testing)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# 5.5 Create the Neural Network
model = MLPClassifier(
    hidden_layer_sizes=(5,),
    activation="relu",
    solver="adam",
    max_iter=1000,
    random_state=42
)

# 5.6 Train the Neural Network
model.fit(X_train, y_train)

# 5.7 Make Predictions
y_pred = model.predict(X_test)

print("\nActual:")
print(y_test.values)

print("Predicted:")
print(y_pred)

# 5.8 Calculate Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy:", accuracy)
print("Accuracy Percentage:", accuracy * 100, "%")

# 5.9 Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

# 5.10 Test a New Student
new_student = [[5, 82]]

prediction = model.predict(new_student)

print("New Student -> Study Hours = 5, Attendance = 82%")
if prediction[0] == 1:
    print("Prediction: PASS")
else:
    print("Prediction: FAIL")

# 5.11 Test Multiple Students
new_students = [
    [5, 10],
    [6, 0],
    [4, 75],
    [5, 82],
    [0, 100]
]

predictions = model.predict(new_students)

print("\nMultiple Student Predictions:")
for i, prediction in enumerate(predictions):
    if prediction == 1:
        result = "PASS"
    else:
        result = "FAIL"

    print(
        "Student", i + 1,
        "Study Hours:", new_students[i][0],
        "Attendance:", new_students[i][1],
        "Prediction:", result
    )

# Visualize the dataset (study hours vs. attendance, colored by result)
colors = ["red" if r == 0 else "green" for r in df["result"]]
plt.figure(figsize=(6, 5))
plt.scatter(df["study_hours"], df["attendance"], c=colors, s=80, edgecolors="black")
plt.xlabel("Study Hours")
plt.ylabel("Attendance (%)")
plt.title("Student Dataset: Study Hours vs. Attendance\n(green = Pass, red = Fail)")
plt.tight_layout()
plt.savefig("outputs/dataset_scatter.png", dpi=150)
print("\nSaved dataset visualization to outputs/dataset_scatter.png")
