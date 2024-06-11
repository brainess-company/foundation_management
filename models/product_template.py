from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    criar_conta_analitica = fields.Boolean(string='Criar Conta Analítica')
