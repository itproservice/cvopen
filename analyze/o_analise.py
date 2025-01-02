import os
import uuid
from helper import extract_data_analysis, get_pdf_paths, read_uploaded_file
from database import AnalyzeDatabase
from ai import GroqClient
from models.resum import Resum
from models.file import File

# Instanciar a base de dados
database = AnalyzeDatabase()

# Instanciar o cliente AI
ai = GroqClient()

# Obter job pelo nome
job = database.get_job_by_name('Vaga de Assessor Legislativo')
if not job:
    raise ValueError("Job 'Vaga de Assessor Legislativo' não encontrado.")

# Obter o caminho absoluto do diretório 'curriculos'
current_dir = os.path.dirname(os.path.abspath(__file__))
cv_paths = get_pdf_paths(os.path.join(current_dir, 'drive', 'curriculos'))
if not cv_paths:
    print("Nenhum currículo encontrado no diretório 'drive/curriculos'.")
    exit()

# Processar cada currículo
for path in cv_paths:
    try:
        content = read_uploaded_file(path)
        resum = ai.resume_cv(content)
        opinion = ai.generate_opinion(content, job.get('name'))
        
        # Truncar opinião para respeitar o limite de 1000 caracteres
        if len(opinion) > 1000:
            opinion = opinion[:997] + "..."
        
        score = ai.generate_score(content, job.get('name'), max_attempts=5)  # Reduzido para 5 tentativas

        if score is None:
            score = 0

        print(f"Tamanho da opinião: {len(opinion)} caracteres")

        resum_schema = Resum(
            id=str(uuid.uuid4()),
            job_id=job.get('id'),
            content=resum,
            file=str(path),
            opinion=opinion  # Salva a opinião truncada
        )

        file_schema = File(
            file_id=str(uuid.uuid4()),
            job_id=job.get('id'),
        )

        analysis_schema = extract_data_analysis(resum, job.get('id'), resum_schema.id, score)

        # Inserir no banco de dados
        database.resums.insert(resum_schema.model_dump())
        database.analysis.insert(analysis_schema.model_dump())
        database.files.insert(file_schema.model_dump())
    except Exception as e:
        print(f"Erro ao processar o currículo {path}: {e}")
