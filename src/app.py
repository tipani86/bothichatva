import os
import base64
import aiohttp
import asyncio
import traceback
from PIL import Image
import streamlit as st
from transformers import AutoTokenizer
from app_config import *
from utils import *

# Set global variables

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["TOKENIZERS_PARALLELISM"] = "false"


# Check environment variables

errors = []
for key in [
    "OPENAI_API_KEY", "OPENAI_ORG_ID",  # For OpenAI APIs
]:
    if key not in os.environ:
        errors.append(f"Please set the {key} environment variable.")
if len(errors) > 0:
    st.error("\n".join(errors))
    st.stop()


### FUNCTION DEFINITIONS ###


@st.cache_data(show_spinner=False)
def get_local_img(file_path: str) -> str:
    # Load a byte image and return its base64 encoded string
    return base64.b64encode(open(file_path, "rb").read()).decode("utf-8")


@st.cache_data(show_spinner=False)
def get_favicon(file_path: str):
    # Load a byte image and return its favicon
    return Image.open(file_path)


@st.cache_data(show_spinner=False)
def get_tokenizer():
    return AutoTokenizer.from_pretrained("gpt2", low_cpu_mem_usage=True)


@st.cache_data(show_spinner=False)
def get_css() -> str:
    # Read CSS code from style.css file
    with open(os.path.join(ROOT_DIR, "src", "style.css"), "r") as f:
        return f"<style>{f.read()}</style>"


def get_chat_message(
    contents: str = "",
    align: str = "left"
) -> str:
    # Formats the message in an chat fashion (user right, reply left)
    div_class = "AI-line"
    color = "rgb(240, 242, 246)"
    file_path = os.path.join(ROOT_DIR, "src", "assets", "AI_icon.png")
    src = f"data:image/gif;base64,{get_local_img(file_path)}"
    if align == "right":
        div_class = "human-line"
        color = "rgb(165, 239, 127)"
        file_path = os.path.join(ROOT_DIR, "src", "assets", "user_icon.png")
        src = f"data:image/gif;base64,{get_local_img(file_path)}"
    icon_code = f"<img class='chat-icon' src='{src}' width=32 height=32 alt='avatar'>"
    if contents == "":
        contents = "&#8203;"
    formatted_contents = f"""
    <div class="{div_class}">
        {icon_code}
        <div class="chat-bubble" style="background: {color};">
        {contents}
        </div>
    </div>
    """
    return formatted_contents


async def main(human_prompt: str) -> dict:
    res = {'status': 0, 'message': "Success"}
    try:

        # Strip the prompt of any potentially harmful html/js injections
        human_prompt = human_prompt.replace("<", "&lt;").replace(">", "&gt;")

        # Update both chat log and the model memory
        st.session_state.LOG.append(f"Human: {human_prompt}")
        st.session_state.MEMORY.append({'role': "user", 'content': human_prompt})

        # Clear the input box after human_prompt is used
        prompt_box.empty()

        with chat_box:
            # Write the latest human message first
            line = st.session_state.LOG[-1]
            contents = line.split("Human: ")[1]
            st.markdown(get_chat_message(contents, align="right"), unsafe_allow_html=True)

            reply_box = st.empty()
            reply_box.markdown(get_chat_message(), unsafe_allow_html=True)

            # This is one of those small three-dot animations to indicate the bot is "writing"
            writing_animation = st.empty()
            file_path = os.path.join(ROOT_DIR, "src", "assets", "loading.gif")
            writing_animation.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<img src='data:image/gif;base64,{get_local_img(file_path)}' width=30 height=10>", unsafe_allow_html=True)

            async with aiohttp.ClientSession() as httpclient:
                # Step 1: Generate the AI-aided image prompt using ChatGPT API
                # (but we first need to generate the prompt for ChatGPT!)
                prompt_res = await generate_prompt_from_memory_async(
                    httpclient,
                    TOKENIZER,
                    st.session_state.MEMORY,
                    os.getenv("OPENAI_API_KEY")
                )

                if DEBUG:
                    with st.sidebar:
                        st.write("prompt_res")
                        st.json(prompt_res, expanded=False)

                if prompt_res['status'] != 0:
                    res['status'] = prompt_res['status']
                    res['message'] = prompt_res['message']
                    return res

                # Call the OpenAI ChatGPT API
                chatbot_res = await get_chatbot_reply_data_async(
                    httpclient,
                    prompt_res['data']['messages'],
                    os.getenv("OPENAI_API_KEY")
                )

                if DEBUG:
                    with st.sidebar:
                        st.write("chatbot_res")
                        st.json(chatbot_res, expanded=False)

                if chatbot_res['status'] != 0:
                    res['status'] = chatbot_res['status']
                    res['message'] = chatbot_res['message']
                    return res

            reply_text = chatbot_res['data']

            if reply_text.startswith("AI: "):
                reply_text = reply_text.split("AI: ", 1)[1]

            # Render the reply as chat reply
            reply_box.markdown(get_chat_message(reply_text), unsafe_allow_html=True)

            # Clear the writing animation
            writing_animation.empty()

            # Update the chat log and the model memory
            st.session_state.LOG.append(f"AI: {reply_text}")
            st.session_state.MEMORY.append({'role': "assistant", 'content': reply_text})

    except:
        res['status'] = 2
        res['message'] = traceback.format_exc()

    return res

