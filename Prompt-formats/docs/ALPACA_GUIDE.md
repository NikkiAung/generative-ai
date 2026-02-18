# Alpaca Prompt Format - Complete Guide

## 📚 Overview

**Alpaca** is a prompt format developed by Stanford University for their Alpaca model, which was created by fine-tuning Meta's LLaMA model on instruction-following data.

---

## 🎯 What is Alpaca Format?

Alpaca format uses **explicit text headers** to separate different parts of a prompt:
- `### Instruction:` - The task to perform
- `### Input:` - Optional context or data (can be omitted)
- `### Response:` - Where the model generates its answer

---

## 📝 Basic Structure

### Without Input (Simple Instruction)
```
### Instruction:
{your_instruction_here}

### Response:
```

### With Input (Instruction + Context)
```
### Instruction:
{your_instruction_here}

### Input:
{your_context_or_data_here}

### Response:
```

---

## 🔍 Detailed Breakdown

### The Headers

1. **`### Instruction:`**
   - Describes the task
   - Should be clear and specific
   - Can include examples or constraints
   - Always required

2. **`### Input:`**
   - Provides context or data for the task
   - Optional (skip if not needed)
   - Can be text, JSON, code, etc.
   - Separates instruction from data

3. **`### Response:`**
   - Marks where the model should respond
   - Always ends with a newline
   - Model generates text after this marker
   - Always required

---

## ✅ Best Practices

### 1. Clear Instructions
```
✅ GOOD:
### Instruction:
Extract the person's name, age, and occupation from the text. Format as JSON.

❌ BAD:
### Instruction:
Get info from text
```

### 2. Separate Instruction from Data
```
✅ GOOD:
### Instruction:
Summarize the following article in 2 sentences.

### Input:
[Long article text here]

❌ BAD:
### Instruction:
Summarize this: [Long article text here]
```

### 3. Consistent Formatting
```
✅ GOOD:
### Instruction:
Translate to French.

### Input:
Hello, how are you?

### Response:


❌ BAD:
###Instruction:
Translate to French.
###Input:
Hello, how are you?
###Response:
```

---

## 📊 Use Cases

### 1. Simple Question Answering
```
### Instruction:
What is the capital of France?

### Response:
```

### 2. Text Summarization
```
### Instruction:
Summarize the following text in one sentence.

### Input:
Artificial intelligence is rapidly transforming industries...

### Response:
```

### 3. Data Extraction
```
### Instruction:
Extract all email addresses from the text.

### Input:
Contact us at support@example.com or sales@example.com

### Response:
```

### 4. Code Generation
```
### Instruction:
Write a Python function to calculate fibonacci numbers.

### Response:
```

### 5. Classification
```
### Instruction:
Classify the sentiment as POSITIVE, NEGATIVE, or NEUTRAL.

### Input:
This product is amazing! Best purchase ever.

### Response:
```

---

## ⚙️ Implementation in Python

```python
def create_alpaca_prompt(instruction: str, input_text: str = "") -> str:
    """
    Create a prompt in Alpaca format.
    
    Args:
        instruction: The task instruction
        input_text: Optional context/data
    
    Returns:
        Formatted Alpaca prompt
    """
    prompt = f"### Instruction:\n{instruction}\n\n"
    
    if input_text:
        prompt += f"### Input:\n{input_text}\n\n"
    
    prompt += "### Response:\n"
    
    return prompt

# Example usage
prompt = create_alpaca_prompt(
    instruction="Translate to Spanish",
    input_text="Hello, how are you?"
)
print(prompt)
```

---

## 🔄 Comparison with Other Formats

| Aspect | Alpaca | ChatML | LLaMA-2 |
|--------|--------|--------|---------|
| **Complexity** | Low | Medium | High |
| **Headers** | `###` text | Special tokens | `[INST]` tags |
| **Multi-turn** | Not designed for it | Native support | Native support |
| **Security** | Medium | High | Medium |
| **Use Case** | Single-turn tasks | Chat applications | LLaMA-2 models |

---

## ⚠️ Common Mistakes

### 1. Wrong Header Format
```
❌ WRONG:
## Instruction:  (only 2 #)
Instruction:    (no #)
###Instruction: (no space)

✅ CORRECT:
### Instruction:
```

### 2. Missing Newlines
```
❌ WRONG:
### Instruction:
Translate this.
### Input:
Hello

✅ CORRECT:
### Instruction:
Translate this.

### Input:
Hello
```

### 3. Forgetting Response Header
```
❌ WRONG:
### Instruction:
What is AI?

✅ CORRECT:
### Instruction:
What is AI?

### Response:
```

---

## 🎯 When to Use Alpaca Format

### ✅ Use Alpaca When:
- Working with Alpaca or Vicuna models
- Single-turn instruction-following tasks
- Clear input/output scenarios
- Creating fine-tuning datasets
- Simple, straightforward tasks

### ❌ Don't Use Alpaca When:
- Building multi-turn chatbots (use ChatML)
- Working with LLaMA-2 models (use LLaMA-2 format)
- Using modern OpenAI models (use ChatML)
- Need advanced security features

---

## 📖 Examples

### Example 1: Translation
```
### Instruction:
Translate the following English text to German.

### Input:
Good morning! How can I help you today?

### Response:
```

### Example 2: Code Explanation
```
### Instruction:
Explain what this Python code does in simple terms.

### Input:
def factorial(n):
    return 1 if n <= 1 else n * factorial(n-1)

### Response:
```

### Example 3: Creative Writing
```
### Instruction:
Write a short poem about artificial intelligence.

### Response:
```

---

## 🔗 Resources

- [Alpaca Paper](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [Alpaca GitHub](https://github.com/tatsu-lab/stanford_alpaca)
- [Alpaca Dataset](https://huggingface.co/datasets/tatsu-lab/alpaca)

---

## 💡 Pro Tips

1. **Be Specific**: Clear instructions = better results
2. **Use Input Field**: Separate task from data
3. **Include Examples**: Show desired format in instruction
4. **Test Variations**: Try different phrasings
5. **Keep It Simple**: Alpaca works best for straightforward tasks

---

**Last Updated**: January 2026  
**Format Version**: Original Alpaca (2023)
