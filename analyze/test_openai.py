from openai import OpenAI

try:
    client = OpenAI()
    print("OpenAI importado e instanciado com sucesso!")
except Exception as e:
    print(f"Erro ao importar ou instanciar OpenAI: {e}")