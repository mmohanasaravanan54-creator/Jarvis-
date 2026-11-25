"""The 'brain' of Jarvis. Swap this file to change which AI model answers."""
from typing import Dict, List

from config import AI_MODEL, ANTHROPIC_API_KEY, SYSTEM_PROMPT

_client = None
if ANTHROPIC_API_KEY:
    import anthropic

    _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def ask_jarvis(history: List[Dict[str, str]], notes: List[str]) -> str:
    """history = [{"role": "user"|"assistant", "content": "..."}, ...] ending with the newest user message."""
    if _client is None:
        return (
            "I'm running in demo mode because no ANTHROPIC_API_KEY is set. "
            "Add your key to the .env file and restart the server to unlock my full brain."
        )

    system = SYSTEM_PROMPT
    if notes:
        system += "\n\nThings the user asked you to remember:\n- " + "\n- ".join(notes)

    try:
        response = _client.messages.create(
            model=AI_MODEL,
            max_tokens=600,
            system=system,
            messages=history,
        )
        return "".join(block.text for block in response.content if block.type == "text").strip()
    except Exception as exc:  # network error, bad key, rate limit...
        return f"Sorry, I couldn't reach my AI brain right now ({type(exc).__name__})."
