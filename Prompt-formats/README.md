# Module 1: The "Hidden" Language of LLMs (Prompt Formats)

## 🎯 Goal
Teach students that LLMs don't just "understand" chat; they expect **specific raw string formats** based on how they were trained.

---

## 📚 Why This Matters

When you use ChatGPT's web interface, you type normal messages. But behind the scenes, OpenAI wraps your message in a special format called **ChatML**. 

If you use a different model (like LLaMA-2 or Alpaca), you need to use **their** format, or the model will perform poorly.

**Think of it like this:**
- English speakers expect: "Hello, how are you?"
- French speakers expect: "Bonjour, comment allez-vous?"
- LLMs expect: Their specific prompt format

---

## 🔍 The Three Major Formats

### 1. Alpaca Format
- **Origin**: Stanford's Alpaca model (fine-tuned LLaMA 1)
- **Use Case**: Older open-source models, simple instruction following
- **Structure**: Explicit headers for Instruction, Input, and Response

### 2. ChatML (Chat Markup Language)
- **Origin**: OpenAI (GPT-4), adopted by Qwen and others
- **Use Case**: Modern chat models, security-critical applications
- **Key Advantage**: Prevents prompt injection with hard token boundaries

### 3. LLaMA-2 Chat Format
- **Origin**: Meta's LLaMA 2
- **Use Case**: LLaMA-2 family models
- **Critical**: Whitespace and brackets matter!

---

## 📁 Files in This Module

1. **`alpaca_format.py`** - Alpaca format implementation and examples
2. **`chatml_format.py`** - ChatML format with security features
3. **`llama2_format.py`** - LLaMA-2 format with proper tokenization
4. **`format_comparison.py`** - Side-by-side comparison of all formats
5. **`ALPACA_GUIDE.md`** - Detailed Alpaca documentation
6. **`CHATML_GUIDE.md`** - Detailed ChatML documentation
7. **`LLAMA2_GUIDE.md`** - Detailed LLaMA-2 documentation

---

## 🚀 Quick Start

```bash
# Run Alpaca examples
python alpaca_format.py

# Run ChatML examples
python chatml_format.py

# Run LLaMA-2 examples
python llama2_format.py

# Compare all formats
python format_comparison.py
```

---

## 🎓 Learning Objectives

By the end of this module, you will:

- ✅ Understand why prompt formats exist
- ✅ Know when to use each format
- ✅ Implement all three major formats
- ✅ Recognize format errors in model outputs
- ✅ Choose the right format for your model

---

## 🔑 Key Concepts

### Raw String Templates
These are the **actual strings** the model sees, not what you type in a chat interface.

### Special Tokens
Tokens like `<|im_start|>`, `[INST]`, and `###` are not regular text - they're special markers the model was trained to recognize.

### Whitespace Matters
In LLaMA-2 format especially, extra spaces or missing newlines can break the model's understanding.

---

## 📊 Format Comparison Table

| Format | Complexity | Security | Use Case |
|--------|-----------|----------|----------|
| **Alpaca** | Low | Medium | Simple tasks, older models |
| **ChatML** | Medium | High | Modern chat, production |
| **LLaMA-2** | High | Medium | LLaMA-2 family only |

---

## 🛠️ Practical Exercise

**Task**: Take this user message: "Explain quantum computing"

Format it in all three styles:
1. Alpaca format
2. ChatML format
3. LLaMA-2 format

Then run `format_comparison.py` to see the differences!

---

## 📖 Additional Resources

- [Alpaca Paper](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [ChatML Specification](https://github.com/openai/openai-python/blob/main/chatml.md)
- [LLaMA-2 Model Card](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)

---

## ⚠️ Common Mistakes

1. **Mixing Formats**: Don't use Alpaca format with a ChatML model
2. **Missing Tokens**: Forgetting `<|im_end|>` or `[/INST]`
3. **Wrong Whitespace**: Extra spaces in LLaMA-2 format
4. **No System Message**: ChatML works best with a system message

---

## 🎯 Next Module

Once you understand prompt formats, move to **Module 2: Structured Outputs** to learn how to get JSON instead of text!

---

**Duration**: 30 minutes  
**Difficulty**: Beginner  
**Prerequisites**: Basic Python knowledge
