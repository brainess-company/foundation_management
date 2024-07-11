from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """
    cria um registro na tabela foundation obra vinvulado com a sale order
    cria varios registros em foundation obra service, um pra cada serviço

    """
    _inherit = 'sale.order'
    nome_obra = fields.Char("Nome da Obra", required=False)
    cei = fields.Char("CEI", required=False)


    # Exemplo de uso destes métodos em create e write seria adaptado aqui

    def _create_foundation_obra_and_services(self):
        """
        cria uma nova obra em foundation_obra com o nome na sale order
        """
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
                # Verifica se a linha não está em branco
                if line.product_id:
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
        order = super().create(vals)
        order._create_foundation_obra_and_services()
        return order

    def write(self, vals):
        res = super().write(vals)
        for order in self:
            if 'state' in vals and vals.get('state') == 'sale':
                order._create_foundation_obra_and_services()
        return res
