from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.checkpoint_atividade import CheckpointAtividade
from models.atividade import Atividade
from models.grupo_trabalho import GrupoTrabalho
from models.planejamento import Planejamento
from models.loja import Loja  # Adicione esta linha
from database import db
from datetime import datetime
from sqlalchemy.orm import joinedload  # Certifique-se de importar joinedload

bp = Blueprint(
    'checkpoint_atividade',
    __name__,
    url_prefix='/checkpoint-atividades'
)

# =====================================================
# ROTAS WEB
# =====================================================

@bp.route('/')
def index():
    """
    Lista agrupada por Checkpoint Atividade com Planejamento e Grupo de Trabalho
    """
    registros = (
        CheckpointAtividade.query
        .join(CheckpointAtividade.atividade)
        .join(CheckpointAtividade.planejamento)
        .join(Planejamento.grupo_trabalho)
        .join(GrupoTrabalho.lojas)
        .order_by(
            CheckpointAtividade.nome_checkpoint.asc(),
            CheckpointAtividade.data_ini.desc()
        )
        .all()
    )

    return render_template(
        'checkpoint_atividade/index.html',
        registros=registros
    )


@bp.route('/create', methods=['GET', 'POST'])
def create():
    atividades = Atividade.query.order_by(Atividade.titulo).all()
    planejamentos = Planejamento.query.order_by(Planejamento.data_ini.desc()).all()
    grupos_trabalho = GrupoTrabalho.query.options(joinedload(GrupoTrabalho.lojas)).order_by(GrupoTrabalho.nome_grupo).all()

    if request.method == 'POST':
        nome_checkpoint = request.form.get('nome_checkpoint')
        id_atividade = request.form.get('id_atividade', type=int)
        id_grupo_trabalho = request.form.get('id_grupo_trabalho', type=int)
        lojas_selecionadas = request.form.getlist('lojas')  # Captura as lojas selecionadas
        id_planejamento = request.form.get('id_planejamento', type=int)
        status = request.form.get('status', 'Pendente')
        data_ini = request.form.get('data_ini')
        data_fim = request.form.get('data_fim')
        observacao = request.form.get('observacao')

        # Validação: Certifique-se de que pelo menos uma loja foi selecionada
        if not lojas_selecionadas:
            flash('Selecione pelo menos uma loja.', 'danger')
            return redirect(url_for('checkpoint_atividade.create'))

        if not nome_checkpoint or not id_atividade or not id_grupo_trabalho or not data_ini:
            flash('Título, atividade, grupo de trabalho e data inicial são obrigatórios.', 'danger')
            return redirect(url_for('checkpoint_atividade.create'))

        try:
            # Criar um registro para cada loja selecionada
            for id_loja in lojas_selecionadas:
                registro = CheckpointAtividade(
                    nome_checkpoint=nome_checkpoint,
                    id_atividade=id_atividade,
                    id_loja=int(id_loja),  # Certifique-se de converter para inteiro
                    id_planejamento=id_planejamento,
                    status=status,
                    data_ini=datetime.fromisoformat(data_ini),
                    data_fim=datetime.fromisoformat(data_fim) if data_fim else None,
                    observacao=observacao
                )
                db.session.add(registro)

            db.session.commit()
            flash('Checkpoint criado com sucesso!', 'success')
            return redirect(url_for('checkpoint_atividade.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar: {str(e)}', 'danger')

    return render_template(
        'checkpoint_atividade/create.html',
        atividades=atividades,
        planejamentos=planejamentos,
        grupos_trabalho=grupos_trabalho
    )


@bp.route('/<int:id>/edit')
def edit(id):
    registro = CheckpointAtividade.query.get_or_404(id)
    atividades = Atividade.query.order_by(Atividade.titulo).all()
    planejamentos = Planejamento.query.order_by(
    Planejamento.data_ini.desc()
    ).all()
    lojas = Loja.query.order_by(Loja.nome_loja).all()

    return render_template(
        'checkpoint_atividade/edit.html',
        registro=registro,
        atividades=atividades,
        planejamentos=planejamentos,
        lojas=lojas
    )


@bp.route('/<int:id>/update', methods=['POST'])
def update(id):
    registro = CheckpointAtividade.query.get_or_404(id)

    # Atualizar os campos do checkpoint
    registro.nome_checkpoint = request.form.get(
        'nome_checkpoint',
        registro.nome_checkpoint
    )
    registro.status = request.form.get('status', registro.status)

    data_ini = request.form.get('data_ini')
    data_fim = request.form.get('data_fim')

    registro.data_ini = (
        datetime.fromisoformat(data_ini)
        if data_ini else registro.data_ini
    )

    registro.data_fim = (
        datetime.fromisoformat(data_fim)
        if data_fim else None
    )

    registro.observacao = request.form.get('observacao')

    registro.id_planejamento = request.form.get(
        'id_planejamento', registro.id_planejamento, type=int
    )

    try:
        # Salvar alterações no checkpoint
        db.session.commit()

        # Atualizar o status do planejamento relacionado
        if registro.planejamento:
            registro.planejamento.atualizar_status()
            db.session.commit()

        flash('Registro atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar: {str(e)}', 'danger')

    return redirect(url_for('checkpoint_atividade.index'))


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    registro = CheckpointAtividade.query.get_or_404(id)

    try:
        db.session.delete(registro)
        db.session.commit()
        flash('Registro removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir: {str(e)}', 'danger')

    return redirect(url_for('checkpoint_atividade.index'))

# =====================================================
# ROTAS API
# =====================================================

@bp.route('/api', methods=['GET'])
def api_index():
    registros = CheckpointAtividade.query.all()
    return jsonify([r.to_dict() for r in registros])


@bp.route('/api', methods=['POST'])
def api_create():
    data = request.get_json()

    required = ['nome_checkpoint', 'id_atividade', 'id_planejamento', 'id_loja', 'data_ini']
    if not data or not all(k in data for k in required):
        return jsonify({'error': 'Campos obrigatórios ausentes'}), 400

    try:
        registro = CheckpointAtividade(
            nome_checkpoint=data['nome_checkpoint'],
            id_atividade=data['id_atividade'],
            id_planejamento=data['id_planejamento'],
            id_loja=data['id_loja'],
            status=data.get('status', 'Pendente'),
            data_ini=datetime.fromisoformat(data['data_ini']),
            data_fim=(
                datetime.fromisoformat(data['data_fim'])
                if data.get('data_fim') else None
            ),
            observacao=data.get('observacao')
        )

        db.session.add(registro)
        db.session.commit()

        return jsonify(registro.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
