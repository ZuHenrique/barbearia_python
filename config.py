"""
Configurações do Projeto Barbearia PRO
"""
import os
from datetime import timedelta

class Config:
    """Configurações base"""
    # Banco de dados
    # Banco padrao local; DATABASE_URL permite trocar de banco.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///barbearia.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    # Chave e regras basicas da sessao do usuario.
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Mude para True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Uploads
    # Pasta e limites para arquivos enviados pelo sistema.
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # Email
    # Configuracao SMTP usada em fluxos de email.
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'noreply@barbearia.com'

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Configurações para testes"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
