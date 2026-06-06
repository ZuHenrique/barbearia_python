# Barbearia ZUH - Versão Python

Sistema completo de gestão para barbearias, desenvolvido em **Python com Flask**.

## 🎯 Características

✅ **Frontend Responsivo** - Bootstrap 5  
✅ **Autenticação Segura** - Login com MD5 (compatível com PHP)  
✅ **Agendamentos Online** - Sistema multi-step  
✅ **Gestão de Clientes** - CRUD completo  
✅ **Gestão de Funcionários** - Controle de usuários e permissões  
✅ **Controle de Serviços** - Catálogo e comissões  
✅ **Gestão de Estoque** - Produtos com alertas  
✅ **Financeiro** - Contas a pagar/receber  
✅ **Relatórios** - Agendamentos, Vendas, Comissões, Financeiro  
✅ **API REST** - Para integração com apps  
✅ **Dashboard** - Indicadores principais em tempo real  

---

## 📁 Estrutura do Projeto

```
barbearia-python/
├── app/
│   ├── blueprints/          # Rotas organizadas
│   │   ├── auth.py          # Autenticação
│   │   ├── main.py          # Página pública
│   │   ├── dashboard.py     # Painel
│   │   ├── agendamentos.py  # Agendamentos
│   │   ├── clientes.py      # Clientes
│   │   ├── usuarios.py      # Usuários
│   │   ├── servicos.py      # Serviços
│   │   ├── produtos.py      # Produtos
│   │   ├── financeiro.py    # Financeiro
│   │   ├── relatorios.py    # Relatórios
│   │   └── api.py           # APIs REST
│   ├── templates/           # Templates HTML
│   │   ├── base.html        # Template base
│   │   ├── auth/            # Templates de autenticação
│   │   ├── public/          # Página pública
│   │   └── painel/          # Painel administrativo
│   ├── static/              # Arquivos estáticos
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   └── uploads/
│   ├── models.py            # Modelos do banco de dados (SQLAlchemy)
│   └── __init__.py          # Inicialização da app
├── config.py                # Configurações
├── run.py                   # Script de inicialização
├── requirements.txt         # Dependências Python
└── README.md                # Este arquivo
```

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- MySQL/MariaDB
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. **Clone ou extraia o projeto**
```bash
cd barbearia-python
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o banco de dados**

Edite o arquivo `config.py` e configure a conexão MySQL:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usuario:senha@localhost/barbearia'
```

5. **Crie as tabelas do banco de dados**
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

6. **Inicie a aplicação**
```bash
python run.py
```

A aplicação estará disponível em: **http://localhost:5000**

---

## 📊 Banco de Dados

A aplicação usa **23 tabelas** para gerenciar:

### Gerenciamento de Pessoas
- **usuarios** - Funcionários/Barbeiros
- **clientes** - Clientes
- **fornecedores** - Fornecedores
- **cargos** - Níveis/Cargos

### Serviços e Agendamentos
- **servicos** - Serviços oferecidos
- **cat_servicos** - Categorias de serviços
- **agendamentos** - Agendamentos
- **dias** - Dias de funcionamento
- **horarios** - Horários disponíveis
- **servicos_usuario** - Serviços por usuário

### Produtos
- **produtos** - Produtos para venda
- **cat_produtos** - Categorias de produtos
- **entradas** - Entrada de estoque
- **saidas** - Saída de estoque

### Financeiro
- **receber** - Contas a receber
- **pagar** - Contas a pagar
- **vendas** - Vendas de produtos
- **compras** - Compras de produtos

### Sistema
- **acessos** - Permissões/Funcionalidades
- **grupo_acessos** - Grupos de permissões
- **usuarios_permissoes** - Permissões por usuário
- **config** - Configurações gerais
- **comentarios** - Depoimentos
- **textos_index** - Textos da home

---

## 🔐 Autenticação

