

from abc import ABC, abstractmethod
from tkinter import EventType
from uuid import UUID

from openhands_server.event.event_service import EventService
from openhands_server.local_conversation.local_conversation_models import LocalConversationInfo, LocalConversationPage, StartLocalConversationRequest
from openhands_server.utils.import_utils import get_impl


class LocalConversationService(ABC):
    """
    Local conversations have no concept of a user - it is whoever has been granted access to
    the sandbox in which the conversation is being run.

    A local conversation service is run in the current environment, but it may also pass events
    to another url or process.
    """

    @abstractmethod
    async def search_local_conversations(self, page_id: str | None = None, limit: int = 100) -> LocalConversationPage:
        """Search for local conversations"""

    @abstractmethod
    async def get_local_conversation(self, conversation_id: UUID) -> LocalConversationInfo | None:
        """Get a single local conversation info. Return None if the conversation was not found."""

    @abstractmethod
    async def batch_get_local_conversations(self, conversation_ids: list[UUID]) -> list[LocalConversationInfo | None]:
        """Get a batch of local conversations. Return None for any conversation which was not found."""
        results = []
        for id in conversation_ids:
            result = await self.get_sandbox(id)
            results.append(result)
        return results

    # Write Methods

    @abstractmethod
    async def start_local_conversation(self, request: StartLocalConversationRequest) -> LocalConversationInfo:
        """ Start a local conversation and return its id. """

    @abstractmethod
    async def pause_local_conversation(self, id: UUID) -> bool:
        """ Pause a local conversation. """

    @abstractmethod
    async def resume_local_conversation(self, id: UUID) -> bool:
        """ Resume a local conversation. """

    @abstractmethod
    async def delete_local_conversation(self, id: UUID) -> bool:
        """ Delete a local conversation. Stop it if it is running. """

    # Event methods...

    @abstractmethod
    async def get_event_service(self, id: UUID) -> EventService | None:
        """ Get an event service for a conversation. """

    # Lifecycle methods

    async def __aenter__(self):
        """Start using this runtime image service"""

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Stop using this runtime image service"""

    @classmethod
    @abstractmethod
    def get_instance(cls) -> "LocalConversationService":
        """ Get an instance of runtime image service """


_local_conversation_service: LocalConversationService = None


def get_default_local_conversation_service() -> LocalConversationService:
    global _local_conversation_service
    if _local_conversation_service:
        return _local_conversation_service
    _local_conversation_service = get_impl(LocalConversationService)
    return _local_conversation_service
