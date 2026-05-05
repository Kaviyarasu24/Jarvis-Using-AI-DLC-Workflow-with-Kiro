# Unit 6: Coding Assistant — Domain Entities

## CodingTaskType
The type of coding assistance requested.

```
CodingTaskType: "generate" | "explain" | "debug" | "refactor" | "review"
```

## CodingResponse
Structured response from the coding assistant.

```
CodingResponse
├── task_type: CodingTaskType
├── language: str           — detected/specified programming language
├── code: str | None        — extracted code block (if applicable)
├── explanation: str        — human-readable explanation
└── raw: str                — full raw response from Ollama
```

## CodeBlock
A parsed code block from an Ollama response.

```
CodeBlock
├── language: str
└── content: str
```
