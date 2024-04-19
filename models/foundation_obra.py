from odoo import models, fields, api

class FoundationObra(models.Model):
    _name = 'foundation.obra'
    _description = 'Informações sobre a obra'

    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", required=True)
    nome_obra = fields.Char("Nome da Obra")
    endereco = fields.Char("Endereço")
    cliente_id = fields.Many2one('res.partner', string="Cliente", related='sale_order_id.partner_id', readonly=True,
                                 store=True)
    valor_total = fields.Monetary("Valor Total", related='sale_order_id.amount_total', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', related='sale_order_id.currency_id', readonly=True)

