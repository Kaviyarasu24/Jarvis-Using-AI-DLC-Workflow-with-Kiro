# JARVIS Requirements Clarification Questions

Please answer the following questions by filling in the letter choice after each `[Answer]:` tag.
If none of the provided options match your needs, choose the last option (Other/X) and describe your preference.

Let me know when you are done answering.

---

## Section 1: Platform & Technology Stack

### Question 1
What is the primary platform target for JARVIS?

A) Desktop application (Windows/macOS/Linux)
B) Web application (browser-based)
C) Mobile application (iOS/Android)
D) Cross-platform (Desktop + Web + Mobile)
E) Command-line interface (CLI) only
F) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 2
What programming language(s) should be used for the backend/core of JARVIS?

A) Python (recommended for AI/ML integrations)
B) Node.js / TypeScript
C) Java / Kotlin
D) Go
E) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 3
Which AI/LLM provider should JARVIS integrate with for its intelligence core?

A) OpenAI (GPT-4 / GPT-4o)
B) Amazon Bedrock (Claude, Titan, etc.)
C) Google Gemini / Vertex AI
D) Local/self-hosted model (Ollama, LM Studio, etc.)
E) Multiple providers with fallback support
F) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Section 2: Voice Interaction

### Question 4
What is the expected voice interaction mode?

A) Voice input only (speech-to-text, then text response)
B) Full voice I/O (speech-to-text + text-to-speech responses)
C) Voice as optional input alongside text
D) No voice interaction needed at this stage
E) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 5
Which speech-to-text (STT) engine should be used?

A) OpenAI Whisper (local or API)
B) Google Speech-to-Text API
C) Amazon Transcribe
D) Browser Web Speech API (web only)
E) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Section 3: Browser Automation

### Question 6
What level of browser automation is required?

A) Basic web search and information retrieval only
B) Full browser automation (navigate, click, fill forms, extract data)
C) Headless browser scraping (no visible browser window)
D) Browser extension integration
E) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 7
Which browser automation framework should be used?

A) Playwright
B) Selenium
C) Puppeteer
D) Browser-use (AI-native browser automation)
E) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Section 4: Coding Assistance

### Question 8
What coding assistance capabilities are required?

A) Code generation only (generate code from natural language)
B) Code generation + explanation + debugging
C) Full IDE-like assistance (generation, debugging, refactoring, explanation, code review)
D) Code execution in sandboxed environment
E) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 9
Should JARVIS support code execution (running generated code)?

A) Yes — execute code in a sandboxed/isolated environment
B) Yes — execute code directly on the host system (with user confirmation)
C) No — generate code only, no execution
D) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Section 5: System Control

### Question 10
What system control capabilities should JARVIS have?

A) Read-only system monitoring (CPU, memory, disk, processes)
B) System monitoring + file system read access
C) Full system control (open apps, manage files, run commands, control OS)
D) Limited automation (open URLs, launch apps, clipboard management)
E) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Section 6: User Interface

### Question 11
What type of user interface should JARVIS have?

A) Chat-based UI (text conversation window)
B) Chat UI + voice waveform/visual feedback
C) Floating widget / overlay (always-on-top assistant)
D) System tray / background service with hotkey activation
E) Terminal/CLI interface only
F) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 12
Should JARVIS maintain conversation history/memory across sessions?

A) Yes — persistent memory stored locally
B) Yes — persistent memory stored in cloud/database
C) Session-only memory (cleared when app closes)
D) No memory needed
E) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Section 7: Architecture & Deployment

### Question 13
What is the preferred deployment/distribution model?

A) Standalone local application (runs entirely on user's machine)
B) Client-server (local client + backend server)
C) Cloud-hosted service (SaaS model)
D) Hybrid (local processing + cloud AI APIs)
E) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 14
Should JARVIS support multiple users or is it a single-user personal assistant?

A) Single user only (personal assistant)
B) Multi-user with individual profiles
C) Multi-user with shared workspace
D) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Section 8: Integrations & Alerts

### Question 15
What external integrations are required?

A) None beyond AI provider and browser
B) Calendar / task management (Google Calendar, Outlook, etc.)
C) Communication tools (Slack, email, etc.)
D) Developer tools (GitHub, Jira, VS Code extension, etc.)
E) Multiple integrations (please describe after [Answer]: tag below)
F) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 16
What system monitoring and alerting capabilities are needed?

A) Basic system stats display (CPU, RAM, disk)
B) Proactive alerts when thresholds are exceeded (e.g., high CPU)
C) Process monitoring and management
D) All of the above
E) No monitoring needed
F) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Section 9: Security & Privacy

### Question 17
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)
B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)
X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Section 10: Testing

### Question 18
Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)
B) Partial — enforce PBT rules only for pure functions and serialization round-trips
C) No — skip all PBT rules (suitable for simple CRUD applications or thin integration layers)
X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Section 11: Project Scope & Priorities

### Question 19
What is the MVP (Minimum Viable Product) scope for the initial version?

A) Core chat assistant with AI integration only
B) Chat + voice interaction + basic coding assistance
C) Chat + voice + coding + browser automation
D) Full feature set as described (all capabilities)
E) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 20
What is the priority order for feature development?

A) Voice → Coding → Browser → System Control
B) Coding → Browser → Voice → System Control
C) Chat/AI Core → Coding → Voice → Browser → System Control
D) All features developed in parallel
E) Other (please describe after [Answer]: tag below)

[Answer]: 
