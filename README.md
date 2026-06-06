# Barbearia Python

Sistema web em Flask para gerenciamento de barbearia. O projeto tem site publico, area do cliente, painel administrativo, agendamentos, clientes, usuarios/barbeiros, servicos, produtos, estoque, financeiro, relatorios e APIs auxiliares.

## O que o sistema faz

- Exibe paginas publicas de apresentacao, servicos, produtos e agendamento.
- Permite cadastro de barbearia ou barbeiro pelo fluxo de onboarding.
- Oferece login administrativo em `/sistema/login`.
- Organiza o painel em modulos: dashboard, clientes, usuarios, servicos, produtos, financeiro, agendamentos e relatorios.
- Permite login/cadastro de cliente em `/area-cliente`.
- Expoe endpoints REST em `/api` para servicos, funcionarios, horarios, clientes e criacao de agendamento.
- Usa SQLAlchemy para mapear tabelas e Flask-Migrate/Alembic para migracoes.

## Tecnologias

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-Migrate
- Jinja2
- Authlib
- SQLite por padrao, com suporte a MySQL via `DATABASE_URL`

## Como rodar localmente

1. Crie e ative o ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Configure as variaveis de ambiente:

```bash
copy .env.example .env
```

O projeto roda com SQLite se `DATABASE_URL` nao for informado. Para MySQL, configure algo como:

```env
DATABASE_URL=mysql+pymysql://usuario:senha@localhost/barbearia
```

4. Crie dados iniciais de teste:

```bash
python init_db.py
```

5. Inicie a aplicacao:

```bash
python run.py
```

Acesse no navegador:

```text
http://localhost:3000
```

## Credenciais de teste

Depois de executar `python init_db.py`, use:

```text
Email: admin@admin
Senha: 123
```

## Estrutura do projeto

```text
barbearia-python/
|-- app/
|   |-- blueprints/       # Rotas separadas por modulo
|   |-- static/           # Imagens, uploads e arquivos estaticos
|   |-- templates/        # Telas HTML renderizadas pelo Flask/Jinja
|   |-- __init__.py       # Factory create_app, extensoes e blueprints
|   `-- models.py         # Modelos do banco de dados
|-- instance/             # Banco SQLite local e dados de instancia
|-- migrations/           # Migracoes Alembic/Flask-Migrate
|-- config.py             # Configuracoes por ambiente
|-- init_db.py            # Cria tabelas e dados de teste
|-- run.py                # Ponto de entrada da aplicacao
|-- requirements.txt      # Dependencias Python
|-- QUICK_START.md        # Guia rapido
`-- README.md             # Documentacao principal
```

## Explicacao do codigo

### `run.py`

E o ponto de entrada do projeto. Ele importa `create_app`, cria a aplicacao usando o ambiente definido em `FLASK_ENV` e inicia o servidor Flask na porta `3000`.

Tambem define `make_shell_context()`, que deixa `db` e os modelos disponiveis automaticamente quando voce abre o shell do Flask. Isso ajuda a testar consultas e manipular dados sem importar tudo manualmente.

### `config.py`

Centraliza as configuracoes da aplicacao.

- `Config`: configuracao base compartilhada por todos os ambientes.
- `DevelopmentConfig`: modo de desenvolvimento, com debug ativo.
- `ProductionConfig`: modo de producao, com cookies seguros para HTTPS.
- `TestingConfig`: configuracao para testes.
- `config`: dicionario usado pelo `create_app()` para escolher o ambiente.

O banco padrao e `sqlite:///barbearia.db`, mas pode ser trocado com `DATABASE_URL`.

### `app/__init__.py`

Contem a factory `create_app()`, responsavel por montar o Flask:

- cria a instancia `Flask`;
- carrega as configuracoes;
- inicializa `db`, `login_manager` e `migrate`;
- configura o login de usuarios e clientes;
- registra todos os blueprints;
- chama `db.create_all()` para garantir as tabelas no ambiente local.

O `user_loader` diferencia usuarios administrativos e clientes pelo formato do ID:

- `usuario_1`
- `cliente_1`

### `app/models.py`

Define as tabelas principais do sistema com SQLAlchemy.

Principais grupos de modelos:

- Pessoas: `Usuario`, `Cliente`, `Fornecedor`, `Cargo`.
- Servicos e agenda: `Servico`, `CategoriaServico`, `Agendamento`, `Dia`, `Horario`, `ServicoUsuario`.
- Produtos e estoque: `Produto`, `CatagoriaProduto`, `Entrada`, `Saida`.
- Financeiro: `ContaReceber`, `ContaPagar`, `Venda`, `Compra`.
- Acesso e permissoes: `Acesso`, `GrupoAcesso`, `UsuarioPermissao`.
- Configuracao e conteudo publico: `Config`, `Comentario`, `TextoIndex`.
- SaaS/onboarding: `Barbearia`, `Plano`, `Cupom`.

