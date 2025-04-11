from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    qtdd_itens = fields.Integer(string="Quantidade de Itens", help="Quantidade de itens agrupados nesta linha")