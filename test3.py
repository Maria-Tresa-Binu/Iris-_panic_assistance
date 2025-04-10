import streamlit as st
from openai import OpenAI
import os
import requests
import altair as alt

st.set_page_config(page_title="Iris")

DJANGO_API_URL = "" 

with st.sidebar:
    st.title('🤙💬 IRIS Daily journalling')
    st.write('This chatbot is created using the open-source Llama 2 LLM model.')
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
        api_key=os.environ['LLAMA_API_TOKEN'] ,
        base_url="https://api.llmapi.com/" 
    )

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['llama2-7b', 'llama2-13b'], key='selected_model')
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=20, max_value=80, value=50, step=5)
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi Maria, It's me Iris your personal healing partner. How was your day"}
    ]
if "mood" not in st.session_state:
    st.session_state.mood = None
if "waiting_for_mood" not in st.session_state:
    st.session_state.waiting_for_mood = False
if "response_emotion" not in st.session_state:
    st.session_state.response_emotion = [] 

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi Maria, It's me Iris your personal healing partner. How was your day"}
    ]
    st.session_state.mood = None
    st.session_state.waiting_for_mood = False
    st.session_state.response_emotion = [] 

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

def send_mood_to_django(mood):
    data = {"user_name": "Maria", "mood": mood}
    try:
        response = requests.post(DJANGO_API_URL, json=data)
        if response.status_code == 201:
            st.sidebar.success("Mood saved to database!")
        else:
            st.sidebar.error(f"Failed to save mood: {response.text}")
    except Exception as e:
        st.sidebar.error(f"Error connecting to Django API: {str(e)}")

def generate_llama2_response(prompt_input):
    global flag
    if flag:
        string_dialogue = ("You are a helpful medical assistant. You do not respond as 'User' or pretend to be 'User'. "
                          "If you sense anxiety in the user's response ask the user to name the feeling and rate it out of 100. "
                          "Ask the user to explain what makes them anxious and help them find positive alternatives of the negative thoughts. "
                          "Do it step by step not all together wait for each user response. "
                          "Do not assume that the user has anxiety only ask the user to rate the feelings if the user is in distress. "
                          "You don't respond as User or pretend to be the User ") + prompt_input 
        flag = False
    else:
        string_dialogue = ("You are a helpful medical assistant. You do not respond as 'User' or pretend to be 'User'. "
                          "You only respond as 'Assistant'. If the User is sharing about a problem in their life and is anxious, "
                          "help them find positive alternative to their negative thoughts and give them a different perspective where things will go right ") + prompt_input 

    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": string_dialogue},
            {"role": "user", "content": prompt_input or "Please respond"}
        ],
        model="llama3-8b",
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_length,
        stream=False
    )
    return chat_completion.choices[0].message.content

if user_input := st.chat_input(placeholder="Type your response here..."):
    if user_input.lower() != "im better now":
        st.session_state.response_emotion.append(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(user_input)
            placeholder = st.empty()
            full_response = response 
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
    
    if user_input.lower() == "im better now":
        print(st.session_state.response_emotion)  
        st.session_state.waiting_for_mood = True
       
        emotion_prompt = " ".join(st.session_state.response_emotion + 
                                ["Extract the most prevalent emotion from the user's response. Your response should be one word, just the extracted emotion."])
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": emotion_prompt},
                {"role": "user", "content": "Please extract the emotion"}
            ],
            model=selected_model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_length,
            stream=False
        )
        full_output = chat_completion.choices[0].message.content
        st.session_state.mood = full_output.strip()
        send_mood_to_django(st.session_state.mood) 

if st.session_state.mood:
    with st.sidebar:
        st.write(f"Stored Mood: {st.session_state.mood}")