from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_engineering_service = fields.Boolean(string="Serviço de Engenharia", default=False)

    # Override write or create method if necessary to ensure the checkbox only appears for services
    def write(self, vals):
        return super(ProductTemplate, self).write(vals)

    def create(self, vals):
        return super(ProductTemplate, self).create(vals)
