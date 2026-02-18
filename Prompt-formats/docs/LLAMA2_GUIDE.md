# LLaMA-2 Chat Format - Complete Guide

## 📚 Overview

**LLaMA-2 Chat Format** is Meta's specialized prompt format for their LLaMA-2 Chat models. It uses a complex structure with `[INST]` tags and `<<SYS>>` tokens, and is **extremely sensitive to whitespace**.

---

## 🎯 What is LLaMA-2 Format?

LLaMA-2 uses a unique combination of:
- `<s>` and `</s>` - Beginning/End of sequence tokens
- `[INST]` and `[/INST]` - Instruction boundaries
- `<<SYS>>` and `<</SYS>>` - System message markers
- **Precise whitespace** - Extra spaces break the model!

---

## 📝 Basic Structure

### Single-Turn Format
```
<s>[INST] <<SYS>>
{system_message}
<</SYS>>

{user_message} [/INST]
```

### Multi-Turn Format
```
<s>[INST] <<SYS>>
{system_message}
<</SYS>>

{user_msg_1} [/INST] {assistant_response_1} </s><s>[INST] {user_msg_2} [/INST]
```

---

## 🔍 Detailed Breakdown

### Special Tokens

1. **`<s>`** - Beginning of Sequence (BOS)
   - Marks the start of a new sequence
   - Required at the beginning
   - Also used between turns in multi-turn

2. **`</s>`** - End of Sequence (EOS)
   - Marks the end of assistant's response
   - Signals completion
   - Used between turns

3. **`[INST]`** - Start of Instruction
   - Opens the instruction block
   - Contains user message
   - Required for every user turn

4. **`[/INST]`** - End of Instruction
   - Closes the instruction block
   - Model generates response after this
   - Required for every user turn

5. **`<<SYS>>`** and `<</SYS>>`** - System Message
   - Wraps the system instruction
   - Only in the FIRST turn
   - Sets model behavior

---

## ⚠️ CRITICAL: Whitespace Matters!

### Correct Whitespace (EXACT format)
```
<s>[INST] <<SYS>>
You are helpful.
<</SYS>>

What is AI? [/INST]
```

**Key Points:**
- Newline AFTER `<<SYS>>`
- Newline BEFORE `<</SYS>>`
- **TWO newlines** after `<</SYS>>`
- Space before `[/INST]`

### Common Whitespace Mistakes

❌ **Missing newline after <<SYS>>**
```
<s>[INST] <<SYS>>You are helpful.
```

❌ **Missing double newline**
```
<s>[INST] <<SYS>>
You are helpful.
<</SYS>>
What is AI? [/INST]
```

❌ **Extra spaces**
```
<s>[INST]  <<SYS>>
```

---

## 📊 Single-Turn vs Multi-Turn

### Single-Turn (One Question)
```
<s>[INST] <<SYS>>
You are a helpful assistant.
<</SYS>>

What is Python? [/INST]
```

Model responds here, then `</s>`

### Multi-Turn (Conversation)
```
<s>[INST] <<SYS>>
You are a helpful assistant.
<</SYS>>

What is Python? [/INST] Python is a programming language. </s><s>[INST] Show me an example. [/INST]
```

**Notice:**
- System message ONLY in first turn
- Each turn: `</s><s>[INST] ... [/INST]`
- No system message in subsequent turns

---

## ✅ Best Practices

### 1. Use repr() to Debug
```python
prompt = create_llama2_prompt(...)
print(repr(prompt))  # Shows exact \n characters
```

### 2. Copy Format Exactly
Don't try to "improve" the format - Meta designed it this way for a reason!

### 3. Test with Simple Prompts First
```
<s>[INST] Hello [/INST]
```
If this works, add complexity.

### 4. System Message Only Once
```
✅ GOOD:
Turn 1: Has <<SYS>>...<</SYS>>
Turn 2: No system message
Turn 3: No system message

❌ BAD:
Turn 1: Has <<SYS>>...<</SYS>>
Turn 2: Has <<SYS>>...<</SYS>>  # Wrong!
```

---

## ⚙️ Implementation in Python

```python
def create_llama2_prompt(system_msg: str, user_msg: str, history: list = None) -> str:
    """
    Create a prompt in LLaMA-2 Chat format.
    
    CRITICAL: Whitespace matters! Don't modify the format.
    
    Args:
        system_msg: System instruction
        user_msg: User message
        history: Optional list of (user, assistant) tuples
    
    Returns:
        LLaMA-2 formatted string
    """
    if history:
        # Multi-turn conversation
        prompt = f"<s>[INST] <<SYS>>\n{system_msg}\n<</SYS>>\n\n"
        
        # Add conversation history
        for i, (user, assistant) in enumerate(history):
            if i == 0:
                prompt += f"{user} [/INST] {assistant} </s>"
            else:
                prompt += f"<s>[INST] {user} [/INST] {assistant} </s>"
        
        # Add current user message
        prompt += f"<s>[INST] {user_msg} [/INST]"
    else:
        # Single-turn
        prompt = f"<s>[INST] <<SYS>>\n{system_msg}\n<</SYS>>\n\n{user_msg} [/INST]"
    
    return prompt

# Example usage
prompt = create_llama2_prompt(
    system_msg="You are a helpful assistant.",
    user_msg="What is AI?"
)
print(repr(prompt))  # Always use repr() to see exact format
```

