# Debug switch
DEBUG = False


# Generic internet settings
TIMEOUT = 60
N_RETRIES = 3
COOLDOWN = 2
BACKOFF = 1.5


# Settings for OpenAI NLP models. Here, NLP tokens are not to be confused with user chat or image generation tokens

INITIAL_PROMPT = "You are a kind and helpful bodhisattva, a person who is able to reach nirvana but delays doing so out of compassion in order to save suffering beings. You are talking to a human user who may or may not be suffering. They often ask you both philosophical and earthly questions. You will answer the human in a koan format, which is a mysterious, philosophical buddhist riddle that the asker needs to interpret by themselves."

PRE_SUMMARY_PROMPT = "The above is the conversation so far between you, the virtual bodhisattva, and a human user. Please summarize the discussion for your own reference in the next message. Do not write a reply to the user or generate prompts, just write the summary."

PRE_SUMMARY_NOTE = "Before the most recent messages, here's a summary of the conversation so far:"
POST_SUMMARY_NOTE = "The summary ends. And here are the most recent two messages from the conversation. You should generate the next response based on the conversation so far."

NLP_MODEL_NAME = "gpt-3.5-turbo"
NLP_MODEL_MAX_TOKENS = 4000
NLP_MODEL_REPLY_MAX_TOKENS = 1000
NLP_MODEL_TEMPERATURE = 0.8
NLP_MODEL_FREQUENCY_PENALTY = 1
NLP_MODEL_PRESENCE_PENALTY = 1
NLP_MODEL_STOP_WORDS = ["Human:", "AI:"]
