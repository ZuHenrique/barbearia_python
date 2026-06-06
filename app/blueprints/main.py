"""
Blueprint Principal - Página Pública - Barbearia PRO
"""
from flask import Blueprint, render_template, request, jsonify
from app.models import db, Servico, Produto, Comentario, TextoIndex, Config, Cliente

main_bp = Blueprint('main', __name__)


@main_bp.route('/login')
def login_redirect():
    """Atalho: /login redireciona para /sistema/login"""
    from flask import redirect
    return redirect('/sistema/login')

@main_bp.route('/')
def index():
    """Página inicial pública"""
    # Busca dados editaveis que aparecem na home publica.
    config = Config.query.first()
    comentarios = Comentario.query.filter_by(ativo='Sim').all()
    textos = TextoIndex.query.filter_by(ativo='Sim').order_by(TextoIndex.ordem).all()
    
    return render_template('public/index.html', 
                         config=config,
                         comentarios=comentarios,
                         textos=textos)


@main_bp.route('/servicos')
def servicos():
    """Página de serviços"""
    # Mostra apenas servicos ativos para visitantes.
    config = Config.query.first()
    servicos = Servico.query.filter_by(ativo='Sim').all()
    
    return render_template('public/servicos.html',
                         config=config,
                         servicos=servicos)


@main_bp.route('/produtos')
def produtos():
    """Página de produtos"""
    # Produtos ainda nao possuem filtro de ativo neste modelo.
    config = Config.query.first()
    produtos = Produto.query.all()
    
    return render_template('public/produtos.html',
                         config=config,
                         produtos=produtos)


@main_bp.route('/agendamentos', methods=['GET', 'POST'])
def agendamentos():
    """Página de agendamentos multi-step"""
    # A tela renderiza o fluxo; a criacao real acontece pela API.
    config = Config.query.first()
    
    if request.method == 'POST':
        # Será tratado pela API
        pass
    
    return render_template('public/agendamentos.html',
                         config=config)
