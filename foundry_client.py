import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

ENDPOINT = os.environ.get(
    "AZURE_AI_PROJECT_ENDPOINT",
    "https://ai103-interview-coach-2.services.ai.azure.com/api/projects/ai-interview-coach-2"
)
AGENT_NAME = "AI-Interview-Coach"
TENANT_ID = os.environ.get(
    "AZURE_TENANT_ID",
    "631d9c12-cb9d-4e4d-baaf-8e90208da033"
)

openai_client = None


def get_client():
    """Initializes and returns the OpenAI client from Azure AI Project Client."""
    global openai_client
    if openai_client is None:
        try:
            # First try DefaultAzureCredential (leverages active az login)
            credential = DefaultAzureCredential(tenant_id=TENANT_ID)
            project = AIProjectClient(endpoint=ENDPOINT, credential=credential)
            openai_client = project.get_openai_client()
        except Exception as e:
            print(f"DefaultAzureCredential attempt failed: {e}. Falling back to InteractiveBrowserCredential...")
            credential = InteractiveBrowserCredential(tenant_id=TENANT_ID)
            project = AIProjectClient(endpoint=ENDPOINT, credential=credential)
            openai_client = project.get_openai_client()
    return openai_client


def create_conversation():
    """Creates a new conversation thread in Azure AI Foundry."""
    client = get_client()
    conversation = client.conversations.create()
    return conversation.id


def ask_agent(conversation_id, message, vector_store_id=None):
    """Sends a message to the AI agent and returns the response."""
    client = get_client()
    if vector_store_id:
        response = client.responses.create(
            model="gpt-4.1-mini",
            conversation=conversation_id,
            input=message,
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id]
                }
            ]
        )
    else:
        response = client.responses.create(
            model="gpt-4.1-mini",
            conversation=conversation_id,
            input=message
        )
    return response.output_text


def upload_resume(resume_file):
    """Uploads resume to Azure AI Files and links to a new Vector Store for File Search."""
    client = get_client()
    file = client.files.create(
        file=(resume_file.name, resume_file.getvalue()),
        purpose="assistants"
    )

    vector_store = client.vector_stores.create(
        name=f"resume_{resume_file.name}"
    )

    client.vector_stores.files.create(
        vector_store_id=vector_store.id,
        file_id=file.id
    )

    # File Search only works after the vector store finishes indexing.
    for _ in range(40):
        vs = client.vector_stores.retrieve(vector_store.id)
        status = getattr(vs, "status", None)
        if status in ("completed", "ready"):
            break
        time.sleep(0.75)

    return vector_store.id


def request_evaluation_report(conversation_id, vector_store_id=None):
    """Requests a structured final evaluation report at the end of the interview."""
    report_prompt = """
The interview has concluded. Now generate the comprehensive final candidate evaluation report based on the candidate's answers.
Format the output in clean, structured Markdown with the following exact sections:

# Final Candidate Evaluation Report

## Overall Performance
- Overall Score: [X]/10
- Performance Tier: [Job Ready / Needs Preparation / Significant Growth Required]
- Executive Summary: [A concise 2-3 sentence summary of candidate performance]

## Question-Wise Scores
- Question 1: [Score]/10 - [Brief feedback on answer quality]
- Question 2: [Score]/10 - [Brief feedback]
(Include score for each question asked)

## Strengths
- [Key strength 1 with evidence from candidate answers]
- [Key strength 2 with evidence]
- [Key strength 3]

## Weaknesses
- [Key weakness 1]
- [Key weakness 2]

## Technical Gaps
- [Specific technical concepts, tools, or best practices missing or needing depth]
- [Technical architecture or coding gaps]

## Communication Analysis
- Structure & Articulation: [Assessment of clarity, conciseness, and precision]
- STAR Method Alignment: [How well candidate structured behavioral scenarios]
- Confidence & Professional Tone: [Assessment of candidate communication style]

## Improvement Suggestions
- [Actionable suggestion 1]
- [Actionable suggestion 2]
- [Actionable suggestion 3]
"""
    return ask_agent(conversation_id, report_prompt, vector_store_id)


def request_study_plan(conversation_id, vector_store_id=None):
    """Requests a personalized 7-day study plan tailored to the candidate's interview gaps."""
    plan_prompt = """
Based on the candidate's performance, gaps, and selected role, generate a personalized 7-day preparation and study plan.
Format the output in clean Markdown with the following exact structure:

# Personalized 7-Day Study & Preparation Plan

## Personalized Topics to Improve
- [Topic 1: Specific skill or concept to master]
- [Topic 2: Specific skill or concept]
- [Topic 3: Specific skill or concept]

## Daily Action Plan
- **Day 1: Core Fundamentals & Concept Refresh** - [Specific actionable task]
- **Day 2: Technical Deep-Dive & Architecture** - [Specific actionable task]
- **Day 3: Hands-on Implementation & Problem Solving** - [Specific actionable task]
- **Day 4: System Design & Cloud Best Practices** - [Specific actionable task]
- **Day 5: Behavioral Questions & STAR Mastery** - [Specific actionable task]
- **Day 6: Timed Mock Drill & Scenario Practice** - [Specific actionable task]
- **Day 7: Final Review, Confidence & Presentation Prep** - [Specific actionable task]

## Recommended Resources
- [Curated resource 1]
- [Curated resource 2]
- [Curated resource 3]
"""
    return ask_agent(conversation_id, plan_prompt, vector_store_id)