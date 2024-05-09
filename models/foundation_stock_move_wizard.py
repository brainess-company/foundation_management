from odoo import models, fields, api
from odoo.exceptions import UserError


class StockMoveWizard(models.TransientModel):
    _name = 'stock.move.wizard'
    _description = 'Assistente para criar movimento de estoque'

    product_id = fields.Many2one(
        'product.product',
        string="Produto",
        required=True,
        domain="[('id', 'in', available_product_ids)]"
    )
    product_qty = fields.Float(string="Quantidade", default=1.0)
    maquina_registro_id = fields.Many2one('foundation.maquina.registro', string="Dados de Origem",
                                          required=True)
    available_product_ids = fields.Many2many(
        'product.product',
        compute='_compute_available_product_ids',
        store=False
    )

    @api.depends('maquina_registro_id')
    def _compute_available_product_ids(self):
        for wizard in self:
            if wizard.maquina_registro_id:
                stock_location_id = wizard.maquina_registro_id.specific_stock_location_id.id
                quants = wizard.env['stock.quant'].search(
                    [('location_id', '=', stock_location_id), ('quantity', '>', 0)])
                wizard.available_product_ids = quants.mapped('product_id')
            else:
                wizard.available_product_ids = self.env['product.product']

    def action_create_stock_move(self):
        self.ensure_one()

        # Obtém a quantidade disponível no local de origem
        stock_location_id = self.maquina_registro_id.specific_stock_location_id.id
        quant = self.env['stock.quant'].search(
            [('location_id', '=', stock_location_id), ('product_id', '=', self.product_id.id)],
            limit=1)
        available_qty = quant.quantity if quant else 0.0

        if self.product_qty > available_qty:
            raise UserError(
                f"Quantidade solicitada ({self.product_qty}) excede a quantidade disponível ({available_qty}) para o produto '{self.product_id.display_name}'.")

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
        stock_move.quantity_done = self.product_qty
        stock_move._action_done()

        return {
            'type': 'ir.actions.act_window_close',
            'name': 'Movimento de Estoque',
            'res_model': 'stock.move',
            'view_mode': 'form',
            'res_id': stock_move.id,
            'target': 'new',
        }
