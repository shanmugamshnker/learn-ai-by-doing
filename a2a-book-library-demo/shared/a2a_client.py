"""
A2A Client
===========
Async client for communicating with A2A-compliant agents.
"""

import httpx
import uuid
from typing import Optional

try:
    from fasta2a.client import A2AClient as FastA2AClient
except ImportError:  # pragma: no cover - optional dependency
    FastA2AClient = None

from .models import AgentCard, TaskRequest, TaskResponse, Message, TextPart, TaskStatus, TaskStatusState


class A2AClient:
    """
    Async A2A Protocol client for agent-to-agent communication.

    Usage:
        async with A2AClient("http://localhost:8001") as client:
            # Discover agent
            card = await client.discover()
            print(f"Connected to: {card.name}")

            # Send a query
            response = await client.send_task("Search for Python books")
            print(response)
    """

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._agent_card: Optional[AgentCard] = None
        self._raw_agent_card: Optional[dict] = None
        self._uses_fast_a2a: bool = False

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        return self._client

    async def discover(self) -> AgentCard:
        """
        A2A Discovery: Fetch the Agent Card from the remote agent.

        Some providers (e.g., Pydantic AI FastA2A) expose the card at
        ``/.well-known/agent-card.json`` instead of ``agent.json`` – try both.
        """
        discovery_paths = ["/.well-known/agent-card.json", "/.well-known/agent.json"]
        last_error: Optional[Exception] = None

        for path in discovery_paths:
            url = f"{self.base_url}{path}"
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                data = response.json()
                self._raw_agent_card = data
                self._agent_card = AgentCard.model_validate(data)
                self._uses_fast_a2a = bool(
                    data.get("protocolVersion") or data.get("protocol_version")
                )
                return self._agent_card
            except httpx.HTTPStatusError as exc:
                last_error = exc
                # If the endpoint truly doesn't exist, try the next fallback
                if exc.response.status_code == 404:
                    continue
                raise
            except Exception as exc:  # Capture transport errors to retry fallback
                last_error = exc
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Unable to discover agent card – no discovery endpoints responded")

    @property
    def agent_card(self) -> Optional[AgentCard]:
        return self._agent_card

    async def send_task(
        self,
        query: str,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> TaskResponse:
        """
        Send a task to the remote agent and get the response.

        Args:
            query: The user's query text
            task_id: Optional task ID (auto-generated if not provided)
            session_id: Optional session ID for multi-turn conversations

        Returns:
            TaskResponse with the agent's response
        """
        if task_id is None:
            task_id = str(uuid.uuid4())

        # Prefer FastA2A path if discovery told us the agent speaks that protocol
        if self._uses_fast_a2a:
            return await self._send_task_fast_a2a(query, task_id, session_id)

        try:
            return await self._send_task_rest(query, task_id, session_id)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in (404, 405):
                raise
        except httpx.ConnectError:
            pass

        if FastA2AClient is None:
            raise RuntimeError(
                "Unable to reach REST A2A endpoint and FastA2A client is unavailable."
            )
        return await self._send_task_fast_a2a(query, task_id, session_id)

    async def _send_task_rest(self, query: str, task_id: str, session_id: Optional[str]) -> TaskResponse:
        task_request = TaskRequest(
            id=task_id,
            message=Message(
                role="user",
                parts=[TextPart(text=query)]
            ),
            session_id=session_id
        )

        url = f"{self.base_url}/tasks/send"
        response = await self.client.post(
            url,
            json=task_request.model_dump(by_alias=True, exclude_none=True)
        )
        response.raise_for_status()
        return TaskResponse.model_validate(response.json())

    async def _send_task_fast_a2a(self, query: str, task_id: str, session_id: Optional[str]) -> TaskResponse:
        if FastA2AClient is None:  # pragma: no cover - defensive
            raise RuntimeError("FastA2A support not available")

        fast_client = FastA2AClient(base_url=self.base_url, http_client=self.client)
        message = {
            "role": "user",
            "kind": "message",
            "message_id": task_id,
            "parts": [
                {
                    "kind": "text",
                    "text": query
                }
            ],
        }
        if session_id:
            message["context_id"] = session_id

        rpc_response = await fast_client.send_message(message)
        if rpc_response.get("error"):
            raise RuntimeError(f"FastA2A error: {rpc_response['error']}")

        payload = rpc_response.get("result") or {}
        state = payload.get("status", {}).get("state", TaskStatusState.COMPLETED.value)
        if state not in TaskStatusState._value2member_map_:
            state = TaskStatusState.FAILED.value

        agent_text = self._extract_fast_a2a_text(payload) or "No response"
        user_message = Message(role="user", parts=[TextPart(text=query)])
        agent_message = Message(role="agent", parts=[TextPart(text=agent_text)])

        return TaskResponse(
            id=task_id,
            status=TaskStatus(state=TaskStatusState(state)),
            messages=[user_message, agent_message]
        )

    def _extract_fast_a2a_text(self, payload: dict) -> str:
        """Extract the final agent response from FastA2A payloads."""

        def parts_to_text(parts: list[dict]) -> str:
            texts = [p.get("text", "") for p in parts if p.get("kind") == "text"]
            return "\n".join(t for t in texts if t)

        if not payload:
            return ""

        kind = payload.get("kind")
        if kind == "task":
            history = payload.get("history") or []
            for message in reversed(history):
                if message.get("role") == "agent":
                    text = parts_to_text(message.get("parts", []))
                    if text:
                        return text
            status_msg = payload.get("status", {}).get("message")
            if isinstance(status_msg, dict):
                return parts_to_text(status_msg.get("parts", []))
            return ""
        elif kind == "message":
            return parts_to_text(payload.get("parts", []))

        return ""

    async def health_check(self) -> dict:
        """Check if the remote agent is healthy."""
        url = f"{self.base_url}/health"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    def get_response_text(self, task_response: TaskResponse) -> str:
        """Extract the text response from a TaskResponse."""
        if task_response.status.state == TaskStatusState.COMPLETED:
            if task_response.messages:
                # Get the last agent message
                for msg in reversed(task_response.messages):
                    if msg.role == "agent":
                        return "".join(part.text for part in msg.parts)
        elif task_response.error:
            return f"Error: {task_response.error.message}"
        return "No response"

    async def send_query_simple(self, query: str) -> str:
        """Send a query and return just the text response."""
        try:
            response = await self.send_task(query)
            return self.get_response_text(response)
        except Exception as e:
            return f"Error communicating with agent: {str(e)}"


class A2AClientSync:
    """
    Synchronous wrapper for A2AClient.
    Useful for simple scripts and testing.
    """

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)
        self._agent_card: Optional[AgentCard] = None

    def discover(self) -> AgentCard:
        """Fetch the Agent Card."""
        url = f"{self.base_url}/.well-known/agent.json"
        response = self._client.get(url)
        response.raise_for_status()
        self._agent_card = AgentCard.model_validate(response.json())
        return self._agent_card

    def send_task(self, query: str, task_id: Optional[str] = None) -> TaskResponse:
        """Send a task and get response."""
        if task_id is None:
            task_id = str(uuid.uuid4())

        task_request = TaskRequest(
            id=task_id,
            message=Message(
                role="user",
                parts=[TextPart(text=query)]
            )
        )

        url = f"{self.base_url}/tasks/send"
        response = self._client.post(
            url,
            json=task_request.model_dump(by_alias=True, exclude_none=True)
        )
        response.raise_for_status()
        return TaskResponse.model_validate(response.json())

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
