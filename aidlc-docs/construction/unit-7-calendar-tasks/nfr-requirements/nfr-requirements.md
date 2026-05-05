# Unit 7: Calendar & Tasks — NFR Requirements

## Reliability

| ID | Requirement |
|---|---|
| NFR-U7-R01 | Task data MUST NOT be lost on shutdown — write-on-update (FR-NFR-013) |
| NFR-U7-R02 | Corrupted tasks.json MUST reset to empty list gracefully |
| NFR-U7-R03 | REST endpoints MUST return appropriate HTTP status codes (200, 201, 404) |

## Usability

| ID | Requirement |
|---|---|
| NFR-U7-U01 | CalendarPanel MUST show today + tomorrow reminders on load |
| NFR-U7-U02 | Tasks MUST be viewable by date filter (all, today, tomorrow, specific date) |
| NFR-U7-U03 | Natural language date parsing MUST support "today", "tomorrow", day names, YYYY-MM-DD |
