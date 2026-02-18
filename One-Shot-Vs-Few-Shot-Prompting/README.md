Assignment: One-Shot vs Few-Shot Prompting
Objective:
Compare one-shot and few-shot prompting using a structured data extraction task.
Task:
Extract from customer feedback:

- sentiment (positive/negative/neutral)
- product
- issue_type
- urgency_level (low/medium/high)
  Steps:

1. One-Shot Prompt
   Write a single instruction and test it on:
   "I ordered the X200 router. It disconnects every 10 minutes. Fix ASAP."
   Evaluate accuracy, JSON format correctness, hallucination, and consistency.
2. Few-Shot Prompt
   Add 2 examples before the same test input.
   Run and compare output quality.
3. Comparison
   Create a small table comparing:

- Accuracy
- Format stability
- Hallucination
- Token cost
- Bias effects

4. Theory (Short Answers)

- Why does few-shot prompting work?
- What is in-context learning?
- When is one-shot better?
- How can bad examples degrade performance?
  Deliverables:
- One-shot prompt + output
- Few-shot prompt + output
- Comparison table
- 200–300 word analysis
