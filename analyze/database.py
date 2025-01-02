from tinydb import TinyDB, Query

class AnalyzeDatabase:
    def __init__(self, file_path='db.json'):
        self.db = TinyDB(file_path)
        self.jobs = self.db.table('jobs')  # Tabela de vagas
        self.resums = self.db.table('resums')  # Tabela de currículos
        self.analysis = self.db.table('analysis')  # Tabela de análises
        self.files = self.db.table('files')  # Tabela de arquivos

    def get_jobs(self):
        # Retorna os valores do dicionário de vagas
        jobs_data = self.jobs.all()
        if jobs_data:
            return list(jobs_data[0].values())
        return []

    def get_job_by_name(self, name):
        # Busca uma vaga pelo nome
        jobs_data = self.get_jobs()
        for job in jobs_data:
            if job.get('name') == name:
                return job
        return None

    def add_job(self, job_data):
        # Adiciona uma nova vaga ao banco de dados
        existing_jobs = self.jobs.all()
        if existing_jobs:
            jobs_dict = existing_jobs[0]  # TinyDB retorna os dados em uma lista
        else:
            jobs_dict = {}

        job_id = job_data.get('id')
        jobs_dict[job_id] = job_data

        self.jobs.truncate()  # Remove os dados antigos
        self.jobs.insert(jobs_dict)  # Insere o dicionário atualizado
