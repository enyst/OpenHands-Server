from typing import Optional
from uuid import UUID
from pydantic import Field
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase


class StoredConversationMetricsSnapshot(DeclarativeBase):
    """StoredConversationMetrics - see openhands.sdk.llm.utils.metrics.MetricsSnapshot"""
    conversation_id = Column(UUID, primary_key=True)
    model_name = Column(String)
    accumulated_cost = Column(Float, default=0)
    max_budget_per_task = Column(Float, default=0)

    # Accumulated token usage
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cache_read_tokens = Column(Integer, default=0)
    cache_write_tokens = Column(Integer, default=0)
    reasoning_tokens = Column(Integer, default=0)
    context_window = Column(Integer, default=0)
    per_turn_token = Column(Integer, default=0)
