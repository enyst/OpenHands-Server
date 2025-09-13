
from huggingface_hub import Agent
from openhands.sdk import LLM, Tool
from openhands.tools import BashTool, FileEditorTool, TaskTrackerTool
from pydantic import BaseModel

from openhands_server.local_conversation.tool_info import ToolInfo


class AgentInfo(BaseModel):
    llm: LLM
    tools: list[ToolInfo] = None

    def create_agent(self, cwd: str):
        return Agent(
            llm=self.llm,
            tools=self.create_tools(cwd),
        )

    def create_tools(self, cwd: str) -> list[Tool]:
        if self.tools is not None:
            return [tool.create_tool() for tool in self.tools]
        else:
            return [
                BashTool.create(working_dir=cwd),
                FileEditorTool.create(),
                TaskTrackerTool.create(save_dir=cwd),
            ]