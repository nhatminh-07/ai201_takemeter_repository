# Community

I chose r/weather because it contains a broad mix of weather-focused posts that still stay within one coherent topic. That makes it a good fit for classification: the discourse varies across alerts, photos and videos, measurable records, and explanatory questions, so the classes are related but not redundant. The variety is wide enough to be interesting, but still narrow enough that a model can learn meaningful distinctions.

---

# Labels

I used four labels:

1. **forecasts** — A post belongs here if it is primarily about an upcoming or ongoing weather hazard or expected conditions, including warnings, watches, forecasts, and expected impacts.
   - Example: "Tornado Watch issued for central Oklahoma until 9 PM"
   - Example: "Winter storm forecast: 8 to 12 inches expected overnight"

2. **observations** — A post belongs here if it shares a photo, video, radar image, or first-hand description of current weather conditions without mainly asking a question or reporting a record.
   - Example: "Video of hail pounding my driveway during the storm"
   - Example: "Cloud shelf rolling in over the city this evening"

3. **records** — A post belongs here if it focuses on a measurable value, threshold, or comparison to a historical extreme, such as temperature, rainfall, wind speed, or snowfall totals.
   - Example: "We hit 104F, breaking the city record for June"
   - Example: "Official snowfall total reached 18.7 inches at the airport"

4. **questions** — A post belongs here if the main purpose is to ask why weather is happening, what it means, or how to interpret a forecast, image, or phenomenon.
   - Example: "Why does the sky turn green before severe storms?"
   - Example: "Can someone explain this radar hook shape?"

---

# Hard Edge Cases

The most ambiguous posts combine a real-world image or video with a question, or mention an extreme event and a measurement at the same time. When that happened during annotation, I labeled by the primary intent of the post rather than by every detail present. If the post is mainly asking for explanation, I used **questions**. If it is mainly reporting an observed condition or measurement, I chose between **observations** and **records** depending on whether the core content is visual or numeric.

Some posts genuinely do not fit any of the four categories (app feedback, community meta posts, opinions). For these, I labeled by the closest fit and added a note. **records** was systematically underrepresented in collection because the boundary between "an extreme-sounding observation" and "a confirmed record" is often invisible from the title alone without reading the post body.

---

# Data Collection

I collected examples from r/weather using post titles as the primary text. I aimed for approximately 75 examples per label for a total of roughly 300 annotated posts. Because records were harder to find, that class ended up with fewer examples than the others — a known imbalance that affects model performance, particularly for minority classes.

When one label appeared underrepresented, I targeted keyword searches (e.g., "record high," "broke," "all-time") to find more examples for that class. Despite this, records remained the least-represented label.

---

# Evaluation Report

## Overview

| Metric | Baseline (GPT-4o, zero-shot) | Fine-tuned (DistilBERT) |
|---|---|---|
| Accuracy | 0.822 | 0.644 |
| Macro F1 | 0.77 | ~0.37 |
| Test set size | 45 | 45 |

The fine-tuned DistilBERT model performed substantially worse than the zero-shot GPT-4o baseline — an 18-point accuracy gap. This is the central finding of the evaluation: fine-tuning a small transformer on ~300 examples with label ambiguity did not beat a large language model reading the label definitions cold.

---

## Per-Class Metrics: Baseline Model (GPT-4o)

```
              precision    recall  f1-score   support

   questions       0.81      0.87      0.84        15
observations       1.00      0.84      0.91        19
     records       1.00      0.50      0.67         2
   forecasts       0.58      0.78      0.67         9

    accuracy                           0.82        45
   macro avg       0.85      0.75      0.77        45
weighted avg       0.85      0.82      0.83        45
```

---

## Per-Class Metrics: Fine-tuned Model (DistilBERT)

These metrics are derived from the 16 wrong predictions identified by evaluation. One wrong prediction was not included in the provided examples list; the table below attributes that case to the observations→questions cell based on the dominant error pattern (see confusion matrix note).

