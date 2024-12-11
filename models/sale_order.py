from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    """
    Cria um registro na tabela foundation obra vinculado com a sale order
    Cria vários registros em foundation obra service, um para cada serviço
    """
    _inherit = 'sale.order'

    nome_obra = fields.Char("Nome da Obra", required=False)
    cei = fields.Char("CEI", required=False)
    cnpj_gfip = fields.Char("CNPJ GFIP", required=False)

    def _create_foundation_obra_and_services(self):
        """
        Cria uma nova obra em foundation_obra com o nome na sale order
        """
        foundation_obra = self.env['foundation.obra']
        foundation_obra_service = self.env['foundation.obra.service']

        for order in self:
            # Verifica se já existe uma obra associada a esta ordem
            obra = foundation_obra.search([('sale_order_id', '=', order.id)], limit=1)
            if not obra:
                obra = foundation_obra.create({
                    'sale_order_id': order.id
                })

            # Cria um serviço para cada template de produto único
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

    def action_confirm(self):
        """
        Sobrescreve o método de confirmação para disparar a criação de obra e serviços
        """
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order._create_foundation_obra_and_services()
        return res
