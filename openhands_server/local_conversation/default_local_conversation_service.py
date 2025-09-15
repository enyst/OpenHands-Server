import asyncio
import logging
import shutil
from dataclasses import dataclass, field
from mailbox import Message
from pathlib import Path
from uuid import UUID, uuid4

from openhands_server.event.event_context import EventContext
from openhands_server.local_conversation.local_conversation_event_context import (
    LocalConversationEventContext,
)
from openhands.sdk import Message
from openhands_server.local_conversation.local_conversation_models import (
    ConfirmationResponseRequest,
    LocalConversationInfo,
    LocalConversationPage,
    SendMessageRequest,
    StartLocalConversationRequest,
    StoredLocalConversation,
)
from openhands_server.local_conversation.local_conversation_service import (
    LocalConversationService,
)
from openhands_server.utils.date_utils import utc_now


logger = logging.getLogger(__name__)


@dataclass
class DefaultLocalConversationService(LocalConversationService):
    """
    Conversation service which stores to a local file store. When the context starts
    all conversations are loaded into memory, and stored when it stops.
    """

    file_store_path: Path = field(default=Path("/workspace/conversations"))
    workspace_path: Path = field(default=Path("/workspace"))
    _conversations: dict[UUID, LocalConversationEventContext] | None = field(
        default=None, init=False
    )

    async def get_local_conversation(self, id: UUID) -> LocalConversationInfo:
        conversation = self._conversations.get(id)
        if conversation is None:
            return None
        status = await conversation.get_status()
        return LocalConversationInfo(**conversation.stored.model_dump(), status=status)

    async def search_local_conversations(
        self, page_id: str | None = None, limit: int = 100
    ) -> LocalConversationPage:
        items = []
        for id, conversation in self._conversations.items():
            # If we have reached the start of the page
            if id == page_id:
                page_id = None

            # Skip pass entries before the first item...
            if page_id:
                continue

            # If we have reached the end of the page, return it
            if limit <= 0:
                return LocalConversationPage(items=items, next_page_id=id.hex)
            limit -= 1

            items.append(
                LocalConversationInfo(
                    **conversation.stored.model_dump(),
                    status=await conversation.get_status(),
                )
            )
        return LocalConversationPage(items=items)

    # Write Methods

    async def start_local_conversation(
        self, request: StartLocalConversationRequest
    ) -> LocalConversationInfo:
        """Start a local conversation and return its id."""
        id = uuid4()
        stored = StoredLocalConversation(id=id, **request.model_dump())
        conversation = LocalConversationEventContext(
            stored=stored,
            file_store_path=self.file_store_path / id.hex / "conversation",
            working_dir=self.workspace_path / id.hex,
        )
        await conversation.subscribe_to_events(_EventListener(self, id))
        self._conversations[id] = conversation
        await conversation.start()
        return await self.get_local_conversation(id)

    async def pause_local_conversation(self, conversation_id: UUID) -> bool:
        conversation = self._conversations.get(conversation_id)
        if conversation:
            await conversation.pause()
        return bool(conversation)

    async def resume_local_conversation(self, conversation_id: UUID) -> bool:
        conversation = self._conversations.get(conversation_id)
        if conversation:
            await conversation.start()
        return bool(conversation)

    async def delete_local_conversation(self, conversation_id: UUID) -> bool:
        conversation = self._conversations.pop(conversation_id, None)
        if conversation:
            await conversation.close()
            shutil.rmtree(self.file_store_path / conversation_id.hex, ignore_errors=True)
            shutil.rmtree(self.workspace_path / conversation_id.hex, ignore_errors=True)
            return True
        return False

    async def send_message_to_conversation(
        self, conversation_id: UUID, request: SendMessageRequest
    ) -> bool:
        """Send a message to a conversation and optionally run it."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return False
        
        message = Message(role=request.role, content=request.content)
        await conversation.send_message(message)
        
        if request.run:
            await conversation.run()
        
        return True

    async def run_conversation(self, conversation_id: UUID) -> bool:
        """Start or resume the agent run for a conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return False
        
        await conversation.start()
        return True

    async def respond_to_confirmation(
        self, conversation_id: UUID, request: ConfirmationResponseRequest
    ) -> bool:
        """Accept or reject a pending action in confirmation mode."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return False
        
        # TODO: Implement confirmation response logic
        # This would need to be implemented in the conversation/agent SDK
        # For now, we'll just resume if accepted, pause if rejected
        if request.accept:
            await conversation.start()
        else:
            await conversation.pause()
        
        return True

    async def get_event_context(self, id: UUID) -> EventContext | None:
        event_context = self._conversations.get(id)
        if event_context:
            return event_context

    async def __aenter__(self):
        conversations = {}
        for conversation_dir in self.file_store_path.iterdir():
            meta_file = conversation_dir / "meta.json"
            json_str = meta_file.read_text()
            id = UUID(conversation_dir.name)
            conversations[id] = LocalConversationEventContext(
                stored=StoredLocalConversation.model_validate_json(json_str),
                file_store_path=self.file_store_path / id.hex,
                working_dir=self.workspace_path / id.hex,
            )
        self._conversations = conversations
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        conversations = self._conversations
        self._conversations = None
        # This stops convesations and saves meta
        await asyncio.gather(
            *[
                conversation.__aexit__(exc_type, exc_value, traceback)
                for conversation in conversations.values()
            ]
        )

    @classmethod
    def get_instance(cls) -> LocalConversationService:
        return DefaultLocalConversationService()


@dataclass
class _EventListener:
    service: "DefaultLocalConversationService"
    conversation_id: UUID

    async def __call__(self, event):
        conversation = self.service._conversations.get(self.conversation_id)
        if conversation:
            conversation.stored.updated_at = utc_now()
