
from dataclasses import dataclass, field
import os


@dataclass
class Config:
    session_api_key: str | None = field(default_factory=lambda: os.getenv('SESSION_API_KEY') or None)


def get_default_config() -> Config:
    return Config()