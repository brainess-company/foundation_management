from odoo import models, fields


class FoundationObraService(models.Model):
    _name = 'foundation.obra.service'
    _description = 'Serviços em uma obra'

    service_id = fields.Many2one('product.product', string="Serviço", domain=[('sale_ok', '=', True)])
    foundation_maquina_id = fields.Many2one('foundation.maquina', string="Máquina")
