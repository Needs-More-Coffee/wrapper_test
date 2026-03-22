import os
import sys
from pathlib import Path
from datetime import datetime

# Add jedi and sith folders to path so we can import the wrappers
sys.path.append(str(Path(__file__).parent / "jedi"))
sys.path.append(str(Path(__file__).parent / "sith"))

from jedi_wrapper import JediWrapper
from sith_wrapper import SithWrapper

EXCHANGES_DIR = Path(__file__).parent / "exchanges"


def get_turn_label(agent: str, turn: int) -> str:
    """
    Returns a formatted label for an exchange document entry.
    e.g. '[JEDI - TURN 1]' or '[SITH - TURN 2]'
    """
    return f"[{agent.upper()} - TURN {turn}]"


def append_to_exchange(doc_path: Path, label: str, content: str):
    """
    Appends a labeled entry to the exchange document.
    Adds spacing between entries for readability.
    """
    with open(doc_path, "a", encoding="utf-8") as f:
        f.write(f"\n{label}\n")
        f.write(content.strip())
        f.write("\n")


def load_or_create_document(doc_path: Path | None, user_prompt: str) -> Path:
    """
    If doc_path is given and exists, append the user prompt and return path.
    If doc_path is None or doesn't exist, create a new document with the
    user prompt as the first entry and return the new path.
    """
    EXCHANGES_DIR.mkdir(exist_ok=True)

    if doc_path and doc_path.exists():
        # Continue existing exchange
        append_to_exchange(doc_path, "[USER PROMPT]", user_prompt)
        return doc_path
    else:
        # Create new exchange document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_path = EXCHANGES_DIR / f"exchange_{timestamp}.txt"
        with open(new_path, "w", encoding="utf-8") as f:
            f.write("[USER PROMPT]\n")
            f.write(user_prompt.strip())
            f.write("\n")
        return new_path


def count_labeled_entries(doc_path: Path) -> int:
    """
    Counts the number of labeled agent entries in the exchange document.
    Only counts JEDI and SITH turn labels, not USER PROMPT labels.
    """
    count = 0
    with open(doc_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("[JEDI - TURN") or line.startswith("[SITH - TURN"):
                count += 1
    return count


def determine_opener(doc_path: Path | None) -> bool:
    """
    Determines which agent opens the next exchange.
    Returns True if Jedi opens, False if Sith opens.

    If doc_path given and contains labeled entries:
        Count total labeled entries, divide by 4 to get completed exchanges.
        If even -> Jedi opens. If odd -> Sith opens.

    If doc_path not given or document has no labeled entries:
        Count files in exchanges folder.
        If even (including zero) -> Jedi opens. If odd -> Sith opens.
    """
    if doc_path and doc_path.exists():
        entry_count = count_labeled_entries(doc_path)
        if entry_count > 0:
            completed_exchanges = entry_count // 4
            return completed_exchanges % 2 == 0

    # Fall through to folder count
    existing_files = [
        f for f in EXCHANGES_DIR.iterdir()
        if f.is_file() and f.suffix == ".txt" and f.name != ".gitkeep"
    ] if EXCHANGES_DIR.exists() else []

    return len(existing_files) % 2 == 0


def run_exchange(doc_path: Path, jedi_opens: bool, jedi: JediWrapper, sith: SithWrapper):
    """
    Runs one full four-turn exchange on the given document.
    Turn order:
        If jedi_opens: Jedi T1, Sith T2, Jedi T3, Sith T4
        If not jedi_opens: Sith T1, Jedi T2, Sith T3, Jedi T4
    """
    if jedi_opens:
        turn_order = [
            ("JEDI", 1, jedi),
            ("SITH", 2, sith),
            ("JEDI", 3, jedi),
            ("SITH", 4, sith),
        ]
    else:
        turn_order = [
            ("SITH", 1, sith),
            ("JEDI", 2, jedi),
            ("SITH", 3, sith),
            ("JEDI", 4, jedi),
        ]

    for agent_name, turn_num, wrapper in turn_order:
        print(f"  {agent_name} responding (turn {turn_num})...")
        label = get_turn_label(agent_name, turn_num)
        response = wrapper.respond(str(doc_path))
        append_to_exchange(doc_path, label, response)

    print(f"\nExchange complete.")


def main():
    """
    Entry point.

    Usage:
        New exchange:      python hand_off_system.py "your prompt here"
        Continue exchange: python hand_off_system.py "your prompt here" exchanges/exchange_TIMESTAMP.txt
    """
    if len(sys.argv) < 2:
        print("Usage:")
        print("  New exchange:      python hand_off_system.py \"your prompt\"")
        print("  Continue exchange: python hand_off_system.py \"your prompt\" exchanges/exchange_TIMESTAMP.txt")
        sys.exit(1)

    user_prompt = sys.argv[1]
    doc_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    print("Initializing wrappers...")
    jedi = JediWrapper()
    sith = SithWrapper()
    print("Wrappers ready.\n")

    print("Loading exchange document...")
    active_doc = load_or_create_document(doc_path, user_prompt)
    print(f"Exchange document: {active_doc}\n")

    jedi_opens = determine_opener(doc_path)
    opener = "JEDI" if jedi_opens else "SITH"
    print(f"Opener this exchange: {opener}\n")

    print("Running exchange...")
    run_exchange(active_doc, jedi_opens, jedi, sith)

    print(f"\nExchange document saved to: {active_doc}")


if __name__ == "__main__":
    main()