"""Registra as estacas que foram preparadas para serem cobradas, gerar invoice"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class FoundationMedicao(models.Model):
    """Registra as estacas que foram preparadas para serem cobradas, gerar invoice"""

    _name = 'foundation.medicao'
    _description = 'Medições das Estacas'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Herdar de mail.thread e mail.activity.mixin
    _rec_name = 'display_medicao'

    nome = fields.Char("Numero da Medição", required=True)
    data = fields.Date(
        "Data da Medição",
        default=fields.Date.context_today,
        required=True
    )
    situacao = fields.Selection([
        ('aguardando', 'Aguardando Conferência'),
        ('emissao', 'Aguardando Emissão de Nota'),
        ('rejeitado', 'Rejeitado pelo cliente'),
        ('arquivada', 'Arquivada')
    ], string="Situação", default='aguardando')

    # RELACIONA ESSA MEDIÇÃO COM UMA SALE ORDER
    sale_order_id = fields.Many2one('sale.order',
                                    string="Ordem de Venda Relacionada",  tracking=True)

    nome_obra = fields.Char(related='sale_order_id.nome_obra', string="Obra", readonly=True)

    # CAMPO INVERSO QUE MOSTRA AS ESTACAS QUE ESTÃO RELACIONADAS COM ESSA MEDIÇÃO
    estacas_ids = fields.One2many('foundation.estacas', 'medicao_id',
                                  string="Estacas Medidas",  tracking=True)

    # CAMPOS COMPUTADOS
    valor_total = fields.Float("Total", compute='_compute_valor_total', store=True)
    invoice_id = fields.Many2one('account.move', string="Fatura Estática", readonly=True,
                                        copy=False)
    invoice_count = fields.Integer(compute='_compute_invoice_count',
                                   string='Invoice Countagem', default=0)

    display_medicao = fields.Char(string="Medição", compute='_compute_display_medicao')

    active = fields.Boolean(string="Ativo", default=True)


    @api.depends('nome')
    def _compute_display_medicao(self):
        """computa o nome da medição sequecial"""
        for record in self:
            # Certifique-se de que nome_medicao é uma string
            # e contém apenas números antes de formatar
            if isinstance(record.nome, str) and record.nome.isdigit():
                record.display_medicao = f"Medição {record.nome}"
            else:
                # Um valor padrão ou erro se o nome_medicao não for válido
                record.display_medicao = ""

    @api.depends('estacas_ids.total_price')
    def _compute_valor_total(self):
        """calcula o valor total"""
        for record in self:
            record.valor_total = sum(estaca.total_price for estaca in record.estacas_ids)

    @api.depends('estacas_ids.total_price')
    def action_create_invoice(self):
        """sobrescreve create para criar fatura"""
        self.ensure_one()  # Garante que apenas um registro seja processado

        if not self.sale_order_id:
            raise ValidationError("Não existe uma Ordem de Venda relacionada a esta medição.")

        invoice_lines = []
        for estaca in self.estacas_ids:
            if not estaca.sale_order_line_id:
                raise ValidationError(
                    f"Estaca {estaca.nome_estaca} "
                    f"não possui uma linha de pedido de venda relacionada.")

            product = estaca.sale_order_line_id.product_id
            quantity = estaca.profundidade
            price_unit = estaca.sale_order_line_id.price_unit

            line_vals = {
                'product_id': product.id,
                'quantity': quantity,
                'price_unit': price_unit,
                'name': f'Estaca {estaca.nome_estaca}: {product.display_name}',
                'account_id':
                    product.categ_id.property_account_income_categ_id.id
                    or product.categ_id.property_account_expense_categ_id.id,
                'sale_line_ids': [(6, 0, [estaca.sale_order_line_id.id])]
            }
            invoice_lines.append((0, 0, line_vals))

        # Busca o diário de vendas padrão, caso exista
        # todo o certo seria o diário de venda da empresa da sale order
        # TODO Implementado: Usar o diário de vendas da empresa da Ordem de Venda
        company = self.sale_order_id.company_id
        sale_journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', company.id)
        ], limit=1)

        if not sale_journal:
            raise ValidationError(
                f"Não há um diário de vendas configurado para a empresa {company.name}."
            )
        invoice_vals = {
            'partner_id': self.sale_order_id.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_origin': self.sale_order_id.name,
            'invoice_payment_term_id': self.sale_order_id.payment_term_id.id,
            'currency_id': self.sale_order_id.currency_id.id,
            'invoice_line_ids': invoice_lines,
            'journal_id': sale_journal.id,  # Define o diário de vendas
            'company_id': company.id,  # Define a empresa da fatura
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
        """define a ação do clique no botão"""
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
        """computa a quantidade de faturas relacionadas"""
        for record in self:
            record.invoice_count = 1 if record.invoice_id else 0

    def unlink(self):
        """Exclui a fatura associada antes de excluir a medição."""
        for record in self:
            if record.invoice_id:
                record.invoice_id.unlink()  # Exclui a fatura antes de excluir a medição
        return super(FoundationMedicao, self).unlink()

