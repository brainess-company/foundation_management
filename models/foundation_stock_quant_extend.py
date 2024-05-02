from odoo import models, fields, api
from odoo.exceptions import UserError

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # Campos calculados que pegam valores do contexto
    context_specific_stock_location_id = fields.Many2one(
        'stock.location',
        string="Localização Específica de Estoque",
        compute='_compute_context_fields',
        store=False  # Não persistir no banco de dados
    )

    context_specific_stock_output_id = fields.Many2one(
        'stock.location',
        string="Localização de Saída de Estoque",
        compute='_compute_context_fields',
        store=False
    )

    context_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Conta Analítica",
        compute='_compute_context_fields',
        store=False
    )

    @api.depends('context_specific_stock_location_id', 'context_specific_stock_output_id', 'context_analytic_account_id')
    def _compute_context_fields(self):
        for record in self:
            record.context_specific_stock_location_id = self.env.context.get('default_location_id')
            record.context_specific_stock_output_id = self.env.context.get('default_location_dest_id')
            record.context_analytic_account_id = self.env.context.get('default_analytic_account_id')

    def prepare_action_use_product(self):
        self.ensure_one()
        if not self.context_specific_stock_location_id or not self.context_specific_stock_output_id or not self.context_analytic_account_id:
            raise UserError("Informações essenciais para a movimentação de estoque estão faltando.")

        # Procede à criação da movimentação de estoque com os IDs fornecidos pelo contexto
        stock_move = self.env['stock.move'].create({
            'name': 'Usar Produto: ' + self.product_id.name,
            'location_id': self.context_specific_stock_location_id.id,
            'location_dest_id': self.context_specific_stock_output_id.id,
            'product_id': self.product_id.id,
            'product_uom_qty': 1,
            'product_uom': self.product_id.uom_id.id,
            'analytic_account_id': self.context_analytic_account_id.id
        })

        stock_move._action_confirm()
        stock_move._action_assign()
        stock_move._action_done()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Transferência de Produto',
            'res_model': 'stock.move',
            'view_mode': 'form',
            'res_id': stock_move.id,
            'target': 'new',
        }
