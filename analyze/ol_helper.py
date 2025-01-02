import re
import uuid
import os
import fitz
from models.analysis import Analysis

def read_uploaded_file(file_path):
    """
    Lê o conteúdo de um arquivo PDF e retorna o texto extraído.

    Args:
        file_path (str): Caminho do arquivo PDF.

    Returns:
        str: Texto extraído do PDF.
    """
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        raise RuntimeError(f"Erro ao ler o arquivo PDF '{file_path}': {e}")

def extract_data_analysis(resum_cv, job_id, resum_id, score) -> Analysis:
    """
    Extrai dados estruturados de um texto de currículo usando regex.

    Args:
        resum_cv (str): Texto do currículo.
        job_id (str): ID da vaga associada.
        resum_id (str): ID do resumo associado.
        score (float): Pontuação calculada.

    Returns:
        Analysis: Instância do modelo Analysis com os dados extraídos.
    """
    secoes_dict = {
        "id": str(uuid.uuid4()),
        "job_id": job_id,
        "resum_id": resum_id,
        "name": "",
        "skills": [],
        "education": [],
        "languages": [],
        "score": score
    }

    patterns = {
        "name": r"(?:## Nome Completo\s*|Nome Completo\s*\|\s*Valor\s*\|\s*\S*\s*\|\s*)(.*)",
        "skills": r"## Habilidades\s*([\s\S]*?)(?=##|$)",
        "education": r"## Educação\s*([\s\S]*?)(?=##|$)",
        "languages": r"## Idiomas\s*([\s\S]*?)(?=##|$)"
    }

    def clean_string(string: str) -> str:
        """
        Limpa uma string removendo caracteres indesejados.

        Args:
            string (str): Texto para limpar.

        Returns:
            str: Texto limpo.
        """
        return re.sub(r"[\*\-]+", "", string).strip()

    for secao, pattern in patterns.items():
        match = re.search(pattern, resum_cv)
        if match:
            if secao == "name":
                secoes_dict[secao] = clean_string(match.group(1))
            else:
                secoes_dict[secao] = [clean_string(item) for item in match.group(1).split('\n') if item.strip()]

    # Validação para garantir que nenhuma seção obrigatória esteja vazia
    for key in ["name", "education", "skills"]:
        if not secoes_dict[key] or (isinstance(secoes_dict[key], list) and not any(secoes_dict[key])):
            raise ValueError(f"A seção '{key}' não pode ser vazia ou uma lista vazia.")

    return Analysis(**secoes_dict)

def get_pdf_paths(directory):
    """
    Lista os caminhos de todos os arquivos PDF em um diretório.

    Args:
        directory (str): Caminho do diretório.

    Returns:
        list: Lista de caminhos para arquivos PDF.
    """
    if not os.path.exists(directory):
        raise RuntimeError(f"O diretório '{directory}' não existe.")

    try:
        pdf_files = [
            os.path.join(directory, filename)
            for filename in os.listdir(directory) if filename.endswith('.pdf')
        ]
        return pdf_files
    except Exception as e:
        raise RuntimeError(f"Erro ao listar arquivos no diretório '{directory}': {e}")
