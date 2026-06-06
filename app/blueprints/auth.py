"""
Blueprint de Autenticação - Barbearia PRO
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Usuario
from werkzeug.security import check_password_hash
import hashlib

auth_bp = Blueprint('auth', __name__, url_prefix='/sistema')

@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    """Página de login"""
    # Usuario ja logado nao precisa ver a tela de login.
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # Captura credenciais enviadas pelo formulario.
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not email or not senha:
            flash('Email e senha são obrigatórios', 'danger')
            return redirect(url_for('auth.login'))
        
        # Buscar usuário por email ou CPF
        # Permite login usando email ou CPF no mesmo campo.
        usuario = Usuario.query.filter(
            (Usuario.email == email) | (Usuario.cpf == email)
        ).first()
        
        if usuario and usuario.verifica_senha(senha):
            if usuario.ativo == 'Não':
                flash('Seu usuário foi desativado, contate o administrador!', 'danger')
                return redirect(url_for('auth.login'))
            
            # Registra usuario na sessao do Flask-Login.
            login_user(usuario)
            session['id'] = usuario.id
            session['nivel'] = usuario.nivel
            session['nome'] = usuario.nome
            
            # Volta para a pagina solicitada antes do login, se existir.
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Usuário ou Senha Incorretos!', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Faz logout do usuário"""
    logout_user()
    session.clear()
    flash('Você foi desconectado', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    """Recuperação de senha"""
    if request.method == 'POST':
        # Resposta igual para email existente ou nao evita enumeracao de usuarios.
        email = request.form.get('email')
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario:
            flash('Se o email existe, você receberá uma mensagem de recuperação', 'info')
            # TODO: Implementar envio de email
        else:
            flash('Se o email existe, você receberá uma mensagem de recuperação', 'info')
    
    return render_template('auth/recuperar-senha.html')


@auth_bp.route('/perfil')
@login_required
def perfil():
    """Página de perfil do usuário"""
    return render_template('auth/perfil.html', usuario=current_user)


@auth_bp.route('/perfil/editar', methods=['POST'])
@login_required
def editar_perfil():
    """Edita perfil do usuário"""
    # Atualiza apenas campos enviados no formulario.
    nome = request.form.get('nome')
    email = request.form.get('email')
    telefone = request.form.get('telefone')
    chave_pix = request.form.get('chave_pix')
    
    usuario = current_user
    if nome:
        usuario.nome = nome
    if email:
        usuario.email = email
    if telefone:
        usuario.telefone = telefone
    if chave_pix:
        usuario.chave_pix = chave_pix
    
    db.session.commit()
    flash('Perfil atualizado com sucesso!', 'success')
    return redirect(url_for('auth.perfil'))


@auth_bp.route('/alterar-senha', methods=['POST'])
@login_required
def alterar_senha():
    """Altera a senha do usuário"""
    # Confere senha atual antes de aceitar uma nova.
    senha_atual = request.form.get('senha_atual')
    senha_nova = request.form.get('senha_nova')
    senha_confirmacao = request.form.get('senha_confirmacao')
    
    usuario = current_user
    
    if not usuario.verifica_senha(senha_atual):
        flash('Senha atual incorreta', 'danger')
        return redirect(url_for('auth.perfil'))
    
    if senha_nova != senha_confirmacao:
        flash('As novas senhas não conferem', 'danger')
        return redirect(url_for('auth.perfil'))
    
    # Salva a nova senha usando o hash definido no modelo Usuario.
    usuario.set_senha(senha_nova)
    db.session.commit()
    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('auth.perfil'))
