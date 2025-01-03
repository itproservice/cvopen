import os
import logging
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from authenticate import authenticate_drive  # Importando a função de autenticação

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para listar arquivos em uma pasta
def list_files_in_folder(service, folder_id):
    try:
        logging.info(f"Listando arquivos na pasta ID: {folder_id}")
        results = service.files().list(
            q=f"'{folder_id}' in parents", fields="files(id, name)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        logging.error("Erro ao listar arquivos", exc_info=True)
        raise e

# Função para baixar arquivos
def download_file(service, file_id, file_name, download_path):
    try:
        logging.info(f"Baixando arquivo: {file_name} (ID: {file_id})")
        request = service.files().get_media(fileId=file_id)
        file_path = os.path.join(download_path, file_name)
        os.makedirs(download_path, exist_ok=True)

        with open(file_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logging.info(f"Download {int(status.progress() * 100)}% concluído.")
    except Exception as e:
        logging.error(f"Erro ao baixar arquivo: {file_name}", exc_info=True)
        raise e

# Função para atualizar o repositório no GitHub
def update_github_repo():
    try:
        logging.info("Atualizando o repositório GitHub...")
        # Configuração do repositório
        repo_url = os.getenv('github.com/itproservice/cvopen.git')  # URL do repositório
        token = os.getenv('GITHUB_TOKEN')  # Token do GitHub
        repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

        if not repo_url or not token:
            raise ValueError("As variáveis de ambiente 'GITHUB_REPO_URL' e 'GITHUB_TOKEN' devem estar configuradas.")

        os.chdir(repo_path)  # Navegar até o diretório do repositório

        # Comandos Git
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", "Atualizando currículos"], check=True)
        subprocess.run(["git", "push", f"https://{token}@{repo_url}"], check=True)

        logging.info("Repositório atualizado com sucesso!")
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao enviar para o GitHub: {e}")
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")

if __name__ == "__main__":
    TOKEN_PATH = "token.json"
    CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "../credentials.json")
    FOLDER_ID = "1Kg_krUauUwMEHVeR9vWEj1-4eqHT-qEc"
    
    # Define o diretório "curriculos" dentro de "analyze"
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, "curriculos")

    try:
        # Autenticar e construir o serviço
        creds = authenticate_drive(token_path=TOKEN_PATH, credentials_path=CREDENTIALS_PATH)
        service = build('drive', 'v3', credentials=creds)

        # Listar arquivos
        files = list_files_in_folder(service, FOLDER_ID)
        if not files:
            logging.warning("Nenhum arquivo encontrado na pasta especificada.")
        else:
            for file in files:
                download_file(service, file['id'], file['name'], DOWNLOAD_DIR)

        # Atualizar repositório no GitHub
        update_github_repo()
    except Exception as e:
        logging.critical("Erro crítico na execução do script", exc_info=True)
