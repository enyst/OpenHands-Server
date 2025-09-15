from abc import ABC, abstractmethod
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from openhands.sdk import Tool
from openhands.tools import BashTool, FileEditorTool, TaskTrackerTool


# TODO: Replace with items from SDK


class ToolInfo(BaseModel, ABC):
    """Info about a tool for use in an LLM."""

    @abstractmethod
    def create_tool(self) -> Tool:
        """Create a tool"""


class BashToolInfo(ToolInfo):
    type: Literal["BashTool"] = "BashTool"
    working_dir: str

    def create_tool(self):
        return BashTool.create(working_dir=self.working_dir)


class FileEditorToolInfo(ToolInfo):
    type: Literal["FileEditorTool"] = "FileEditorTool"

    def create_tool(self):
        return FileEditorTool.create()


class TaskTrackerToolInfo(ToolInfo):
    type: Literal["TaskTrackerTool"] = "TaskTrackerTool"
    save_dir: str

    def create_tool(self):
        return TaskTrackerTool.create(save_dir=self.save_dir)

{
    type: ""
    ...
}

{
    type: ""
    instance: {
        ...
    }
}



ToolInfoType = Annotated[Union[BashToolInfo, FileEditorToolInfo, TaskTrackerToolInfo], Field(discriminator="type")]
