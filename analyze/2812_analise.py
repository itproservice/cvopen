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
    content = read_uploaded_file(path)
    resum = ai.resume_cv(content)
    print(resum)
    opnion = ai.generate_opnion(content, job)
    print(opnion)
    score = ai.generate_score(content, job)
    print(score)

    resum_schema = Resum(
        id=str(uuid.uuid4()),
        job_id = job.get('id'),
        content=resum,
        file=str(path),
        opnion=opnion
    )

    file_schema = File(
        file_id = str(uuid.uuid4),
        job_id = job.get('id'),
    )
    
    analysis_schema = extract_data_analysis(resum, job.get('id'), resum_schema.id, score)

    # Inserir no banco de dados
    database.resums.insert(resum_schema.model_dump())
    database.analysis.insert(analysis_schema.model_dump())
    database.files.insert(file_schema.model_dump())

