"""
Renders the captured console output (outputs/*.txt, produced by real runs of
neural_network.py and task_experiments.py) into terminal-style PNG images for
the lab report / submission screenshots (handout section 7.1.2).

These are not mockups: every character comes from the actual stdout of the
actual program runs.
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

OUT_DIR = "outputs"


def text_to_png(text, out_path, title):
    lines = text.rstrip("\n").split("\n")
    n_lines = len(lines)

    fig_width = 9.5
    line_height = 0.205
    fig_height = max(1.2, n_lines * line_height + 0.9)

    fig = plt.figure(figsize=(fig_width, fig_height), facecolor="#1e1e1e")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_facecolor("#1e1e1e")
    ax.axis("off")

    # fake terminal title bar
    ax.add_patch(plt.Rectangle((0, 1 - 0.6 / fig_height), 1, 0.6 / fig_height,
                                transform=ax.transAxes, facecolor="#323233",
                                edgecolor="none", zorder=1))
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        ax.add_patch(plt.Circle((0.018 + i * 0.018, 1 - 0.3 / fig_height), 0.006,
                                 transform=ax.transAxes, facecolor=color,
                                 edgecolor="none", zorder=2))
    ax.text(0.5, 1 - 0.3 / fig_height, title, transform=ax.transAxes,
            ha="center", va="center", color="#cccccc", fontsize=10,
            fontfamily="monospace", zorder=2)

    body_top = 1 - 0.75 / fig_height
    y = body_top
    step = line_height / fig_height
    for line in lines:
        color = "#d4d4d4"
        if line.strip().startswith(("Accuracy", "Prediction:", "===")):
            color = "#4ec9b0"
        elif "PASS" in line:
            color = "#6a9955"
        elif "FAIL" in line:
            color = "#f14c4c"
        ax.text(0.015, y, line, transform=ax.transAxes, ha="left", va="top",
                color=color, fontsize=9, fontfamily="monospace", zorder=2)
        y -= step

    fig.savefig(out_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("Saved", out_path)


def section(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    if end_marker:
        end = text.index(end_marker, start)
        return text[start:end].strip("\n")
    return text[start:].strip("\n")


with open(f"{OUT_DIR}/task1_run.txt", encoding="utf-8") as f:
    task1_text = f.read()

with open(f"{OUT_DIR}/task_experiments_run.txt", encoding="utf-8") as f:
    exp_text = f.read()

# Task 1: full required screenshot (dataset, actual/predicted, accuracy, report)
text_to_png(task1_text, f"{OUT_DIR}/task1_execution.png",
            "neural_network.py — Task 1: Run the Program")

# Task 2: dataset change
t2 = section(exp_text, "TASK 2 - Change the Dataset", "TASK 3 - Change the Neural Network")
text_to_png(t2, f"{OUT_DIR}/task2_dataset_change.png",
            "task_experiments.py — Task 2: Change the Dataset")

# Task 3: neural network / hidden layers
t3 = section(exp_text, "TASK 3 - Change the Neural Network", "TASK 4 - Change the Activation Function")
text_to_png(t3, f"{OUT_DIR}/task3_hidden_layers.png",
            "task_experiments.py — Task 3: Change the Neural Network")

# Task 4: activation function
t4 = section(exp_text, "TASK 4 - Change the Activation Function", "TASK 5 - Test Your Own Student")
text_to_png(t4, f"{OUT_DIR}/task4_activation.png",
            "task_experiments.py — Task 4: Change the Activation Function")

# Task 5: own student + summary table
t5 = section(exp_text, "TASK 5 - Test Your Own Student", "APPENDIX")
summary = section(exp_text, "SUMMARY TABLE - all variants")
text_to_png(t5 + "\n\n" + summary, f"{OUT_DIR}/task5_own_student.png",
            "task_experiments.py — Task 5: Test Your Own Student + Summary")
