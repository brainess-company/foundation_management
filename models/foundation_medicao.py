from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FoundationMedicao(models.Model):
    _name = 'foundation.medicao'
    _description = 'Medições das Estacas'
    _rec_name = 'nome'

    nome = fields.Char("Nome da Medição", required=True)
    data = fields.Date("Data da Medição")
    situacao = fields.Selection([
        ('aguardando', 'Aguardando Conferência'),
        ('emissao', 'Aguardando Emissão de Nota')
    ], string="Situação", default='aguardando')
    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda Relacionada")
    estacas_ids = fields.One2many('foundation.estacas', 'medicao_id', string="Estacas Medidas")

    # Campo computado para calcular o valor total
    valor_total = fields.Float("Valor Total", compute="_compute_valor_total", store=True)
    # foundation_estacas.sale_order_line_id

    @api.depends('estacas_ids.total_price')
    def _compute_valor_total(self):
        for record in self:
            total = 0.0
            for estaca in record.estacas_ids:
                total += estaca.total_price
            record.valor_total = total


    def action_create_invoice(self):
        if len(self) != 1:
            raise ValidationError("Please select exactly one measurement to process.")

        record = self[0]  # Trabalha com o único registro selecionado
        invoice_lines = []
        for estaca in record.estacas_ids:
            if not estaca.sale_order_line_id:
                raise ValidationError(f"Estaca {estaca.nome_estaca} does not have a related sale order line.")

            line_vals = {
                'product_id': estaca.sale_order_line_id.product_id.id,
                'quantity': estaca.sale_order_line_id.product_uom_qty,
                'price_unit': estaca.sale_order_line_id.price_unit,
                'name': f'{estaca.nome_estaca} - {estaca.sale_order_line_id.product_id.display_name}',
                'account_id': estaca.sale_order_line_id.order_id.partner_id.property_account_receivable_id.id,
            }
            invoice_lines.append((0, 0, line_vals))

        invoice_vals = {
            'partner_id': record.sale_order_id.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': invoice_lines,
        }
        invoice = self.env['account.move'].create(invoice_vals)
        invoice.action_post()  # Confirmar a fatura

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }

