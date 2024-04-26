from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class FoundationMedicao(models.Model):
    _name = 'foundation.medicao'
    _description = 'Medições das Estacas'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Herdar de mail.thread e mail.activity.mixin
    _rec_name = 'display_medicao'

    nome = fields.Char("Numero da Medição", required=True)
    data = fields.Date("Data da Medição", default=lambda self: fields.Date.context_today(self), required=True)
    situacao = fields.Selection([
        ('aguardando', 'Aguardando Conferência'),
        ('emissao', 'Aguardando Emissão de Nota'),
        ('rejeitado', 'Rejeitado pelo cliente'),
        ('arquivada', 'Arquivada')
    ], string="Situação", default='aguardando')

    # RELACIONA ESSA MEDIÇÃO COM UMA SALE ORDER
    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda Relacionada",  tracking=True)

    nome_obra = fields.Char(related='sale_order_id.nome_obra', string="Obra", readonly=True)

    # CAMPO INVERSO QUE MOSTRA AS ESTACAS QUE ESTÃO RELACIONADAS COM ESSA MEDIÇÃO
    estacas_ids = fields.One2many('foundation.estacas', 'medicao_id', string="Estacas Medidas",  tracking=True)

    # CAMPOS COMPUTADOS
    valor_total = fields.Float("Valor Total", compute='_compute_valor_total', store=True)
    invoice_id = fields.Many2one('account.move', string="Fatura Relacionada", compute="_compute_invoice_id", store=True, tracking=True)
    invoice_count = fields.Integer(compute='_compute_invoice_count', string='Invoice Count', default=0)

    display_medicao = fields.Char(string="NMedição", compute='_compute_display_medicao')

    @api.depends('nome')
    def _compute_display_medicao(self):
        for record in self:
            # Certifique-se de que nome_medicao é uma string e contém apenas números antes de formatar
            if isinstance(record.nome, str) and record.nome.isdigit():
                record.display_medicao = f"Medição {record.nome}"
            else:
                record.display_medicao = ""  # Um valor padrão ou erro se o nome_medicao não for válido

    @api.depends('estacas_ids.total_price')
    def _compute_valor_total(self):
        for record in self:
            record.valor_total = sum(estaca.total_price for estaca in record.estacas_ids)

    @api.depends('estacas_ids.sale_order_line_id.invoice_lines.move_id')
    def _compute_invoice_id(self):
        for record in self:
            record.invoice_id = False  # Resetando o invoice_id para evitar associações erradas
            related_invoice_ids = set()

            for estaca in record.estacas_ids:
                invoice_lines = estaca.sale_order_line_id.invoice_lines.filtered(
                    lambda l: l.move_id.state == 'draft' and
                              l.product_id == estaca.sale_order_line_id.product_id and
                              l.move_id.invoice_origin == record.sale_order_id.name)
                for invoice_line in invoice_lines:
                    related_invoice_ids.add(invoice_line.move_id.id)

            # Associar a fatura somente se houver uma única fatura em rascunho relacionada corretamente
            if len(related_invoice_ids) == 1:
                record.invoice_id = self.env['account.move'].browse(related_invoice_ids.pop())

    @api.depends('estacas_ids.total_price')
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
            quantity = estaca.profundidade
            price_unit = estaca.sale_order_line_id.price_unit

            line_vals = {
                'product_id': product.id,
                'quantity': quantity,
                'price_unit': price_unit,
                'name': f'Estaca {estaca.nome_estaca}: {product.display_name}',
                'account_id': product.categ_id.property_account_income_categ_id.id or product.categ_id.property_account_expense_categ_id.id,
                'sale_line_ids': [(6, 0, [estaca.sale_order_line_id.id])]
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


    def action_view_invoice(self):
        self.ensure_one()  # Garante que apenas um registro seja processado
        if not self.invoice_id:
            raise UserError("Não há fatura relacionada para abrir.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Fatura Relacionada',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }


    @api.depends('invoice_id')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = 1 if record.invoice_id else 0








