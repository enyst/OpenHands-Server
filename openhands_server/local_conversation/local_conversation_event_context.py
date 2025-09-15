import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

from openhands.sdk import Conversation, EventBase, LocalFileStore, Message, TextContent
from openhands.sdk.conversation.state import AgentExecutionStatus
from openhands.sdk.utils.async_utils import (
    AsyncCallbackWrapper,
    AsyncConversationCallback,
)
from openhands_server.event.event_context import EventContext
from openhands_server.event.event_models import EventPage
from openhands_server.local_conversation.local_conversation_models import (
    StoredLocalConversation,
)
from openhands_server.utils.date_utils import utc_now
from openhands_server.utils.pub_sub import PubSub


@dataclass
class LocalConversationEventContext(EventContext):
    """
    Event service for a conversation running locally. Use an event manager to start the service before use
    """

    stored: StoredLocalConversation
    file_store_path: Path
    working_dir: str
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
    _conversation: Conversation | None = field(default=None, init=False)
    _pub_sub: PubSub = field(default_factory=PubSub, init=False)

    async def load_meta(self):
        meta_file = self.file_store_path / "meta.json"
        self.stored = StoredLocalConversation.model_validate_json(meta_file.read_text())

    async def save_meta(self):
        self.stored.updated_at = utc_now()
        meta_file = self.file_store_path / "meta.json"
        meta_file.write_text(self.stored.model_dump_json())

    async def get_event(self, event_id: str) -> EventBase | None:
        # TODO: It would be better to be able to get the event by its id directly here!
        # Is there an API for this?
        event = next(
            (
                event
                for event in self._conversation.state.events
                if event.id == event_id
            ),
            None,
        )
        return event

    async def search_events(self, page_id: str = None, limit: int = 100) -> EventPage:
        items = []
        async with self._lock:
            with self._conversation.state as state:
                for event in state.events:
                    # If we have reached the start of the page
                    if event.id == page_id:
                        page_id = None

                    # Skip pass entries before the first item...
                    if page_id:
                        continue

                    # If we have reached the end of the page, return it
                    if limit <= 0:
                        return EventPage(items=items, next_page_id=event.id)
                    limit -= 1

                    items.append(event)

        return EventPage(items=items)

    async def send_message(self, message: Message):
        async with self._lock:
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, self._conversation.send_message, message)
            with self._conversation.state as state:
                if state.agent_status != AgentExecutionStatus.RUNNING:
                    loop.run_in_executor(None, self._conversation.run, message)


    async def subscribe_to_events(self, callback: AsyncConversationCallback) -> UUID:
        return self._pub_sub.subscribe(callback)

    async def unsubscribe_from_events(self, callback_id: UUID) -> bool:
        return self._pub_sub.unsubscribe(callback_id)

    async def start(self):
        async with self._lock:
            if self._conversation:
                with self._conversation.state as state:
                    # Agent has finished
                    if state.agent_status == AgentExecutionStatus.FINISHED:
                        return

                    # Agent is already running
                    if state.agent_status not in [AgentExecutionStatus.PAUSED, AgentExecutionStatus.WAITING_FOR_CONFIRMATION]:
                        return

            agent = self.stored.agent.create_agent(self.working_dir)
            conversation = Conversation(
                agent=agent,
                callbacks=[AsyncCallbackWrapper(self._pub_sub, asyncio.get_running_loop())],
                persist_filestore=LocalFileStore(str(self.file_store_path / "events")),
            )
            self._conversation = conversation
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, conversation.run)

    async def pause(self):
        async with self._lock:
            if self._conversation:
                loop = asyncio.get_running_loop()
                loop.run_in_executor(None, self._conversation.pause)

    async def close(self):
        async with self._lock:
            if self._conversation:
                loop = asyncio.get_running_loop()
                loop.run_in_executor(None, self._conversation.close)

    async def get_status(self) -> AgentExecutionStatus:
        async with self._lock:
            if not self._conversation:
                return AgentExecutionStatus.ERROR
            with self._conversation.state as state:
                return state.agent_status

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.save_meta()
        await self.close()
