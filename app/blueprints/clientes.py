"""
Blueprint Clientes - Barbearia PRO
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from app.models import db, Cliente, Agendamento

clientes_bp = Blueprint('clientes', __name__, url_prefix='/sistema/painel/clientes')

@clientes_bp.route('/')
@login_required
def listar():
    """Lista clientes com busca"""
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('q', '')

    query = Cliente.query
    if busca:
        query = query.filter(
            Cliente.nome.ilike(f'%{busca}%') |
            Cliente.telefone.ilike(f'%{busca}%') |
            Cliente.email.ilike(f'%{busca}%')
        )

    clientes = query.order_by(Cliente.nome).paginate(page=page, per_page=25)
    return render_template('painel/clientes/listar.html', clientes=clientes, busca=busca)


@clientes_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver perfil completo do cliente"""
    cliente = Cliente.query.get_or_404(id)
    agendamentos = Agendamento.query.filter_by(cliente_id=id).order_by(Agendamento.data.desc()).limit(20).all()
    return render_template('painel/clientes/ver.html', cliente=cliente, agendamentos=agendamentos)


@clientes_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Criar novo cliente"""
    if request.method == 'POST':
        try:
            data_nasc_str = request.form.get('data_nasc')
            data_nasc = datetime.strptime(data_nasc_str, '%Y-%m-%d').date() if data_nasc_str else None

            cliente = Cliente(
                nome=request.form.get('nome'),
                telefone=request.form.get('telefone'),
                email=request.form.get('email') or None,
                endereco=request.form.get('endereco'),
                data_nasc=data_nasc,
                alertado=request.form.get('alertado', 'Não')
            )
            db.session.add(cliente)
            db.session.commit()
            flash('Cliente cadastrado com sucesso!', 'success')
            return redirect(url_for('clientes.ver', id=cliente.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar cliente: {str(e)}', 'danger')

    return render_template('painel/clientes/novo.html')


@clientes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar cliente"""
    cliente = Cliente.query.get_or_404(id)

    if request.method == 'POST':
        try:
            data_nasc_str = request.form.get('data_nasc')
            cliente.nome = request.form.get('nome')
            cliente.telefone = request.form.get('telefone')
            cliente.email = request.form.get('email') or None
            cliente.endereco = request.form.get('endereco')
            cliente.data_nasc = datetime.strptime(data_nasc_str, '%Y-%m-%d').date() if data_nasc_str else None
            cliente.cartoes = int(request.form.get('cartoes', 0))
            cliente.alertado = request.form.get('alertado', 'Não')

            db.session.commit()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('clientes.ver', id=cliente.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar cliente: {str(e)}', 'danger')

    return render_template('painel/clientes/editar.html', cliente=cliente)


@clientes_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir cliente"""
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente excluído com sucesso!', 'success')
    return redirect(url_for('clientes.listar'))

@clientes_bp.route('/api/criar-rapido', methods=['POST'])
@login_required
def criar_rapido():
    """Cria cliente rapidamente via JSON (para modal)"""
    from flask import jsonify
    try:
        data = request.get_json()
        nome     = (data.get('nome') or '').strip()
        telefone = (data.get('telefone') or '').strip()
        email    = (data.get('email') or '').strip() or None

        if not nome or not telefone:
            return jsonify({'status': 'error', 'message': 'Nome e telefone são obrigatórios'}), 400

        cliente = Cliente(
            nome=nome,
            telefone=telefone,
            email=email,
            alertado='Não'
        )
        db.session.add(cliente)
        db.session.commit()
        return jsonify({'status': 'success', 'id': cliente.id, 'nome': cliente.nome, 'telefone': cliente.telefone})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
