# Unit 2: Voice Module — Tech Stack Decisions

| Component | Choice | Rationale |
|---|---|---|
| STT Library | `speech_recognition` 3.10+ | User-specified; supports Google Web Speech API; simple Python API |
| TTS Library | `pyttsx3` 2.90 | User-specified; offline TTS; Windows SAPI5 support |
| Threading | Python `threading.Thread` | TTS blocks; must run off asyncio event loop |
| Async bridge | `asyncio.get_event_loop().run_in_executor()` | Clean way to run blocking TTS in thread pool from async context |
| Microphone | `speech_recognition.Microphone` | Built into speech_recognition; uses PyAudio |
| Audio backend | `pyaudio` | Required by speech_recognition for microphone access on Windows |

## Windows-Specific Notes
- `pyttsx3` uses Windows SAPI5 voice engine — works out of the box on Windows
- `pyaudio` requires Microsoft Visual C++ Build Tools or pre-built wheel on Windows
- Recommended install: `pip install pyaudio` (use pre-built wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/ if build fails)
