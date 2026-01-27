from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models import Loja, DivisaoBandeira, GrupoTrabalho, CheckpointAtividade, Planejamento, Atividade
from database import db

from models import (
Loja,
DivisaoBandeira,
GrupoTrabalho,
Responsavel,
CheckpointAtividade,
Planejamento,
Atividade,
)

bp = Blueprint('gestao', __name__, url_prefix='/gestao')

@bp.route('/dashboard')
def dashboard():
    divisoes = DivisaoBandeira.query.order_by(DivisaoBandeira.nome_bandeira).all()
    grupos = (
        GrupoTrabalho.query
        .order_by(GrupoTrabalho.nome_grupo)
        .all()
    )

    selected_id = request.args.get('divisao_id', type=int)
    selected_group_id = request.args.get('grupo_id', type=int)

    # Lojas gerais (não filtradas)
    all_lojas = Loja.query.order_by(Loja.nome_loja).all()

    lojas_divisao = []
    selected_divisao = None

    if selected_id:
        query = Loja.query.filter_by(id_divisao_bandeira=selected_id)
        if selected_group_id:
            query = query.filter_by(id_grupo_trabalho=selected_group_id)
        lojas_divisao = query.order_by(Loja.id_loja).all()

        selected_divisao = DivisaoBandeira.query.get(selected_id)

        grupos = (
            GrupoTrabalho.query
            .join(Loja)
            .filter(Loja.id_divisao_bandeira == selected_id)
            .distinct()
            .order_by(GrupoTrabalho.nome_grupo)
            .all()
        )

    # **Filtros adicionais para cards**
    if selected_id:
        atividades_query = (
            db.session.query(Atividade)
            .join(Planejamento, Planejamento.id_atividade == Atividade.id_atividade)
            .outerjoin(GrupoTrabalho, GrupoTrabalho.id_grupo_trabalho == Planejamento.id_grupo_trabalho)
        )
        if selected_group_id:
            atividades_query = atividades_query.filter(GrupoTrabalho.id_grupo_trabalho == selected_group_id)
        atividades = atividades_query.order_by(Atividade.id_atividade.desc()).all()

        planejamentos_query = (
            Planejamento.query
            .join(GrupoTrabalho, GrupoTrabalho.id_grupo_trabalho == Planejamento.id_grupo_trabalho)
        )
        if selected_group_id:
            planejamentos_query = planejamentos_query.filter(Planejamento.id_grupo_trabalho == selected_group_id)
        planejamentos = planejamentos_query.order_by(Planejamento.data_ini.desc()).all()

        # Ajuste para filtrar checkpoints
        checkpoints_query = CheckpointAtividade.query.join(Loja, CheckpointAtividade.id_loja == Loja.id_loja)
        if selected_id:
            checkpoints_query = checkpoints_query.filter(Loja.id_divisao_bandeira == selected_id)
        if selected_group_id:
            checkpoints_query = checkpoints_query.join(Planejamento, Planejamento.id_atividade == CheckpointAtividade.id_atividade)
            checkpoints_query = checkpoints_query.filter(Planejamento.id_grupo_trabalho == selected_group_id)
        checkpoints = checkpoints_query.order_by(CheckpointAtividade.data_ini.desc()).all()
    else:
        atividades = Atividade.query.order_by(Atividade.id_atividade.desc()).all()
        planejamentos = Planejamento.query.order_by(Planejamento.data_ini.desc()).all()
        checkpoints = CheckpointAtividade.query.order_by(CheckpointAtividade.data_ini.desc()).all()

    grupo_por_loja = (
        db.session.query(
            Loja.nome_loja.label('nome_loja'),
            Loja.qtd_sku.label('qtd_sku'),
            Loja.qtd_pessoas.label('qtd_pessoas'),
            GrupoTrabalho.nome_grupo.label('nome_grupo'),
            Responsavel.nome.label('responsavel_nome'),
            Responsavel.contato.label('responsavel_contato'),
        )
        .join(GrupoTrabalho, GrupoTrabalho.id_grupo_trabalho == Loja.id_grupo_trabalho)
        .outerjoin(Responsavel, Responsavel.id_responsavel == GrupoTrabalho.id_responsavel)
    )

    if selected_id:
        grupo_por_loja = grupo_por_loja.filter(
            Loja.id_divisao_bandeira == selected_id
        )

    if selected_group_id:
        grupo_por_loja = grupo_por_loja.filter(
            GrupoTrabalho.id_grupo_trabalho == selected_group_id
        )

    grupo_por_loja = grupo_por_loja.order_by(Loja.nome_loja).all()

    # Adicionando o nome do responsável ao grupo de trabalho
    grupos_com_responsavel = [
        {
            'id_grupo_trabalho': grupo.id_grupo_trabalho,
            'nome_grupo': grupo.nome_grupo,
            'responsavel_nome': grupo.responsavel.nome if grupo.responsavel else 'Não definido'
        }
        for grupo in grupos
    ]



    atividades_planejamento_query = (
        db.session.query(
            GrupoTrabalho.nome_grupo.label('nome_grupo'),
            Atividade.titulo.label('titulo'),
            Atividade.descricao.label('descricao'),
            Planejamento.data_ini.label('data_ini'),
            Planejamento.data_fim.label('data_fim'),
        )
        .join(
            Planejamento,
            Planejamento.id_atividade == Atividade.id_atividade
        )
        .outerjoin(
            GrupoTrabalho,
            GrupoTrabalho.id_grupo_trabalho == Planejamento.id_grupo_trabalho
        )
        .filter((Planejamento.id_grupo_trabalho == selected_group_id))
    )

    if selected_group_id:
        atividades_planejamento_query = atividades_planejamento_query.filter(
            Planejamento.id_grupo_trabalho == selected_group_id
        )

    atividades_planejamento = atividades_planejamento_query.order_by(
        Planejamento.data_ini.desc()
    ).all()


    # Acompanhamento Planejado x Executado
    acompanhamento_query = (
        db.session.query(
            GrupoTrabalho.nome_grupo.label("nome_grupo"),

            Planejamento.data_ini.label("plan_data_ini"),
            Planejamento.data_fim.label("plan_data_fim"),
            Planejamento.titulo.label("titulo"),

            # Previsto (Planejado)
            (Planejamento.data_fim - Planejamento.data_ini).label("previsto"),

            Loja.nome_loja.label("nome_loja"),

            CheckpointAtividade.nome_checkpoint.label("nome_checkpoint"),
            CheckpointAtividade.data_ini.label("ck_data_ini"),
            CheckpointAtividade.data_fim.label("ck_data_fim"),

            # Executado
            (CheckpointAtividade.data_fim - CheckpointAtividade.data_ini).label("executado"),
        )
        .select_from(CheckpointAtividade)
        .join(Atividade, Atividade.id_atividade == CheckpointAtividade.id_atividade)
        .join(Loja, Loja.id_loja == CheckpointAtividade.id_loja)
        .outerjoin(
            Planejamento,
            Planejamento.id_planejamento == CheckpointAtividade.id_planejamento
        )
        .outerjoin(
            GrupoTrabalho,
            GrupoTrabalho.id_grupo_trabalho == Planejamento.id_grupo_trabalho
        )
    )

    # 🔹 Filtro por divisão
    if selected_id:
        acompanhamento_query = acompanhamento_query.filter(
            Loja.id_divisao_bandeira == selected_id
        )

    # 🔹 Filtro por grupo
    if selected_group_id:
        acompanhamento_query = acompanhamento_query.filter(
            GrupoTrabalho.id_grupo_trabalho == selected_group_id
        )

    acompanhamento_planejamento = (
        acompanhamento_query
        .order_by(
            GrupoTrabalho.nome_grupo,
            Loja.nome_loja,
            Planejamento.data_ini.desc()
        )
        .all()
    )


    return render_template(
        'dashboard.html',
        divisoes=divisoes,
        grupos=grupos_com_responsavel,  # Enviando os grupos com o nome do responsável
        grupos_loja=grupo_por_loja,
        selected_id=selected_id,
        selected_group_id=selected_group_id,
        selected_divisao=selected_divisao,
        all_lojas=all_lojas,
        lojas_divisao=lojas_divisao,
        atividades=atividades,
        planejamentos=planejamentos,
        checkpoints=checkpoints,
        atividades_planejamento=atividades_planejamento,
        acompanhamento_planejamento=acompanhamento_planejamento
    )