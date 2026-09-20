from azure.identity import InteractiveBrowserCredential
from azure.ai.projects import AIProjectClient

ENDPOINT = "https://ai103-interview-coach-2.services.ai.azure.com/api/projects/ai-interview-coach-2"
AGENT_NAME = "AI-Interview-Coach"
TENANT_ID = "631d9c12-cb9d-4e4d-baaf-8e90208da033"

credential = InteractiveBrowserCredential(
    tenant_id=TENANT_ID
)

project = AIProjectClient(
    endpoint=ENDPOINT,
    credential=credential
)

openai = project.get_openai_client(
    agent_name=AGENT_NAME
)


def create_conversation():
    conversation = openai.conversations.create()
    return conversation.id


def ask_agent(conversation_id, message):
    response = openai.responses.create(
        conversation=conversation_id,
        input=message
    )

    return response.output_text