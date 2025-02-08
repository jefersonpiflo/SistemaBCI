import os
from datetime import timedelta

class Config:
    # Configuração básica
    SECRET_KEY = 'dev'
    
    # Configuração do SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bci.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuração do upload de arquivos
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    
    # Configuração da Sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Outras configurações
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True 
