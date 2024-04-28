"""extende o sale order para criar automaticamente uma obra"""
from odoo import models, api, fields


class SaleOrder(models.Model):
    """extende o sale order para criar automaticamente uma obra"""
    _inherit = 'sale.order'
    nome_obra = fields.Char("Nome da Obra", required=True)

    def _create_foundation_obra_and_services(self):
        """para cada serviço na sale order cria um registro aqui"""
        foundation_obra = self.env['foundation.obra']
        foundation_obra_service = self.env['foundation.obra.service']
        # Assuming this is how you access the machine model

        for order in self:
            # Ensure there is an 'obra' for the sale order
            obra = foundation_obra.search([('sale_order_id', '=', order.id)], limit=1)
            if not obra:
                obra = foundation_obra.create({
                    'sale_order_id': order.id
                })

            # Create a service for each unique product template
            template_lines = {}
            for line in order.order_line:
                template = line.product_id.product_tmpl_id
                if template not in template_lines:
                    template_lines[template] = line

            for template, line in template_lines.items():
                if not foundation_obra_service.search([
                    ('variante_id', '=', line.product_id.id),
                    ('obra_id', '=', obra.id)
                ], limit=1):
                    foundation_obra_service.create({
                        'variante_id': line.product_id.id,
                        'obra_id': obra.id
                    })

    @api.model
    def create(self, vals):
        """cria p registro em foundation obra service"""
        order = super().create(vals)
        if vals.get('state') == 'sale':  # Check if the order is confirmed upon creation
            order._create_foundation_obra_and_services()
        return order

    def write(self, vals):
        """Atualiza o registro quando a sale order muda de status."""
        res = super().write(vals)
        if 'state' in vals and vals.get(
                'state') == 'sale':  # Only trigger on state change to 'sale'
            self.filtered(lambda x: x.state == 'sale')._create_foundation_obra_and_services()
        return res
