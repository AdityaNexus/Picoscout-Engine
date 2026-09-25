import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(temperature : float = 0.1,max_tokens : int = 512):
    return ChatOpenAI(
        model = os.getenv("MODEL_NAME","local_model"),
        openai_api_key = os.getenv("OPENAI_API_KEY","local-key"),
        openai_api_base = os.getenv("OPENAI_API_BASE","http://localhost:8000/v1"),
        temperature = temperature,
        max_tokens = max_tokens,
    )
