# Unit 5: Browser Module — Business Logic Model

## Search Pipeline

```
User: "search for Python async best practices"
      |
      v
IntentRouter classifies: "search"
      |
      v
BrowserModule.search(query="Python async best practices")
      |
      v
browser-use Agent executes search task:
  - Opens browser (headless)
  - Navigates to search results
  - Extracts relevant content from top results
      |
      v
Raw content returned from browser-use
      |
      v
AICore.chat(summarize_prompt + raw_content)
  → "Here's what I found about Python async best practices: ..."
      |
      v
BrowserResult { success, summary, sources }
      |
      v
chat_response { text: summary + sources, message_type: "text" }
```

## Query Extraction

```
extract_query(message) -> SearchIntent:
  # Strip trigger words
  patterns = [
    r"search for (.+)",
    r"find (.+)",
    r"look up (.+)",
    r"what is (.+)",
    r"who is (.+)",
    r"how to (.+)",
    r"browse (.+)",
  ]
  FOR pattern IN patterns:
    match = re.search(pattern, message, re.IGNORECASE)
    IF match:
      RETURN SearchIntent(query=match.group(1).strip(), is_url=False)
  
  # Check if it's a direct URL
  IF message starts with "http":
    RETURN SearchIntent(query=message, is_url=True)
  
  # Fallback: use entire message as query
  RETURN SearchIntent(query=message, is_url=False)
```

## Error Handling

```
TRY:
  result = browser_agent.run(task)
EXCEPT TimeoutError:
  RETURN BrowserResult(success=False, error="Search timed out. Please try again.")
EXCEPT Exception as e:
  log error
  RETURN BrowserResult(success=False, error="Web search failed. Please try again later.")
```