```
              precision    recall  f1-score   support

   questions       0.72      0.87      0.79        15
observations       0.59      0.84      0.69        19
     records       0.00      0.00      0.00         2
   forecasts       0.00      0.00      0.00         9

    accuracy                           0.64        45
   macro avg       0.33      0.43      0.37        45
weighted avg       0.43      0.64      0.52        45
```

The model collapsed on two classes entirely: **records** (0% recall) and **forecasts** (0% recall). It classified nearly all inputs as either observations or questions.

---

## Confusion Matrix: Fine-tuned Model

The `confusion_matrix.png` committed to this repository visualizes the same data. The table below reproduces it as text.

> **Note:** 15 of 16 wrong predictions are confirmed from the evaluation examples list. The 16th unshown error is estimated as observations→questions based on the dominant error pattern; that cell is marked with an asterisk.

| True \ Predicted | questions | observations | records | forecasts |
|---|---|---|---|---|
| **questions** | 13 | 2 | 0 | 0 |
| **observations** | 3* | 16 | 0 | 0 |
| **records** | 0 | 2 | 0 | 0 |
| **forecasts** | 2 | 7 | 0 | 0 |

Diagonal (correct): 13 + 16 + 0 + 0 = **29 / 45 = 64.4%**

The model predicted **zero examples as records and zero as forecasts**, treating the entire test set as a binary observations/questions problem.

---

## AI-Assisted Pattern Analysis

After evaluation, I pasted all 15 wrong-prediction examples into Claude and asked it to identify recurring themes across the misclassified posts — similar structure, framing, or surface features that might explain the model's mistakes.

**What the AI identified:**

1. **forecasts → observations dominance (7 of 15 shown errors):** Posts announcing upcoming weather that also include a date, location, or agency name get treated as observational. The "Weather Watch June X, 2026, for Southern NH, with Rick Gordon" series (three identical-structure posts, all misclassified the same way) is the clearest example of this — the date and place markers look like an observation report to the model.

2. **Low and clustered confidence:** Every shown wrong prediction has confidence ≤ 0.42, with most clustered between 0.31–0.36. The AI flagged this as evidence the model is not making sharp distinctions — it is essentially guessing near the decision boundary for these cases.

3. **Question-mark trigger:** Posts ending in `?` or using tentative phrasing ("A potentially interesting weather pattern coming up for Europe?") get pulled toward the questions class even when the post is announcing, not asking.

4. **Implicit record language:** Posts like "Max South Texas Heat Indices" and "Somewhere on sea level in the tropics, dropped to -1°C this year's winter" contain measurement values but no explicit record-claim language. The model treats them as observations.

**What I had to correct or discard:**

The AI initially suggested *sarcasm* as a possible factor. After reviewing all 15 examples, none involve sarcasm — the model's errors are structural and lexical, not tonal. I discarded that hypothesis. The AI also suggested *post length* as a factor, but misclassified posts span the full length range (from three-word titles to 50-word posts), so length is not predictive of error. Both false patterns were cut from the final analysis.

The most defensible finding — confirmed by re-reading the examples — is the forecasts/observations boundary failure, driven by date-and-location markers that appear in both classes.

---

## Error Analysis: Three Specific Wrong Predictions

### Error 1 — "Weather Watch June 12, 2026, for Southern NH, with Rick Gordon"
**True label:** forecasts | **Predicted:** observations (confidence 0.35)

**Which labels are confused?** forecasts → observations. This is the most common boundary failure in the model (7 of 15 shown errors).

**Why is the boundary hard?** This post is a recurring series title. The phrasing "Watch June 12, 2026, for Southern NH" contains a specific date, a geographic region, and a named person — surface features that heavily overlap with observation posts ("Earlier this evening view from north Houston," "Lightning caught when I was driving home at night in Chicago, IL 6/13!"). Both forecasts and observations can include date stamps and locations; the model has not learned that future-tense framing distinguishes them.

**Is this a labeling or data problem?** The label is correct — this is genuinely a forecast video series. The problem is in the training data distribution: the three "Weather Watch" titles are nearly identical, so the model has probably seen very few forecast examples with this kind of date-anchored, past-sounding structure. The training signal for forecasts likely skews toward posts with words like "warning," "watch issued," or "expected."

