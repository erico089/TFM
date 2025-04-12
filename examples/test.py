from smolagents import CodeAgent, DuckDuckGoSearchTool, OpenAIServerModel, tool
from smolagents.tools import Tool
from dotenv import load_dotenv
import requests
import os


# ---------- Configuración del agente ----------
load_dotenv()
api_key = os.environ["OPENROUTER_API_KEY"]

model = OpenAIServerModel(
    model_id="deepseek/deepseek-v3-base:free",
    api_key=api_key,
    api_base="https://openrouter.ai/api/v1"
)

agent = CodeAgent(
    model=model,
    tools=[
        DuckDuckGoSearchTool()
    ]
)

agent.run("Who is the CEO of Hugging Face?")