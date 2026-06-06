"""
Modelos do Banco de Dados - Barbearia PRO
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import hashlib

# Instancia global do SQLAlchemy, inicializada em app/__init__.py.
db = SQLAlchemy()

# =====================================================
# 1. GERENCIAMENTO DE PESSOAS
# =====================================================

class Usuario(UserMixin, db.Model):
    """Modelo de Usuários (Funcionários/Barbeiros)"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    senha_crip = db.Column(db.String(255), nullable=False)
    nivel = db.Column(db.String(50), default='Barbeiro')  # Administrador, Gerente, Recepcionista, Barbeiro
    foto = db.Column(db.String(255))
    telefone = db.Column(db.String(20))
    atendimento = db.Column(db.String(3), default='Sim')  # Sim/Não
    chave_pix = db.Column(db.String(255))
    ativo = db.Column(db.String(3), default='Sim')  # Sim/Não
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    permissoes = db.relationship('UsuarioPermissao', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    agendamentos = db.relationship('Agendamento', foreign_keys='Agendamento.usuario_id', backref='usuario', lazy='dynamic')
    servicos_usuario = db.relationship('ServicoUsuario', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    barbearia_id = db.Column(db.Integer, db.ForeignKey('barbearias.id'))
    
    def set_senha(self, senha):
        """Define senha com hash seguro (werkzeug)"""
        # Gera hash seguro antes de salvar no banco.
        from werkzeug.security import generate_password_hash
        self.senha_crip = generate_password_hash(senha)
    
    def verifica_senha(self, senha):
        """Verifica se a senha está correta"""
        # Mantem compatibilidade com senhas antigas em MD5.
        from werkzeug.security import check_password_hash
        # Fallback para MD5 antigo caso tenha usuários antigos não migrados
        if len(self.senha_crip) == 32:
            import hashlib
            if self.senha_crip == hashlib.md5(senha.encode()).hexdigest():
                # Atualiza para o novo hash seguro automaticamente no login
                self.set_senha(senha)
                db.session.commit()
                return True
            return False
        return check_password_hash(self.senha_crip, senha)
    
    def tem_permissao(self, chave_acesso):
        """Verifica se usuário tem permissão"""
        # Procura uma permissao ligada a chave recebida.
        from app.models import Acesso
        permissao = UsuarioPermissao.query.filter_by(
            usuario_id=self.id
        ).join(Acesso).filter(Acesso.chave == chave_acesso).first()
        return permissao is not None
        
    def get_id(self):
        # Prefixo permite diferenciar Usuario de Cliente no Flask-Login.
        return f"usuario_{self.id}"
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'


class Cliente(UserMixin, db.Model):
    """Modelo de Clientes"""
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True)
    senha_crip = db.Column(db.String(255))
    telefone = db.Column(db.String(20), nullable=False)
    endereco = db.Column(db.String(255))
    data_nasc = db.Column(db.Date)
    cartoes = db.Column(db.Integer, default=0)  # Fidelidade
    data_retorno = db.Column(db.Date)  # Sugestão de retorno
    alertado = db.Column(db.String(3), default='Não')  # Não, WhatsApp, Email
    google_id = db.Column(db.String(100), unique=True)
    facebook_id = db.Column(db.String(100), unique=True)
    data_cad = db.Column(db.Date, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='cliente', lazy='dynamic', cascade='all, delete-orphan')
    barbearia_id = db.Column(db.Integer, db.ForeignKey('barbearias.id'))
    
    def get_id(self):
        # Prefixo permite diferenciar Cliente de Usuario no Flask-Login.
        return f"cliente_{self.id}"
        
    def set_senha(self, senha):
        """Define senha com hash seguro (werkzeug)"""
        from werkzeug.security import generate_password_hash
        self.senha_crip = generate_password_hash(senha)
    
    def verifica_senha(self, senha):
        # Cliente social pode nao ter senha local cadastrada.
        if not self.senha_crip: return False
        from werkzeug.security import check_password_hash
        # Fallback para MD5 antigo
        if len(self.senha_crip) == 32:
            import hashlib
            if self.senha_crip == hashlib.md5(senha.encode()).hexdigest():
                self.set_senha(senha)
                db.session.commit()
                return True
            return False
        return check_password_hash(self.senha_crip, senha)
        
    def __repr__(self):
        return f'<Cliente {self.nome}>'


class Fornecedor(db.Model):
    """Modelo de Fornecedores"""
    __tablename__ = 'fornecedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(255))
    tipo_chave = db.Column(db.String(50))  # CPF, CNPJ, Email, Telefone
    chave_pix = db.Column(db.String(255))
    data_cad = db.Column(db.Date, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    contas_pagar = db.relationship('ContaPagar', backref='fornecedor', lazy='dynamic')
    entradas = db.relationship('Entrada', backref='fornecedor', lazy='dynamic')
    
    def __repr__(self):
        return f'<Fornecedor {self.nome}>'


class Cargo(db.Model):
    """Modelo de Cargos"""
    __tablename__ = 'cargos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(35), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Cargo {self.nome}>'


# =====================================================
# 2. SERVIÇOS E AGENDAMENTOS
# =====================================================

class Servico(db.Model):
    """Modelo de Serviços"""
    __tablename__ = 'servicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('cat_servicos.id'))
    valor = db.Column(db.Float, nullable=False)
    valor_comissao = db.Column(db.Float, default=0)  # Valor ou porcentagem da comissão
    dias_retorno = db.Column(db.Integer, default=30)  # Sugestão de retorno
    barbearia_id = db.Column(db.Integer, db.ForeignKey('barbearias.id'))
    foto = db.Column(db.String(255))
    descricao = db.Column(db.Text)
    ativo = db.Column(db.String(3), default='Sim')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    categoria = db.relationship('CategoriaServico', backref='servicos')
    agendamentos = db.relationship('Agendamento', backref='servico', lazy='dynamic')
    servicos_usuario = db.relationship('ServicoUsuario', backref='servico', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Servico {self.nome}>'


class CategoriaServico(db.Model):
    """Modelo de Categorias de Serviços"""
    __tablename__ = 'cat_servicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<CategoriaServico {self.nome}>'


class Agendamento(db.Model):
    """Modelo de Agendamentos"""
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    # funcionario_id e o barbeiro; usuario_id e quem criou o agendamento.
    funcionario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))  # Quem criou
    barbearia_id = db.Column(db.Integer, db.ForeignKey('barbearias.id'))
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Agendado')  # Agendado, Concluído, Cancelado
    obs = db.Column(db.String(255))
    data_lanc = db.Column(db.Date, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    funcionario = db.relationship('Usuario', foreign_keys=[funcionario_id], backref='agendamentos_como_funcionario')
    criador = db.relationship('Usuario', foreign_keys=[usuario_id])
    
    def __repr__(self):
        return f'<Agendamento {self.cliente.nome} - {self.data} {self.hora}>'


class Dia(db.Model):
    """Modelo de Dias de Trabalho"""
    __tablename__ = 'dias'
    
    id = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.String(20), nullable=False)  # Segunda, Terça, ...
    funcionario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relacionamentos
    funcionario = db.relationship('Usuario', backref='dias_trabalho')
    
    def __repr__(self):
        return f'<Dia {self.dia} - {self.funcionario.nome}>'


class Horario(db.Model):
    """Modelo de Horários Disponíveis"""
    __tablename__ = 'horarios'
    
    id = db.Column(db.Integer, primary_key=True)
    horario = db.Column(db.Time, nullable=False)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relacionamentos
    funcionario = db.relationship('Usuario', backref='horarios_trabalho')
    
    def __repr__(self):
        return f'<Horario {self.horario}>'


class ServicoUsuario(db.Model):
    """Modelo de Serviços por Usuário (Serviços que cada funcionário oferece)"""
    __tablename__ = 'servicos_usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    comissao = db.Column(db.Float)  # Comissão específica do usuário para este serviço
    
    def __repr__(self):
        return f'<ServicoUsuario {self.usuario.nome} - {self.servico.nome}>'


# =====================================================
# 3. PRODUTOS
# =====================================================

class Produto(db.Model):
    """Modelo de Produtos"""
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('cat_produtos.id'))
    valor_compra = db.Column(db.Float, nullable=False)
    valor_venda = db.Column(db.Float, nullable=False)
    # estoque guarda quantidade atual; nivel_estoque dispara alerta.
    estoque = db.Column(db.Integer, default=0)
    nivel_estoque = db.Column(db.Integer, default=10)  # Nível mínimo de alerta
    foto = db.Column(db.String(255))
    descricao = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    categoria = db.relationship('CatagoriaProduto', backref='produtos')
    entradas = db.relationship('Entrada', backref='produto', lazy='dynamic')
    saidas = db.relationship('Saida', backref='produto', lazy='dynamic')
    vendas = db.relationship('Venda', backref='produto', lazy='dynamic')
    
    def __repr__(self):
        return f'<Produto {self.nome}>'


