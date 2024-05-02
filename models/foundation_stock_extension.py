from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Conta Analítica',
        help='Selecione a conta analítica para esta movimentação de estoque.'
    )
