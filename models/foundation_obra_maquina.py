"""
    OBRAS RELACIONADAS COM ORDEM DE VENDAS

    """
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)  # Configuração do logger


class FoundationObraMaquina(models.Model):
    """
    OBRAS RELACIONADAS COM ORDEM DE VENDAS

    """
    _name = 'foundation.obra.maquina'
    _description = 'Informações sobre a obra e maquina'
    _rec_name = 'nome_obra'

    # RELACIONA ESSA TABELA FOUNDATION OBRA COM  UMA SALE ORDER
    sale_order_id = fields.Many2one('sale.order',
                                    string="Ordem de Venda", required=True)

    maquina_id = fields.Many2one('foundation.maquina',
                                 string="Máquina Associada",
                                 readonly=True, store=True)

    nome_obra = fields.Char(related='sale_order_id.nome_obra',
                            store=True, readonly=True, string="Nome da Obra")



