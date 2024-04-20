from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)  # Configuração do logger

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, **kwargs):
        """
        Sobrescreve para verificar estacas relacionadas sem medição, criar uma nova medição,
        vinculá-la à fatura, mas não incluir as estacas nas linhas da fatura.
        """
        # Criando faturas usando o método original da 'sale.order'
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, **kwargs)

        Medicao = self.env['foundation.medicao']
        Estacas = self.env['foundation.estacas']

        for invoice in invoices:
            # Processando a Sale Order correspondente
            sale_order = invoice.mapped('invoice_line_ids.sale_line_ids.order_id')[0]

            # Logging initial invoice lines
            initial_line_ids = invoice.invoice_line_ids.ids
            _logger.info(f'Initial invoice line IDs for invoice {invoice.id}: {initial_line_ids}')

            # Procurando por estacas não medidas
            estacas = Estacas.search([
                ('sale_order_id', '=', sale_order.id),
                ('medicao_id', '=', False)
            ])
            _logger.info(f'Found {len(estacas)} unmeasured stakes for sale order ID {self.id}')

            if estacas:
                # Criando uma nova medição
                last_medicao = Medicao.search([('sale_order_id', '=', sale_order.id)], order='create_date desc', limit=1)
                next_number = int(last_medicao.nome.split(' ')[-1]) + 1 if last_medicao else 1
                nome_medicao = f"Medição {next_number}"

                new_medicao = Medicao.create({
                    'nome': nome_medicao,
                    'sale_order_id': sale_order.id,
                    'data': fields.Date.today(),
                    'situacao': 'aguardando'
                })
                _logger.info(f'New measurement {nome_medicao} (ID: {new_medicao.id}) created and linked to invoice ID {invoice.id}')

                # Vinculando estacas à nova medição
                estacas.write({'medicao_id': new_medicao.id})
                _logger.info(f'All unmeasured stakes now linked to new measurement ID {new_medicao.id}')

                # Associando a medição à fatura
                new_medicao.invoice_id = invoice.id
                _logger.info(f'Measurement ID {new_medicao.id} linked to Invoice ID {invoice.id}')

            # Logging final state of invoice lines
            final_line_ids = invoice.invoice_line_ids.ids
            _logger.info(f'Final invoice line IDs for invoice {invoice.id}: {final_line_ids}')

        return invoices
