from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)  # Configuração do logger

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, **kwargs):
        """
        Sobrescreve para criar uma nova medição para estacas relacionadas sem medição,
        vincular a medição à fatura criada e incluir cada estaca na nova linha da fatura.
        """
        # Chamando o método original usando super() para criar faturas
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, **kwargs)

        Medicao = self.env['foundation.medicao']
        Estacas = self.env['foundation.estacas']
        linhas_a_remover = []

        for invoice in invoices:
            # Apenas processar a Sale Order correspondente
            sale_order = invoice.mapped('invoice_line_ids.sale_line_ids.order_id')[0]
            # Log dos IDs das linhas de fatura antes de adicionar novas
            initial_line_ids = [line.id for line in invoice.invoice_line_ids]
            linhas_a_remover.extend(initial_line_ids)
            _logger.info(f'Linhas que ja estavam na fatura {invoice.id}: {initial_line_ids}')

            # Procurar por estacas relacionadas a esta Sale Order que ainda não foram medidas
            estacas = Estacas.search([
                ('sale_order_id', '=', sale_order.id),
                ('medicao_id', '=', False)
            ])

            if estacas:
                # Criar uma medição se existem estacas a serem medidas
                last_medicao = Medicao.search([('sale_order_id', '=', sale_order.id)], order='create_date desc', limit=1)
                nome_medicao = "Medição {}".format(int(last_medicao.nome.split(' ')[-1]) + 1 if last_medicao else 1)

                new_medicao = Medicao.create({
                    'nome': nome_medicao,
                    'sale_order_id': sale_order.id,
                    'data': fields.Date.today(),
                    'situacao': 'aguardando',
                })

                created_lines_ids = []

                # Vincular todas as estacas à nova medição criada
                for estaca in estacas:
                    estaca.medicao_id = new_medicao.id

                    # Adicionar cada estaca como uma linha da fatura
                    line_vals = {
                        'move_id': invoice.id,
                        'product_id': estaca.variante_id.id if estaca.variante_id else False,
                        'quantity': estaca.profundidade,
                        'price_unit': estaca.unit_price,
                        'name': f'Estaca {estaca.nome_estaca}: Profundidade {estaca.profundidade}m'
                    }
                    line = self.env['account.move.line'].create(line_vals)
                    created_lines_ids.append(line.id)

                # Associar a nova medição com a fatura
                new_medicao.invoice_id = invoice.id
                # Remover as linhas de fatura indesejadas que não correspondem às estacas adicionadas
                all_lines = invoice.invoice_line_ids.filtered(lambda l: l.id not in created_lines_ids)
                _logger.info(
                    f'Linhas que devem ser removidas: {[line.id for line in all_lines]}')  # Log das linhas a remover


            # Log dos IDs das linhas de fatura após adicionar novas
            final_line_ids = [line.id for line in invoice.invoice_line_ids]

            _logger.info(f'Linhas que estão na fatura final {invoice.id}: {final_line_ids}')

            _logger.info(f'Linhas a remover: {linhas_a_remover}')
            # Removendo linhas indesejadas após todas as adições
            linhas = self.env['account.move.line'].browse(linhas_a_remover)#.unlink()
            _logger.info(f'Linhas que estão com unlink: {linhas}')


        return invoices
