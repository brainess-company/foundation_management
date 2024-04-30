import unittest

from odoo.tests.common import TransactionCase

class TestFoundationObra(TransactionCase):
    """
    Test class for the FoundationObra model to ensure computed fields and relationships
    are functioning correctly.
    """

    def setUp(self):
        """
        Setup basic entities to be used in the tests.
        """
        super(TestFoundationObra, self).setUp()
        self.SaleOrder = self.env['sale.order']
        self.ResPartner = self.env['res.partner']
        self.ProductProduct = self.env['product.product']
        self.FoundationObra = self.env['foundation.obra']

        # Create a customer
        self.customer = self.ResPartner.create({'name': 'Test Customer'})

        # Create products
        self.product1 = self.ProductProduct.create({
            'name': 'Test Product 1',
            'lst_price': 100
        })

        # Create a sale order
        self.sale_order = self.SaleOrder.create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.product1.id,
                'product_uom_qty': 5,
                'price_unit': self.product1.lst_price
            })]
        })

    def test_compute_fields(self):
        """
        Tests the computed fields 'valor_faturado' and 'valor_a_faturar'.
        """
        # Create an obra associated with the sale order
        obra = self.FoundationObra.create({
            'sale_order_id': self.sale_order.id,
            'endereco': '123 Main St'
        })

        # Validate the initial computed values
        self.assertEqual(obra.valor_faturado, 0, "Valor faturado should initially be zero.")
        self.assertEqual(obra.valor_a_faturar, 500, "Valor a faturar should be equal to the total order value initially.")

        # Confirm the sale order and invoice it partially
        self.sale_order.action_confirm()
        invoice = self.sale_order._create_invoices()
        invoice.invoice_line_ids[0].quantity = 3  # Invoice partially
        invoice.action_post()

        # Check the updated computed fields
        obra.invalidate_cache()  # Refresh the cache to ensure computed fields are updated
        self.assertEqual(obra.valor_faturado, 300, "Valor faturado should reflect the invoiced amount.")
        self.assertEqual(obra.valor_a_faturar, 200, "Valor a faturar should reflect the remaining amount to be invoiced.")

if __name__ == '__main__':
    unittest.main()
