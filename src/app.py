import os
import base64
import aiohttp
import asyncio
import traceback
import streamlit as st
from openai import AsyncOpenAI

from app_config import *

# Set global variables

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
client = AsyncOpenAI()

# Check environment variables

errors = []
for key in [
    "OPENAI_API_KEY"  # For OpenAI APIs
]:
    if key not in os.environ:
        errors.append(f"Please set the {key} environment variable.")
if len(errors) > 0:
    st.error("\n".join(errors))
    st.stop()


@st.cache_data(show_spinner=False)
def get_local_img(file_path: str) -> str:
    # Load a byte image and return its base64 encoded string
    return base64.b64encode(open(file_path, "rb").read()).decode("utf-8")


async def main():

    ### INITIALIZE AND LOAD ###

    # Initialize page config
    st.set_page_config(
        page_title="bothichatva 🙏 - a bodhisattva chatbot",
        page_icon=os.path.join(ROOT_DIR, "src", "assets", "AI_icon.png"),
    )

    ### MAIN STREAMLIT UI STARTS HERE ###


    # Define main layout
    st.header("Amitabha 🙏")
    info_box = st.container()
    chat_box = st.container()

    with info_box:
        st.info("""
        1. bo·dhi·satt·va _noun_  
        (in Mahayana Buddhism) a person who is able to reach nirvana but delays doing so out of compassion in order to save suffering beings. [[1](https://www.oxfordreference.com/display/10.1093/oi/authority.20110803095514796)]
        2. bot·hi·chat·va _noun_  
        a virtual bodhisattva chatbot with 24/7 access to everyone.
        """, icon="ℹ️")
        st.markdown("""
        <div align=right><small>
        <img src="https://www.cutercounter.com/hits.php?id=hmxndffd&nd=3&style=1" border="0" alt="best free website hit counter"> souls have sought out bothichatva <img src="https://www.cutercounter.com/hits.php?id=hxndfac&nd=4&style=1" border="0" alt="hit counter"> times.
        </small></div>
        """, unsafe_allow_html=True)
        st.write("")


    # Initialize/maintain a chat log and chat memory in Streamlit's session state
    # Log is the actual line by line chat, while memory is limited by model's maximum token context length
    if "MEMORY" not in st.session_state:
        st.session_state.MEMORY = [{'role': "system", 'content': INITIAL_PROMPT}]


    # Render chat history so far
    with chat_box:
        for item in st.session_state.MEMORY:
            if item['role'] == "user":
                with st.chat_message("user", avatar=os.path.join(ROOT_DIR, "src", "assets", "user_icon.png")):
                    st.markdown(item['content'])
            elif item['role'] == "assistant":
                with st.chat_message("assistant", avatar=os.path.join(ROOT_DIR, "src", "assets", "AI_icon.png")):
                    st.markdown(item['content'])


    # Define an input box for human prompts
    human_prompt = st.chat_input(
        placeholder="Ask me anything about Buddhism, meditation, or life in general."
    )

    # Gate the subsequent chatbot response to only when the user has entered a prompt
    if human_prompt:

        try:

            # Strip the prompt of any potentially harmful html/js injections
            human_prompt = human_prompt.replace("<", "&lt;").replace(">", "&gt;")

            # Update model memory
            st.session_state.MEMORY.append({'role': "user", 'content': human_prompt})

            with chat_box:
                # Write the latest human message first
                with st.chat_message("user", avatar=os.path.join(ROOT_DIR, "src", "assets", "user_icon.png")):
                    st.markdown(human_prompt)

                file_path = os.path.join(ROOT_DIR, "src", "assets", "loading.gif")
                with st.chat_message("assistant", avatar=os.path.join(ROOT_DIR, "src", "assets", "AI_icon.png")):
                    reply_box = st.empty()
                    with reply_box:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<img src='data:image/gif;base64,{get_local_img(file_path)}' width=30 height=10>", unsafe_allow_html=True)

                # Call the OpenAI API to generate a response
                stream = await client.chat.completions.create(
                    model=NLP_MODEL_NAME,
                    messages=st.session_state.MEMORY,
                    stream=True,
                    temperature=NLP_MODEL_TEMPERATURE,
                    max_completion_tokens=NLP_MODEL_REPLY_MAX_TOKENS,
                )

                reply_text = ""

                async for chunk in stream:
                    chunk_content = chunk.choices[0].delta.content
                    if chunk_content is not None:
                        reply_text += chunk_content
                        with reply_box:
                            st.markdown(reply_text)

                # Update the model memory
                st.session_state.MEMORY.append({'role': "assistant", 'content': reply_text})

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()


asyncio.run(main())