
    # FOUNDATION MAQUINA REGISTROS
'foundation.maquina.registro'sale_order_id
'foundation.maquina.registro'nome_obra
'foundation.maquina.registro'maquina_id
'foundation.maquina.registro'service_id


    'foundation.maquina.registro'data_registro
    'foundation.maquina.registro'nome_servico
    'foundation.maquina.registro'obra_id
    'foundation.maquina.registro'variante_id
    'foundation.maquina.registro'service_template_id
    'foundation.maquina.registro'operador_id
    'foundation.maquina.registro'estacas_ids



tentativa 1
    contexto
    defalt_(tebela_futura): tabela atual
    defalt_ = foundation.relatorio : foundation_maquina_registro

<record id="view_foundation_maquina_registro_tree" model="ir.ui.view">
            context="{
                                'default_foundation_maquina_registro_id': id,
                                'default_sale_order_id': sale_order_id,
                                'default_nome_obra': nome_obra,
                                'default_service_template_id': service_id,
                                'default_endereco': endereco
                            }"/>

                <


# FONDATION RELATORIOS
'foundation.relatorios'service_id

    'foundation.relatorios'data
    'foundation.relatorios'estacas_ids
    'foundation.relatorios'assinatura
    'foundation.relatorios'state
    'foundation.relatorios'nome_servico
    'foundation.relatorios'maquina_id
    'foundation.relatorios'nome_obra
    'foundation.relatorios'endereco_obra
    'foundation.relatorios'sale_order_id


    'foundation.relatorios'service_template_id
    'foundation.relatorios'foundation_maquina_registro_id



    # FOUNDATION ESTACAS
'foundation.estacas'nome_estaca
'foundation.estacas'profundidade
'foundation.estacas'data
'foundation.estacas'observacao
'foundation.estacas'service_template_id

    'foundation.estacas'foundation_maquina_registro_id
    'foundation.estacas'nome_obra
    'foundation.estacas'relatorio_id
    'foundation.estacas'foundation_obra_service_id
    'foundation.estacas'sale_order_id
    'foundation.estacas'sale_order_line_id
    'foundation.estacas'variante_id