import re
import uuid
import os
import fitz
from models.analysis import Analysis


def read_uploaded_file(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def format_cv(text):
    """Formata o texto do currículo para um padrão consistente."""
    # Remover espaços extras
    text = " ".join(text.split())
    # Remover caracteres especiais (mantendo acentos e letras)
    text = re.sub(r"[^a-zA-Zà-úÀ-Ú0-9\s\.\,\-\:\#\n]", "", text)
    return text

def extract_data_analysis(resum_cv, original_cv, job_id, resum_id, score) -> Analysis:
    secoes_dict = {
        "id": str(uuid.uuid4()),
        "job_id": job_id,
        "resum_id": resum_id,
        "name": "",
        "skills": [],
        "education": [],
        "languages": [],
        "score": score,
    }

    name_patterns = [
        r"(?:##\s*Nome Completo\s*|Nome Completo\s*\|\s*Valor\s*\|\s*\S*\s*\|\s*|##\s*Nome\s*|Nome\s*|:\s*)([A-ZÀ-Úa-zà-ú\s\.\'\-]+)(?:$|\n)",
        r"nome\s*completo\s*[:\s-]*([\w\s\.\'\-]+)",
        r"nome\s*[:\s-]*([\w\s\.\'\-]+)",
         r"([A-ZÀ-Úa-zà-ú\s\.\'\-]+)(?:$|\n)"
    ]

    def clean_string(string: str) -> str:
        return re.sub(r"[\*\-]+", "", string).strip()
    
    found_name = False
    for pattern in name_patterns:
        match = re.search(pattern, resum_cv)
        if match:
            name = clean_string(match.group(1)).strip()
            if name and not name.isdigit() and name:
                secoes_dict["name"] = name
                found_name = True
                break
        
    if not found_name:
        for pattern in name_patterns:
            match = re.search(pattern, original_cv)
            if match:
                name = clean_string(match.group(1)).strip()
                if name and not name.isdigit() and name:
                  secoes_dict["name"] = name
                  found_name = True
                  break
    
    if not found_name:
      secoes_dict["name"] = "Nome não encontrado"

    patterns = {
        "skills": r"## Habilidades\s*([\s\S]*?)(?=##|$)",
        "education": r"## Educação\s*([\s\S]*?)(?=##|$)",
        "languages": r"## Idiomas\s*([\s\S]*?)(?=##|$)",
        "salary_expectation": r"## Pretensão Salarial\s*([\s\S]*?)(?=##|$)",
    }
    
    for secao, pattern in patterns.items():
        match = re.search(pattern, resum_cv)
        if match:
            secoes_dict[secao] = [
                clean_string(item) for item in match.group(1).split("\n") if item.strip()
            ]
        else:
             if secao in ["skills", "education", "languages"]:
                secoes_dict[secao] = []

    # Validação para garantir que nenhuma seção obrigatória esteja vazia
    for key in ["name", "education", "skills"]:
        if not secoes_dict[key] or (
            isinstance(secoes_dict[key], list) and not any(secoes_dict[key])
        ):
            if key == "name":
                secoes_dict[key] = "Nome não encontrado"
            else:
                secoes_dict[key] = []

    return Analysis(**secoes_dict)


def get_pdf_paths(directory):
    pdf_files = []

    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            pdf_files.append(file_path)

    return pdf_files