### Usuários de Teste (após criar no banco)
```
Email: admin@admin
Senha: 123
Nível: Administrador
```

### Fluxo de Autenticação
1. Usuário acessa `/sistema/login`
2. Valida credenciais (email ou CPF + senha MD5)
3. Verifica se usuário está ativo
4. Cria sessão e redireciona para `/sistema/painel`

---

## 📱 Funcionalidades Principais

### 1. Página Pública
- **Home** - Apresentação, depoimentos
- **Serviços** - Catálogo de serviços
- **Produtos** - Loja online
- **Agendamentos** - Formulário multi-step

### 2. Painel Administrativo
- **Dashboard** - Indicadores principais
- **Agendamentos** - CRUD completo
- **Clientes** - Gestão de clientes
- **Usuários** - Gestão de funcionários
- **Serviços** - Cadastro de serviços
- **Produtos** - Gestão de estoque
- **Financeiro** - Contas a pagar/receber
- **Relatórios** - Diversos relatórios

### 3. APIs REST
```
GET  /api/servicos                    # Lista serviços
GET  /api/funcionarios                # Lista funcionários
GET  /api/horarios/<id>/<data>        # Horários disponíveis
POST /api/agendamentos                # Criar agendamento
GET  /api/clientes/verificar/<tel>    # Verificar cliente
GET  /api/health                      # Health check
```

---

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-app
```

### Banco de Dados MySQL

Exemplo de conexão:
```python
# Development
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/barbearia'

# Production
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@servidor.com/barbearia'
```

---

## 📝 Migrando do PHP para Python

Este projeto é uma **conversão completa** do projeto PHP original:

| Funcionalidade | PHP | Python |
|---|---|---|
| **Framework** | Vanilla PHP | Flask |
| **Banco de Dados** | PDO MySQL | SQLAlchemy + PyMySQL |
| **Autenticação** | Sessions | Flask-Login |
| **Templates** | PHP Templates | Jinja2 |
| **Frontend** | Bootstrap 4 | Bootstrap 5 |
| **APIs** | AJAX/PHP | REST API JSON |

---

## 🔄 Sincronizando com PHP

Se você ainda tem o projeto PHP em uso:

1. **Banco de Dados Compartilhado**
   - Ambas aplicações podem usar o mesmo banco MySQL
   - Use a mesma estrutura de tabelas

2. **Migrar Dados**
   ```bash
   # Exportar do PHP MySQL
   mysqldump -u root barbearia > backup.sql
   
   # Importar no Python MySQL
   mysql -u root barbearia < backup.sql
   ```

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Erro: "No module named 'pymysql'"
```bash
pip install mysql-connector-python
```

### Erro de Conexão com Banco de Dados
Verifique:
- MySQL está rodando
- Credenciais corretas em `config.py`
- Banco de dados `barbearia` existe

### Erro 404 ao acessar rotas
- Verifique a URL correta
- Certifique-se de que o blueprint está registrado em `app/__init__.py`

---

## 📚 Documentação das APIs

### Criar Agendamento
```bash
curl -X POST http://localhost:5000/api/agendamentos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "telefone": "(11) 99999-9999",
    "funcionario_id": 1,
    "servico_id": 1,
    "data": "2024-05-15",
    "hora": "14:00",
    "obs": "Observação"
  }'
```

### Listar Serviços
```bash
curl http://localhost:5000/api/servicos
```

### Verificar Horários Disponíveis
```bash
curl http://localhost:5000/api/horarios/1/2024-05-15
```

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs em `app.log`
2. Use `FLASK_DEBUG=True` para mais detalhes
3. Consulte a documentação de Flask em https://flask.palletsprojects.com

---

## 📄 Licença

Este projeto é fornecido como está. Sinta-se livre para adaptá-lo às suas necessidades.

---

**Barbearia ZUH - Sistema de Gestão v1.0 (Python)**  
Desenvolvido com ❤️ em Python
