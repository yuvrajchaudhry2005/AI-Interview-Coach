import streamlit as st
from foundry_client import create_conversation, ask_agent
from speech_service import speech_to_text

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 AI Interview Coach")
st.write("Your personal AI-powered interview practice partner.")

# Store interview data
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False


# Sidebar
with st.sidebar:
    st.header("Interview Setup")

    resume = st.file_uploader(
        "Upload your resume",
        type=["pdf"],
        help="Upload your resume in PDF format"
    )

    role = st.text_input(
        "Target Job Role",
        placeholder="e.g. Backend Developer"
    )

    experience = st.selectbox(
        "Experience Level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    if st.button("Start New Interview"):

        if not role:
            st.warning("Please enter your target job role.")

        elif not resume:
            st.warning("Please upload your resume.")

        else:
            st.session_state.conversation_id = create_conversation()
            st.session_state.messages = []
            st.session_state.interview_started = True

            first_prompt = f"""
I am preparing for a {role} interview.
My experience level is {experience}.

I have uploaded my resume.

Start my interview using my resume when relevant.
Ask me one interview question at a time.
Start with my projects and technical skills.
Wait for my answer before asking the next question.
Evaluate my answers and give a score out of 10 with feedback.
"""

            response = ask_agent(
                st.session_state.conversation_id,
                first_prompt
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )


# Display chat
if st.session_state.interview_started:

    st.subheader("💬 Interview")

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Text answer
    answer = st.chat_input("Type your answer here...")

    # Voice answer
    voice_answer = st.audio_input("🎤 Answer using your voice")

    # Convert voice to text
    if voice_answer:

        with open("voice_input.wav", "wb") as f:
            f.write(voice_answer.getvalue())

        with st.spinner("🎤 Converting your voice to text..."):
            answer = speech_to_text("voice_input.wav")

        if answer:
            st.info(f"🎤 You said: {answer}")
        else:
            st.warning("Sorry, I could not understand the audio.")


    # Send answer to AI
    if answer:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": answer
            }
        )

        with st.chat_message("user"):
            st.write(answer)

        with st.chat_message("assistant"):

            with st.spinner("Evaluating your answer..."):

                response = ask_agent(
                    st.session_state.conversation_id,
                    answer
                )

            st.write(response)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )