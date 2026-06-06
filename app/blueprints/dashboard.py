"""
Blueprint Dashboard - Painel Administrativo - Barbearia PRO
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import db, Agendamento, Cliente, Produto, ContaReceber, ContaPagar, Usuario

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/sistema/painel')

@dashboard_bp.route('/index')
@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal do painel"""
    # Dados gerais
    # Indicadores principais exibidos no topo do painel.
    total_clientes = Cliente.query.count()
    total_servicos_mes = Agendamento.query.filter(
        Agendamento.status == 'Concluído'
    ).count()
    
    # Contas
    # Contas vencidas ou vencendo ate hoje.
    hoje = datetime.now().date()
    contas_vencer_hoje = ContaPagar.query.filter(
        ContaPagar.data_venc <= hoje,
        ContaPagar.pago == 'Não'
    ).count()
    
    recebimentos_vencer = ContaReceber.query.filter(
        ContaReceber.data_venc <= hoje,
        ContaReceber.pago == 'Não'
    ).count()
    
    # Estoque baixo
    # Produtos que precisam de reposicao.
    produtos_baixo = Produto.query.filter(
        Produto.estoque <= Produto.nivel_estoque
    ).count()
    
    # Agendamentos de hoje
    # Volume de atendimentos marcados para hoje.
    agendamentos_hoje = Agendamento.query.filter(
        Agendamento.data == hoje
    ).count()
    
    # Cálculos
    # Percentual simples de agendamentos concluidos.
    total_agendamentos = Agendamento.query.count()
    taxa_conclusao = (total_servicos_mes / total_agendamentos * 100) if total_agendamentos > 0 else 0
    
    # Últimos agendamentos
    # Lista curta para atividade recente do painel.
    ultimos_agendamentos = Agendamento.query.order_by(
        Agendamento.data_lanc.desc()
    ).limit(5).all()
    
    dados = {
        'total_clientes': total_clientes,
        'total_servicos_mes': total_servicos_mes,
        'contas_vencer_hoje': contas_vencer_hoje,
        'recebimentos_vencer': recebimentos_vencer,
        'produtos_baixo': produtos_baixo,
        'agendamentos_hoje': agendamentos_hoje,
        'taxa_conclusao': round(taxa_conclusao, 2),
        'ultimos_agendamentos': ultimos_agendamentos,
    }
    
    return render_template('painel/dashboard.html', **dados)


@dashboard_bp.route('/api/dados-dashboard')
@login_required
def api_dados_dashboard():
    """API para dados do dashboard"""
    try:
        # Dados compactos para cards/graficos carregados via AJAX.
        hoje = datetime.now().date()
        
        # Agendamentos últimos 7 dias
        agendamentos_7dias = Agendamento.query.filter(
            Agendamento.data >= hoje - timedelta(days=7)
        ).count()
        
        # Receita últimos 7 dias
        receita = ContaReceber.query.filter(
            ContaReceber.data_pgto >= (hoje - timedelta(days=7)),
            ContaReceber.pago == 'Sim'
        ).count()
        
        return jsonify({
            'status': 'success',
            'agendamentos_7dias': agendamentos_7dias,
            'receita_7dias': receita
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
