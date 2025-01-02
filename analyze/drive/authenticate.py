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

def authenticate_drive(token_path='token.json', credentials_path=None):
    """
    Autentica o acesso ao Google Drive usando OAuth 2.0.

    Args:
        token_path (str): Caminho para o arquivo token.json.
        credentials_path (str): Caminho absoluto para o arquivo credentials.json.

    Returns:
        Credentials: Objeto de credenciais autenticado.
    """
    if credentials_path is None:
        credentials_path = r'C:\\IT\\CLOUD\\OneDrive - iTPRO SERVICE\\PROJETOS\\2016-01-000-iTPRO\\IA\\IAC\\analyze\\credentials.json'
    
    token_path = os.path.abspath(token_path)
    credentials_path = os.path.abspath(credentials_path)

    logging.info(f"Procurando arquivo de token em: {token_path}")
    logging.info(f"Procurando arquivo de credenciais em: {credentials_path}")

    # Verifica se o arquivo credentials.json existe
    if not os.path.exists(credentials_path) or not os.path.isfile(credentials_path):
        logging.error(f"Arquivo de credenciais não encontrado ou inacessível: {credentials_path}")
        raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {credentials_path}")
    else:
        logging.info(f"Arquivo de credenciais encontrado: {credentials_path}")
        logging.info(f"Tamanho do arquivo: {os.path.getsize(credentials_path)} bytes")

    creds = None
    if os.path.exists(token_path):
        logging.info("Carregando credenciais do arquivo token.json")
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Renovando credenciais expiradas...")
            creds.refresh(Request())
        else:
            logging.info("Iniciando o fluxo de autorização do OAuth...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            logging.info("Credenciais salvas no arquivo token.json")

    return creds

if __name__ == "__main__":
    try:
        creds = authenticate_drive()
        logging.info("Autenticação concluída com sucesso!")
    except Exception as e:
        logging.critical("Erro crítico durante a autenticação", exc_info=True)