### INITIALIZE AND LOAD ###

# Initialize page config
favicon = get_favicon(os.path.join(ROOT_DIR, "src", "assets", "AI_icon.png"))
st.set_page_config(
    page_title="bothichatva 🙏 - a bodhisattva chatbot",
    page_icon=favicon,
)

# Get query parameters
query_params = st.experimental_get_query_params()
if "debug" in query_params and query_params["debug"][0].lower() == "true":
    st.session_state.DEBUG = True

if "DEBUG" in st.session_state and st.session_state.DEBUG:
    DEBUG = True


# Initialize some useful class instances
with st.spinner("Initializing App..."):
    TOKENIZER = get_tokenizer()  # First time after deployment takes a few seconds


### MAIN STREAMLIT UI STARTS HERE ###


# Define main layout
st.header("Amitabha 🙏")
chat_box = st.container()
prompt_box = st.empty()
footer = st.container()

with footer:
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

if DEBUG:
    with st.sidebar:
        st.subheader("Debug area")


# Load CSS code
st.markdown(get_css(), unsafe_allow_html=True)


# Initialize/maintain a chat log and chat memory in Streamlit's session state
# Log is the actual line by line chat, while memory is limited by model's maximum token context length
if "MEMORY" not in st.session_state:
    st.session_state.MEMORY = [{'role': "system", 'content': INITIAL_PROMPT}]
    st.session_state.LOG = [INITIAL_PROMPT]


# Render chat history so far
with chat_box:
    for i, line in enumerate(st.session_state.LOG[1:]):
        # For AI response
        if line.startswith("AI: "):
            contents = line.split("AI: ")[1]
            st.markdown(get_chat_message(contents), unsafe_allow_html=True)

        # For human prompts
        if line.startswith("Human: "):
            contents = line.split("Human: ")[1]
            st.markdown(get_chat_message(contents, align="right"), unsafe_allow_html=True)


# Define an input box for human prompts
with prompt_box:
    human_prompt = st.text_input("Enter:", value="", label_visibility="hidden",
                                 placeholder="Ask me anything about Buddhism, meditation, or life in general.", key=f"text_input_{len(st.session_state.LOG)}")


# Gate the subsequent chatbot response to only when the user has entered a prompt
if len(human_prompt) > 0:
    run_res = asyncio.run(main(human_prompt))
    if run_res['status'] == 0 and not DEBUG:
        st.experimental_rerun()

    else:
        if run_res['status'] != 0:
            st.error(run_res['message'])
        with prompt_box:
            if st.button("Show text input field"):
                st.experimental_rerun()
