from odoo import models, api, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    nome_obra = fields.Char("OBRA")


    def _create_foundation_obra_and_services(self):
        FoundationObra = self.env['foundation.obra']
        FoundationObraService = self.env['foundation.obra.service']
        # Assuming this is how you access the machine model

        for order in self:
            # Ensure there is an 'obra' for the sale order
            obra = FoundationObra.search([('sale_order_id', '=', order.id)], limit=1)
            if not obra:
                obra = FoundationObra.create({
                    'sale_order_id': order.id
                })

            # Create a service for each unique product template
            template_lines = {}
            for line in order.order_line:
                template = line.product_id.product_tmpl_id
                if template not in template_lines:
                    template_lines[template] = line

            for template, line in template_lines.items():
                if not FoundationObraService.search([
                    ('variante_id', '=', line.product_id.id),
                    ('obra_id', '=', obra.id)
                ], limit=1):
                    FoundationObraService.create({
                        'variante_id': line.product_id.id,
                        'obra_id': obra.id
                    })

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if vals.get('state') == 'sale':  # Check if the order is confirmed upon creation
            order._create_foundation_obra_and_services()
        return order

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'state' in vals and vals.get('state') == 'sale':  # Only trigger on state change to 'sale'
            self.filtered(lambda x: x.state == 'sale')._create_foundation_obra_and_services()
        return res
