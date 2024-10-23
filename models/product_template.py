from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_engineering_service = fields.Boolean(string="Serviço de Engenharia", default=False)

    # Override write or create method if necessary to ensure the checkbox only appears for services
    def write(self, vals):
        if 'is_engineering_service' in vals and self.type != 'service':
            raise ValidationError("Este campo só pode ser marcado para produtos do tipo Serviço.")
        return super(ProductTemplate, self).write(vals)

    def create(self, vals):
        if 'is_engineering_service' in vals and vals.get('type') != 'service':
            raise ValidationError("Este campo só pode ser marcado para produtos do tipo Serviço.")
        return super(ProductTemplate, self).create(vals)