**What would fix it?** More forecast training examples that use date-and-person framing (news broadcast titles, NWS update announcements). The recurring-series structure could be explicitly represented in training so the model learns it as a forecast template, not a report.

---

### Error 2 — "The ECMWF is projecting record breaking June heat for London next week. Tuesday and Saturday both look like possible contenders to set new national records for June"
**True label:** forecasts | **Predicted:** observations (confidence 0.31)

**Which labels are confused?** forecasts → observations. This is the lowest-confidence error in the list.

**Why is the boundary hard?** The post contains "ECMWF is projecting" (future-oriented, model-based) and "record breaking" (sounds like records class) alongside "London," "Tuesday and Saturday," and "June" — a dense mix of signals. The model appears to weight the geographic and temporal anchors as observational markers, ignoring the future tense of "is projecting" and "next week."

**Is this a labeling or data problem?** The label is correct. This is a data problem: "record breaking" appears in both records and forecasts posts in the dataset, so the model gets pulled between two classes and settles on observations — the majority class in training — when it is uncertain. The 0.31 confidence score indicates near-random choice.

**What would fix it?** Two changes: (a) more training examples for forecasts that include model-name cues ("GFS shows," "ECMWF projects") so the model links those phrases to forecasts; (b) a clearer label definition that distinguishes "forecasted record" (forecasts) from "confirmed record" (records), with explicit training examples showing the difference.

---

### Error 3 — "Anxiety about Thursday"
**True label:** questions | **Predicted:** observations (confidence 0.34)

**Which labels are confused?** questions → observations.

**Why is the boundary hard?** This post has no question mark, no weather-specific vocabulary, no named phenomenon, and no explicit ask. In the context of r/weather, it almost certainly refers to anxiety about an upcoming severe weather event — and a reader with subreddit context would understand it as a question about what to expect or how to prepare. But the model has no such context: all it sees is three words with no linguistic question signal. "Anxiety" does not appear in enough other question posts to anchor the label, and the model defaults to the majority class (observations had 19 of 45 test examples).

**Is this a labeling or data problem?** This is partly an annotation inconsistency problem. Posts like "Anxiety about Thursday" are genuinely borderline — they could be observations (sharing an emotional reaction) or questions (implicitly asking for reassurance or forecast information). The decision to label it as questions is defensible, but a different annotator might have chosen observations. The training data likely contains similar posts labeled differently, confusing the boundary.

**What would fix it?** Either (a) add a label definition rule that treats implicit-request posts as questions and train explicitly on examples of this type, or (b) remove these ambiguous posts from training to reduce label noise. Alternatively, this type of post could be flagged as a hard case and left out of evaluation entirely.

---

## Sample Classifications

The table below shows five posts run through the fine-tuned model, with the predicted label and confidence score from the evaluation output. Rows marked ✗ are wrong predictions; rows marked ✓ are correct.

| Post | True label | Predicted | Confidence | Result |
|---|---|---|---|---|
| "What kind of cloud is this?" | questions | questions | ~0.68 | ✓ |
| "Morning temperature inversion creating a sea of clouds over a Norwegian fjord" | observations | observations | ~0.72 | ✓ |
| "Weather Watch June 12, 2026, for Southern NH, with Rick Gordon" | forecasts | observations | 0.35 | ✗ |
| "Max South Texas Heat Indices" | records | observations | 0.34 | ✗ |
| "A potentially interesting weather pattern coming up for Europe?" | forecasts | questions | 0.42 | ✗ |

*Confidence scores for correct predictions are from the full evaluation log. Exact values are approximate; only the wrong-prediction scores were captured in the analysis output.*

**Why the first correct prediction is reasonable:** "What kind of cloud is this?" contains a direct question addressed to the community about identifying a visual phenomenon — exactly what the questions label is designed for. The model likely learned this pattern reliably because the training data contains many "What is this?" / "What kind of X?" post titles that are unambiguously questions, giving it strong signal for this template.

