from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    nome_obra = fields.Char("Nome da Obra", required=True)
    specific_stock_location_id = fields.Many2one('stock.location',
                                                 string="Local de Estoque Específico",
                                                 readonly=True)

    def _ensure_central_stock_location(self):
        """Verifica e cria um estoque central se não existir."""
        StockLocation = self.env['stock.location']
        central_stock = StockLocation.search([
            ('name', '=', 'ESTOQUE CENTRAL'),
            ('company_id', '=', False),
            ('usage', '=', 'internal')
        ], limit=1)

        if central_stock:
            _logger.info("Estoque Central já existente: %s", central_stock.name)
        else:
            central_stock = StockLocation.create({
                'name': 'ESTOQUE CENTRAL',
                'usage': 'internal',
                'location_id': self.env.ref('stock.stock_location_locations').id,
                # Base physical location
                'company_id': False  # No company to make it shared
            })
            _logger.info("Estoque Central criado: %s", central_stock.name)
        return central_stock

    def _create_specific_stock_location(self):
        """Cria um estoque específico para esta sale.order."""
        StockLocation = self.env['stock.location']
        stock_name = f"{self.nome_obra} - {self.name}"
        specific_stock = StockLocation.create({
            'name': stock_name,
            'usage': 'internal',
            'location_id': self._ensure_central_stock_location().id,
            'company_id': False  # Associated with the company of the sale.order
        })
        self.specific_stock_location_id = specific_stock.id
        _logger.info("Estoque específico criado para a Sale Order %s: %s", self.name, stock_name)
        return specific_stock

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
        order = super().create(vals)
        order._ensure_central_stock_location()
        order._create_specific_stock_location()
        order._create_foundation_obra_and_services()
        return order

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals and vals.get('state') == 'sale':
            self._ensure_central_stock_location()
            self._create_specific_stock_location()
            self._create_foundation_obra_and_services()
        return res
