"""
Blueprint Financeiro - Barbearia PRO
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime, date
from app.models import db, ContaReceber, ContaPagar, Fornecedor

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/sistema/painel/financeiro')

@financeiro_bp.route('/receber')
@login_required
def receber():
    """Listar contas a receber"""
    # Lista contas a receber ordenadas pelo vencimento.
    page = request.args.get('page', 1, type=int)
    contas = ContaReceber.query.order_by(ContaReceber.data_venc).paginate(page=page, per_page=20)
    return render_template('painel/financeiro/receber.html', contas=contas, today=date.today())


@financeiro_bp.route('/receber/novo', methods=['GET', 'POST'])
@login_required
def receber_novo():
    """Criar conta a receber"""
    if request.method == 'POST':
        try:
            # Converte vencimento do formulario para date.
            data_venc = datetime.strptime(request.form.get('data_venc'), '%Y-%m-%d').date()
            # Toda nova conta comeca como nao paga.
            conta = ContaReceber(
                descricao=request.form.get('descricao'),
                valor=float(request.form.get('valor')),
                tipo=request.form.get('tipo'),
                data_venc=data_venc,
                pago='Não'
            )
            db.session.add(conta)
            db.session.commit()
            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('financeiro.receber'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro: {str(e)}', 'danger')
    
    return render_template('painel/financeiro/receber-novo.html')


@financeiro_bp.route('/pagar')
@login_required
def pagar():
    """Listar contas a pagar"""
    # Lista despesas cadastradas.
    page = request.args.get('page', 1, type=int)
    contas = ContaPagar.query.paginate(page=page, per_page=20)
    return render_template('painel/financeiro/pagar.html', contas=contas)


@financeiro_bp.route('/pagar/novo', methods=['GET', 'POST'])
@login_required
def pagar_novo():
    """Criar conta a pagar"""
    if request.method == 'POST':
        try:
            # Converte vencimento do formulario para date.
            data_venc = datetime.strptime(request.form.get('data_venc'), '%Y-%m-%d').date()
            # Toda nova despesa comeca como nao paga.
            conta = ContaPagar(
                descricao=request.form.get('descricao'),
                valor=float(request.form.get('valor')),
                fornecedor_id=request.form.get('fornecedor_id'),
                data_venc=data_venc,
                pago='Não'
            )
            db.session.add(conta)
            db.session.commit()
            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('financeiro.pagar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro: {str(e)}', 'danger')
    
    # Fornecedores preenchem o select da despesa.
    fornecedores = Fornecedor.query.all()
    return render_template('painel/financeiro/pagar-novo.html', fornecedores=fornecedores)


@financeiro_bp.route('/receber/<int:id>/pagar', methods=['POST'])
@login_required
def receber_pagar(id):
    """Marcar conta a receber como paga"""
    # Registra baixa de uma receita.
    conta = ContaReceber.query.get_or_404(id)
    conta.pago = 'Sim'
    conta.data_pgto = datetime.now().date()
    db.session.commit()
    flash('Pagamento registrado!', 'success')
    return redirect(url_for('financeiro.receber'))


@financeiro_bp.route('/pagar/<int:id>/pagar', methods=['POST'])
@login_required
def pagar_pagar(id):
    """Marcar conta a pagar como paga"""
    # Registra baixa de uma despesa.
    conta = ContaPagar.query.get_or_404(id)
    conta.pago = 'Sim'
    conta.data_pgto = datetime.now().date()
    db.session.commit()
    flash('Pagamento registrado!', 'success')
    return redirect(url_for('financeiro.pagar'))
