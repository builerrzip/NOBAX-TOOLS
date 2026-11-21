"""
Manajemen Context Window & Memory Percakapan AI.
"""

from typing import Any


class ConversationMemory:
    def __init__(self, max_turns: int = 20) -> None:
        self.max_turns = max_turns

    def build_context(
        self,
        system_prompt: str,
        history_messages: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        context: list[dict[str, str]] = []
        if system_prompt.strip():
            context.append({"role": "system", "content": system_prompt.strip()})

        recent = history_messages[-self.max_turns :]
        for msg in recent:
            role = msg.get("role", "user")
            content = str(msg.get("content", "")).strip()
            if role in ("user", "assistant") and content:
                context.append({"role": role, "content": content})
        return context
