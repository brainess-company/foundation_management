from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)  # Configuração do logger

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, **kwargs):
        """
        Sobrescreve para verificar estacas relacionadas sem medição, criar uma nova medição,
        vinculá-la à fatura, inserir estacas nas linhas da fatura com as variantes de produtos corretas,
        e manter os logs detalhados para monitoramento.
        """
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, **kwargs)

        Medicao = self.env['foundation.medicao']
        Estacas = self.env['foundation.estacas']

        for invoice in invoices:
            _logger.info(f'Processing invoice ID {invoice.id} for sale order ID {self.id}')

            estacas = Estacas.search([
                ('sale_order_id', '=', self.id),
                ('medicao_id', '=', False),
                ('sale_order_line_id', '!=', False)
            ])
            _logger.info(f'Found {len(estacas)} unmeasured stakes with associated sale order lines for sale order ID {self.id}')

            if not estacas:
                continue

            invoice_lines = []
            for estaca in estacas:
                product = estaca.sale_order_line_id.product_id
                if not product:
                    raise ValidationError(f"Estaca {estaca.nome_estaca} não possui produto associado na linha de pedido.")

                line_vals = {
                    'product_id': product.id,
                    'quantity': estaca.profundidade,
                    'price_unit': estaca.sale_order_line_id.price_unit,
                    'name': f'Estaca {estaca.nome_estaca}: {product.display_name}',
                    'account_id': product.categ_id.property_account_income_categ_id.id or product.categ_id.property_account_expense_categ_id.id,
                    'sale_line_ids': [(6, 0, [estaca.sale_order_line_id.id])]
                }
                invoice_lines.append((0, 0, line_vals))
                _logger.info(f'Prepared invoice line for stake {estaca.nome_estaca} with product {product.display_name}')

            # Vincular as linhas de fatura à fatura atual
            invoice.write({'invoice_line_ids': invoice_lines})
            _logger.info(f'Invoice lines added to invoice ID {invoice.id}')

            # Criar e associar medição
            next_code = self.env['ir.sequence'].next_by_code('foundation.medicao') or 1
            nome_medicao = f"Medição {next_code}"
            new_medicao = Medicao.create({
                'nome': nome_medicao,
                'sale_order_id': self.id,
                'data': fields.Date.today(),
                'situacao': 'aguardando',
                'invoice_id': invoice.id  # Associando diretamente a fatura à medição
            })
            estacas.write({'medicao_id': new_medicao.id})
            _logger.info(f'New measurement {nome_medicao} created and linked with invoice ID {invoice.id}')

        return invoices
