from odoo import models, fields, api

class FoundationObra(models.Model):
    _name = 'foundation.obra'
    _description = 'Informações sobre a obra'

    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", required=True)
    nome_obra = fields.Char("Nome da Obra")
    endereco = fields.Char("Endereço")

