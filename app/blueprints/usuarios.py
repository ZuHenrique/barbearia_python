"""
Blueprint Usuários - Barbearia PRO
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, Usuario

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/sistema/painel/usuarios')

@usuarios_bp.route('/')
@login_required
def listar():
    """Lista usuários"""
    page = request.args.get('page', 1, type=int)
    usuarios = Usuario.query.paginate(page=page, per_page=20)
    return render_template('painel/usuarios/listar.html', usuarios=usuarios)


@usuarios_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Criar novo usuário"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            cpf = request.form.get('cpf')
            
            if Usuario.query.filter_by(email=email).first():
                flash('Email já existe!', 'danger')
                return redirect(url_for('usuarios.novo'))
            
            if Usuario.query.filter_by(cpf=cpf).first():
                flash('CPF já existe!', 'danger')
                return redirect(url_for('usuarios.novo'))
            
            usuario = Usuario(
                nome=request.form.get('nome'),
                email=email,
                cpf=cpf,
                nivel=request.form.get('nivel'),
                telefone=request.form.get('telefone'),
                atendimento=request.form.get('atendimento', 'Não'),
                chave_pix=request.form.get('chave_pix')
            )
            usuario.set_senha(request.form.get('senha'))
            
            db.session.add(usuario)
            db.session.commit()
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('usuarios.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar usuário: {str(e)}', 'danger')
    
    return render_template('painel/usuarios/novo.html')


@usuarios_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar usuário"""
    usuario = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            usuario.nome = request.form.get('nome')
            usuario.nivel = request.form.get('nivel')
            usuario.telefone = request.form.get('telefone')
            usuario.atendimento = request.form.get('atendimento', 'Não')
            usuario.chave_pix = request.form.get('chave_pix')
            usuario.ativo = request.form.get('ativo', 'Não')
            
            senha = request.form.get('senha')
            if senha:
                usuario.set_senha(senha)
            
            db.session.commit()
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('usuarios.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar usuário: {str(e)}', 'danger')
    
    return render_template('painel/usuarios/editar.html', usuario=usuario)


@usuarios_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir usuário"""
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('usuarios.listar'))
