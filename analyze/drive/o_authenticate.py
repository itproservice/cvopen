import os
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Defina o escopo de acesso que você precisa
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly"
]

def authenticate_drive(token_path='token.json', credentials_path='analyses/credentials.json'):
    """
    Autentica o acesso ao Google Drive usando OAuth 2.0.

    Args:
        token_path (str): Caminho para o arquivo token.json.
        credentials_path (str): Caminho para o arquivo credentials.json.

    Returns:
        Credentials: Objeto de credenciais autenticado.
    """
    creds = None

    try:
        # Verifica se o arquivo token.json existe
        if os.path.exists(token_path):
            logging.info("Carregando credenciais do arquivo token.json")
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # Verifica se as credenciais são inválidas ou expiradas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logging.info("Renovando credenciais expiradas...")
                creds.refresh(Request())
            else:
                # Inicia o fluxo de autorização se não houver credenciais válidas
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {credentials_path}")
                logging.info("Iniciando o fluxo de autorização do OAuth...")
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Salva as credenciais renovadas ou novas no arquivo token.json
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
                logging.info("Credenciais salvas no arquivo token.json")

    except Exception as e:
        logging.error("Erro durante o processo de autenticação", exc_info=True)
        raise e

    return creds

if __name__ == "__main__":
    try:
        creds = authenticate_drive()
        logging.info("Autenticação concluída com sucesso!")
    except Exception as e:
        logging.critical("Erro crítico durante a autenticação", exc_info=True)
