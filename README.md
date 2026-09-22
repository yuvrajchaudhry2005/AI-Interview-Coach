# AI Interview Coach

Practice realistic technical, HR, behavioral, or mixed interviews with an adaptive AI interviewer.

## Flow

Resume upload → Interview setup → Live interview → Final report → Study plan

- Questions are grounded in your PDF resume through Azure AI File Search.
- The interviewer asks one question at a time and does not score live.
- Voice answers use Azure Speech-to-Text (with a local fallback if speech credentials are missing).
- After the loop you get scores, gaps, communication notes, and a 7-day checklist.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Configure Azure in `.env` (`AZURE_AI_PROJECT_ENDPOINT`, `AZURE_TENANT_ID`, optional `SPEECH_KEY` / `SPEECH_REGION`). Sign in with Azure CLI or the interactive browser credential on first run.

## Accounts

The app includes login and sign-up. User records and completed interview history are stored in the local SQLite database `interview_coach.db`, with passwords protected by PBKDF2 hashing. After login, the setup screen shows interview count, average score, best score, total questions, and recent attempts. Set `AUTH_DATABASE_PATH` in `.env` to use a different database location.

## Privacy and Responsible AI

- Resumes are uploaded to Microsoft Foundry File Search so questions can reference the candidate's own projects and experience.
- Interview answers are sent through the Foundry conversation to generate follow-up questions, evaluation reports, and study plans.
- Camera access is optional. Captured frames are not sent to Foundry or stored in interview history.
- Local account data and scores are stored in `interview_coach.db`. Users can delete their local account and history from the sidebar.
- AI scores are practice guidance, can contain errors or bias, and must not be used as the sole hiring decision.
- Human review is expected before using interview results for a consequential decision.
- Production deployments should use HTTPS, managed identity or a secret manager, access controls, backups, and a documented Azure data-retention policy.

## Originality and Acknowledgements

The application logic and user experience are this project's work. It uses the following third-party technologies and services:

- Streamlit for the web interface.
- Microsoft Azure AI Foundry and `azure-ai-projects` for conversations, model responses, and File Search.
- Azure Identity for Microsoft Entra authentication.
- Azure Cognitive Services Speech SDK for speech-to-text.
- `SpeechRecognition` as a local/demo speech fallback.
- Python standard-library SQLite and PBKDF2-SHA256 password hashing for local account storage.
- AI-assisted development tools were used during implementation and reviewed by the project team.

The team should add the exact source links, licenses, datasets, prompts, and AI-assisted tools used in the final submission package.

## Known Responsible-AI Limitations

The prototype does not yet perform formal demographic fairness testing, independent model benchmarking, or remote Azure-data deletion. Those checks and retention controls are required before production use. The current design supports transparency, user control, local account deletion, and human oversight for a student prototype.
