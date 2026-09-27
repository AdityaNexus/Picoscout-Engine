import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(temperature: float | None = None, max_tokens: int = 512, thinking: bool = False):
    if thinking:
        temperature = 0.6 if temperature is None else temperature
        extra_body = {"top_p": 0.95, "top_k": 20, "min_p": 0}
    else:
        temperature = 0.3 if temperature is None else temperature
        extra_body = {"top_p": 0.8, "top_k": 20, "repetition_penalty": 1.1}

    return ChatOpenAI(
        model=os.getenv("MODEL_NAME", "local_model"),
        openai_api_key=os.getenv("OPENAI_API_KEY", "local-key"),
        openai_api_base=os.getenv("OPENAI_API_BASE", "http://localhost:8000/v1"),
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body=extra_body,
    )
