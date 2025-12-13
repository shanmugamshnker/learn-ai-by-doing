"""Shared A2A models and utilities for the Book Library Federation."""

from .models import (
    AgentCard,
    AgentSkill,
    AgentCapabilities,
    TaskRequest,
    TaskResponse,
    Message,
    TextPart,
    TaskStatus,
    Book,
)
from .a2a_client import A2AClient

__all__ = [
    "AgentCard",
    "AgentSkill",
    "AgentCapabilities",
    "TaskRequest",
    "TaskResponse",
    "Message",
    "TextPart",
    "TaskStatus",
    "Book",
    "A2AClient",
]