class CatagoriaProduto(db.Model):
    """Modelo de Categorias de Produtos"""
    __tablename__ = 'cat_produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<CatagoriaProduto {self.nome}>'


class Entrada(db.Model):
    """Modelo de Entradas de Estoque"""
    __tablename__ = 'entradas'
    
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(255))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='entradas_estoque')
    
    def __repr__(self):
        return f'<Entrada {self.produto.nome} - {self.quantidade}>'


class Saida(db.Model):
    """Modelo de Saídas de Estoque"""
    __tablename__ = 'saidas'
    
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(255))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='saidas_estoque')
    
    def __repr__(self):
        return f'<Saida {self.produto.nome} - {self.quantidade}>'


# =====================================================
# 4. FINANCEIRO
# =====================================================

class ContaReceber(db.Model):
    """Modelo de Contas a Receber"""
    __tablename__ = 'receber'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(50), default='Serviço')  # Serviço, Produto
    agendamento_id = db.Column(db.Integer)  # Relacionado a agendamento
    data_venc = db.Column(db.Date, nullable=False)
    data_pgto = db.Column(db.Date)
    pago = db.Column(db.String(3), default='Não')  # Sim/Não
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContaReceber {self.descricao} - R$ {self.valor}>'


class ContaPagar(db.Model):
    """Modelo de Contas a Pagar"""
    __tablename__ = 'pagar'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'))
    data_venc = db.Column(db.Date, nullable=False)
    data_pgto = db.Column(db.Date)
    pago = db.Column(db.String(3), default='Não')  # Sim/Não
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContaPagar {self.descricao} - R$ {self.valor}>'


