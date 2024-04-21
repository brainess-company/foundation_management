from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)  # Configuração do logger


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, **kwargs):
        """
        Sobrescreve para verificar estacas relacionadas sem medição, criar uma nova medição,
        vinculá-la à fatura, zerar quantidades das linhas existentes, inserir estacas nas linhas da fatura,
        diminuir a quantidade faturada na ordem de venda e registrar detalhes completos nos logs.
        """
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, **kwargs)

        Medicao = self.env['foundation.medicao']
        Estacas = self.env['foundation.estacas']

        for invoice in invoices:
            _logger.info(f'Processing invoice ID {invoice.id} for sale order ID {self.id}')

            # Zerando quantidades das linhas de fatura existentes
            for line in invoice.invoice_line_ids:
                line.quantity = 0
                _logger.info(f'Quantity zeroed for line ID {line.id} with product {line.product_id.display_name}')

            # Procurando por estacas que estão ligadas a esta ordem de venda e que não têm medição
            estacas = Estacas.search([
                ('sale_order_id', '=', self.id),
                ('medicao_id', '=', False),
                ('sale_order_line_id', '!=', False)  # Estacas que estão ligadas a uma linha de pedido de venda
            ])
            _logger.info(
                f'Found {len(estacas)} unmeasured stakes linked to sale order lines for sale order ID {self.id}')

            if estacas:
                # Criando uma nova medição
                last_medicao = Medicao.search([('sale_order_id', '=', self.id)], order='create_date desc', limit=1)
                next_number = int(last_medicao.nome.split(' ')[-1]) + 1 if last_medicao else 1
                nome_medicao = f"Medição {next_number}"
                new_medicao = Medicao.create({
                    'nome': nome_medicao,
                    'sale_order_id': self.id,
                    'data': fields.Date.today(),
                    'situacao': 'aguardando'
                })
                _logger.info(
                    f'New measurement {nome_medicao} (ID: {new_medicao.id}) created and linked to invoice ID {invoice.id}')

                # Vinculando estacas à nova medição e adicionando como linhas de fatura
                for estaca in estacas:
                    estaca.medicao_id = new_medicao.id
                    _logger.info(
                        f'Stake {estaca.nome_estaca} (ID: {estaca.id}) linked to measurement ID {new_medicao.id}')

                    # Adicionando linha de fatura para cada estaca
                    line_vals = {
                        'move_id': invoice.id,
                        'product_id': estaca.sale_order_line_id.product_id.id,
                        'quantity': estaca.profundidade,
                        'price_unit': estaca.sale_order_line_id.price_unit,
                        'name': f'Estaca {estaca.nome_estaca}: Profundidade {estaca.profundidade}m',
                        'account_id': estaca.sale_order_line_id.product_id.categ_id.property_account_income_categ_id.id or estaca.sale_order_line_id.product_id.categ_id.property_account_expense_categ_id.id
                    }
                    new_line = self.env['account.move.line'].create(line_vals)
                    _logger.info(
                        f'Invoice line for stake {estaca.nome_estaca} added to invoice ID {invoice.id}: {new_line.name}')

                    # Diminuindo a quantidade faturada na linha de pedido correspondente
                    if estaca.sale_order_line_id:
                        estaca.sale_order_line_id.qty_invoiced -= estaca.profundidade
                        _logger.info(
                            f'Decreased invoiced quantity for SO line {estaca.sale_order_line_id.id} by {estaca.profundidade}')

                # Associando a nova medição com a fatura corretamente
                new_medicao.invoice_id = invoice
                _logger.info(
                    f'Measurement {nome_medicao} (ID: {new_medicao.id}) is now linked with invoice ID {invoice.id}')

            _logger.info(f'Finalized processing for invoice ID {invoice.id}. All stakes are linked and invoiced.')

        return invoices
