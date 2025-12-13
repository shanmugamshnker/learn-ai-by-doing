"""
A2A Protocol Models
====================
Pydantic models for Agent-to-Agent communication protocol.
Based on the A2A specification: https://a2a-protocol.org
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


# =============================================================================
# AGENT CARD MODELS (Discovery)
# =============================================================================

class AgentSkill(BaseModel):
    """Describes a specific capability/skill of an agent."""
    id: str
    name: str
    description: str
    tags: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)


class AgentCapabilities(BaseModel):
    """Agent capability flags."""
    streaming: bool = False
    push_notifications: bool = Field(default=False, alias="pushNotifications")
    multi_turn: bool = Field(default=True, alias="multiTurn")

    class Config:
        populate_by_name = True


class AgentCard(BaseModel):
    """
    A2A Agent Card - Describes an agent's identity and capabilities.
    Served at /.well-known/agent.json
    """
    name: str
    description: str
    url: str
    version: str = "1.0.0"
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    skills: list[AgentSkill] = Field(default_factory=list)
    default_input_modes: list[str] = Field(
        default=["text/plain"],
        alias="defaultInputModes"
    )
    default_output_modes: list[str] = Field(
        default=["text/plain"],
        alias="defaultOutputModes"
    )
    provider: Optional[str] = None
    documentation_url: Optional[str] = Field(default=None, alias="documentationUrl")

    class Config:
        populate_by_name = True


# =============================================================================
# TASK MODELS (Communication)
# =============================================================================

class TextPart(BaseModel):
    """A text content part in a message."""
    text: str


class Message(BaseModel):
    """A message in the A2A conversation."""
    role: Literal["user", "agent"]
    parts: list[TextPart]


class TaskStatusState(str, Enum):
    """Possible states for a task."""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class TaskStatus(BaseModel):
    """Status of a task."""
    state: TaskStatusState
    message: Optional[str] = None


class TaskError(BaseModel):
    """Error information for failed tasks."""
    code: Optional[str] = None
    message: str


class TaskRequest(BaseModel):
    """A2A Task Request - Sent by client to initiate a task."""
    id: str
    message: Message
    session_id: Optional[str] = Field(default=None, alias="sessionId")

    class Config:
        populate_by_name = True


class TaskResponse(BaseModel):
    """A2A Task Response - Returned by server after processing."""
    id: str
    status: TaskStatus
    messages: list[Message] = Field(default_factory=list)
    artifacts: list[dict] = Field(default_factory=list)
    error: Optional[TaskError] = None

    class Config:
        populate_by_name = True


# =============================================================================
# DOMAIN MODELS (Book Library)
# =============================================================================

class Book(BaseModel):
    """Book entity in the library catalog."""
    id: str
    title: str
    author: str
    genre: str
    year: int
    isbn: Optional[str] = None
    available_copies: int = Field(ge=0, alias="availableCopies")
    total_copies: int = Field(ge=1, alias="totalCopies")
    description: Optional[str] = None
    location: Optional[str] = None  # Which library

    class Config:
        populate_by_name = True

    @property
    def is_available(self) -> bool:
        return self.available_copies > 0


class BookSearchResult(BaseModel):
    """Search result from a library."""
    library_name: str
    library_url: str
    books: list[Book]
    total_found: int
