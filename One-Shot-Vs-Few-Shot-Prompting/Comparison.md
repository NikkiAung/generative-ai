# One-Shot vs Few-Shot Prompting — Comparison

## Test Input

> "I ordered the X200 router. It disconnects every 10 minutes. Fix ASAP."

## Outputs

**Zero-Shot:**

```json
{
  "sentiment": "negative",
  "product": "X200 router",
  "issue_type": "connectivity issues",
  "urgency_level": "high"
}
```

**Few-Shot (3 examples):**

```json
{
  "sentiment": "negative",
  "product": "X200 router",
  "issue_type": "frequent disconnections",
  "urgency_level": "high"
}
```

---

## Comparison Table

| Criteria             | Zero-Shot                                                    | Few-Shot                                                              |
| -------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------- |
| **Accuracy**         | Correct but vague (`connectivity issues`)                    | More precise (`frequent disconnections`)                              |
| **Format Stability** | Pretty-printed multi-line JSON — format may vary across runs | Compact single-line JSON — consistent with examples                   |
| **Hallucination**    | Low — all fields grounded in input                           | Low — examples anchor the output further                              |
| **Token Cost**       | Lower — short system prompt                                  | Higher — 3 examples add ~100 extra tokens                             |
| **Bias Effects**     | Neutral; model uses broad training knowledge                 | Examples can bias output style (e.g. compact JSON, specific phrasing) |

---

## Key Takeaway

- **Zero-shot** is cheaper and simpler but produces less precise and less predictable formatting.
- **Few-shot** improves specificity and format consistency at the cost of a slightly larger prompt.
- For structured extraction tasks (like JSON output), few-shot is generally preferred.
- For case like when you need quick answers, the task is straightforward, and you don't have examples to provide, **Zero-shot** is preferred.
- In-context learning is the ability of a language model to learn a new task at inference time by conditioning on examples provided directly in the prompt without any weight updates or fine-tuning. All learning is "in the context window"
- Bad examples are particularly damaging in in-context learning (ICL) because the model treats them as ground truth for the task. Several failure modes:
  If examples have incorrect labels, the model learns the wrong mapping:
  ```
  # The model will flip its own classifications to match the bad pattern.
  "The movie was amazing" → Negative ← wrong!
  "Terrible experience" → Positive ← wrong!
  ```
