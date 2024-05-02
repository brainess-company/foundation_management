from odoo import models, fields, api

class StockMoveWizard(models.TransientModel):
    _name = 'stock.move.wizard'
    _description = 'Assistente para criar movimento de estoque'

    product_id = fields.Many2one('product.product', string="Produto", required=True)
    product_qty = fields.Float(string="Quantidade", default=1.0)
    maquina_registro_id = fields.Many2one('foundation.maquina.registro', string="Dados de Origem", required=True)

    def action_create_stock_move(self):
        self.ensure_one()
        stock_move = self.env['stock.move'].create({
            'name': 'Movimento via Árvore: {}'.format(self.product_id.display_name),
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': self.product_qty,
            'location_id': self.maquina_registro_id.specific_stock_location_id.id,
            'location_dest_id': self.maquina_registro_id.specific_stock_output_id.id,
            'analytic_account_id': self.maquina_registro_id.analytic_account_id.id,
        })
        stock_move._action_confirm()
        stock_move._action_assign()
        stock_move._action_done()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Movimento de Estoque',
            'res_model': 'stock.move',
            'view_mode': 'form',
            'res_id': stock_move.id,
            'target': 'new',
        }
