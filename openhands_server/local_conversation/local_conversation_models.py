

from datetime import UTC, datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field

from openhands_server.local_conversation.agent_info import AgentInfo
from openhands_server.local_conversation.tool_info import ToolInfo
from openhands_server.utils.date_utils import utc_now


# TODO: Review these status with Calvin & Xingyao
class ConversationStatus(Enum):
    RUNNING = 'RUNNING'
    PAUSED = 'PAUSED'
    FINISHED = 'FINISHED'
    STOPPED = 'STOPPED'


class StartLocalConversationRequest(BaseModel):
    title: str | None
    agent: AgentInfo


class StoredLocalConversation(StartLocalConversationRequest):
    id: UUID
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class LocalConversationInfo(StoredLocalConversation):
    """ Information about a conversation running locally without a Runtime sandbox. """
    status: ConversationStatus = ConversationStatus.STOPPED


class LocalConversationPage(BaseModel):
    items: list[LocalConversationInfo]
    next_page_id: str | None = None
