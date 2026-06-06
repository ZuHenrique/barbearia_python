#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Aplicação Barbearia PRO - Entrada Principal
"""
import os
from app import create_app, db
from app.models import (
    Usuario, Cliente, Fornecedor, Cargo, Servico, CategoriaServico,
    Agendamento, Dia, Horario, ServicoUsuario, Produto, CatagoriaProduto,
    Entrada, Saida, ContaReceber, ContaPagar, Venda, Compra, Acesso,
    GrupoAcesso, UsuarioPermissao, Config, Comentario, TextoIndex
)

# Criar aplicação
# Cria a aplicacao usando o ambiente definido em FLASK_ENV.
app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Contexto do shell Flask"""
    return {
        'db': db,
        'Usuario': Usuario,
        'Cliente': Cliente,
        'Fornecedor': Fornecedor,
        'Cargo': Cargo,
        'Servico': Servico,
        'CategoriaServico': CategoriaServico,
        'Agendamento': Agendamento,
        'Dia': Dia,
        'Horario': Horario,
        'ServicoUsuario': ServicoUsuario,
        'Produto': Produto,
        'CatagoriaProduto': CatagoriaProduto,
        'Entrada': Entrada,
        'Saida': Saida,
        'ContaReceber': ContaReceber,
        'ContaPagar': ContaPagar,
        'Venda': Venda,
        'Compra': Compra,
        'Acesso': Acesso,
        'GrupoAcesso': GrupoAcesso,
        'UsuarioPermissao': UsuarioPermissao,
        'Config': Config,
        'Comentario': Comentario,
        'TextoIndex': TextoIndex
    }

if __name__ == '__main__':
    # Sobe o servidor local na porta padrao do projeto.
    app.run(debug=True, host='0.0.0.0', port=3000)
