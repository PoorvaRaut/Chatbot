import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import shelve

# Load environment variables
load_dotenv('example.env')  # Ensure 'example.env' exists and contains 'OPEN_API_KEY'
st.title("Chatbot")
api_key = os.getenv("OPEN_API_KEY")
if not api_key:
    st.error("OpenAI API key is missing. Check your environment variables.")
    st.stop()  # Stop execution if the API key is missing

client = OpenAI(api_key=api_key)

# Ensure OpenAI model and chat history are initialized
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

def load_chat_history():
    try:
        with shelve.open("chat_history") as db:
            return db.get("messages", [])
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
        return []

def save_chat_history(messages):
    try:
        with shelve.open("chat_history", "c") as db:
            db["messages"] = messages
    except Exception as e:
        st.error(f"Error saving chat history: {str(e)}")

# Load existing chat history
st.session_state.messages = load_chat_history()

# Sidebar to clear chat history
with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        save_chat_history(st.session_state.messages)

# Display existing chat messages
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Capture new user input
prompt = st.chat_input("How can I help?")

# Process user input
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🤖"):
        full_response = ""
        message_placeholder = st.empty()  # Initialize message placeholder
        
        try:
            for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=st.session_state["messages"],
                stream=True,
            ):
                full_response += response.choices[0].delta.content or ""
                message_placeholder.markdown(full_response + "|")
            message_placeholder.markdown(full_response)  # Finalize response display
        
        except Exception as e:
            st.error(f"Error in chat response: {str(e)}")
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Save updated chat history
    save_chat_history(st.session_state.messages)
