from odoo import models, fields

class FoundationObra(models.Model):
    _name = 'foundation.obra'
    _description = 'Informações sobre a obra'

    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", required=True)
    nome_obra = fields.Char("Nome da Obra", required=True)
    endereco = fields.Char("Endereço")