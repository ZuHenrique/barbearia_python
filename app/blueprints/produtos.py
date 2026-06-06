"""
Blueprint Produtos - Barbearia PRO
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, Produto, CatagoriaProduto, Entrada, Saida, Venda

produtos_bp = Blueprint('produtos', __name__, url_prefix='/sistema/painel/produtos')

@produtos_bp.route('/')
@login_required
def listar():
    """Lista produtos"""
    # Pagina produtos para manter a listagem rapida.
    page = request.args.get('page', 1, type=int)
    produtos = Produto.query.paginate(page=page, per_page=20)
    return render_template('painel/produtos/listar.html', produtos=produtos)


@produtos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Criar novo produto"""
    if request.method == 'POST':
        try:
            # Cria produto com precos e estoque inicial.
            produto = Produto(
                nome=request.form.get('nome'),
                categoria_id=request.form.get('categoria_id'),
                valor_compra=float(request.form.get('valor_compra')),
                valor_venda=float(request.form.get('valor_venda')),
                estoque=int(request.form.get('estoque', 0)),
                nivel_estoque=int(request.form.get('nivel_estoque', 10)),
                descricao=request.form.get('descricao')
            )
            db.session.add(produto)
            db.session.commit()
            flash('Produto criado com sucesso!', 'success')
            return redirect(url_for('produtos.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar produto: {str(e)}', 'danger')
    
    # Categorias preenchem o select do formulario.
    categorias = CatagoriaProduto.query.all()
    return render_template('painel/produtos/novo.html', categorias=categorias)


@produtos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar produto"""
    # Carrega o produto antes de editar.
    produto = Produto.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Atualiza cadastro, precos e limites de estoque.
            produto.nome = request.form.get('nome')
            produto.categoria_id = request.form.get('categoria_id')
            produto.valor_compra = float(request.form.get('valor_compra'))
            produto.valor_venda = float(request.form.get('valor_venda'))
            produto.estoque = int(request.form.get('estoque', 0))
            produto.nivel_estoque = int(request.form.get('nivel_estoque', 10))
            produto.descricao = request.form.get('descricao')
            
            db.session.commit()
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('produtos.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar produto: {str(e)}', 'danger')
    
    # Recarrega categorias para a tela de edicao.
    categorias = CatagoriaProduto.query.all()
    return render_template('painel/produtos/editar.html', produto=produto, categorias=categorias)


@produtos_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir produto"""
    # Remove o produto selecionado.
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('produtos.listar'))


@produtos_bp.route('/estoque')
@login_required
def estoque_baixo():
    """Listar produtos com estoque baixo"""
    # Compara estoque atual com nivel minimo definido no produto.
    produtos = Produto.query.filter(
        Produto.estoque <= Produto.nivel_estoque
    ).all()
    return render_template('painel/produtos/estoque-baixo.html', produtos=produtos)


@produtos_bp.route('/entradas')
@login_required
def entradas():
    """Listar entradas de estoque"""
    # Historico de entradas de estoque.
    page = request.args.get('page', 1, type=int)
    entradas = Entrada.query.paginate(page=page, per_page=20)
    return render_template('painel/produtos/entradas.html', entradas=entradas)


@produtos_bp.route('/saidas')
@login_required
def saidas():
    """Listar saídas de estoque"""
    # Historico de saidas de estoque.
    page = request.args.get('page', 1, type=int)
    saidas = Saida.query.paginate(page=page, per_page=20)
    return render_template('painel/produtos/saidas.html', saidas=saidas)
