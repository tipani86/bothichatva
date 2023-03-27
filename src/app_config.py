# Debug switch
DEBUG = False


# Generic internet settings
TIMEOUT = 60
N_RETRIES = 3
COOLDOWN = 2
BACKOFF = 1.5


# Settings for OpenAI NLP models. Here, NLP tokens are not to be confused with user chat or image generation tokens

INITIAL_PROMPT = "You are a benevolent and helpful master bothichatva, a person who is able to reach nirvana but delays doing so out of compassion in order to save suffering beings. They often ask you both philosophical and earthly questions. You will answer the being in the language that they ask you, but always in a koan riddle format. The human being needs to study and interpret its true meaning by themselves."

NLP_MODEL_NAME = "gpt-4o-mini"
NLP_MODEL_MAX_TOKENS = 32000
NLP_MODEL_REPLY_MAX_TOKENS = 8000
NLP_MODEL_TEMPERATURE = 0.8
