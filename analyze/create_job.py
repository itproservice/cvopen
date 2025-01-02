import uuid
from models.job import Job
from database import AnalyzeDatabase
import logging
from textwrap import dedent

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_job(database: AnalyzeDatabase, name: str, activities: str, prerequisites: str, differentials: str):
    """
    Cria e insere uma vaga no banco de dados.

    Args:
        database (AnalyzeDatabase): Instância do banco de dados.
        name (str): Nome da vaga.
        activities (str): Atividades principais.
        prerequisites (str): Pré-requisitos.
        differentials (str): Diferenciais.
    """
    try:
        # Verifica se uma vaga com o mesmo nome já existe
        existing_job = database.get_job_by_name(name)
        if existing_job:
            logging.warning(f"Uma vaga com o nome '{name}' já existe no banco de dados.")
            return

        # Cria a vaga
        job = Job(
            id=str(uuid.uuid4()),
            name=name,
            main_activities=activities.strip(),
            prerequisites=prerequisites.strip(),
            differentials=differentials.strip(),
        )

        # Insere no banco de dados
        database.jobs.insert(job.model_dump())
        logging.info(f"Vaga '{name}' criada e inserida no banco de dados com sucesso.")
    except Exception as e:
        logging.error("Erro ao criar ou inserir a vaga no banco de dados.", exc_info=True)
        raise e


if __name__ == "__main__":
    # Instância do banco de dados
    database = AnalyzeDatabase()

    # Informações da vaga
    name = "Vaga de Assessor Legislativo"

    activities = dedent('''
        Assessorar a Mesa Diretora e os Vereadores na orientação e desenvolvimento dos trabalhos legislativos.
        Receber, registrar, classificar, tramitar e controlar a movimentação de documentos e processos legislativos, conforme orientação e determinação da chefia imediata.
        Recepcionar e atender munícipes, entidades, associações de classe e demais visitantes que procuram os Vereadores, inteirando-se dos assuntos a serem tratados, objetivando prestar-lhes as informações desejadas.
        Organizar e manter atualizados os arquivos de documentos do setor legislativo, visando à agilização de informações.
        Assessorar e auxiliar na elaboração das pautas das sessões, organizando as matérias a serem discutidas.
        Permanecer à disposição da Câmara no horário de expediente para serviços internos e externos, que lhe forem determinados.
        Participar das sessões ordinárias, extraordinárias e solenes, assessorando e auxiliando a Mesa e os Vereadores.
        Auxiliar nas atividades de protocolo nas solenidades oficiais, recepcionando autoridades e visitantes para cumprir a programação estabelecida.
        Encaminhar documentos, tais como: ofícios, convites, convocações e demais comunicados de interesse dos Vereadores.
        Realizar demais tarefas ligadas à sua área de atuação.
    ''')

    prerequisites = dedent('''
        Ensino superior completo em Direito, Administração Pública, Ciências Políticas ou áreas correlatas.
        Domínio comprovado do processo legislativo e suas etapas.
        Conhecimento aprofundado da Lei Orgânica Municipal e Regimento Interno da Câmara.
        Excelente capacidade de redação oficial e técnica legislativa.
        Experiência prévia em cargo similar em órgãos públicos (mínimo 2 anos).
        Habilidade avançada em gestão documental e sistemas de protocolo.
        Domínio do pacote Office e sistemas internos de tramitação.
        Excelente comunicação verbal e capacidade de atendimento ao público.
        Disponibilidade para horário flexível (incluindo período noturno para sessões).
        Capacidade comprovada de organização e atenção aos detalhes.
        Habilidade em articulação política e relacionamento institucional.
    ''')

    differentials = dedent('''
        Pós-graduação na área.
        Experiência em articulação governamental.
        Domínio de ferramentas tecnológicas avançadas.
        Certificações especializadas.
        Conhecimento aprofundado do município.
        Habilidade com mídias sociais.
        Fluência em outro idioma.
    ''')

    # Cria a vaga
    create_job(database, name, activities, prerequisites, differentials)