class Venda(db.Model):
    """Modelo de Vendas (Produtos vendidos)"""
    __tablename__ = 'vendas'
    
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    cliente = db.relationship('Cliente', backref='vendas')
    usuario = db.relationship('Usuario', backref='vendas')
    
    def __repr__(self):
        return f'<Venda {self.produto.nome} - {self.quantidade}>'


class Compra(db.Model):
    """Modelo de Compras (Produtos comprados)"""
    __tablename__ = 'compras'
    
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Compra {self.produto.nome} - {self.quantidade}>'


# =====================================================
# 5. AUTENTICAÇÃO E PERMISSÕES
# =====================================================

class Acesso(db.Model):
    """Modelo de Acessos (Permissões/Funcionalidades)"""
    __tablename__ = 'acessos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo_acessos.id'), nullable=False)
    
    # Relacionamentos
    grupo = db.relationship('GrupoAcesso', backref='acessos')
    permissoes = db.relationship('UsuarioPermissao', backref='acesso', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Acesso {self.nome}>'


class GrupoAcesso(db.Model):
    """Modelo de Grupos de Acessos"""
    __tablename__ = 'grupo_acessos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<GrupoAcesso {self.nome}>'


class UsuarioPermissao(db.Model):
    """Modelo de Permissões por Usuário"""
    __tablename__ = 'usuarios_permissoes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    permissao_id = db.Column(db.Integer, db.ForeignKey('acessos.id'), nullable=False)
    
    def __repr__(self):
        return f'<UsuarioPermissao {self.usuario.nome} - {self.acesso.nome}>'


# =====================================================
# 6. CONFIGURAÇÕES
# =====================================================

class Config(db.Model):
    """Modelo de Configurações do Sistema"""
    __tablename__ = 'config'
    
    id = db.Column(db.Integer, primary_key=True, default=1)
    nome = db.Column(db.String(120), default='Barbearia PRO')
    email = db.Column(db.String(120), default='barbearia@email.com')
    telefone_whatsapp = db.Column(db.String(20))
    telefone_fixo = db.Column(db.String(20))
    endereco = db.Column(db.String(255))
    instagram = db.Column(db.String(100))
    logo = db.Column(db.String(255), default='logo.png')
    icone = db.Column(db.String(255), default='favicon.ico')
    logo_rel = db.Column(db.String(255), default='logo_rel.jpg')
    img_banner_index = db.Column(db.String(255), default='hero-bg.jpg')
    tipo_rel = db.Column(db.String(10), default='pdf')  # pdf, html
    tipo_comissao = db.Column(db.String(50), default='Porcentagem')  # Porcentagem ou Fixo
    quantidade_cartoes = db.Column(db.Integer, default=10)  # Fidelidade
    texto_rodape = db.Column(db.Text, default='Edite este texto nas configurações')
    texto_agendamento = db.Column(db.String(255), default='Selecionar Prestador de Serviço')
    msg_agendamento = db.Column(db.String(3), default='Sim')
    icone_site = db.Column(db.String(255))
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Config {self.nome}>'


class Comentario(db.Model):
    """Modelo de Comentários/Depoimentos"""
    __tablename__ = 'comentarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    foto = db.Column(db.String(255))
    ativo = db.Column(db.String(3), default='Não')  # Sim/Não
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Comentario {self.nome}>'


class TextoIndex(db.Model):
    """Modelo de Textos da Home"""
    __tablename__ = 'textos_index'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text)
    ordem = db.Column(db.Integer, default=0)
    ativo = db.Column(db.String(3), default='Sim')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TextoIndex {self.titulo}>'


