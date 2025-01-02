import os
import uuid
import time
import re
from helper import extract_data_analysis, get_pdf_paths, read_uploaded_file, format_cv
from database import AnalyzeDatabase
from ai import OpenAIClient  # Mudando para OpenAIClient
from models.resum import Resum
from models.file import File
from openai import RateLimitError  # Mudando o import do RateLimitError


# Instanciar a base de dados
database = AnalyzeDatabase()

# Instanciar o cliente AI
ai = OpenAIClient()  # Mudando para OpenAIClient

# Obter job pelo nome
job = database.get_job_by_name("Vaga de Assessor Legislativo")
if not job:
    raise ValueError("Job 'Vaga de Assessor Legislativo' não encontrado.")

# Obter o caminho absoluto do diretório 'curriculos'
current_dir = os.path.dirname(os.path.abspath(__file__))
cv_paths = get_pdf_paths(os.path.join(current_dir, "drive", "curriculos"))
if not cv_paths:
    print("Nenhum currículo encontrado no diretório 'drive/curriculos'.")
    exit()

# Configurações
batch_size = 1  # Processar 1 currículo por vez inicialmente
max_attempts = 5  # Máximo de tentativas por arquivo
base_wait_time = 5  # tempo de espera minimo


def extract_wait_time(error_message):
    """Extrai o tempo de espera da mensagem de erro da API."""
    match = re.search(r"Please try again in ([\d.]+)(s|m)", error_message)
    if match:
        wait_time = float(match.group(1))
        unit = match.group(2)
        if unit == "m":
            wait_time *= 60
        return wait_time
    return base_wait_time  # tempo de espera padrão se não encontrar tempo na mensagem


# Processar cada currículo com espera dinâmica
for path in cv_paths:
    attempts = 0
    while attempts < max_attempts:
        try:
            # Verificar se o arquivo já foi processado
            existing_resum = database.get_resum_by_file(path)
            if existing_resum:
                print(f"Currículo {path} já foi processado. Pulando.")
                break
                
            content = read_uploaded_file(path)
            
            # Formatar o currículo
            formatted_content = format_cv(content)

            resum = ai.resume_cv(formatted_content)
            if resum is None:
                print(f"Erro ao gerar resumo para {path}. Pulando arquivo")
                break

            opnion = ai.generate_opnion(formatted_content, job)
            if opnion is None:
                print(f"Erro ao gerar opiniao para {path}. Pulando arquivo")
                break

            score = ai.generate_score(formatted_content, job)
            if score is None:
                print(f"Erro ao gerar score para {path}. Pulando arquivo")
                break

            resum_schema = Resum(
                id=str(uuid.uuid4()),
                job_id=job.get("id"),
                content=resum,
                file=str(path),
                opnion=opnion,
            )

            file_schema = File(
                file_id=str(uuid.uuid4()),
                job_id=job.get("id"),
            )

            analysis_schema = extract_data_analysis(
                resum, content, job.get("id"), resum_schema.id, score
            )

            # Inserir no banco de dados
            database.resums.insert(resum_schema.model_dump())
            database.analysis.insert(analysis_schema.model_dump())
            database.files.insert(file_schema.model_dump())

            break  # Se o processamento for bem-sucedido, saia do loop de tentativas

        except RateLimitError as e:
            attempts += 1
            wait_time = extract_wait_time(str(e))
            print(
                f"Rate limit atingido ao processar {path}. Aguardando {wait_time:.2f} segundos..."
            )
            time.sleep(wait_time)
            if attempts >= max_attempts:
                print(
                    f"Número máximo de tentativas atingido ao processar {path}, pulando para o proximo..."
                )
        except Exception as e:
            print(f"Erro inesperado ao processar {path}: {e}")
            break  # se ocorrer algum outro erro, sair do loop
    else:
        print(f"Falha ao processar {path} após varias tentativas")

print("Todos os currículos foram processados (ou pulados devido a falhas).")