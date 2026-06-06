"""
Blueprint Relatórios - Barbearia PRO
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from datetime import datetime, timedelta
from app.models import db, Agendamento, Venda, ContaReceber, ContaPagar, Cliente, Usuario
from sqlalchemy import func

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/sistema/painel/relatorios')

@relatorios_bp.route('/')
@login_required
def index():
    """Página principal de relatórios"""
    return render_template('painel/relatorios/index.html')


@relatorios_bp.route('/agendamentos')
@login_required
def agendamentos():
    """Relatório de agendamentos"""
    # Filtros opcionais de periodo.
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    # Monta consulta conforme o periodo informado.
    query = Agendamento.query
    
    if data_inicio:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(Agendamento.data >= data_inicio)
    
    if data_fim:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(Agendamento.data <= data_fim)
    
    agendamentos = query.order_by(Agendamento.data.desc()).all()
    
    return render_template('painel/relatorios/agendamentos.html', 
                         agendamentos=agendamentos,
                         data_inicio=data_inicio,
                         data_fim=data_fim)


@relatorios_bp.route('/vendas')
@login_required
def vendas():
    """Relatório de vendas"""
    # Filtros opcionais de periodo.
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    # Monta consulta de vendas conforme periodo.
    query = Venda.query
    
    if data_inicio:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(func.date(Venda.data) >= data_inicio)
    
    if data_fim:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(func.date(Venda.data) <= data_fim)
    
    vendas = query.order_by(Venda.data.desc()).all()
    # Soma o valor total das vendas filtradas.
    total = sum(v.valor_total for v in vendas)
    
    return render_template('painel/relatorios/vendas.html',
                         vendas=vendas,
                         total=total,
                         data_inicio=data_inicio,
                         data_fim=data_fim)


@relatorios_bp.route('/comissoes')
@login_required
def comissoes():
    """Relatório de comissões de funcionários"""
    # Filtros opcionais de periodo.
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = Agendamento.query.filter(Agendamento.status == 'Concluído')
    
    if data_inicio:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(Agendamento.data >= data_inicio)
    
    if data_fim:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(Agendamento.data <= data_fim)
    
    agendamentos = query.all()
    
    # Agrupa comissoes por funcionario.
    comissoes = {}
    for agendamento in agendamentos:
        funcionario_id = agendamento.funcionario_id
        comissao_valor = agendamento.servico.valor_comissao
        
        if funcionario_id not in comissoes:
            comissoes[funcionario_id] = {
                'funcionario': agendamento.funcionario.nome,
                'total': 0,
                'servicos': 0
            }
        
        comissoes[funcionario_id]['total'] += comissao_valor
        comissoes[funcionario_id]['servicos'] += 1
    
    return render_template('painel/relatorios/comissoes.html',
                         comissoes=comissoes,
                         data_inicio=data_inicio,
                         data_fim=data_fim)


@relatorios_bp.route('/financeiro')
@login_required
def financeiro():
    """Relatório financeiro"""
    # Filtros opcionais de periodo.
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    hoje = datetime.now().date()
    
    # Consultas separadas para entradas e saidas.
    query_receber = ContaReceber.query
    query_pagar = ContaPagar.query
    
    if data_inicio:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query_receber = query_receber.filter(ContaReceber.data_venc >= data_inicio)
        query_pagar = query_pagar.filter(ContaPagar.data_venc >= data_inicio)
    
    if data_fim:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query_receber = query_receber.filter(ContaReceber.data_venc <= data_fim)
        query_pagar = query_pagar.filter(ContaPagar.data_venc <= data_fim)
    
    contas_receber = query_receber.all()
    contas_pagar = query_pagar.all()
    
    # Lucro simples: recebido pago menos despesa paga.
    total_receber = sum(c.valor for c in contas_receber if c.pago == 'Sim')
    total_pagar = sum(c.valor for c in contas_pagar if c.pago == 'Sim')
    lucro = total_receber - total_pagar
    
    return render_template('painel/relatorios/financeiro.html',
                         contas_receber=contas_receber,
                         contas_pagar=contas_pagar,
                         total_receber=total_receber,
                         total_pagar=total_pagar,
                         lucro=lucro,
                         data_inicio=data_inicio,
                         data_fim=data_fim)


@relatorios_bp.route('/clientes')
@login_required
def clientes():
    """Relatório de clientes"""
    # Relatorio simples com clientes mais recentes primeiro.
    clientes = Cliente.query.order_by(Cliente.data_cad.desc()).all()
    total_clientes = len(clientes)
    
    return render_template('painel/relatorios/clientes.html',
                         clientes=clientes,
                         total_clientes=total_clientes)