class Cupom(db.Model):
    """Modelo de Cupons de Desconto"""
    __tablename__ = 'cupons'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False) # Ex: ZUH20
    desconto = db.Column(db.Float, nullable=False) # Ex: 20.00
    tipo = db.Column(db.String(20), default='Porcentagem') # Porcentagem ou Fixo
    ativo = db.Column(db.String(3), default='Sim')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Cupom {self.codigo}>'

class Plano(db.Model):
    """Modelo de Planos SaaS"""
    __tablename__ = 'planos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)  # Basico, Pro, Enterprise
    preco_mensal = db.Column(db.Float, default=0.0)
    max_funcionarios = db.Column(db.Integer, default=2)  # -1 = ilimitado
    max_agendamentos_mes = db.Column(db.Integer, default=100)  # -1 = ilimitado
    permite_relatorios = db.Column(db.String(3), default='Nao')
    permite_financeiro = db.Column(db.String(3), default='Nao')
    permite_estoque = db.Column(db.String(3), default='Nao')
    permite_api = db.Column(db.String(3), default='Nao')
    permite_dominio_custom = db.Column(db.String(3), default='Nao')
    ativo = db.Column(db.String(3), default='Sim')

    def __repr__(self):
        return f'<Plano {self.nome}>'


class Barbearia(db.Model):
    """Modelo de Barbearias/Barbeiros (Tenants do SaaS)"""
    __tablename__ = 'barbearias'

    id = db.Column(db.Integer, primary_key=True)
    # Tipo de conta
    tipo = db.Column(db.String(20), default='barbearia')  # 'barbearia' ou 'barbeiro'
    # Identidade
    nome = db.Column(db.String(120), nullable=False)
    # slug identifica a barbearia em URLs/subdominios.
    slug = db.Column(db.String(60), unique=True, nullable=False)  # subdominio: zuh, joao-silva
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_crip = db.Column(db.String(255), nullable=False)  # Senha do DONO/PROPRIETARIO
    telefone = db.Column(db.String(20))
    # Endereco (opcional para barbeiro freelancer)
    endereco = db.Column(db.String(255))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    # Perfil publico
    foto = db.Column(db.String(255))
    descricao = db.Column(db.Text)  # Bio do barbeiro ou descricao da barbearia
    instagram = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    # Dominio customizado (plano Enterprise)
    dominio_customizado = db.Column(db.String(255))
    # Plano e status
    plano_id = db.Column(db.Integer, db.ForeignKey('planos.id'))
    status = db.Column(db.String(20), default='trial')  # trial, ativo, suspenso, cancelado
    trial_ate = db.Column(db.DateTime)  # Data de expiracao do trial
    ativo = db.Column(db.String(3), default='Sim')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    plano = db.relationship('Plano', backref='barbearias')
    usuarios = db.relationship('Usuario', backref='barbearia', lazy='dynamic', cascade='all, delete-orphan')
    clientes = db.relationship('Cliente', backref='barbearia', lazy='dynamic', cascade='all, delete-orphan')
    agendamentos = db.relationship('Agendamento', backref='barbearia', lazy='dynamic', cascade='all, delete-orphan')
    servicos = db.relationship('Servico', backref='barbearia', lazy='dynamic', cascade='all, delete-orphan')

    def set_senha(self, senha):
        # Senha do dono tambem fica com hash seguro.
        from werkzeug.security import generate_password_hash
        self.senha_crip = generate_password_hash(senha)

    def verifica_senha(self, senha):
        # Confere senha do dono da conta SaaS.
        from werkzeug.security import check_password_hash
        return check_password_hash(self.senha_crip, senha)

    @property
    def em_trial(self):
        # Trial so esta ativo enquanto a data limite nao passou.
        if self.status == 'trial' and self.trial_ate:
            return datetime.utcnow() < self.trial_ate
        return False

    @property
    def is_barbeiro(self):
        return self.tipo == 'barbeiro'

    @property
    def is_barbearia(self):
        return self.tipo == 'barbearia'

    def __repr__(self):
        return f'<Barbearia [{self.tipo}] {self.nome} ({self.slug})>'
