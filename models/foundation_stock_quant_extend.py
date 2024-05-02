from odoo import models, fields, api
from odoo.exceptions import UserError

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def prepare_action_use_product(self):
        self.ensure_one()
        # Busca por uma localização de produção;
        # Deve ser um estoque de produção aninhado com o stock_location
        location_dest_id = self.env['stock.location'].search([('usage', '=', 'production')],
                                                             limit=1)
        # Busca por uma conta analítica; ajuste conforme necessário.
        analytic_account = self.env['account.analytic.account'].search([],
                                                                       limit=1)  # Busca mais genérica.

        if not location_dest_id:
            raise UserError("Localização de destino para produção não encontrada.")
        if not analytic_account:
            raise UserError("Conta analítica não encontrada.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Transfer',
            'res_model': 'stock.move',
            'view_mode': 'form',
            'context': {
                'default_product_id': self.product_id.id,
                'default_location_id': self.location_id.id,
                'default_location_dest_id': location_dest_id.id,
                'default_product_uom_qty': 1,
                'default_analytic_account_id': analytic_account.id
            },
            'target': 'new'
        }

