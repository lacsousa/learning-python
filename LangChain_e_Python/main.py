from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
minha_api_key = os.getenv("OPENAI_API_KEY")

numero_dias = 2
numero_pessoas = 4
cidade_destino = "Paris"

prompt = f"""Crie um roteiro de viagem de {numero_dias} dias, para uma família de {numero_pessoas} pessoas, sem crianças, 
          para a cidade de {cidade_destino}, incluindo opções de restaurantes e hotéis adequados para famílias.""" 


client = OpenAI(api_key=minha_api_key)

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Você é um assistente de viagem especializado em criar roteiros personalizados para famílias."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    print(response.choices[0].message.content)

except Exception as e:
    print(f"Erro ao chamar API: {e}")