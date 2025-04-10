import streamlit as st
from openai import OpenAI
import os
from gtts import gTTS
import base64
import requests

# App title
flag = 0
st.set_page_config(page_title="🤙💬 IRIS Personal assistance")

DJANGO_API_URL = ""  # Define your Django API URL here if needed

# Navigation Panel using st.html in the sidebar
with st.sidebar:
    st.title('🤙💬 IRIS Panic Attack Assistance')
    st.write('This chatbot is created using the LLM model.')

    # HTML for navigation buttons
    navigation_html = """
    <style>
        .nav-button {
            display: block;
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            background-color: #4CAF50;
            color: white;
            text-align: center;
            text-decoration: none;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .nav-button:hover {
            background-color: #45a049;
        }
        .logout-button {
            background-color: #f44336;
        }
        .logout-button:hover {
            background-color: #da190b;
        }
    </style>
    <button class="nav-button" onclick="window.location.href='#panic'">Panic Attack Assistance</button>
    <button class="nav-button" onclick="window.location.href='#journaling'">Daily Journaling</button>
    <button class="nav-button" onclick="window.location.href='#dashboard'">Dashboard</button>
    <button class="nav-button logout-button" onclick="window.location.href='#logout'">Logout</button>
    """
    st.html(navigation_html)

    client = OpenAI(
        api_key=os.environ['LLAMA_API_TOKEN'],
        base_url="https://api.llmapi.com/"  
    )

    st.subheader('Models and parameters')
    selected_model = "llama3-8b" 
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=20, max_value=80, value=50, step=5)
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Hi Maria, It's me Kinsuki your personal healing partner. I'm sorry that you are having a panic attack, Let's guide you through this shall we?"}]
if "trigger" not in st.session_state.keys():
    st.session_state.trigger = None 
if "waiting_for_trigger" not in st.session_state.keys():
    st.session_state.waiting_for_trigger = False 


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi Maria, It's me Kinsuki your personal healing partner. I'm sorry that you are having a panic attack, Let's guide you through this shall we?"}]
    st.session_state.trigger = None
    st.session_state.waiting_for_trigger = False

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


if st.button("🚨 Panic Button"):
    pass

if user_input := st.chat_input(placeholder="Type your response here..."):
    pass