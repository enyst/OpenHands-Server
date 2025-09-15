

from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field

from openhands.sdk.llm.utils.metrics import MetricsSnapshot
from openhands_server.git.git_models import GitInfo
from openhands_server.local_conversation.agent_info import AgentInfo
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
    # TODO: This will need to be copied from user settings..
    # git_models: list[GitInfo] = Field(default_factory=list)


class StoredLocalConversation(StartLocalConversationRequest):
    id: UUID
    metrics: MetricsSnapshot | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class LocalConversationInfo(StoredLocalConversation):
    """ Information about a conversation running locally without a Runtime sandbox. """
    status: ConversationStatus = ConversationStatus.STOPPED


class LocalConversationPage(BaseModel):
    items: list[LocalConversationInfo]
    next_page_id: str | None = None
