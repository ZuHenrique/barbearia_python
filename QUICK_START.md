# GUIA RÁPIDO DE USO - Barbearia PRO (Python)

## ⚡ Início Rápido (5 minutos)

### 1. Preparação do Ambiente
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados
```bash
# Editar config.py com suas credenciais MySQL
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/barbearia'
```

### 3. Inicializar com Dados de Teste
```bash
python init_db.py
```

### 4. Iniciar a Aplicação
```bash
python run.py
```

Acesse: **http://localhost:5000**

---

## 🔐 Credenciais de Teste

```
Email: admin@admin
Senha: 123
```

---

## 📱 URLs Principais

| URL | Descrição |
|-----|-----------|
| `/` | Página inicial pública |
| `/servicos` | Catálogo de serviços |
| `/produtos` | Loja de produtos |
| `/agendamentos` | Agendar serviço |
| `/sistema/login` | Fazer login |
| `/sistema/painel` | Dashboard administrativo |
| `/sistema/painel/agendamentos` | Gerenciar agendamentos |
| `/sistema/painel/clientes` | Gerenciar clientes |
| `/sistema/painel/usuarios` | Gerenciar usuários |
| `/sistema/painel/servicos` | Gerenciar serviços |
| `/sistema/painel/produtos` | Gerenciar produtos |
| `/sistema/painel/financeiro/receber` | Contas a receber |
| `/sistema/painel/financeiro/pagar` | Contas a pagar |
| `/sistema/painel/relatorios` | Relatórios |

---

## 🔌 APIs REST

### GET - Listar Serviços
```bash
curl http://localhost:5000/api/servicos
```

### GET - Listar Funcionários
```bash
curl http://localhost:5000/api/funcionarios
```

### GET - Horários Disponíveis
```bash
curl http://localhost:5000/api/horarios/1/2024-05-20
```

### POST - Criar Agendamento
```bash
curl -X POST http://localhost:5000/api/agendamentos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João",
    "telefone": "(11) 99999-9999",
    "funcionario_id": 1,
    "servico_id": 1,
    "data": "2024-05-20",
    "hora": "14:00"
  }'
```

---

## 📁 Estrutura de Arquivos

```
barbearia-python/
├── app/                 # Código da aplicação
│   ├── blueprints/      # Rotas (auth, main, dashboard, etc)
│   ├── templates/       # Templates HTML
│   ├── static/          # CSS, JS, images
│   ├── models.py        # Modelos do banco de dados
│   └── __init__.py      # Inicialização
├── config.py            # Configurações
├── run.py               # Script principal
├── init_db.py           # Inicializar banco de dados
├── requirements.txt     # Dependências
├── README.md            # Documentação
├── QUICK_START.md       # Este arquivo
└── .env.example         # Variáveis de exemplo
```

---

## 🐛 Troubleshooting

### Erro: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Erro: Database connection refused
- MySQL está rodando?
- Credenciais corretas em `config.py`?
- Banco `barbearia` existe?

### Erro: "405 Method Not Allowed"
- Verifique o método HTTP (GET, POST, etc)
- Verifique a URL da rota

---

## 🚀 Próximos Passos

1. **Criar Usuários** - `/sistema/painel/usuarios/novo`
2. **Criar Serviços** - `/sistema/painel/servicos/novo`
3. **Criar Produtos** - `/sistema/painel/produtos/novo`
4. **Configurar Sistema** - Editar `config.py`
5. **Testar Agendamentos** - `/agendamentos`

---

## 📖 Documentação Completa

Leia o `README.md` para documentação completa do projeto.

---

## 💡 Dicas

- Use `FLASK_DEBUG=True` para development
- Verifique logs no console
- Use o DevTools do navegador (F12)
- Teste APIs com Postman ou cURL

---

**Sucesso! 🎉**
