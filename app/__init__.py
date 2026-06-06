"""
Inicialização da Aplicação Flask - Barbearia PRO
"""
from flask import Flask
from flask_login import LoginManager
from config import config
from app.models import db, Usuario, Cliente
from flask_migrate import Migrate

login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name='development'):
    """Factory para criar aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para acessar esta página'
    login_manager.login_message_category = 'info'
    
    # Inicializar Flask-Migrate
    migrate.init_app(app, db)
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            if user_id.startswith('usuario_'):
                return Usuario.query.get(int(user_id.split('_')[1]))
            elif user_id.startswith('cliente_'):
                return Cliente.query.get(int(user_id.split('_')[1]))
        except:
            pass
        return None
    
    # Criar contexto de aplicação
    with app.app_context():
        # Importar blueprints
        from app.blueprints.auth import auth_bp
        from app.blueprints.main import main_bp
        from app.blueprints.dashboard import dashboard_bp
        from app.blueprints.agendamentos import agendamentos_bp
        from app.blueprints.clientes import clientes_bp
        from app.blueprints.usuarios import usuarios_bp
        from app.blueprints.servicos import servicos_bp
        from app.blueprints.produtos import produtos_bp
        from app.blueprints.financeiro import financeiro_bp
        from app.blueprints.relatorios import relatorios_bp
        from app.blueprints.api import api_bp
        from app.blueprints.area_cliente import area_cliente_bp, init_oauth
        from app.blueprints.onboarding import onboarding_bp
        
        # Inicializar OAuth
        init_oauth(app)
        
        # Registrar blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(agendamentos_bp)
        app.register_blueprint(clientes_bp)
        app.register_blueprint(usuarios_bp)
        app.register_blueprint(servicos_bp)
        app.register_blueprint(produtos_bp)
        app.register_blueprint(financeiro_bp)
        app.register_blueprint(relatorios_bp)
        app.register_blueprint(api_bp)
        app.register_blueprint(area_cliente_bp)
        app.register_blueprint(onboarding_bp)
        
        # Criar tabelas
        db.create_all()
    
    return app
