from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_foundation_obra_and_services(self):
        FoundationObra = self.env['foundation.obra']
        FoundationObraService = self.env['foundation.obra.service']

        for order in self:
            # Cria uma obra para a ordem de venda
            obra = FoundationObra.create({
                'sale_order_id': order.id
            })

            # Dicionário para armazenar a primeira linha de cada template de produto
            template_lines = {}
            for line in order.order_line:
                template = line.product_id.product_tmpl_id
                if template not in template_lines:
                    template_lines[template] = line

            # Cria um serviço de obra para cada template de produto único
            for template, line in template_lines.items():
                FoundationObraService.create({
                    'service_id': line.product_id.id,  # Usar o ID do produto, não do template
                    'obra_id': obra.id  # Associa o serviço à obra criada
                })

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if order.state == 'sale':
            order._create_foundation_obra_and_services()
        return order

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'state' in vals and vals['state'] == 'sale':
            self.filtered(lambda x: x.state == 'sale')._create_foundation_obra_and_services()
        return res
