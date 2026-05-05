# Unit 6: Coding Assistant — Business Logic Model

## 1. Task Type Detection

```
detect_task_type(message) -> CodingTaskType:
  msg_lower = message.lower()
  
  IF any word in ["generate", "write", "create", "build", "make", "implement"]:
    RETURN "generate"
  IF any word in ["explain", "what does", "what is", "how does", "describe"]:
    RETURN "explain"
  IF any word in ["debug", "fix", "error", "bug", "issue", "broken", "not working"]:
    RETURN "debug"
  IF any word in ["refactor", "improve", "clean", "optimize", "rewrite"]:
    RETURN "refactor"
  IF any word in ["review", "check", "audit", "analyze", "critique"]:
    RETURN "review"
  
  DEFAULT: RETURN "generate"
```

## 2. System Prompt Selection

```
CODING_PROMPTS = {
  "generate": "You are an expert coding assistant. Generate clean, well-commented code. Always specify the language and wrap code in markdown code blocks with the language name.",
  "explain":  "You are an expert coding assistant. Explain the provided code clearly and concisely. Break down what each part does.",
  "debug":    "You are an expert debugging assistant. Identify the bug, explain why it occurs, and provide a corrected version of the code.",
  "refactor": "You are an expert coding assistant. Refactor the provided code to be cleaner, more efficient, and follow best practices. Explain the changes made.",
  "review":   "You are an expert code reviewer. Review the provided code for bugs, security issues, performance problems, and style. Provide specific, actionable feedback.",
}
```

## 3. Response Parsing

```
parse_response(raw: str) -> (code_blocks: list[CodeBlock], explanation: str):
  # Extract all ```language ... ``` blocks
  pattern = r'```(\w*)\n(.*?)```'
  matches = re.findall(pattern, raw, re.DOTALL)
  
  code_blocks = [CodeBlock(language=lang or "text", content=code.strip())
                 for lang, code in matches]
  
  # Explanation = raw text with code blocks removed
  explanation = re.sub(pattern, '', raw, flags=re.DOTALL).strip()
  
  RETURN code_blocks, explanation
```

## 4. Full Pipeline

```
handle(message) -> dict:
  task_type = detect_task_type(message)
  system_prompt = CODING_PROMPTS[task_type]
  
  raw_response = await ai_core.chat(message, system_prompt=system_prompt)
  
  code_blocks, explanation = parse_response(raw_response)
  
  IF code_blocks:
    primary_block = code_blocks[0]
    RETURN {
      "text": raw_response,
      "message_type": "code",
      "language": primary_block.language or "text",
    }
  ELSE:
    RETURN { "text": raw_response, "message_type": "text" }
```
