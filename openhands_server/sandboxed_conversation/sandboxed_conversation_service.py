

from abc import ABC, abstractmethod
from tkinter import EventType
from uuid import UUID

from openhands_server.event.event_service import EventService
from openhands_server.sandboxed_conversation.sandboxed_conversation_models import SandboxedConversationInfo, SandboxedConversationPage, StartSandboxedConversationRequest
from openhands_server.utils.import_utils import get_impl


class SandboxedConversationService(ABC):
    """
    Sandboxed conversations have no concept of a user - it is whoever has been granted access to
    the sandbox in which the conversation is being run.

    A sandboxed conversation service is run in the current environment, but it may also pass events
    to another url or process.
    """

    @abstractmethod
    async def search_sandboxed_conversations(self, user_id: UUID | None = None, page_id: str | None = None, limit: int = 100) -> SandboxedConversationPage:
        """Search for sandboxed conversations"""

    @abstractmethod
    async def get_sandboxed_conversation(self, user_id: UUID, conversation_id: UUID) -> SandboxedConversationInfo | None:
        """Get a single sandboxed conversation info. Return None if the conversation was not found."""

    @abstractmethod
    async def batch_get_sandboxed_conversations(self, user_id: UUID, conversation_ids: list[UUID]) -> list[SandboxedConversationInfo | None]:
        """Get a batch of sandboxed conversations. Return None for any conversation which was not found."""
        results = []
        for conversation_id in conversation_ids:
            result = await self.get_sandboxed_conversation(user_id, conversation_id)
            results.append(result)
        return results

    # Event methods...

    # TODO THE EVENT SERVICE HERE IS WRONG! IT SHOULD BE READ ONLY!!!

    @abstractmethod
    async def get_event_service(self, id: UUID) -> EventService | None:
        """ Get an event from a conversation. """

    # Lifecycle methods

    async def __aenter__(self):
        """Start using this runtime image service"""

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Stop using this runtime image service"""

    @classmethod
    @abstractmethod
    def get_instance(cls) -> "SandboxedConversationService":
        """ Get an instance of runtime image service """


_sandboxed_conversation_service: SandboxedConversationService = None


def get_default_sandboxed_conversation_service() -> SandboxedConversationService:
    global _sandboxed_conversation_service
    if _sandboxed_conversation_service:
        return _sandboxed_conversation_service
    _sandboxed_conversation_service = get_impl(SandboxedConversationService)
    return _sandboxed_conversation_service
