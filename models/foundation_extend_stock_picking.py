from odoo import models, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        picking = super().create(vals)

        # Verifica se a transferência é para um local de saída do tipo 'production'
        output_location = picking.location_dest_id
        if output_location and output_location.usage == 'production':
            picking.action_confirm()
            picking.action_assign()
            for move in picking.move_lines:
                move.quantity_done = move.product_uom_qty
            picking.button_validate()

        return picking