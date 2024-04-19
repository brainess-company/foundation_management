from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, **kwargs):
        """
        Override to include related stakes without measurement in invoice lines and create a new measurement.
        """
        # Creating invoices using the original logic from super
        invoice_vals_list = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, **kwargs)
        invoices = self.env['account.move'].browse([vals['id'] for vals in invoice_vals_list if 'id' in vals])

        Medicao = self.env['foundation.medicao']
        Estacas = self.env['foundation.estacas']

        for invoice in invoices:
            sale_order = invoice.invoice_line_ids.mapped('sale_line_ids.order_id')
            if not sale_order:
                continue
            sale_order = sale_order[0]

            # Search for stakes related to the sale order that have not been measured yet
            estacas = Estacas.search([
                ('sale_order_id', '=', sale_order.id),
                ('medicao_id', '=', False)
            ])

            if estacas:
                # Create a measurement if there are stakes to measure
                last_medicao = Medicao.search([('sale_order_id', '=', sale_order.id)], order='create_date desc',
                                              limit=1)
                nome_medicao = "Medição {}".format(int(last_medicao.nome.split(' ')[-1]) + 1 if last_medicao else 1)

                new_medicao = Medicao.create({
                    'nome': nome_medicao,
                    'sale_order_id': sale_order.id,
                    'data': fields.Date.today(),
                    'situacao': 'aguardando',
                })

                # Add each stake as an invoice line
                for estaca in estacas:
                    line_vals = {
                        'move_id': invoice.id,
                        'product_id': estaca.variante_id.id if estaca.variante_id else False,
                        'quantity': estaca.profundidade,
                        'price_unit': estaca.unit_price,
                        'name': f'Estaca: {estaca.nome_estaca} - Profundidade: {estaca.profundidade}m'
                    }
                    invoice_line = self.env['account.move.line'].with_context(check_move_validity=False).create(
                        line_vals)
                    estaca.medicao_id = new_medicao.id

        return invoice_vals_list
