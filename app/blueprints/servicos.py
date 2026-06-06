"""
Blueprint Serviços - Barbearia PRO
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, Servico, CategoriaServico

servicos_bp = Blueprint('servicos', __name__, url_prefix='/sistema/painel/servicos')

@servicos_bp.route('/')
@login_required
def listar():
    """Lista serviços"""
    # Pagina a listagem de servicos.
    page = request.args.get('page', 1, type=int)
    servicos = Servico.query.paginate(page=page, per_page=20)
    return render_template('painel/servicos/listar.html', servicos=servicos)


@servicos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Criar novo serviço"""
    if request.method == 'POST':
        try:
            # Converte valores numericos antes de salvar.
            servico = Servico(
                nome=request.form.get('nome'),
                categoria_id=request.form.get('categoria_id'),
                valor=float(request.form.get('valor')),
                valor_comissao=float(request.form.get('valor_comissao', 0)),
                dias_retorno=int(request.form.get('dias_retorno', 30)),
                descricao=request.form.get('descricao'),
                ativo=request.form.get('ativo', 'Sim')
            )
            db.session.add(servico)
            db.session.commit()
            flash('Serviço criado com sucesso!', 'success')
            return redirect(url_for('servicos.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar serviço: {str(e)}', 'danger')
    
    # Categorias preenchem o select do formulario.
    categorias = CategoriaServico.query.all()
    return render_template('painel/servicos/novo.html', categorias=categorias)


@servicos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar serviço"""
    # Carrega o servico antes de editar.
    servico = Servico.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Atualiza dados comerciais e visibilidade do servico.
            servico.nome = request.form.get('nome')
            servico.categoria_id = request.form.get('categoria_id')
            servico.valor = float(request.form.get('valor'))
            servico.valor_comissao = float(request.form.get('valor_comissao', 0))
            servico.dias_retorno = int(request.form.get('dias_retorno', 30))
            servico.descricao = request.form.get('descricao')
            servico.ativo = request.form.get('ativo', 'Não')
            
            db.session.commit()
            flash('Serviço atualizado com sucesso!', 'success')
            return redirect(url_for('servicos.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar serviço: {str(e)}', 'danger')
    
    # Recarrega categorias para a tela de edicao.
    categorias = CategoriaServico.query.all()
    return render_template('painel/servicos/editar.html', servico=servico, categorias=categorias)


@servicos_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir serviço"""
    # Exclui o servico selecionado.
    servico = Servico.query.get_or_404(id)
    db.session.delete(servico)
    db.session.commit()
    flash('Serviço excluído com sucesso!', 'success')
    return redirect(url_for('servicos.listar'))
