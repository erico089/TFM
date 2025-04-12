from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

# Establecer el path de la caché
os.environ["TRANSFORMERS_VERBOSITY"] = "debug"
os.environ['HF_HOME'] = 'D:/huggingface_cache'

# Verificar si hay GPU disponible
if torch.cuda.is_available():
    print(f"🚀 GPU detectada: {torch.cuda.get_device_name(0)}")
else:
    print("⚠️ No se detectó GPU. Usando CPU.")

# Cargar el modelo localmente
model_name = "Qwen/Qwen2.5-Coder-32B-instruct"  # Ruta del modelo en Hugging Face

# Cargar el modelo y tokenizer de manera local
print(f"📦 Cargando modelo: {model_name}")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
    offload_folder="offload"
)

print("✅ Modelo cargado.")

print("📦 Cargando tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
print("✅ Tokenizer cargado.")

# Crear el modelo local para smolagents
class LocalHfApiModel(HfApiModel):
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def __call__(self, prompt, stop_sequences=None, **kwargs):
        # Asegúrate de que prompt sea siempre una cadena
        if not isinstance(prompt, str):
            prompt = str(prompt)

        print("🧠 Generando respuesta...")

        # Asegúrate de que el tokenizer haga truncado y padding
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.model.device)

        # Si hay stop_sequences, convertirlos en tokens para que el modelo los entienda
        if stop_sequences:
            # Asegúrate de que stop_sequences sea también una lista de strings
            stop_tokens = self.tokenizer(stop_sequences, return_tensors="pt", padding=True, truncation=True, max_length=512).input_ids
            eos_token_id = stop_tokens[0]  # Tomamos el primer token de stop_sequence como el EOS token
        else:
            eos_token_id = self.tokenizer.eos_token_id  # Usamos el EOS token por defecto

        # Generar la salida del modelo
        generated_ids = self.model.generate(
            **inputs,
            max_new_tokens=512,
            eos_token_id=eos_token_id,  # Usar eos_token_id para detener la generación
            **kwargs  # Asegurarse de pasar los demás argumentos
        )
        
        # Decodificar la salida generada
        response = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        
        # Asegurarse de retornar solo el string generado, sin tratar de acceder a un atributo 'content'
        return response

# Instanciar el modelo local
local_model = LocalHfApiModel(model, tokenizer)

# Crear el agente de búsqueda con un nombre único
web_agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=local_model,
    name="web_search_agent",  # Cambié el nombre aquí
    description="Runs web searches for you. Give it your query as an argument."
)

# Crear el agente principal con un nombre único también
manager_agent = CodeAgent(
    tools=[], model=local_model, managed_agents=[web_agent], name="main_manager_agent"  # Cambié el nombre aquí también
)

# Ejecutar la consulta
manager_agent.run("Who is the CEO of Hugging Face?")
