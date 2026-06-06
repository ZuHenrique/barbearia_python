# Guia Rapido - Barbearia Python

## Inicio rapido

### 1. Preparar ambiente

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variaveis

```bash
copy .env.example .env
```

O app usa SQLite por padrao. Para usar MySQL, configure `DATABASE_URL` no `.env`:

```env
DATABASE_URL=mysql+pymysql://root:senha@localhost/barbearia
```

### 3. Inicializar banco com dados de teste

```bash
python init_db.py
```

### 4. Iniciar aplicacao

```bash
python run.py
```

Acesse:

```text
http://localhost:3000
```

## Login de teste

```text
Email: admin@admin
Senha: 123
```

## URLs principais

| URL | Descricao |
| --- | --- |
| `/` | Pagina inicial publica |
| `/servicos` | Catalogo de servicos |
| `/produtos` | Produtos |
| `/agendamentos` | Agendar servico |
| `/cadastro/barbearia` | Cadastro de barbearia |
| `/cadastro/barbeiro` | Cadastro de barbeiro autonomo |
| `/area-cliente` | Area do cliente |
| `/sistema/login` | Login administrativo |
| `/sistema/painel` | Dashboard administrativo |
| `/sistema/painel/agendamentos` | Gerenciar agendamentos |
| `/sistema/painel/clientes` | Gerenciar clientes |
| `/sistema/painel/usuarios` | Gerenciar usuarios |
| `/sistema/painel/servicos` | Gerenciar servicos |
| `/sistema/painel/produtos` | Gerenciar produtos |
| `/sistema/painel/financeiro/receber` | Contas a receber |
| `/sistema/painel/financeiro/pagar` | Contas a pagar |
| `/sistema/painel/relatorios` | Relatorios |

## APIs REST

### Health check

```bash
curl http://localhost:3000/api/health
```

### Listar servicos

```bash
curl http://localhost:3000/api/servicos
```

### Listar funcionarios

```bash
curl http://localhost:3000/api/funcionarios
```

### Horarios disponiveis

```bash
curl http://localhost:3000/api/horarios/1/2026-06-20
```

### Criar agendamento

```bash
curl -X POST http://localhost:3000/api/agendamentos ^
  -H "Content-Type: application/json" ^
  -d "{\"nome\":\"Joao\",\"telefone\":\"(11) 99999-9999\",\"funcionario_id\":1,\"servico_id\":1,\"data\":\"2026-06-20\",\"hora\":\"14:00\"}"
```

## Estrutura resumida

```text
app/
|-- blueprints/   # Rotas do sistema
|-- templates/    # Paginas HTML
|-- static/       # Arquivos estaticos
|-- models.py     # Modelos do banco
`-- __init__.py   # Criacao do app Flask
```

## Problemas comuns

### `ModuleNotFoundError`

```bash
pip install -r requirements.txt
```

### Banco nao conecta

- Confirme se `DATABASE_URL` esta correto.
- Se usar MySQL, confira se o servidor esta rodando.
- Se quiser desenvolvimento simples, remova `DATABASE_URL` e use SQLite.

### A pagina nao abre em `localhost:5000`

Este projeto roda na porta `3000` pelo `run.py`. Use:

```text
http://localhost:3000
```

## Proximos passos

1. Entrar no painel com `admin@admin` e senha `123`.
2. Cadastrar ou revisar servicos.
3. Cadastrar produtos.
4. Testar um agendamento publico.
5. Ler o `README.md` para entender a arquitetura completa.
