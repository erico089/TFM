from smolagents import CodeAgent
from dotenv import load_dotenv
import os
from azureOpenAIServerModel import AzureOpenAIServerModel

class OrchestrationAgent:
    def __init__(self):
        load_dotenv()
        api_key = os.environ["AZURE_OPENAI_KEY"]
        deployment_name = os.environ["AZURE_OPENAI_MODEL_ID"]
        api_base = os.environ["AZURE_OPENAI_ENDPOINT"] 
        api_version = os.environ["AZURE_API_VERSION"] 

        model = AzureOpenAIServerModel(
            model_id = deployment_name,
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=api_base
        )

        self.agent = CodeAgent(
            model=model
        )

    def analyze_prompt(self, prompt):
        print(f"Analizando el prompt recibido: '{prompt}'")
        # Aquí es donde más adelante implementarás tu lógica real
        # Por ahora simplemente respondemos con un mensaje simulado
        print("Este es un análisis básico del prompt. (Lógica real pendiente de implementar)")
