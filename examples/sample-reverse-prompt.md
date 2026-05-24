# Sample: Reverse Prompt

Input: dark cinematic UI screenshot

Command:

```bash
mq-image analyze screenshot.png --json | jq '.prompt'
```

Output:

```text
"person, monitor, terminal, dark scene, moderate contrast, shallow depth of field, color palette: #0a0a0f, #1c1f2e, #3a4a6b, centered, rule-of-thirds alignment"
```

Full structured breakdown:

```json
{
  "objects": ["person", "monitor", "terminal"],
  "palette": ["#0a0a0f", "#1c1f2e", "#3a4a6b", "#c8d4e8", "#f0f4ff"],
  "brightness": "dark",
  "contrast": "moderate contrast",
  "depth": "shallow depth of field",
  "composition": "centered, rule-of-thirds alignment",
  "symmetry": 0.871,
  "rule_of_thirds": 0.453,
  "prompt": "person, monitor, terminal, dark scene, moderate contrast, shallow depth of field, color palette: #0a0a0f, #1c1f2e, #3a4a6b, centered, rule-of-thirds alignment"
}
```

## Use in image generation

```text
Midjourney: /imagine person, monitor, terminal, dark scene, moderate contrast, shallow depth of field, color palette: #0a0a0f, #1c1f2e, #3a4a6b, centered --ar 16:9
```
