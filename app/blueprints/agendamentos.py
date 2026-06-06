"""
Blueprint Agendamentos - Barbearia PRO
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, time
from app.models import db, Agendamento, Cliente, Servico, Usuario, Horario
from sqlalchemy import and_

agendamentos_bp = Blueprint('agendamentos', __name__, url_prefix='/sistema/painel/agendamentos')

@agendamentos_bp.route('/')
@login_required
def listar():
    """Lista agendamentos com filtros"""
    # Filtros chegam pela URL; por padrao mostra a agenda de hoje.
    data_filtro = request.args.get('data', date.today().isoformat())
    status_filtro = request.args.get('status', '')
    funcionario_filtro = request.args.get('funcionario_id', '')

    # Monta a consulta aos poucos conforme os filtros.
    query = Agendamento.query

    try:
        data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
        query = query.filter(Agendamento.data == data_obj)
    except:
        data_obj = date.today()
        query = query.filter(Agendamento.data == data_obj)

    if status_filtro:
        query = query.filter(Agendamento.status == status_filtro)
    if funcionario_filtro:
        query = query.filter(Agendamento.funcionario_id == funcionario_filtro)

    agendamentos = query.order_by(Agendamento.hora).all()
    funcionarios = Usuario.query.filter_by(atendimento='Sim', ativo='Sim').all()

    return render_template('painel/agendamentos/listar.html',
                           agendamentos=agendamentos,
                           funcionarios=funcionarios,
                           data_filtro=data_filtro,
                           status_filtro=status_filtro,
                           funcionario_filtro=funcionario_filtro)


@agendamentos_bp.route('/<int:id>/confirmar', methods=['POST'])
@login_required
def confirmar(id):
    """Confirmar chegada do cliente"""
    # get_or_404 evita atualizar um agendamento inexistente.
    ag = Agendamento.query.get_or_404(id)
    ag.status = 'Confirmado'
    db.session.commit()
    flash(f'Agendamento #{id} confirmado!', 'success')
    return redirect(request.referrer or url_for('agendamentos.listar'))


@agendamentos_bp.route('/<int:id>/concluir', methods=['POST'])
@login_required
def concluir(id):
    """Concluir servico - adiciona ponto fidelidade"""
    # Marca como concluido e depois adiciona ponto de fidelidade.
    ag = Agendamento.query.get_or_404(id)
    ag.status = 'Concluido'
    db.session.commit()
    if ag.cliente:
        ag.cliente.cartoes = (ag.cliente.cartoes or 0) + 1
        db.session.commit()
    flash(f'Servico concluido! +1 ponto de fidelidade para {ag.cliente.nome if ag.cliente else "cliente"}.', 'success')
    return redirect(request.referrer or url_for('agendamentos.listar'))


@agendamentos_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar(id):
    """Cancelar agendamento"""
    # Registra cancelamento mantendo o motivo nas observacoes.
    ag = Agendamento.query.get_or_404(id)
    motivo = request.form.get('motivo', '')
    ag.status = 'Cancelado'
    if motivo:
        ag.obs = f"[CANCELADO: {motivo}] {ag.obs or ''}"
    db.session.commit()
    flash(f'Agendamento #{id} cancelado.', 'warning')
    return redirect(request.referrer or url_for('agendamentos.listar'))


@agendamentos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Criar novo agendamento"""
    if request.method == 'POST':
        try:
            # Converte campos do formulario para os tipos usados no banco.
            funcionario_id = request.form.get('funcionario_id')
            cliente_id = request.form.get('cliente_id')
            servico_id = request.form.get('servico_id')
            data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()
            hora = datetime.strptime(request.form.get('hora'), '%H:%M').time()
            obs = request.form.get('obs')

            # Impede dois agendamentos no mesmo funcionario/data/hora.
            agendamento_existente = Agendamento.query.filter(
                and_(
                    Agendamento.data == data,
                    Agendamento.hora == hora,
                    Agendamento.funcionario_id == funcionario_id
                )
            ).first()

            if agendamento_existente:
                flash('Este horario nao esta disponivel!', 'danger')
                return redirect(url_for('agendamentos.novo'))

            # Extrai o id numerico do usuario logado.
            uid = current_user.get_id()
            usuario_id = int(uid.split('_')[1]) if '_' in str(uid) else current_user.id

            # Cria o registro com status inicial Agendado.
            novo_agendamento = Agendamento(
                funcionario_id=funcionario_id,
                cliente_id=cliente_id,
                servico_id=servico_id,
                usuario_id=usuario_id,
                data=data,
                hora=hora,
                obs=obs,
                status='Agendado',
                data_lanc=datetime.now().date()
            )

            db.session.add(novo_agendamento)
            db.session.commit()

            flash('Agendamento criado com sucesso!', 'success')
            return redirect(url_for('agendamentos.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar agendamento: {str(e)}', 'danger')
            return redirect(url_for('agendamentos.novo'))

    # Dados usados para preencher selects do formulario.
    funcionarios = Usuario.query.filter_by(atendimento='Sim').all()
    clientes = Cliente.query.order_by(Cliente.nome).all()
    servicos = Servico.query.filter_by(ativo='Sim').all()
    return render_template('painel/agendamentos/novo.html',
                           funcionarios=funcionarios,
                           clientes=clientes,
                           servicos=servicos,
                           today=date.today().isoformat())


@agendamentos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar agendamento"""
    # Carrega o agendamento antes de editar.
    agendamento = Agendamento.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Atualiza somente os campos editaveis da tela.
            agendamento.funcionario_id = request.form.get('funcionario_id')
            agendamento.servico_id = request.form.get('servico_id')
            agendamento.data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()
            agendamento.hora = datetime.strptime(request.form.get('hora'), '%H:%M').time()
            agendamento.obs = request.form.get('obs')
            agendamento.status = request.form.get('status')

            db.session.commit()
            flash('Agendamento atualizado com sucesso!', 'success')
            return redirect(url_for('agendamentos.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar agendamento: {str(e)}', 'danger')

    # Recarrega opcoes para renderizar a tela de edicao.
    funcionarios = Usuario.query.filter_by(atendimento='Sim').all()
    servicos = Servico.query.filter_by(ativo='Sim').all()
    return render_template('painel/agendamentos/editar.html',
                           agendamento=agendamento,
                           funcionarios=funcionarios,
                           servicos=servicos,
                           today=date.today().isoformat())


@agendamentos_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir agendamento"""
    # Remove definitivamente o agendamento selecionado.
    agendamento = Agendamento.query.get_or_404(id)
    db.session.delete(agendamento)
    db.session.commit()
    flash('Agendamento excluido!', 'success')
    return redirect(url_for('agendamentos.listar'))
