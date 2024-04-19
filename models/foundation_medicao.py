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
    invoice_id = fields.Many2one('account.move', string="Fatura Relacionada", compute="_compute_invoice_id", store=True)

    @api.depends('estacas_ids.sale_order_line_id.invoice_lines.move_id')
    def _compute_invoice_id(self):
        for record in self:
            # Inicializar uma lista para armazenar os IDs das faturas candidatas
            invoice_ids = []
            for estaca in record.estacas_ids:
                # Iterar sobre as linhas de fatura associadas às linhas de pedido de venda da estaca
                invoice_lines = estaca.sale_order_line_id.invoice_lines.filtered(
                    lambda l: l.move_id.move_type == 'out_invoice')
                # Adicionar os IDs das faturas encontradas na lista
                invoice_ids.extend(invoice_lines.mapped('move_id').ids)

            # Definir o invoice_id para o primeiro ID de fatura único encontrado, ou False se nenhum for encontrado
            # Utiliza set para remover duplicatas, garantindo que a fatura capturada é única
            record.invoice_id = self.env['account.move'].browse(list(set(invoice_ids))[:1]).id if invoice_ids else False

    @api.depends('estacas_ids.total_price')
    def _compute_valor_total(self):
        for record in self:
            total = 0.0
            for estaca in record.estacas_ids:
                total += estaca.total_price
            record.valor_total = total

    def action_create_invoice(self):
        self.ensure_one()  # Garante que apenas um registro seja processado

        if not self.sale_order_id:
            raise ValidationError("Não existe uma Ordem de Venda relacionada a esta medição.")

        invoice_lines = []
        for estaca in self.estacas_ids:
            if not estaca.sale_order_line_id:
                raise ValidationError(
                    f"Estaca {estaca.nome_estaca} não possui uma linha de pedido de venda relacionada.")

            product = estaca.sale_order_line_id.product_id
            quantity = estaca.profundidade  # A quantidade é baseada na profundidade
            price_unit = estaca.sale_order_line_id.price_unit

            line_vals = {
                'product_id': product.id,
                'quantity': quantity,
                'price_unit': price_unit,
                'name': f'Estaca {estaca.nome_estaca}: {product.display_name}',
                'account_id': product.categ_id.property_account_income_categ_id.id or product.categ_id.property_account_expense_categ_id.id,
                'sale_line_ids': [(6, 0, [estaca.sale_order_line_id.id])]  # Vinculando à linha de pedido de venda
            }
            invoice_lines.append((0, 0, line_vals))

        invoice_vals = {
            'partner_id': self.sale_order_id.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_origin': self.sale_order_id.name,
            'invoice_payment_term_id': self.sale_order_id.payment_term_id.id,
            'currency_id': self.sale_order_id.currency_id.id,
            'invoice_line_ids': invoice_lines,
        }

        invoice = self.env['account.move'].create(invoice_vals)
        invoice.action_post()  # Postar a fatura imediatamente após a criação, se desejado
        self.invoice_id = invoice.id  # Associar a fatura criada com esta medição corretamente

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }





