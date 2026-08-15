const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageBreak
} = require("docx");

const PAGE_WIDTH = 12240, PAGE_HEIGHT = 15840;
const MARGIN = 1440;
const CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN; // 9360 DXA

const border = { style: BorderStyle.SINGLE, size: 1, color: "BFBFBF" };
const borders = { top: border, bottom: border, left: border, right: border };
const HEAD_FILL = "2E5395";
const ALT_FILL = "EEF3FA";

function headCell(text, width) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: HEAD_FILL, type: ShadingType.CLEAR },
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 20 })]
    })]
  });
}
function bodyCell(text, width, opts = {}) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: opts.alt ? ALT_FILL : "FFFFFF", type: ShadingType.CLEAR },
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    children: [new Paragraph({
      alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: [new TextRun({ text: String(text), size: 20, bold: !!opts.bold })]
    })]
  });
}
function dataTable(headers, rows, widths) {
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => headCell(h, widths[i])) }),
      ...rows.map((r, ri) => new TableRow({
        children: r.map((c, i) => bodyCell(c, widths[i], { alt: ri % 2 === 1, center: i > 0 }))
      }))
    ]
  });
}

function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
}
function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 160 },
    children: [new TextRun({ text, italics: !!opts.italics, bold: !!opts.bold })]
  });
}
function bullet(text) {
  return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 60 }, children: [new TextRun(text)] });
}
function numbered(text, ref = "numbers") {
  return new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 100 }, children: [new TextRun(text)] });
}
function qa(number, question, answer) {
  return [
    new Paragraph({
      spacing: { before: 160, after: 60 },
      children: [new TextRun({ text: `${number} ${question}`, bold: true })]
    }),
    new Paragraph({ spacing: { after: 100 }, children: [new TextRun(answer)] })
  ];
}
function caption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 240 },
    children: [new TextRun({ text, italics: true, size: 18, color: "555555" })]
  });
}

function image(fileName, dispW, altTitle) {
  const buf = fs.readFileSync(`outputs/${fileName}`);
  const { width, height } = require("./img_sizes.json")[fileName];
  const dispH = Math.round(dispW * (height / width));
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60 },
    children: [new ImageRun({
      type: "png",
      data: buf,
      transformation: { width: dispW, height: dispH },
      altText: { title: altTitle, description: altTitle, name: fileName }
    })]
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, font: "Arial", color: "1F3864" },
        paragraph: { spacing: { before: 320, after: 180 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "2E5395" },
        paragraph: { spacing: { before: 220, after: 140 }, outlineLevel: 1 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: { page: { size: { width: PAGE_WIDTH, height: PAGE_HEIGHT }, margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN } } },
    children: [
      // Title block
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 60 },
        children: [new TextRun({ text: "Laboratory Exercise No. 3", bold: true, size: 36, color: "1F3864" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 300 },
        children: [new TextRun({ text: "Building and Training a Neural Network for Classification Using Python", size: 26, color: "2E5395" })]
      }),
      dataTable(
        ["Field", "Details"],
        [
          ["Name", "________________________________"],
          ["Section", "________________________________"],
          ["Date", "________________________________"],
          ["Library", "scikit-learn (MLPClassifier)"],
          ["Estimated Time", "2 hours"],
        ],
        [2200, 7160]
      ),
      p(""),
      new Paragraph({
        spacing: { before: 160, after: 300 },
        children: [new TextRun({
          text: "Note on the handout header: page 1 lists “Algorithm: Isolation Forest,” but every code listing, guide question, and the concept-mapping table in the handout (§5–§6) specifies MLPClassifier, a supervised feedforward neural network. Isolation Forest is an unsupervised anomaly detector and cannot produce the Pass/Fail classification report the exercise requires, so this report follows MLPClassifier as the handout body directs.",
          italics: true, size: 18, color: "555555"
        })]
      }),

      // Objective
      h1("1. Objective"),
      p("At the end of this laboratory activity, the objective was to be able to:"),
      bullet("Create a simple dataset for classification."),
      bullet("Prepare training and testing data."),
      bullet("Create a neural network using Python."),
      bullet("Train the neural network using training data."),
      bullet("Generate predictions using the trained model."),
      bullet("Evaluate the model's performance."),
      bullet("Explain the relationship between the Python program and the neural network training process."),

      // Procedure
      h1("2. Procedure"),
      p("A school wants to predict whether a student will PASS or FAIL based on Study Hours and Attendance (%). neural_network.py was built following the handout's steps, then task_experiments.py was built to run the required Task 2–5 variants."),
      h2("2.1 neural_network.py (handout §5.1–§5.11)"),
      numbered("Import the Libraries — pandas, matplotlib.pyplot, and scikit-learn's train_test_split, MLPClassifier, accuracy_score, classification_report."),
      numbered("Create the Dataset — 12 students as a dict of study_hours, attendance, and result (0 = Fail, 1 = Pass), loaded into a pandas DataFrame."),
      numbered("Separate Inputs and Outputs — X = df[[\"study_hours\", \"attendance\"]], y = df[\"result\"]."),
      numbered("Split the Dataset — train_test_split(test_size=0.25, random_state=42, stratify=y): 75% training, 25% testing."),
      numbered("Create the Neural Network — MLPClassifier(hidden_layer_sizes=(5,), activation=\"relu\", solver=\"adam\", max_iter=1000, random_state=42)."),
      numbered("Train the Neural Network — model.fit(X_train, y_train)."),
      numbered("Make Predictions — model.predict(X_test), printed alongside the actual y_test values."),
      numbered("Calculate Accuracy — accuracy_score(y_test, y_pred)."),
      numbered("Classification Report — classification_report(y_test, y_pred), giving precision, recall, f1-score, support."),
      numbered("Test a New Student — a single hypothetical student, Study Hours = 5, Attendance = 82%."),
      numbered("Test Multiple Students — five hypothetical students predicted in a loop."),
      p("A matplotlib scatter plot (study hours vs. attendance, colored by result) was added and saved to outputs/dataset_scatter.png to fulfil the handout's stated purpose for the matplotlib import (“allows us to visualize the data”), which the handout's own listing never actually calls."),
      h2("2.2 task_experiments.py (handout §5.12.2–§5.12.5)"),
      bullet("Task 2 — Change the Dataset: added 5 students to reach 17 rows, then re-ran the pipeline."),
      bullet("Task 3 — Change the Neural Network: hidden_layer_sizes run at (5,), (10,), and (10, 5)."),
      bullet("Task 4 — Change the Activation Function: activation run at \"relu\" and \"logistic\"."),
      bullet("Task 5 — Test Your Own Student: a custom student (Study Hours = 6, Attendance = 88) plus a borderline case (Study Hours = 3, Attendance = 62)."),
      p("An appendix run with StandardScaler-scaled features was also included, purely to explain (not to replace) the accuracy figures observed — see §3.3 below."),

      // Results
      h1("3. Results"),
      h2("3.1 Dataset"),
      dataTable(
        ["Study Hours", "Attendance (%)", "Result"],
        [
          ["1", "55", "Fail"], ["2", "60", "Fail"], ["2", "65", "Fail"], ["3", "70", "Pass"],
          ["4", "75", "Pass"], ["5", "80", "Pass"], ["6", "85", "Pass"], ["7", "90", "Pass"],
          ["1", "50", "Fail"], ["3", "68", "Fail"], ["4", "78", "Pass"], ["6", "88", "Pass"],
        ],
        [3120, 3120, 3120]
      ),
      p(""),
      image("dataset_scatter.png", 460, "Scatter plot of study hours vs attendance colored by pass/fail"),
      caption("Figure 1. Base 12-student dataset (green = Pass, red = Fail)."),

      h2("3.2 Task 1 — Program Execution"),
      p("neural_network.py ran successfully end to end. Full console output (dataset, actual vs. predicted values, accuracy, and classification report):"),
      image("task1_execution.png", 560, "Console output of neural_network.py showing dataset, predictions, accuracy, and classification report"),
      caption("Figure 2. neural_network.py — successful execution (real captured output)."),

      h2("3.3 Tasks 2–5"),
      image("task2_dataset_change.png", 560, "Console output of Task 2 dataset change run"),
      caption("Figure 3. Task 2 — dataset extended to 17 students."),
      image("task3_hidden_layers.png", 560, "Console output of Task 3 hidden layer size changes"),
      caption("Figure 4. Task 3 — hidden_layer_sizes (5,) → (10,) → (10, 5)."),
      image("task4_activation.png", 560, "Console output of Task 4 activation function change"),
      caption("Figure 5. Task 4 — activation relu vs. logistic."),
      image("task5_own_student.png", 560, "Console output of Task 5 custom student prediction and summary table"),
      caption("Figure 6. Task 5 — custom student predictions and full run summary."),

      p("Accuracy figures fluctuate across configurations because the dataset is very small (12–17 rows, 3–5 test rows) and the two input features are on very different numeric scales (study hours 1–8 vs. attendance 50–95%) with no scaling applied — exactly as the handout's code specifies. The appendix run below shows that adding StandardScaler stabilizes accuracy at 1.00 across every configuration on the same data, which pinpoints unscaled features (not the model itself) as the main source of the swings seen in Tasks 2–4."),

      h2("3.4 Accuracy Comparison"),
      dataTable(
        ["Configuration", "Rows", "Hidden Layers", "Activation", "Scaled", "Test Size", "Accuracy"],
        [
          ["Task 1 baseline", "12", "(5,)", "relu", "No", "3", "66.67%"],
          ["Task 2: dataset extended", "17", "(5,)", "relu", "No", "5", "60.00%"],
          ["Task 3: (10,)", "17", "(10,)", "relu", "No", "5", "40.00%"],
          ["Task 3: (10, 5)", "17", "(10, 5)", "relu", "No", "5", "80.00%"],
          ["Task 4: logistic", "17", "(5,)", "logistic", "No", "5", "60.00%"],
          ["Appendix: (5,), scaled", "17", "(5,)", "relu", "Yes", "5", "100.00%"],
          ["Appendix: (10,), scaled", "17", "(10,)", "relu", "Yes", "5", "100.00%"],
          ["Appendix: (10, 5), scaled", "17", "(10, 5)", "relu", "Yes", "5", "100.00%"],
        ],
        [2340, 900, 1560, 1440, 1000, 1160, 960]
      ),
      p(""),
      p("Task 5 predictions on the final trained model (17 students, (5,), relu):"),
      bullet("Study Hours = 6, Attendance = 88 → Prediction: PASS"),
      bullet("Study Hours = 3, Attendance = 62 (borderline) → Prediction: PASS"),

      new Paragraph({ children: [new PageBreak()] }),

      // Guide questions
      h1("4. Answers to Guide Questions"),
      ...qa("4.1", "What are the input features in this activity?",
        "Study Hours and Attendance (%) — the two numeric columns selected as X = df[[\"study_hours\", \"attendance\"]]."),
      ...qa("4.2", "What is the target/output?",
        "The Result column, y = df[\"result\"], a binary label where 0 = Fail and 1 = Pass."),
      ...qa("4.3", "What does MLPClassifier represent?",
        "A Multi-Layer Perceptron classifier — a feedforward artificial neural network made of an input layer, one or more hidden layers, and an output layer, trained with backpropagation. It is scikit-learn's supervised neural-network classifier."),
      ...qa("4.4", "What is the purpose of the hidden layer?",
        "It lets the network learn non-linear combinations of the inputs. Each hidden neuron takes a weighted sum of study hours and attendance and passes it through an activation function; combining several such neurons lets the network represent decision boundaries a single linear layer could not."),
      ...qa("4.5", "What does the ReLU activation function do?",
        "ReLU(x) = max(0, x): it passes positive values through unchanged and outputs zero for negative values. This adds the non-linearity a neural network needs while being cheap to compute and less prone to vanishing gradients than older activations."),
      ...qa("4.6", "What happens during model.fit()?",
        "This single call runs the full training loop: for each iteration the network performs a forward pass over the training data, computes the loss between predictions and true labels, backpropagates that error to get the gradient for every weight, and updates the weights with the Adam optimizer. This repeats until the loss stops improving or max_iter (1000) is reached."),
      ...qa("4.7", "How does the neural network learn from errors?",
        "Through backpropagation: the error at the output is propagated backward layer by layer using the chain rule, producing a gradient for every weight in the network. Adam then adjusts each weight in the direction that reduces that error, so weights that contributed more to a wrong prediction are corrected more."),
      ...qa("4.8", "What is the purpose of the test dataset?",
        "It holds out data (25% here) the model never trained on, so accuracy/precision/recall reflect the model's ability to generalize to new students rather than its ability to memorize the training rows."),
      ...qa("4.9", "What does accuracy measure?",
        "The fraction of test-set predictions that matched the actual Pass/Fail label — correct predictions divided by total test predictions."),
      ...qa("4.10", "What happened when you increased the number of neurons?",
        "Going from hidden_layer_sizes=(5,) to (10,) on the 17-student dataset dropped accuracy from 60.00% to 40.00% (Table 3.4). More neurons did not automatically help — with only 17 rows, the larger network had more parameters to fit from the same small amount of data."),
      ...qa("4.11", "What happened when you added another hidden layer?",
        "Going from (10,) to (10, 5) raised accuracy from 40.00% to 80.00%, the best result among the unscaled runs. The direction of the change (better or worse) was not predictable from layer count alone — it depended on how that specific architecture happened to fit this specific small, unscaled dataset."),
      ...qa("4.12", "Why does adding more layers not automatically guarantee better results?",
        "On a dataset this small (12–17 rows), each added neuron or layer increases the number of trainable parameters relative to the amount of data available to constrain them. That raises the risk of overfitting or of gradient descent settling into a worse local optimum, rather than guaranteeing a better fit. Network depth needs to match the complexity and volume of the data, not just be maximized — confirmed here by the (10,) configuration performing worse than both the smaller (5,) and the deeper (10, 5) networks."),

      // Conclusion
      h1("5. Conclusion"),
      h2("5.1 How does the Python program demonstrate the neural-network learning process discussed in the lecture?"),
      p("Every stage of the lecture's neural-network learning cycle has a direct, one-line counterpart in the program. The raw student records become the input layer (X); MLPClassifier instantiates the network architecture, with hidden_layer_sizes fixing the hidden layer(s) and activation=\"relu\" fixing the non-linearity applied at each neuron. Calling model.fit(X_train, y_train) is where the lecture's training cycle actually executes: internally scikit-learn repeats forward pass → calculate loss → backpropagation → update weights until the loss stops improving or max_iter is hit — the exact loop from §5.6 of the handout. model.predict() is the trained network doing inference on data it has never seen, and accuracy_score() / classification_report() are the lecture's evaluation step, turning raw predictions into a measure of how well the learned weights generalize. Running the same architecture on different data (Task 2), a different capacity (Task 3), and a different activation function (Task 4) then made visible what the lecture calls generalization and overfitting: identical code produced accuracies ranging from 40% to 100% depending only on those three factors, showing concretely that a neural network's performance is inseparable from the data it is given and the capacity/activation choices made for it, not just the fact that it was “trained.”"),
      p("Overall, the exercise met its objective: a working MLPClassifier was built, trained, and evaluated end to end, and the required experiments (dataset size, network depth, activation function, and a custom prediction) produced concrete, explainable evidence — rather than assumed results — for why those design choices matter."),

      h2("5.2 Lecture Concept ↔ Python Implementation"),
      dataTable(
        ["Lecture Concept", "Python Implementation"],
        [
          ["Input Layer", "X"],
          ["Output/Target", "y"],
          ["Neural Network", "MLPClassifier"],
          ["Hidden Layer", "hidden_layer_sizes"],
          ["Activation Function", 'activation="relu"'],
          ["Training", "model.fit()"],
          ["Prediction", "model.predict()"],
          ["Loss/Optimization", "Internal training process"],
          ["Backpropagation", "Internal training process"],
          ["Evaluation", "accuracy_score()"],
          ["Classification", "Pass/Fail"],
        ],
        [4680, 4680]
      ),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("Laboratory_Report_3.docx", buffer);
  console.log("Wrote Laboratory_Report_3.docx");
});