Os modelos `Usuario`, `Cliente` e `Barbearia` possuem metodos para criar e validar senha com hash seguro usando Werkzeug.

### `app/blueprints/`

Cada arquivo agrupa rotas de uma parte do sistema:

- `main.py`: paginas publicas, como home, servicos, produtos e agendamentos.
- `auth.py`: login, logout, perfil e troca de senha do painel.
- `dashboard.py`: painel inicial e dados do dashboard.
- `agendamentos.py`: CRUD e alteracao de status dos agendamentos.
- `clientes.py`: cadastro, edicao, listagem e criacao rapida de clientes.
- `usuarios.py`: gerenciamento de usuarios/barbeiros.
- `servicos.py`: cadastro e manutencao de servicos.
- `produtos.py`: cadastro, estoque, entradas e saidas.
- `financeiro.py`: contas a receber e contas a pagar.
- `relatorios.py`: telas de relatorios.
- `api.py`: endpoints JSON usados por telas e integracoes.
- `area_cliente.py`: login, cadastro e painel do cliente.
- `onboarding.py`: cadastro publico de barbearia ou barbeiro.

### `app/templates/`

Guarda as telas HTML renderizadas pelo Flask. Existem tres areas principais:

- `public/`: paginas abertas ao publico.
- `auth/`: telas de login, perfil e recuperacao de senha.
- `painel/`: telas do sistema administrativo.

### `init_db.py`

Cria as tabelas e popula o banco com dados de teste: usuarios, permissoes, clientes, servicos, produtos, horarios, comentarios, textos da home, contas e agendamentos.

Use esse arquivo em ambiente local para comecar rapido. Em producao, prefira migracoes e dados reais.

## Rotas principais

| Rota | Descricao |
| --- | --- |
| `/` | Pagina inicial publica |
| `/servicos` | Lista publica de servicos |
| `/produtos` | Lista publica de produtos |
| `/agendamentos` | Agendamento publico |
| `/cadastro/barbearia` | Cadastro de nova barbearia |
| `/cadastro/barbeiro` | Cadastro de barbeiro autonomo |
| `/area-cliente` | Area do cliente |
| `/sistema/login` | Login administrativo |
| `/sistema/painel` | Dashboard administrativo |
| `/sistema/painel/clientes` | Clientes |
| `/sistema/painel/usuarios` | Usuarios/barbeiros |
| `/sistema/painel/servicos` | Servicos |
| `/sistema/painel/produtos` | Produtos e estoque |
| `/sistema/painel/financeiro/receber` | Contas a receber |
| `/sistema/painel/financeiro/pagar` | Contas a pagar |
| `/sistema/painel/relatorios` | Relatorios |

## APIs

| Metodo | Endpoint | Funcao |
| --- | --- | --- |
| `GET` | `/api/health` | Verifica se a API esta online |
| `GET` | `/api/servicos` | Lista servicos ativos |
| `GET` | `/api/funcionarios` | Lista funcionarios/barbeiros |
| `GET` | `/api/horarios/<funcionario_id>/<data>` | Lista horarios disponiveis |
| `GET` | `/api/clientes/verificar/<telefone>` | Verifica cliente por telefone |
| `POST` | `/api/agendamentos` | Cria um agendamento |

Exemplo:

```bash
curl http://localhost:3000/api/health
```

## Banco de dados

Em desenvolvimento, o projeto pode usar SQLite automaticamente. Para MySQL, defina `DATABASE_URL`.

Com Flask-Migrate instalado, o fluxo recomendado para mudancas de schema e:

```bash
flask db migrate -m "descricao da mudanca"
flask db upgrade
```

Observacao: `create_app()` tambem executa `db.create_all()`, o que facilita desenvolvimento local, mas em producao o ideal e controlar schema com migracoes.

## Variaveis importantes

| Variavel | Descricao |
| --- | --- |
| `FLASK_ENV` | Ambiente usado pelo app: `development`, `production` ou `testing` |
| `SECRET_KEY` | Chave de sessao do Flask |
| `DATABASE_URL` | URL do banco de dados |
| `MAIL_USERNAME` | Usuario SMTP |
| `MAIL_PASSWORD` | Senha ou app password SMTP |

## GitHub

Este README foi escrito para aparecer bem na pagina inicial do repositorio no GitHub. Para publicar alteracoes:

```bash
git status
git add README.md QUICK_START.md
git commit -m "Melhora documentacao do projeto"
git push origin main
```

## Pontos de melhoria futuros

- Adicionar testes automatizados para rotas e modelos principais.
- Remover `db.create_all()` do fluxo de producao e depender apenas de migracoes.
- Revisar regras multi-tenant para garantir filtros por `barbearia_id` em todas as consultas.
- Padronizar nomes com acento e corrigir typos como `CatagoriaProduto`.
- Criar pagina de configuracoes para evitar editar `config.py` manualmente.
- Adicionar validacoes mais fortes nos formularios.

## Licenca

Este projeto esta distribuido sob os termos descritos em `LICENSE`.
