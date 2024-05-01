"""
HERDA MODELO DE CONTA ANALITICA PARA CRIAR
"""
from odoo import models, fields


class AccountAnalyticAccount(models.Model):
    """HERDA CONTA ANALITICA PARA CRIAR"""
    _inherit = 'account.analytic.account'

    foundation_maquina_registro_id = fields.Many2one('foundation.maquina.registro',
                                                     string="Registro de Máquina")
    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", index=True)
