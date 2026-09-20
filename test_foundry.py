from azure.identity import InteractiveBrowserCredential
from azure.ai.projects import AIProjectClient

endpoint = "https://ai103-interview-coach-2.services.ai.azure.com/api/projects/ai-interview-coach-2"
agent_name = "AI-Interview-Coach"

credential = InteractiveBrowserCredential(
    tenant_id="631d9c12-cb9d-4e4d-baaf-8e90208da033"
)

project = AIProjectClient(
    endpoint=endpoint,
    credential=credential
)

openai = project.get_openai_client(agent_name=agent_name)

conversation = openai.conversations.create()

response = openai.responses.create(
    conversation=conversation.id,
    input="Say hello and introduce yourself as an AI Interview Coach."
)

print("\nAGENT RESPONSE:")
print(response.output_text)