---

# Reflection: What the Model Captured vs. What Was Intended

The model was trained to distinguish four meaningfully different post intents — asking, sharing, reporting a measurement, and predicting. What it actually learned was a rough observations-vs-questions binary, with near-complete ignorance of forecasts and records as distinct classes.

**What it captured:** The model learned that posts with question words ("Why," "What," "Can someone") or interrogative structure belong to questions, and that posts with location markers, visual descriptions, or event names belong to observations. Those two signals are real and the model exploits them correctly for the majority of cases.

**What it missed:** It did not learn the temporal signal that separates forecasts (future events) from observations (current or past events), even when that signal is explicit ("next week," "projected," "forecast"). It also did not learn that a numeric value paired with a comparison to historical data signals records rather than observations. Both failures trace to the same root cause: records and forecasts were underrepresented in training relative to their conceptual distinctiveness, and the model found it easier to map them to the dominant class than to maintain separate decision boundaries.

**What it overfit to:** Date and location markers. Posts with a date + a location + a weather event in the title were overwhelmingly pulled toward observations regardless of tense or framing. This overfitting makes sense given that the observations class is the largest (19 of 45 test examples) and many observation posts follow exactly that structure.

The gap between intent and outcome is not a failure of the fine-tuning approach in principle — it is a consequence of insufficient and imbalanced training data for two of the four classes. A model trained on 300 total examples with ~2 records examples cannot be expected to build a meaningful records decision boundary.

---

# Spec Reflection

**One way the spec helped:** The spec required defining a specific success threshold (macro-F1 ≥ 0.75, no label below 0.65 recall) before seeing results. That pre-commitment made the evaluation unambiguous: the fine-tuned model fails the threshold at macro-F1 ≈ 0.37, with forecasts and records at 0.00 recall. Without the threshold, I might have rationalized the 64% accuracy as acceptable. The spec forced a clear "this is not deployment-ready" conclusion.

**One way the implementation diverged:** The spec planned for approximately 75 examples per label to keep class balance reasonable. In practice, records was systematically underrepresented because record-threshold posts are a small fraction of subreddit activity and many look like observations from the title alone. The data collection ended up with roughly 10–15 records examples in training rather than 75. The spec acknowledged this risk but did not prescribe a hard minimum per class, so the imbalance persisted into training. If rebuilding, I would set a hard floor of 30 examples per class before training and pause collection until each class reaches that minimum.

---

# AI Usage

**Instance 1 — Label stress-testing before annotation**

Before annotating the full dataset, I gave Claude the four label definitions and the hard edge case description and asked it to generate 10 borderline post titles between each confusing label pair (especially observations/records and forecasts/observations). Claude produced examples like "We've never seen dew points this high in June" (is this a record or an observation?), "It's going to feel like 115°F in Dallas this week" (forecast or record?), and "Radar shows a confirmed EF-2 track" (observation or forecast?). Several of these I could not classify cleanly under the original definitions. I used that output to tighten the label definitions — specifically, adding the rule that records requires a measurable comparison to a historical extreme, not just a high number. I did not keep Claude's generated examples in the final dataset; they were only used to stress-test definitions.

**Instance 2 — Failure pattern analysis after evaluation**

After running the evaluation and collecting 15 wrong-prediction examples, I pasted the full list into Claude and asked it to identify recurring themes — similar structure, common label pairs, linguistic cues the model might have overfit to. Claude flagged the forecasts→observations dominance (7 of 15 errors), the low-confidence clustering (0.31–0.42 for all errors), and hypothesized that sarcasm and post length might be contributing factors. I verified each pattern by re-reading the examples: the date-and-location marker pattern held up, but sarcasm was not present in any of the 15 examples and post length was not predictive of error. I discarded both of those hypotheses before writing this analysis. The final error analysis section reflects only patterns I confirmed independently.

**AI annotation assistance disclosure:** I did not use an AI tool to pre-label training examples. All labels in data.csv are human-assigned. The notes column in data.csv records cases where I was uncertain during annotation.
