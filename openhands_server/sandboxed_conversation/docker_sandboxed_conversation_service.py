

from openhands_server.sandboxed_conversation.sandboxed_conversation_service import SandboxedConversationService


class DockerSandboxedConversationService(SandboxedConversationService):
    async def search_sandboxed_conversations(self, user_id = None, page_id = None, limit = 100):
        raise NotImplementedError

    async def get_sandboxed_conversation(self, user_id, conversation_id):
        raise NotImplementedError

    async def batch_get_sandboxed_conversations(self, user_id, conversation_ids):
        raise NotImplementedError

    async def get_event_service(self, id):
        raise NotImplementedError

    @classmethod
    def get_instance(cls):
        raise NotImplementedError

