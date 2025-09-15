from abc import ABC, abstractmethod

from pydantic import BaseModel

from openhands.sdk import Tool
from openhands.tools import BashTool, FileEditorTool, TaskTrackerTool


# TODO: Replace with items from SDK


class ToolInfo(BaseModel, ABC):
    """Info about a tool for use in an LLM."""

    @abstractmethod
    def create_tool(self) -> Tool:
        """Create a tool"""


class BashToolInfo(ToolInfo):
    working_dir: str

    def create_tool(self):
        return BashTool.create(working_dir=self.working_dir)


class FileEditorToolInfo(ToolInfo):
    def create_tool(self):
        return FileEditorTool.create()


class TaskTrackerToolInfo(ToolInfo):
    save_dir: str

    def create_tool(self):
        return TaskTrackerTool.create(save_dir=self.save_dir)


ToolInfoType = BashToolInfo | FileEditorToolInfo | TaskTrackerToolInfo
