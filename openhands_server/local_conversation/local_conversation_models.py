from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from openhands.sdk.conversation.state import AgentExecutionStatus
from openhands.sdk.llm.utils.metrics import MetricsSnapshot
from openhands_server.local_conversation.agent_info import AgentInfo
from openhands_server.utils.date_utils import utc_now


class StartLocalConversationRequest(BaseModel):
    title: str | None = Field(default=None, description="Preset title for a conversation")
    agent: AgentInfo
    # TODO: This will need to be copied from user settings..
    # git_models: list[GitInfo] = Field(default_factory=list)


class StoredLocalConversation(StartLocalConversationRequest):
    id: UUID
    metrics: MetricsSnapshot | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class LocalConversationInfo(StoredLocalConversation):
    """Information about a conversation running locally without a Runtime sandbox."""

    status: AgentExecutionStatus = AgentExecutionStatus.IDLE


class LocalConversationPage(BaseModel):
    items: list[LocalConversationInfo]
    next_page_id: str | None = None
