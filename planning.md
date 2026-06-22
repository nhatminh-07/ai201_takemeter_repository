# Planning

# Community
I chose r/weather because it contains a broad mix of weather-focused posts that still stay within one coherent topic. That makes it a good fit for classification: the discourse varies across alerts, photos and videos, measurable records, and explanatory questions, so the classes are related but not redundant. The variety is wide enough to be interesting, but still narrow enough that a model can learn meaningful distinctions.

# Labels
I will use four labels.

1. Severe weather alert or forecast: A post belongs here if it is primarily about an upcoming or ongoing weather hazard, including warnings, watches, forecasts, and expected impacts.
	- Example post: "Tornado Watch issued for central Oklahoma until 9 PM"
	- Example post: "Winter storm forecast: 8 to 12 inches expected overnight"

2. Weather observation or media: A post belongs here if it shares a photo, video, radar image, or first-hand description of current weather conditions without mainly asking a question or reporting a record.
	- Example post: "Video of hail pounding my driveway during the storm"
	- Example post: "Cloud shelf rolling in over the city this evening"

3. Weather record or measurement: A post belongs here if it focuses on a measurable value, threshold, or comparison to a historical extreme, such as temperature, rainfall, wind speed, or snowfall totals.
	- Example post: "We hit 104F, breaking the city record for June"
	- Example post: "Official snowfall total reached 18.7 inches at the airport"

4. Weather question or explanation: A post belongs here if the main purpose is to ask why weather is happening, what it means, or how to interpret a forecast, image, or phenomenon.
	- Example post: "Why does the sky turn green before severe storms?"
	- Example post: "Can someone explain this radar hook shape?"

# Hard Edge Cases
The most ambiguous posts will be ones that combine a real-world image or video with a question, or posts that mention an extreme event and a measurement at the same time. For example, a post might show a hail photo and ask whether the storm qualifies as severe, or it might mention a record temperature while also asking why the heat wave happened.

When that happens during annotation, I will label by the primary intent of the post rather than by every detail present. If the post is mainly asking for explanation, I will use Weather question or explanation. If it is mainly reporting an observed condition or measurement, I will use Weather observation or media or Weather record or measurement depending on whether the core content is visual or numeric. I will keep a short note of repeated borderline cases and tighten the label definitions before continuing if the same ambiguity appears often.

# Data Collection Plan
I will collect examples from r/weather using post titles, self-text, and linked media context when available. I will aim for about 75 examples per label for a total of roughly 300 annotated posts, which is enough to train and evaluate a small classifier without making the annotation burden too large.

If one label is underrepresented after 200 total examples, I will collect more targeted examples for that label by searching subreddit posts with keywords and event types that match the missing category. I will also rebalance by over-sampling the underrepresented label in the annotation queue until each class has a usable minimum count.

# Evaluation Metrics
Accuracy alone is not enough because the labels are related and the class distribution may be uneven. A model could look good on accuracy by over-predicting the most common label while still failing on the minority classes.

I will use macro-averaged F1 as the main metric because it treats each label equally and penalizes a model that ignores a hard class. I will also report per-class precision and recall so I can see whether the model is missing posts from a particular label or over-labeling them. A confusion matrix will help me see which labels are being confused most often, especially around the boundary cases between observation, record, and question.

# Definition of Success
This classifier will be genuinely useful if it can route posts into the right review bucket with enough reliability that a moderator or community tool can trust it as a first pass. I will consider the model good enough for deployment if it reaches at least 0.75 macro-F1 on the held-out test set, with no label below 0.65 recall and no label below 0.70 precision.

These thresholds are specific enough to judge objectively at the end of the project: I will compute the metrics on the final test set once, compare them to the thresholds above, and decide success or failure based on that result. If the model misses those targets, I will treat it as a useful prototype but not deploy it as a community-facing classifier.

# Original Plans
## AI Tool Plan
### Label Stress-Testing
Before annotating the full dataset, I will give an AI tool the label definitions and hard edge case description and ask it to generate 5 to 10 borderline posts between each confusing pair of labels. If I cannot classify several of those examples cleanly, I will tighten the label definitions immediately and rerun the stress test before continuing.

### Annotation Assistance
I may use an LLM to pre-label batches of examples before I review them manually, but the final label will always be human-checked. If I do this, I will record which examples were pre-labeled by the model so I can disclose that assistance in the AI usage section and avoid mixing machine suggestions with final annotations.

### Failure Analysis
After evaluation, I will provide the model's wrong predictions to an AI tool and ask it to identify recurring error patterns, such as confusion between alerts and questions or mistakes on extreme-but-not-official record posts. I will verify any pattern myself by checking the underlying posts and confusion matrix before I include the interpretation in the final write-up.




