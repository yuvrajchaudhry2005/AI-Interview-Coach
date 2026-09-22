# Interview IQ - AI Interview Coach

Interview IQ is a college AI prototype for realistic, resume-grounded technical, HR, behavioral, and mixed mock interviews. It uses Microsoft Azure AI Foundry for question generation, document grounding, evaluation, and study-plan generation, with Azure AI Speech for optional voice answers.

## 1. Project Overview

Preparing for interviews is more useful when practice is personalized to the candidate's own projects and skills. Interview IQ turns a resume into an interactive interview session instead of relying on a static question bank.

The application provides:

1. Account creation and login.
2. Resume upload and interview configuration.
3. AI-generated questions grounded in the uploaded PDF resume.
4. Typed or voice-based answers with editable transcription.
5. Optional camera capture controlled by the candidate.
6. A final score, strengths, weaknesses, technical gaps, and communication analysis.
7. A personalized seven-day preparation plan.
8. A history dashboard showing interview count and scores.

## 2. Key Features

- **Resume grounding:** Upload a PDF resume, which is indexed through Microsoft Foundry File Search.
- **Adaptive conversation:** Follow-up questions use the current Foundry conversation and previous answers.
- **Configurable interview:** Select the role, experience level, interview type, and number of questions.
- **Voice answers:** Record an answer in the browser and transcribe it with Azure AI Speech.
- **Editable transcript:** Review and correct the generated transcript before submitting it.
- **Optional camera:** Enable camera capture only when desired. Camera frames are not sent to Foundry or saved in history.
- **Post-interview analytics:** Receive an overall score, question-wise scores, strengths, weaknesses, technical gaps, and improvement suggestions.
- **Study plan:** Generate a role-specific seven-day preparation plan from the interview results.
- **Account history:** View previous interview attempts, average score, best score, and total questions.
- **Local privacy controls:** Delete the local account and associated interview history from the sidebar.

## 3. Application Workflow

```text
Candidate browser
       |
       v
Streamlit interface (app.py)
       |
       +--> Login and sign-up
       |        |
       |        +--> SQLite users and interview history
       |
       +--> PDF resume upload
       |        |
       |        +--> Azure AI Foundry File Search / Vector Store
       |
       +--> Interview conversation
       |        |
       |        +--> Microsoft Foundry Responses API
       |        +--> gpt-4.1-mini
       |        +--> File Search grounding
       |
       +--> Optional voice answer
       |        |
       |        +--> Azure AI Speech-to-Text
       |        +--> SpeechRecognition fallback
       |
       +--> Final report and study plan
                |
                +--> Score saved to local interview history
```

## 4. Technology Stack

- **Frontend and application runtime:** Streamlit
- **Language:** Python
- **AI platform:** Microsoft Azure AI Foundry
- **Model:** `gpt-4.1-mini`
- **Foundry SDK:** `azure-ai-projects`
- **Authentication:** Azure Identity with `DefaultAzureCredential` and interactive browser fallback
- **Document grounding:** Microsoft Foundry Files, Vector Stores, and File Search
- **Speech-to-text:** Azure Cognitive Services Speech SDK
- **Speech fallback:** `SpeechRecognition` with Google recognition during local demos
- **Local persistence:** SQLite
- **Password security:** PBKDF2-SHA256 with a random salt
- **Configuration:** `python-dotenv`

## 5. Azure Services Required

1. **Microsoft Foundry project**
   - A Microsoft Foundry project endpoint.
   - Access to the `gpt-4.1-mini` model.
   - Permissions to create conversations, files, and vector stores.

2. **Azure AI Speech resource** (optional)
   - A Speech resource in a supported Azure region.
   - Required only for Azure Speech transcription. The application has a local fallback for demos.

3. **Azure identity access**
   - An Azure CLI login or another credential supported by `DefaultAzureCredential`.

## 6. Environment Variables

Create a `.env` file in the project root:

```env
# Microsoft Foundry project endpoint
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project-name>
AZURE_TENANT_ID=<your-tenant-id>

# Optional Azure AI Speech configuration
SPEECH_KEY=<your-speech-key>
SPEECH_REGION=<your-speech-region>

# Optional local database location
AUTH_DATABASE_PATH=interview_coach.db
```

Never commit `.env`, access keys, passwords, or tokens. The Foundry client uses Azure Identity instead of a hardcoded Foundry API key.

## 7. Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 8. Azure CLI Authentication

```powershell
az login
az account show
```

If multiple subscriptions are available:

```powershell
az account set --subscription "<subscription-name-or-id>"
```

The application first tries `DefaultAzureCredential`. If that cannot authenticate, it opens an interactive browser login using `InteractiveBrowserCredential`.

## 9. Running the Application

```powershell
streamlit run app.py
```

Open the local application at:

```text
http://localhost:8501
```

## 10. Data Storage and Privacy

### Local SQLite database

The file `interview_coach.db` stores:

- User name, email, password hash, and account creation date.
- Completed interview role, interview type, score, question count, and completion date.

Passwords are never stored as plain text. The database is local by default and is ignored by Git.

### Microsoft Foundry

- The uploaded PDF resume is sent to Microsoft Foundry Files and attached to a Vector Store for File Search.
- Interview messages and answers are sent through the Foundry conversation.
- Foundry generates questions, evaluation reports, and study plans.

### Camera

Camera use is optional. Captured frames are not sent to Foundry, saved to SQLite, or included in interview history.

## 11. Testing and Verification

Run the local authentication and history tests:

```powershell
python -m unittest -v test_auth.py
```

Compile the Python modules:

```powershell
python -m py_compile app.py auth_store.py test_auth.py
```

`test_foundry.py` is an interactive Azure Foundry smoke-test script. It requires Azure access and may open a browser for authentication.

## 12. Responsible AI

- **Educational purpose:** Interview IQ is a preparation tool, not a hiring decision system.
- **Transparency:** The application tells users that reports are AI-generated and may contain errors or bias.
- **Human oversight:** A human should review results before they are used in any consequential decision.
- **Privacy:** Users control whether to enable the camera and can delete their local account and interview history.
- **Fairness limitation:** The prototype does not yet include formal demographic fairness testing or independent model benchmarking.
- **No psychological assessment:** The system is intended to evaluate interview answers, technical relevance, depth, and communication structure, not personality, mental state, honesty, or employability.

## 13. Originality and Acknowledgements

The application workflow and user experience are this project's work. The project uses and acknowledges:

- Streamlit for the application interface.
- Microsoft Azure AI Foundry and `azure-ai-projects` for model responses and File Search.
- Azure Identity for Microsoft Entra authentication.
- Azure Cognitive Services Speech SDK for speech-to-text.
- `SpeechRecognition` for the local speech fallback.
- Python SQLite and PBKDF2-SHA256 for local account storage.
- AI-assisted development tools used during implementation and reviewed by the project team.

Add exact source links, licenses, datasets, prompts, and team member contributions to the final submission package where required by the institution.

## 14. Current Limitations and Future Improvements

- Current document upload supports PDF resumes; DOCX and TXT ingestion are not yet implemented.
- Formal fairness testing and model benchmarking are not yet included.
- Azure-side deletion of uploaded resumes and Foundry vector stores is not yet automated.
- Production deployment should add HTTPS, managed identity, secret management, access controls, backups, and a documented data-retention policy.
- Future versions could add custom scoring rubrics, exportable PDF reports, and optional Azure Vision-based presentation coaching with explicit consent.
