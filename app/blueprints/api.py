"""
Blueprint API REST - Barbearia PRO
"""
from flask import Blueprint, jsonify, request
from app.models import db, Usuario, Servico, Cliente, Agendamento, Horario
from datetime import datetime, time
from sqlalchemy import and_

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/servicos', methods=['GET'])
def get_servicos():
    """GET lista de serviços"""
    try:
        # Retorna somente servicos liberados ao publico.
        servicos = Servico.query.filter_by(ativo='Sim').all()
        return jsonify({
            'status': 'success',
            'data': [{
                'id': s.id,
                'nome': s.nome,
                'valor': s.valor,
                'categoria': s.categoria.nome if s.categoria else None,
                'dias_retorno': s.dias_retorno
            } for s in servicos]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/funcionarios', methods=['GET'])
def get_funcionarios():
    """GET lista de funcionários com atendimento"""
    try:
        # Lista apenas profissionais ativos que atendem clientes.
        funcionarios = Usuario.query.filter_by(atendimento='Sim', ativo='Sim').all()
        return jsonify({
            'status': 'success',
            'data': [{
                'id': f.id,
                'nome': f.nome,
                'foto': f.foto,
                'telefone': f.telefone
            } for f in funcionarios]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/horarios/<int:funcionario_id>/<data_str>', methods=['GET'])
def get_horarios(funcionario_id, data_str):
    """GET horários disponíveis de um funcionário em uma data"""
    try:
        # Converte a data recebida na URL para objeto date.
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        
        # Pegar todos os horários do funcionário
        horarios = Horario.query.filter_by(funcionario_id=funcionario_id).all()
        
        # Se não há horários cadastrados para este funcionário, usar horários padrão
        if not horarios:
            horarios_disponiveis = [
                '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
                '11:00', '11:30', '14:00', '14:30', '15:00', '15:30',
                '16:00', '16:30', '17:00', '17:30', '18:00'
            ]
        else:
            # Pegar agendamentos do dia para filtrar ocupados
            # Remove da lista os horarios ja ocupados no dia.
            agendamentos_dia = Agendamento.query.filter(
                and_(
                    Agendamento.data == data,
                    Agendamento.funcionario_id == funcionario_id
                )
            ).all()
            
            def parse_hora(h):
                """Converte horario (obj time ou string) para string HH:MM"""
                if hasattr(h, 'strftime'):
                    return h.strftime('%H:%M')
                # SQLite retorna string como '09:00:00.000000' ou '09:00:00'
                return str(h)[:5]

            horas_ocupadas = {parse_hora(a.hora) for a in agendamentos_dia}
            horarios_disponiveis = []
            
            for h in horarios:
                hora_str = parse_hora(h.horario)
                if hora_str not in horas_ocupadas:
                    horarios_disponiveis.append(hora_str)
        
        return jsonify({
            'status': 'success',
            'data': sorted(horarios_disponiveis)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/agendamentos', methods=['POST'])
def criar_agendamento():
    """POST criar agendamento"""
    try:
        # Dados chegam em JSON pelo formulario publico/agendamento.
        dados = request.get_json()
        
        # Validar dados
        # Garante que o minimo necessario foi enviado.
        campos_obrigatorios = ['nome', 'telefone', 'funcionario_id', 'servico_id', 'data', 'hora']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({'status': 'error', 'message': f'{campo} é obrigatório'}), 400
        
        # Validar horário disponível
        # Valida data e horario antes de gravar.
        data = datetime.strptime(dados['data'], '%Y-%m-%d').date()
        hora = datetime.strptime(dados['hora'], '%H:%M').time()
        
        if data < datetime.now().date():
            return jsonify({'status': 'error', 'message': 'Não é possível agendar em datas passadas!'}), 400
        
        agendamento_existente = Agendamento.query.filter(
            and_(
                Agendamento.data == data,
                Agendamento.hora == hora,
                Agendamento.funcionario_id == dados['funcionario_id']
            )
        ).first()
        
        if agendamento_existente:
            return jsonify({'status': 'error', 'message': 'Este horário não está disponível!'}), 400
        
        # Buscar ou criar cliente
        # Reaproveita cliente pelo telefone; se nao existir, cria um novo.
        cliente = Cliente.query.filter_by(telefone=dados['telefone']).first()
        if not cliente:
            cliente = Cliente(
                nome=dados['nome'],
                telefone=dados['telefone'],
                data_cad=datetime.now().date()
            )
            db.session.add(cliente)
            db.session.flush()
        
        from markupsafe import escape
        # Limpa observacao para evitar HTML injetado.
        obs_limpa = str(escape(dados.get('obs', ''))) if dados.get('obs') else None
        
        # Criar agendamento
        # Cria o agendamento publico, sem usuario administrativo ligado.
        novo_agendamento = Agendamento(
            funcionario_id=dados['funcionario_id'],
            cliente_id=cliente.id,
            servico_id=dados['servico_id'],
            usuario_id=None,  # Agendamento público, sem usuário admin logado
            data=data,
            hora=hora,
            obs=obs_limpa,
            status='Agendado',
            data_lanc=datetime.now().date()
        )
        
        db.session.add(novo_agendamento)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Agendamento criado com sucesso!',
            'data': {
                'id': novo_agendamento.id,
                'data': novo_agendamento.data.isoformat(),
                'hora': novo_agendamento.hora.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/clientes/verificar/<telefone>', methods=['GET'])
def verificar_cliente(telefone):
    """GET verificar se cliente existe"""
    try:
        # Usado por telas que preenchem dados do cliente automaticamente.
        cliente = Cliente.query.filter_by(telefone=telefone).first()
        
        if cliente:
            return jsonify({
                'status': 'success',
                'existe': True,
                'cliente': {
                    'id': cliente.id,
                    'nome': cliente.nome,
                    'telefone': cliente.telefone
                }
            })
        else:
            return jsonify({
                'status': 'success',
                'existe': False
            })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check da API"""
    # Endpoint simples para monitorar se a API esta respondendo.
    return jsonify({
        'status': 'success',
        'message': 'API Barbearia PRO OK',
        'timestamp': datetime.now().isoformat()
    })
