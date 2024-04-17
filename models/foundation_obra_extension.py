from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_foundation_obra_and_services(self):
        FoundationObra = self.env['foundation.obra']
        FoundationObraService = self.env['foundation.obra.service']

        for order in self:
            # Verifica se já existe uma obra para a ordem de venda
            existing_obra = FoundationObra.search([('sale_order_id', '=', order.id)], limit=1)
            if not existing_obra:
                obra = FoundationObra.create({
                    'sale_order_id': order.id
                })
            else:
                obra = existing_obra

            # Dicionário para armazenar a primeira linha de cada template de produto
            template_lines = {}
            for line in order.order_line:
                template = line.product_id.product_tmpl_id
                if template not in template_lines:
                    template_lines[template] = line

            # Cria um serviço de obra para cada template de produto único, se não existir
            for template, line in template_lines.items():
                existing_service = FoundationObraService.search([
                    ('service_id', '=', line.product_id.id),
                    ('obra_id', '=', obra.id)
                ], limit=1)
                if not existing_service:
                    FoundationObraService.create({
                        'service_id': line.product_id.id,  # Usar o ID do produto, não do template
                        'obra_id': obra.id  # Associa o serviço à obra criada
                    })

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if 'state' in vals and vals['state'] == 'sale':
            order._create_foundation_obra_and_services()
        return order

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'state' in vals and vals.get('state') == 'sale':
            self.filtered(lambda x: x.state == 'sale')._create_foundation_obra_and_services()
        return res
