# Wrapper Test — Adversarial AI Dialogue System

A lightweight multi-agent dialogue system where two AI instances — a Jedi apprentice and a Sith apprentice — engage in structured philosophical debate on prompts provided by the user.

This project is a development prototype for testing the core architectural patterns of the [AI Council](https://github.com/Needs-More-Coffee/ai_council) and [Orchestra](https://github.com/Needs-More-Coffee/orchestra) projects: governing document injection, stateless exchange via shared document, and multi-agent orchestration through a neutral handoff system.

---

## What It Does

The user provides a philosophical prompt. Two AI agents — each initialized with a distinct governing document defining their philosophy, reasoning approach, exchange behavior, and tone — respond in a structured four-turn exchange:

- Turn 1: Opening agent frames the question
- Turn 2: Responding agent replies
- Turn 3: Opening agent defends
- Turn 4: Responding agent justifies

The full exchange is written to a timestamped `.txt` file in the `exchanges/` folder. Existing exchange documents can be continued with new prompts, allowing multi-session conversations that build on prior exchanges.

The opener alternates between agents across exchanges — if the Jedi opens the first exchange, the Sith opens the second, and so on.

---

## Architecture

```
wrapper_test/
├── hand_off_system.py        # Orchestrator — manages turn order and document state
├── jedi/
│   ├── jedi_wrapper.py       # Jedi agent — Gemini API wrapper with governing document
│   └── documents/
│       └── *.txt             # Jedi governing document (any .txt file)
├── sith/
│   ├── sith_wrapper.py       # Sith agent — Gemini API wrapper with governing document
│   └── documents/
│       └── *.txt             # Sith governing document (any .txt file)
└── exchanges/
    └── *.txt                 # Exchange documents written here
```

### Key design decisions

**Governing documents are injected once at initialization** as the system instruction — not on every prompt call. This keeps token usage clean and maps directly to how Orchestra handles voice initialization.

**The exchange document is the memory.** Neither agent has session memory between calls. Each turn reads the full exchange document from disk and sends it as the prompt, giving the model complete context without relying on API-side state.

**The orchestrator is a neutral third script.** `hand_off_system.py` manages turn order, document creation, and opener alternation without being part of either agent. This mirrors the Arbitrator pattern in the AI Council.

**Governing documents are discovered dynamically.** Each wrapper looks for the first `.txt` file in its `documents/` folder — drop any governing document in and it gets picked up automatically.

---

## Setup

**1. Clone the repository and create a virtual environment:**

```bash
git clone https://github.com/Needs-More-Coffee/wrapper_test
cd wrapper_test
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows
```

**2. Install dependencies:**

```bash
pip install google-genai python-dotenv
```

**3. Create a `.env` file in the project root:**

```
GEMINI_API_KEY=your_key_here
```

Get a Gemini API key from [Google AI Studio](https://aistudio.google.com).

**4. Add governing documents:**

Place a `.txt` governing document in each agent's documents folder:

```
jedi/documents/your_jedi_document.txt
sith/documents/your_sith_document.txt
```

---

## Usage

**Start a new exchange:**

```bash
python hand_off_system.py "What does it mean to truly know yourself?"
```

**Continue an existing exchange with a new prompt:**

```bash
python hand_off_system.py "Follow up prompt" exchanges/exchange_20260322_143913.txt
```

The exchange document is saved to `exchanges/` with a timestamp in the filename.

---

## Governing Documents

Each agent's behavior is defined entirely by its governing document — a plain text file that specifies identity, philosophy, reasoning approach, exchange behavior, and tone. The documents for this prototype define a Jedi apprentice and a Sith apprentice sharing the same master, engaged in structured philosophical rivalry.

Key constraints built into both documents:
- Neither agent speaks in absolutes
- Neither mocks, belittles, or dismisses the other
- Concession is permitted and followed by reframing — not capitulation
- Both treat the master's prompt as the test case for their respective methodology

The governing document format is intentionally LLM-agnostic — plain text with no API references. Swapping the underlying model requires only changing the model name in the wrapper, not the document.

---

## Relationship to AI Council and Orchestra

This project is a minimal proof of the architectural pattern used in the AI Council governance framework:

| This project | AI Council / Orchestra |
|---|---|
| Jedi wrapper | Governance voice |
| Sith wrapper | Governance voice |
| Governing document | Voice governing document |
| Exchange document | The Paper |
| hand_off_system.py | Orchestrator / Arbitrator |
| Turn order logic | Round management |

Building this project validated the stateless exchange pattern, governing document injection, and neutral orchestration before implementing them at full scale in Orchestra.

---

## Notes

- The `exchanges/` folder is gitignored to keep test output out of the repository
- The `.env` file is gitignored — never commit your API key
- Model selection is configured in the wrapper files — check available models for your API key with `client.models.list()`
