from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

def get_llm():
  load_dotenv()
  llm = init_chat_model("gpt-5-nano", model_provider="openai",temperature=0.1,)
  return llm
