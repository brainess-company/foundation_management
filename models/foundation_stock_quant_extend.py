from odoo import models, fields, api

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def action_use_product(self):
        self.ensure_one()
        stock_move = self.env['stock.move'].create({
            'name': 'Use Product',
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': self.quantity,
            'analytic_account_id': self.analytic_account_id.id
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Transfer',
            'res_model': 'stock.move',
            'view_mode': 'form',
            'res_id': stock_move.id,
            'target': 'new',
        }
