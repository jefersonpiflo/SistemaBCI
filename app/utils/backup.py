import os
import shutil
from datetime import datetime
import subprocess
import boto3
from botocore.exceptions import ClientError
import schedule
import time
import logging

class BackupManager:
    def __init__(self, app_config):
        self.config = app_config
        self.backup_dir = app_config['BACKUP_DIR']
        self.db_uri = app_config['SQLALCHEMY_DATABASE_URI']
        
        # Configuração do S3 (opcional)
        self.s3_client = boto3.client('s3') if app_config.get('AWS_ACCESS_KEY') else None
        self.s3_bucket = app_config.get('AWS_BACKUP_BUCKET')
        
        # Configurar logging
        logging.basicConfig(
            filename=os.path.join(self.backup_dir, 'backup.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('backup')

    def criar_backup_banco(self):
        """Cria backup do banco de dados"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'db_backup_{timestamp}.sql')
        
        try:
            if 'sqlite' in self.db_uri:
                self._backup_sqlite(backup_path)
            else:
                self._backup_postgres(backup_path)
                
            self.logger.info(f'Backup do banco criado: {backup_path}')
            return backup_path
        except Exception as e:
            self.logger.error(f'Erro ao criar backup do banco: {str(e)}')
            raise

    def _backup_sqlite(self, backup_path):
        """Backup específico para SQLite"""
        db_path = self.db_uri.replace('sqlite:///', '')
        shutil.copy2(db_path, backup_path)

    def _backup_postgres(self, backup_path):
        """Backup específico para PostgreSQL"""
        cmd = f'pg_dump -U {self.config["DB_USER"]} -h {self.config["DB_HOST"]} ' \
              f'-d {self.config["DB_NAME"]} > {backup_path}'
        subprocess.run(cmd, shell=True, check=True)

    def backup_arquivos(self):
        """Backup dos arquivos de upload"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'files_backup_{timestamp}.zip')
        
        try:
            shutil.make_archive(
                backup_path.replace('.zip', ''),
                'zip',
                self.config['UPLOAD_FOLDER']
            )
            self.logger.info(f'Backup de arquivos criado: {backup_path}')
            return backup_path
        except Exception as e:
            self.logger.error(f'Erro ao criar backup de arquivos: {str(e)}')
            raise

    def enviar_para_s3(self, arquivo):
        """Envia backup para Amazon S3"""
        if not self.s3_client:
            return
        
        try:
            file_name = os.path.basename(arquivo)
            self.s3_client.upload_file(
                arquivo,
                self.s3_bucket,
                f'backups/{file_name}'
            )
            self.logger.info(f'Backup enviado para S3: {file_name}')
        except ClientError as e:
            self.logger.error(f'Erro ao enviar para S3: {str(e)}')
            raise

    def limpar_backups_antigos(self, dias=30):
        """Remove backups mais antigos que X dias"""
        limite = datetime.now().timestamp() - (dias * 24 * 60 * 60)
        
        for arquivo in os.listdir(self.backup_dir):
            if arquivo.startswith(('db_backup_', 'files_backup_')):
                arquivo_path = os.path.join(self.backup_dir, arquivo)
                if os.path.getctime(arquivo_path) < limite:
                    os.remove(arquivo_path)
                    self.logger.info(f'Backup antigo removido: {arquivo}')

    def executar_backup_completo(self):
        """Executa processo completo de backup"""
        try:
            db_backup = self.criar_backup_banco()
            files_backup = self.backup_arquivos()
            
            if self.s3_client:
                self.enviar_para_s3(db_backup)
                self.enviar_para_s3(files_backup)
                
            self.limpar_backups_antigos()
            self.logger.info('Backup completo finalizado com sucesso')
        except Exception as e:
            self.logger.error(f'Erro no backup completo: {str(e)}')
            raise 