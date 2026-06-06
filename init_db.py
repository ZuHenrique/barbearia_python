#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Inicialização e Seed do Banco de Dados
Cria dados de teste para a aplicação Barbearia PRO
"""
from app import create_app, db
from app.models import (
    Usuario, Cliente, Fornecedor, Cargo, Servico, CategoriaServico,
    Agendamento, Dia, Horario, Produto, CatagoriaProduto, Config,
    Comentario, TextoIndex, Acesso, GrupoAcesso, UsuarioPermissao,
    ContaReceber, ContaPagar, Venda
)
from datetime import datetime, date, timedelta, time

def init_database():
    """Inicializa o banco de dados com dados de teste"""
    
    # Cria app para ter acesso ao contexto Flask e ao banco.
    app = create_app()
    
    with app.app_context():
        print("🗂️  Criando tabelas...")
        # Cria tabelas que ainda nao existem.
        db.create_all()
        
        # Verificar se já tem dados
        # Evita duplicar dados de teste se o seed ja rodou.
        if Usuario.query.count() > 0:
            print("⚠️  Banco de dados já possui dados. Pulando seed.")
            return
        
        print("🌱 Criando dados de teste...")
        
        # ========== GRUPOS DE ACESSOS ==========
        grupos = [
            GrupoAcesso(nome='Pessoas'),
            GrupoAcesso(nome='Cadastros'),
            GrupoAcesso(nome='Produtos'),
            GrupoAcesso(nome='Financeiro'),
            GrupoAcesso(nome='Agendamento'),
            GrupoAcesso(nome='Relatórios'),
            GrupoAcesso(nome='Dados Site'),
        ]
        # flush gera IDs sem fechar a transacao.
        db.session.add_all(grupos)
        db.session.flush()
        
        # ========== ACESSOS/PERMISSÕES ==========
        acessos = [
            Acesso(nome='Usuários', chave='usuarios', grupo_id=1),
            Acesso(nome='Funcionários', chave='funcionarios', grupo_id=1),
            Acesso(nome='Clientes', chave='clientes', grupo_id=1),
            Acesso(nome='Fornecedores', chave='fornecedores', grupo_id=1),
            Acesso(nome='Serviços', chave='servicos', grupo_id=2),
            Acesso(nome='Categoria Serviços', chave='cat_servicos', grupo_id=2),
            Acesso(nome='Produtos', chave='produtos', grupo_id=3),
            Acesso(nome='Categorias', chave='cat_produtos', grupo_id=3),
            Acesso(nome='Estoque Baixo', chave='estoque', grupo_id=3),
            Acesso(nome='Entradas', chave='entradas', grupo_id=3),
            Acesso(nome='Saídas', chave='saidas', grupo_id=3),
            Acesso(nome='Contas a Receber', chave='receber', grupo_id=4),
            Acesso(nome='Contas a Pagar', chave='pagar', grupo_id=4),
            Acesso(nome='Agendamentos', chave='agendamentos', grupo_id=5),
            Acesso(nome='Relatórios', chave='relatorios', grupo_id=6),
            Acesso(nome='Comentários', chave='comentarios', grupo_id=7),
        ]
        # Acessos sao as chaves usadas para permissoes.
        db.session.add_all(acessos)
        db.session.flush()
        
        # ========== USUÁRIOS ==========
        admin = Usuario(
            nome='Administrador',
            email='admin@admin',
            cpf='00000000000',
            nivel='Administrador',
            telefone='(11) 98765-4321',
            atendimento='Sim',
            ativo='Sim'
        )
        # Senha de teste do administrador.
        admin.set_senha('123')
        
        barbeiro1 = Usuario(
            nome='João Silva',
            email='joao@barbearia.com',
            cpf='12345678900',
            nivel='Barbeiro',
            telefone='(11) 99999-8888',
            atendimento='Sim',
            ativo='Sim'
        )
        barbeiro1.set_senha('123')
        
        barbeiro2 = Usuario(
            nome='Carlos Santos',
            email='carlos@barbearia.com',
            cpf='98765432100',
            nivel='Barbeiro',
            telefone='(11) 99999-7777',
            atendimento='Sim',
            ativo='Sim'
        )
        barbeiro2.set_senha('123')
        
        db.session.add_all([admin, barbeiro1, barbeiro2])
        db.session.flush()
        
        # Adicionar permissões
        # Administrador recebe todas as permissoes iniciais.
        for acesso in acessos:
            perm = UsuarioPermissao(usuario_id=admin.id, permissao_id=acesso.id)
            db.session.add(perm)
        
        # ========== CLIENTES ==========
        clientes = [
            Cliente(nome='Fernando Machado', telefone='(11) 99999-1111', endereco='Rua A, 100', data_cad=date.today()),
            Cliente(nome='Roberto Costa', telefone='(11) 99999-2222', endereco='Av B, 200', data_cad=date.today()),
            Cliente(nome='Lucas Oliveira', telefone='(11) 99999-3333', endereco='Rua C, 300', data_cad=date.today()),
        ]
        db.session.add_all(clientes)
        db.session.flush()
        
        # ========== CATEGORIAS DE SERVIÇOS ==========
        cat_servicos = [
            CategoriaServico(nome='Corte'),
            CategoriaServico(nome='Barba'),
            CategoriaServico(nome='Pacotes'),
        ]
        db.session.add_all(cat_servicos)
        db.session.flush()
        
        # ========== SERVIÇOS ==========
        servicos = [
            Servico(nome='Corte Simples', categoria_id=1, valor=35.00, valor_comissao=10.00, dias_retorno=30, ativo='Sim'),
            Servico(nome='Corte Máquina', categoria_id=1, valor=30.00, valor_comissao=8.00, dias_retorno=20, ativo='Sim'),
            Servico(nome='Barba Completa', categoria_id=2, valor=30.00, valor_comissao=8.00, dias_retorno=5, ativo='Sim'),
            Servico(nome='Corte + Barba', categoria_id=3, valor=60.00, valor_comissao=18.00, dias_retorno=30, ativo='Sim'),
            Servico(nome='Hidratação', categoria_id=1, valor=25.00, valor_comissao=7.00, dias_retorno=60, ativo='Sim'),
        ]
        db.session.add_all(servicos)
        db.session.flush()
        
        # ========== CATEGORIAS DE PRODUTOS ==========
        cat_produtos = [
            CatagoriaProduto(nome='Pomadas'),
            CatagoriaProduto(nome='Cremes'),
            CatagoriaProduto(nome='Lâminas'),
            CatagoriaProduto(nome='Bebidas'),
            CatagoriaProduto(nome='Gel'),
        ]
        db.session.add_all(cat_produtos)
        db.session.flush()
        
        # ========== PRODUTOS ==========
        produtos = [
            Produto(nome='Pomada Forte', categoria_id=1, valor_compra=8.00, valor_venda=25.00, estoque=50, nivel_estoque=10),
            Produto(nome='Creme Barbear', categoria_id=2, valor_compra=5.00, valor_venda=20.00, estoque=30, nivel_estoque=10),
            Produto(nome='Lâminas Gillette', categoria_id=3, valor_compra=3.00, valor_venda=15.00, estoque=20, nivel_estoque=5),
            Produto(nome='Gel Fixação', categoria_id=5, valor_compra=4.00, valor_venda=18.00, estoque=15, nivel_estoque=5),
            Produto(nome='Água de Colônia', categoria_id=4, valor_compra=10.00, valor_venda=40.00, estoque=5, nivel_estoque=3),
        ]
        db.session.add_all(produtos)
        db.session.flush()
        
        # ========== HORÁRIOS ==========
        horas = ['09:00', '09:30', '10:00', '10:30', '11:00', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00']
        # Cria horarios de atendimento para cada barbeiro.
        for barbeiro in [barbeiro1, barbeiro2]:
            for hora_str in horas:
                hora = datetime.strptime(hora_str, '%H:%M').time()
                horario = Horario(horario=hora, funcionario_id=barbeiro.id)
                db.session.add(horario)
        
        # ========== DIAS DE TRABALHO ==========
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        # Define dias de trabalho dos barbeiros.
        for barbeiro in [barbeiro1, barbeiro2]:
            for dia in dias_semana:
                dia_obj = Dia(dia=dia, funcionario_id=barbeiro.id)
                db.session.add(dia_obj)
        
        # ========== CONFIGURAÇÕES ==========
        config = Config(
            id=1,
            nome='Barbearia Teste',
            email='barbearia@teste.com',
            telefone_whatsapp='(11) 9999-9999',
            telefone_fixo='(11) 3333-3333',
            endereco='Rua Principal, 123, São Paulo - SP',
            instagram='@barbearia_teste',
            tipo_comissao='Porcentagem',
            quantidade_cartoes=10,
            texto_rodape='Barbearia de qualidade desde 2010'
        )
        db.session.add(config)
        db.session.flush()
        
        # ========== COMENTÁRIOS ==========
        comentarios = [
            Comentario(nome='João Silva', texto='Ótimo atendimento! Voltarei com certeza!', ativo='Sim'),
            Comentario(nome='Roberto Costa', texto='Profissionais muito bons, ambiente agradável!', ativo='Sim'),
            Comentario(nome='Lucas Oliveira', texto='Recomendo para todos meus amigos!', ativo='Sim'),
        ]
        db.session.add_all(comentarios)
        
        # ========== TEXTOS ÍNDICE ==========
        textos = [
            TextoIndex(titulo='Bem-vindo', descricao='Bem-vindo à melhor barbearia da cidade!', ordem=1, ativo='Sim'),
            TextoIndex(titulo='Qualidade', descricao='Profissionais experientes prontos para você', ordem=2, ativo='Sim'),
        ]
        db.session.add_all(textos)
        
        # ========== CONTAS ==========
        receber = ContaReceber(
            descricao='Corte de cabelo - Cliente: Fernando',
            valor=35.00,
            tipo='Serviço',
            data_venc=date.today() + timedelta(days=5),
            pago='Não'
        )
        db.session.add(receber)
        
        # ========== AGENDAMENTOS ==========
        agendamentos = [
            Agendamento(
                funcionario_id=barbeiro1.id,
                cliente_id=clientes[0].id,
                servico_id=servicos[0].id,
                usuario_id=admin.id,
                data=date.today() + timedelta(days=1),
                hora=time(14, 0),
                status='Agendado',
                data_lanc=date.today()
            ),
            Agendamento(
                funcionario_id=barbeiro2.id,
                cliente_id=clientes[1].id,
                servico_id=servicos[3].id,
                usuario_id=admin.id,
                data=date.today() + timedelta(days=2),
                hora=time(15, 30),
                status='Agendado',
                data_lanc=date.today()
            ),
        ]
        db.session.add_all(agendamentos)
        
        # ========== SALVAR ==========
        # Salva todos os dados de teste em uma unica transacao.
        db.session.commit()
        print("✅ Banco de dados inicializado com sucesso!")
        print("\n📊 Dados criados:")
        print(f"  - Usuários: {Usuario.query.count()}")
        print(f"  - Clientes: {Cliente.query.count()}")
        print(f"  - Serviços: {Servico.query.count()}")
        print(f"  - Produtos: {Produto.query.count()}")
        print(f"  - Agendamentos: {Agendamento.query.count()}")
        print(f"  - Acessos: {Acesso.query.count()}")
        
        print("\n🔐 Usuário de teste:")
        print("  Email: admin@admin")
        print("  Senha: 123")
        print("\n🚀 Para iniciar a aplicação, execute: python run.py")

if __name__ == '__main__':
    init_database()