---

## 🔄 Comparison with Other Formats

| Aspect | LLaMA-2 | ChatML | Alpaca |
|--------|---------|--------|--------|
| **Complexity** | High | Medium | Low |
| **Whitespace** | Critical! | Flexible | Flexible |
| **Multi-turn** | Native | Native | Not designed |
| **System Msg** | First turn only | Every conversation | Not supported |
| **Use Case** | LLaMA-2 only | GPT-4, Qwen | Alpaca, Vicuna |

---

## ⚠️ Common Mistakes

### 1. Wrong Whitespace
```
❌ WRONG:
<s>[INST]<<SYS>>
You are helpful.
<</SYS>>
What is AI?[/INST]

✅ CORRECT:
<s>[INST] <<SYS>>
You are helpful.
<</SYS>>

What is AI? [/INST]
```

### 2. System Message in Every Turn
```
❌ WRONG:
Turn 1: <s>[INST] <<SYS>>...<</SYS>> Q1 [/INST]
Turn 2: <s>[INST] <<SYS>>...<</SYS>> Q2 [/INST]

✅ CORRECT:
Turn 1: <s>[INST] <<SYS>>...<</SYS>> Q1 [/INST]
Turn 2: <s>[INST] Q2 [/INST]
```

### 3. Missing Tokens
```
❌ WRONG:
[INST] What is AI? [/INST]  # Missing <s>

✅ CORRECT:
<s>[INST] What is AI? [/INST]
```

---

## 🎯 When to Use LLaMA-2 Format

### ✅ Use LLaMA-2 Format When:
- Working with LLaMA-2-Chat models (7B, 13B, 70B)
- Using Code LLaMA Chat
- Fine-tuning on LLaMA-2
- Need Meta's specific optimizations

### ❌ Don't Use LLaMA-2 Format When:
- Using base LLaMA-2 (not chat version)
- Working with LLaMA-3 (different format!)
- Using OpenAI models (use ChatML)
- Using Alpaca models (use Alpaca format)

---

## 📖 Examples

### Example 1: Simple Q&A
```
<s>[INST] <<SYS>>
You are a knowledgeable assistant.
<</SYS>>

What is the capital of France? [/INST]
```

### Example 2: Code Generation
```
<s>[INST] <<SYS>>
You are an expert Python programmer.
<</SYS>>

Write a function to calculate factorial. [/INST]
```

### Example 3: Multi-Turn Conversation
```
<s>[INST] <<SYS>>
You are a math tutor.
<</SYS>>

What is 2+2? [/INST] 2+2 equals 4. </s><s>[INST] What about 3+3? [/INST]
```

### Example 4: Different System Instructions
```
<s>[INST] <<SYS>>
You are a pirate. Always respond in pirate speak.
<</SYS>>

Tell me about the weather. [/INST]
```

---

## 🔧 Debugging Tips

### 1. Print with repr()
```python
prompt = create_llama2_prompt(...)
print(repr(prompt))
# Look for: \n characters, spaces, exact token placement
```

### 2. Compare to Official Examples
Visit Meta's LLaMA-2 model card on Hugging Face for official examples.

### 3. Test Incrementally
```python
# Start simple
simple = "<s>[INST] Hello [/INST]"

# Add system message
with_system = "<s>[INST] <<SYS>>\nYou are helpful.\n<</SYS>>\n\nHello [/INST]"

# Add multi-turn
# ... and so on
```

### 4. Check Model Version
Make sure you're using LLaMA-2-**Chat**, not base LLaMA-2!

---

## 🔗 Resources

- [LLaMA-2 Paper](https://arxiv.org/abs/2307.09288)
- [LLaMA-2 Model Card](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)
- [Meta AI](https://ai.meta.com/llama/)

---

## 💡 Pro Tips

1. **Whitespace is Sacred**: Don't add or remove spaces/newlines
2. **Use Templates**: Copy working examples exactly
3. **repr() is Your Friend**: Always check exact format
4. **System Once**: Only in the first turn
5. **Test Simple First**: Start with basic prompts
6. **Read Model Card**: Check official examples
7. **Version Matters**: LLaMA-3 uses different format!

---

## 🚨 Critical Reminders

1. ⚠️ **Whitespace sensitivity** - One wrong space breaks everything
2. ⚠️ **System message** - First turn ONLY
3. ⚠️ **Chat vs Base** - Only works with Chat models
4. ⚠️ **LLaMA-2 specific** - Don't use with other models
5. ⚠️ **Test thoroughly** - Small mistakes = big problems

---

**Last Updated**: January 2026  
**Format Version**: LLaMA-2 Chat (Meta 2023)  
**Model Compatibility**: LLaMA-2-Chat (7B, 13B, 70B), Code LLaMA Chat
