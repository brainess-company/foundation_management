from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_engineering_service = fields.Boolean(string="Serviço de Engenharia", default=False)

