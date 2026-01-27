from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models.grupo_trabalho import GrupoTrabalho
from models.responsavel import Responsavel
from models.loja import Loja
from database import db
from sqlalchemy.orm import joinedload

bp = Blueprint('grupo_trabalho', __name__, url_prefix='/grupos_trabalho')

# Criar um novo grupo de trabalho
@bp.route('/', methods=['GET', 'POST'])
def index():
    # Carrega os grupos com as lojas já carregadas
    grupos = GrupoTrabalho.query.options(joinedload(GrupoTrabalho.lojas)).all()
    # Converte cada objeto em dicionário (inclui lojas_info, total_lojas, etc.)
    grupos_dict = [grupo.to_dict() for grupo in grupos]
    responsaveis = Responsavel.query.all()
    return render_template('grupo_trabalho/index.html',
                           grupos_trabalho=grupos_dict,
                           responsaveis=responsaveis)

# Listar todos os grupos de trabalho (JSON)
@bp.route('/api', methods=['GET'])
def get_grupos_trabalho():
    grupos = GrupoTrabalho.query.options(joinedload(GrupoTrabalho.lojas)).all()
    return jsonify([grupo.to_dict() for grupo in grupos]), 200

# Tela para listar todos os grupos de trabalho
@bp.route('/view', methods=['GET'])
def view_grupos_trabalho():
    grupos = GrupoTrabalho.query.options(joinedload(GrupoTrabalho.lojas)).all()
    grupos_dict = [grupo.to_dict() for grupo in grupos]
    return render_template('grupo_trabalho/index.html',
                           grupos_trabalho=grupos_dict)

# Tela para criar um novo grupo de trabalho
@bp.route('/novo', methods=['GET', 'POST'])
def novo_grupo_trabalho():
    if request.method == 'POST':
        # Process form submission
        nome = request.form.get('nome_grupo')
        id_responsavel = request.form.get('id_responsavel')
        if not nome or not id_responsavel:
            return jsonify({'error': 'Nome e responsável são obrigatórios.'}), 400
        # Verify responsible exists
        responsavel = Responsavel.query.get(id_responsavel)
        if not responsavel:
            return jsonify({'error': 'Responsável não encontrado.'}), 404
        # Create new group
        novo_grupo = GrupoTrabalho(nome_grupo=nome, id_responsavel=id_responsavel)
        db.session.add(novo_grupo)
        db.session.commit()
        return redirect(url_for('grupo_trabalho.index'))
    # GET request: show form
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
@bp.route('/editar/<int:id_grupo_trabalho>', methods=['PUT'])
def editar_grupo_trabalho(id_grupo_trabalho):
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
@bp.route('/<int:id_grupo_trabalho>', methods=['POST'])
def delete_grupo_trabalho(id_grupo_trabalho):
    grupo = GrupoTrabalho.query.get(id_grupo_trabalho)
    if not grupo:
        return jsonify({'error': 'Grupo de trabalho não encontrado.'}), 404

    db.session.delete(grupo)
    db.session.commit()
    return jsonify({'message': 'Grupo de trabalho deletado com sucesso.'}), 200