# Unit 6: Coding Assistant — NFR Design Patterns

## 1. Fallback for No Code Block
```python
if code_blocks:
    return {"text": raw, "message_type": "code", "language": code_blocks[0].language}
else:
    return {"text": raw, "message_type": "text"}
```

## 2. Frontend Syntax Highlighting
```tsx
// ChatPanel renders code blocks with react-syntax-highlighter
import SyntaxHighlighter from 'react-syntax-highlighter'
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

{message.type === 'code' ? (
  <SyntaxHighlighter language={message.language || 'text'} style={atomDark}>
    {extractCodeContent(message.content)}
  </SyntaxHighlighter>
) : (
  <span>{message.content}</span>
)}
```
