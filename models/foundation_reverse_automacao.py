from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, **kwargs):
        """
        Sobrescreve para criar uma nova medição para estacas relacionadas sem medição,
        vincular a medição à fatura criada e não incluir novas linhas de fatura para estacas.
        """
        # Chamando o método original usando super() para criar faturas
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, **kwargs)

        Medicao = self.env['foundation.medicao']
        Estacas = self.env['foundation.estacas']

        for invoice in invoices:
            # Apenas processar a Sale Order correspondente
            sale_order = invoice.mapped('invoice_line_ids.sale_line_ids.order_id')[0]

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

                # Vincular todas as estacas à nova medição criada
                for estaca in estacas:
                    estaca.medicao_id = new_medicao.id

                # Associar a nova medição com a fatura, garantindo que o _compute_invoice_id seja acionado corretamente
                new_medicao.invoice_id = invoice.id

        return invoices
