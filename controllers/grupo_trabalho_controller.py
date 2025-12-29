from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models.grupo_trabalho import GrupoTrabalho
from models.responsavel import Responsavel
from models.loja import Loja
from database import db
from sqlalchemy.orm import joinedload

bp = Blueprint('grupo_trabalho', __name__, url_prefix='/grupos_trabalho')

# Criar um novo grupo de trabalho
@bp.route('/', methods=['POST'])
def create_grupo_trabalho():
    nome_grupo = request.form.get('nome_grupo')
    id_responsavel = request.form.get('id_responsavel', type=int)

    # Verificar se o responsável existe
    responsavel = Responsavel.query.get(id_responsavel)
    if not responsavel:
        return render_template('grupo_trabalho/create.html', responsaveis=Responsavel.query.all(), error="Responsável não encontrado.")

    grupo = GrupoTrabalho(nome_grupo=nome_grupo, id_responsavel=id_responsavel)
    db.session.add(grupo)
    db.session.commit()

    return redirect(url_for('grupo_trabalho.view_grupos_trabalho'))

# Listar todos os grupos de trabalho (JSON)
@bp.route('/api', methods=['GET'])
def get_grupos_trabalho():
    grupos = GrupoTrabalho.query.options(joinedload(GrupoTrabalho.lojas)).all()
    return jsonify([grupo.to_dict() for grupo in grupos]), 200

# Tela para listar todos os grupos de trabalho
@bp.route('/view', methods=['GET'])
def view_grupos_trabalho():
    grupos = GrupoTrabalho.query.options(joinedload(GrupoTrabalho.lojas)).all()
    grupos_formatados = [grupo.to_dict() for grupo in grupos]
    return render_template('grupo_trabalho/index.html', grupos_trabalho=grupos_formatados)

# Tela para criar um novo grupo de trabalho
@bp.route('/novo', methods=['GET'])
def novo_grupo_trabalho():
    responsaveis = Responsavel.query.all()
    return render_template('grupo_trabalho/create.html', responsaveis=responsaveis)

# Obter um grupo de trabalho por ID (JSON)
@bp.route('/<int:id_grupo_trabalho>', methods=['GET'])
def get_grupo_trabalho(id_grupo_trabalho):
    grupo = GrupoTrabalho.query.options(joinedload(GrupoTrabalho.lojas)).get(id_grupo_trabalho)
    if not grupo:
        return jsonify({'error': 'Grupo de trabalho não encontrado.'}), 404

    return jsonify(grupo.to_dict()), 200

# Atualizar um grupo de trabalho
@bp.route('/<int:id_grupo_trabalho>', methods=['PUT'])
def update_grupo_trabalho(id_grupo_trabalho):
    grupo = GrupoTrabalho.query.get(id_grupo_trabalho)
    if not grupo:
        return jsonify({'error': 'Grupo de trabalho não encontrado.'}), 404

    data = request.get_json()
    grupo.nome_grupo = data.get('nome_grupo', grupo.nome_grupo)
    id_responsavel = data.get('id_responsavel', grupo.id_responsavel)

    # Verificar se o responsável existe
    if id_responsavel != grupo.id_responsavel:
        responsavel = Responsavel.query.get(id_responsavel)
        if not responsavel:
            return jsonify({'error': 'Responsável não encontrado.'}), 404
        grupo.id_responsavel = id_responsavel

    db.session.commit()
    return jsonify(grupo.to_dict()), 200

# Deletar um grupo de trabalho
@bp.route('/<int:id_grupo_trabalho>', methods=['DELETE'])
def delete_grupo_trabalho(id_grupo_trabalho):
    grupo = GrupoTrabalho.query.get(id_grupo_trabalho)
    if not grupo:
        return jsonify({'error': 'Grupo de trabalho não encontrado.'}), 404

    db.session.delete(grupo)
    db.session.commit()
    return jsonify({'message': 'Grupo de trabalho deletado com sucesso.'}), 200