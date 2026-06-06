"""
Blueprint Área do Cliente - Barbearia PRO
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from app.models import db, Cliente, Agendamento

# Cria o blueprint
area_cliente_bp = Blueprint('area_cliente', __name__, url_prefix='/area-cliente')

oauth = OAuth()

# As credenciais a seguir devem vir do app config ou .env na prática
# Mas definiremos dinamicamente aqui para não quebrar a aplicação caso faltem chaves
def init_oauth(app):
    # Conecta Authlib ao Flask.
    oauth.init_app(app)
    
    # Configura login com Google.
    oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID', 'DUMMY_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', 'DUMMY_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    # Configura login com Facebook.
    oauth.register(
        name='facebook',
        client_id=os.environ.get('FACEBOOK_CLIENT_ID', 'DUMMY_ID'),
        client_secret=os.environ.get('FACEBOOK_CLIENT_SECRET', 'DUMMY_SECRET'),
        api_base_url='https://graph.facebook.com/v15.0/',
        access_token_url='https://graph.facebook.com/v15.0/oauth/access_token',
        authorize_url='https://www.facebook.com/v15.0/dialog/oauth',
        client_kwargs={'scope': 'email public_profile'}
    )

@area_cliente_bp.route('/')
def index():
    """Painel do Cliente"""
    # Apenas clientes devem acessar a area do cliente.
    if not current_user.is_authenticated or not hasattr(current_user, 'cartoes'):
        return redirect(url_for('area_cliente.login'))
        
    # Mostra historico de agendamentos do cliente logado.
    agendamentos = Agendamento.query.filter_by(cliente_id=current_user.id).order_by(Agendamento.data.desc()).all()
    return render_template('public/area_cliente_dashboard.html', agendamentos=agendamentos)

@area_cliente_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Cliente autenticado vai direto para o painel.
    if current_user.is_authenticated and hasattr(current_user, 'cartoes'):
        return redirect(url_for('area_cliente.index'))
        
    if request.method == 'POST':
        # Login simples por email e senha.
        email = request.form.get('email')
        senha = request.form.get('senha')
        cliente = Cliente.query.filter_by(email=email).first()
        
        if cliente and cliente.verifica_senha(senha):
            login_user(cliente)
            return redirect(url_for('area_cliente.index'))
            
        flash('Email ou senha incorretos!', 'danger')
        
    return render_template('public/area_cliente_login.html')

@area_cliente_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    # Evita cadastro duplicado se o cliente ja esta logado.
    if current_user.is_authenticated and hasattr(current_user, 'cartoes'):
        return redirect(url_for('area_cliente.index'))
        
    if request.method == 'POST':
        # Dados minimos para criar a conta do cliente.
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        senha = request.form.get('senha')
        
        # Email identifica a conta do cliente.
        if Cliente.query.filter_by(email=email).first():
            flash('Este email já está cadastrado!', 'danger')
            return redirect(url_for('area_cliente.cadastro'))
            
        # Cria cliente e salva senha com hash.
        cliente = Cliente(nome=nome, email=email, telefone=telefone)
        cliente.set_senha(senha)
        db.session.add(cliente)
        db.session.commit()
        
        login_user(cliente)
        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('area_cliente.index'))
        
    return render_template('public/area_cliente_cadastro.html')

@area_cliente_bp.route('/logout')
@login_required
def logout():
    # Encerra sessao e volta para o site publico.
    logout_user()
    return redirect(url_for('main.index'))

@area_cliente_bp.route('/login/google')
def login_google():
    # Redireciona o cliente para autorizacao do Google.
    redirect_uri = url_for('area_cliente.authorize_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@area_cliente_bp.route('/login/google/authorize')
def authorize_google():
    try:
        # Recebe token e dados do perfil Google.
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        if not user_info:
            flash('Erro ao obter informações do Google.', 'danger')
            return redirect(url_for('area_cliente.login'))
            
        email = user_info['email']
        google_id = user_info['sub']
        nome = user_info['name']
        
        # Procura conta existente por email ou id social.
        cliente = Cliente.query.filter((Cliente.email == email) | (Cliente.google_id == google_id)).first()
        
        if not cliente:
            # Primeiro login social cria o cliente automaticamente.
            cliente = Cliente(nome=nome, email=email, google_id=google_id, telefone='Pendente')
            db.session.add(cliente)
            db.session.commit()
        elif not cliente.google_id:
            cliente.google_id = google_id
            db.session.commit()
            
        login_user(cliente)
        return redirect(url_for('area_cliente.index'))
    except Exception as e:
        flash(f'Erro de autorização: {str(e)}', 'danger')
        return redirect(url_for('area_cliente.login'))

@area_cliente_bp.route('/login/facebook')
def login_facebook():
    # Redireciona o cliente para autorizacao do Facebook.
    redirect_uri = url_for('area_cliente.authorize_facebook', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@area_cliente_bp.route('/login/facebook/authorize')
def authorize_facebook():
    try:
        # Recebe token e busca perfil basico do Facebook.
        token = oauth.facebook.authorize_access_token()
        resp = oauth.facebook.get('me?fields=id,name,email')
        profile = resp.json()
        
        if not profile.get('email'):
            flash('Sua conta do Facebook precisa de um email associado!', 'danger')
            return redirect(url_for('area_cliente.login'))
            
        email = profile['email']
        facebook_id = profile['id']
        nome = profile['name']
        
        # Procura conta existente por email ou id social.
        cliente = Cliente.query.filter((Cliente.email == email) | (Cliente.facebook_id == facebook_id)).first()
        
        if not cliente:
            # Primeiro login social cria o cliente automaticamente.
            cliente = Cliente(nome=nome, email=email, facebook_id=facebook_id, telefone='Pendente')
            db.session.add(cliente)
            db.session.commit()
        elif not cliente.facebook_id:
            cliente.facebook_id = facebook_id
            db.session.commit()
            
        login_user(cliente)
        return redirect(url_for('area_cliente.index'))
    except Exception as e:
        flash(f'Erro de autorização: {str(e)}', 'danger')
        return redirect(url_for('area_cliente.login'))
