---
name: vision-regression-eval
description: Compare mq-image-analyze model, backend or prompt changes on the same reference images with traceable outputs. Use for "blev den nya modellen sämre", "jämför vision-backends", or "utvärdera promptändringen"; exclude pixel-only screenshot regression and model installation.
---

# Vision Regression Eval

Evaluate semantic perception changes using controlled inputs. This skill is
for comparing outputs, not installing models or granting permission for cloud
calls. Pixel/OCR screenshot regression already exists in `mq-image regress`;
it does not measure whether a vision model's interpretation is correct.

## Establish the comparison

Read current provider code and CLI help for supported modes, model defaults,
flags and output contracts. Start with
`mq_image_analyze/vision/semantic/provider.py` and its provider tests. Do not
copy model names from old memory or assume a benchmark command exists.

Use the same authorized images for baseline and candidate. Record image hashes,
source revision, mode, exact model identifier, prompt/settings and runtime
metadata exposed by the provider. Freeze preprocessing and task instructions;
change only the variable under evaluation where possible.

Agree on the task-specific criteria before examining candidate results:
object presence, OCR accuracy, spatial relations, unsupported claims, schema
validity, latency or resource usage as appropriate. Operator-supplied labels
are ground truth; AI-drafted labels require operator confirmation and must be
marked accordingly. A schema-valid response is not proof of factual accuracy.

## Run and interpret

- Save paired raw outputs and errors in a scratch directory with provenance.
  Keep missing responses, unavailable backends and timeouts visible.
- For nondeterministic providers, use a bounded repeat count and disclose it.
  Separate measured timing from estimates and note warm-up/cache differences.
- Present per-image differences and the common evaluated population before
  aggregates. Do not compare averages across different input sets or hide
  failed cases by silently dropping them.
- Do not invent confidence scores, thresholds or benchmark results. If no
  confirmed labels exist, report a qualitative comparison and its limits.
- Report recommendations separately from observed changes. Preserve baselines;
  changing production defaults or accepting a new baseline is a separate action.

Use local authorized inputs by default. Send images to cloud providers only
within the user's authorized scope. Do not download weights or modify
production evidence stores to complete an evaluation.

## Evals

- "Compare old and new models on these diagrams" → use this skill.
- "Evaluate a prompt change on the same screenshots" → use this skill.
- "Find moved buttons between screenshot folders" → existing regress workflow.
- "Doctor cannot find the model" → model-setup-maintainer.
