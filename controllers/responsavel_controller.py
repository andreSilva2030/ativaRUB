from flask import Blueprint, request, jsonify, render_template, redirect
from models.responsavel import Responsavel
from models.grupo_trabalho import GrupoTrabalho
from database import db

bp = Blueprint('responsavel', __name__, url_prefix='/responsaveis')

# Criar um novo responsável
@bp.route('/', methods=['POST'])
def create_responsavel():
    nome = request.form.get('nome')
    contato = request.form.get('contato')

    if not nome:
        return jsonify({'error': 'O campo "nome" é obrigatório.'}), 400

    responsavel = Responsavel(nome=nome, contato=contato)
    db.session.add(responsavel)
    db.session.commit()

    return redirect('/responsaveis/view')

# Rota para renderizar o template create.html
@bp.route('/novo', methods=['GET'])
def novo_responsavel():
    return render_template('responsavel/create.html')

# Listar todos os responsáveis
@bp.route('/lista', methods=['GET'])
def get_responsaveis():
    responsaveis = Responsavel.query.all()
    return jsonify([responsavel.to_dict() for responsavel in responsaveis]), 200

# Obter um responsável por ID
@bp.route('/<int:id_responsavel>', methods=['GET'])
def get_responsavel(id_responsavel):
    responsavel = Responsavel.query.get(id_responsavel)
    if not responsavel:
        return jsonify({'error': 'Responsável não encontrado.'}), 404

    return jsonify(responsavel.to_dict()), 200

# Atualizar um responsável
@bp.route('/<int:id_responsavel>', methods=['PUT'])
def update_responsavel(id_responsavel):
    responsavel = Responsavel.query.get(id_responsavel)
    if not responsavel:
        return jsonify({'error': 'Responsável não encontrado.'}), 404

    data = request.get_json()
    responsavel.nome = data.get('nome', responsavel.nome)
    responsavel.contato = data.get('contato', responsavel.contato)

    db.session.commit()
    return jsonify(responsavel.to_dict()), 200

# Deletar um responsável
@bp.route('/<int:id_responsavel>', methods=['DELETE'])
def delete_responsavel(id_responsavel):
    responsavel = Responsavel.query.get(id_responsavel)
    if not responsavel:
        return jsonify({'error': 'Responsável não encontrado.'}), 404

    db.session.delete(responsavel)
    db.session.commit()
    return jsonify({'message': 'Responsável deletado com sucesso.'}), 200

# Listar grupos de trabalho associados a um responsável
@bp.route('/<int:id_responsavel>/grupos', methods=['GET'])
def get_grupos_responsavel(id_responsavel):
    responsavel = Responsavel.query.get(id_responsavel)
    if not responsavel:
        return jsonify({'error': 'Responsável não encontrado.'}), 404

    grupos = [grupo.to_dict() for grupo in responsavel.grupos_trabalho]
    return jsonify(grupos), 200

# Rota para renderizar o template index.html
@bp.route('/view', methods=['GET'])
def view_responsaveis():
    responsaveis = Responsavel.query.all()
    return render_template('responsavel/index.html', responsaveis=responsaveis)