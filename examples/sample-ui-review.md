# Sample: UI Review

Input: terminal screenshot of a CLI tool output

Command:

```bash
mq-image analyze terminal.png --json
```

Analysis output:

```json
{
  "objects": ["text"],
  "palette": ["#0d1117", "#161b22", "#c9d1d9", "#58a6ff", "#3fb950"],
  "brightness": "dark",
  "contrast": "high contrast",
  "depth": "deep / sharp throughout",
  "composition": "left-heavy",
  "symmetry": 0.423,
  "rule_of_thirds": 0.312,
  "prompt": "terminal interface, dark scene, high contrast, deep / sharp throughout, color palette: #0d1117, #161b22, #c9d1d9, left-heavy"
}
```

## UI Review interpretation

- Dark background with high contrast — good terminal readability
- Blue accent (#58a6ff) and green (#3fb950) — standard GitHub dark palette
- Left-heavy composition — typical for CLI output (left-aligned text)
- Shallow symmetry score — expected for text-heavy terminal content

## Improvement signals

- If contrast falls below "moderate" — readability concern
- If composition is "centered" on a terminal — likely boxed output, good hierarchy
- If symmetry > 0.8 on a terminal — likely a centered dialog or modal
