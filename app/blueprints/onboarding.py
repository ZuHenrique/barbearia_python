"""
Blueprint de Onboarding - Cadastro de Barbearias e Barbeiros no SaaS
"""
import re
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.models import db, Barbearia, Plano

onboarding_bp = Blueprint('onboarding', __name__, url_prefix='/cadastro')

SLUGS_RESERVADOS = ['www', 'app', 'admin', 'api', 'mail', 'ftp', 'blog', 'suporte',
                    'ajuda', 'help', 'status', 'static', 'assets', 'media', 'login',
                    'cadastro', 'planos', 'sobre', 'contato', 'pricing']


def _slug_valido(slug):
    """Verifica se o slug tem formato válido (só letras, números e hífen)"""
    return bool(re.match(r'^[a-z0-9][a-z0-9\-]{1,58}[a-z0-9]$', slug))


def _slug_disponivel(slug):
    """Verifica se o slug está disponível"""
    if slug in SLUGS_RESERVADOS:
        return False
    return Barbearia.query.filter_by(slug=slug).first() is None


# ------------------------------------------------------------------
# Rota: Verificação de slug (AJAX)
# ------------------------------------------------------------------
@onboarding_bp.route('/verificar-slug')
def verificar_slug():
    slug = request.args.get('slug', '').lower().strip()
    if not slug:
        return jsonify({'disponivel': False, 'mensagem': 'Informe um subdomínio'})
    if not _slug_valido(slug):
        return jsonify({'disponivel': False, 'mensagem': 'Apenas letras minúsculas, números e hífen (mín. 3 caracteres)'})
    if not _slug_disponivel(slug):
        return jsonify({'disponivel': False, 'mensagem': 'Este subdomínio já está em uso'})
    return jsonify({'disponivel': True, 'mensagem': 'Disponível! 🎉'})


# ------------------------------------------------------------------
# Rota: Cadastro de BARBEARIA
# ------------------------------------------------------------------
@onboarding_bp.route('/barbearia', methods=['GET', 'POST'])
def cadastro_barbearia():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        slug = request.form.get('slug', '').lower().strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        telefone = request.form.get('telefone', '').strip()
        cidade = request.form.get('cidade', '').strip()
        estado = request.form.get('estado', '').strip()

        # Validações
        erros = []
        if not nome:
            erros.append('Nome da barbearia é obrigatório')
        if not _slug_valido(slug):
            erros.append('Subdomínio inválido')
        if not _slug_disponivel(slug):
            erros.append('Este subdomínio já está em uso')
        if not email or '@' not in email:
            erros.append('E-mail inválido')
        if Barbearia.query.filter_by(email=email).first():
            erros.append('Este e-mail já está cadastrado')
        if len(senha) < 8:
            erros.append('Senha deve ter pelo menos 8 caracteres')
        if senha != confirmar_senha:
            erros.append('As senhas não coincidem')

        if erros:
            for e in erros:
                flash(e, 'danger')
            return render_template('public/cadastro_barbearia.html',
                                   form_data=request.form)

        # Buscar plano Trial (ou criar se não existir)
        plano_trial = Plano.query.filter_by(nome='Trial').first()
        if not plano_trial:
            plano_trial = Plano(
                nome='Trial',
                preco_mensal=0,
                max_funcionarios=10,
                max_agendamentos_mes=-1,
                permite_relatorios='Sim',
                permite_financeiro='Sim',
                permite_estoque='Sim',
                permite_api='Nao',
                permite_dominio_custom='Nao'
            )
            db.session.add(plano_trial)
            db.session.commit()

        # Criar conta
        nova_barbearia = Barbearia(
            tipo='barbearia',
            nome=nome,
            slug=slug,
            email=email,
            telefone=telefone,
            cidade=cidade,
            estado=estado,
            status='trial',
            trial_ate=datetime.utcnow() + timedelta(days=30),
            plano_id=plano_trial.id
        )
        nova_barbearia.set_senha(senha)
        db.session.add(nova_barbearia)
        db.session.commit()

        # Salvar na sessão para redirecionar ao painel
        session['barbearia_id'] = nova_barbearia.id
        session['barbearia_slug'] = nova_barbearia.slug
        session['barbearia_tipo'] = 'barbearia'

        flash(f'Barbearia "{nome}" criada com sucesso! Você tem 30 dias de trial gratuito.', 'success')
        return redirect(url_for('onboarding.sucesso', slug=slug))

    return render_template('public/cadastro_barbearia.html', form_data={})


# ------------------------------------------------------------------
# Rota: Cadastro de BARBEIRO PROFISSIONAL
# ------------------------------------------------------------------
@onboarding_bp.route('/barbeiro', methods=['GET', 'POST'])
def cadastro_barbeiro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        slug = request.form.get('slug', '').lower().strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        telefone = request.form.get('telefone', '').strip()
        cidade = request.form.get('cidade', '').strip()
        estado = request.form.get('estado', '').strip()
        descricao = request.form.get('descricao', '').strip()
        instagram = request.form.get('instagram', '').strip()

        # Validações
        erros = []
        if not nome:
            erros.append('Seu nome é obrigatório')
        if not _slug_valido(slug):
            erros.append('Subdomínio inválido')
        if not _slug_disponivel(slug):
            erros.append('Este subdomínio já está em uso')
        if not email or '@' not in email:
            erros.append('E-mail inválido')
        if Barbearia.query.filter_by(email=email).first():
            erros.append('Este e-mail já está cadastrado')
        if len(senha) < 8:
            erros.append('Senha deve ter pelo menos 8 caracteres')
        if senha != confirmar_senha:
            erros.append('As senhas não coincidem')

        if erros:
            for e in erros:
                flash(e, 'danger')
            return render_template('public/cadastro_barbeiro.html',
                                   form_data=request.form)

        # Buscar/criar plano Trial
        plano_trial = Plano.query.filter_by(nome='Trial').first()
        if not plano_trial:
            plano_trial = Plano(
                nome='Trial',
                preco_mensal=0,
                max_funcionarios=1,
                max_agendamentos_mes=50,
                permite_relatorios='Nao',
                permite_financeiro='Sim',
                permite_estoque='Nao',
                permite_api='Nao',
                permite_dominio_custom='Nao'
            )
            db.session.add(plano_trial)
            db.session.commit()

        # Criar conta do barbeiro
        novo_barbeiro = Barbearia(
            tipo='barbeiro',
            nome=nome,
            slug=slug,
            email=email,
            telefone=telefone,
            cidade=cidade,
            estado=estado,
            descricao=descricao,
            instagram=instagram,
            status='trial',
            trial_ate=datetime.utcnow() + timedelta(days=30),
            plano_id=plano_trial.id
        )
        novo_barbeiro.set_senha(senha)
        db.session.add(novo_barbeiro)
        db.session.commit()

        session['barbearia_id'] = novo_barbeiro.id
        session['barbearia_slug'] = novo_barbeiro.slug
        session['barbearia_tipo'] = 'barbeiro'

        flash(f'Perfil de "{nome}" criado com sucesso! 30 dias gratuitos para começar.', 'success')
        return redirect(url_for('onboarding.sucesso', slug=slug))

    return render_template('public/cadastro_barbeiro.html', form_data={})


# ------------------------------------------------------------------
# Rota: Página de sucesso pós-cadastro
# ------------------------------------------------------------------
@onboarding_bp.route('/sucesso/<slug>')
def sucesso(slug):
    conta = Barbearia.query.filter_by(slug=slug).first_or_404()
    return render_template('public/cadastro_sucesso.html', conta=conta)
