from odoo import models, fields, api
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def action_use_product(self):
        self.ensure_one()
        location_id = self._context.get('default_location_id')
        location_dest_id = self._context.get('default_location_dest_id')
        analytic_account_id = self._context.get('default_analytic_account_id')

        if not location_dest_id:
            raise UserError("Local de destino não configurado para este produto.")

        stock_move = self.env['stock.move'].create({
            'name': 'Use Product',
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': self.quantity,
            'analytic_account_id': analytic_account_id
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Transfer',
            'res_model': 'stock.move',
            'view_mode': 'form',
            'res_id': stock_move.id,
            'target': 'new',
        }
