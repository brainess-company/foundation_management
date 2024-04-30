import unittest
from unittest.mock import patch
from odoo.tests.common import TransactionCase


class TestFoundationMedicao(TransactionCase):
    """
    Classe de teste para FoundationMedicao para verificar a integridade e o comportamento esperado.
    """

    def setUp(self):
        """
        Configuração inicial para cada teste.
        """
        super(TestFoundationMedicao, self).setUp()
        self.FoundationMedicao = self.env['foundation.medicao']
        self.SaleOrder = self.env['sale.order']
        self.AccountMove = self.env['account.move']
        self.Product = self.env['product.product']

        # Criar ordem de venda mock
        self.sale_order = self.SaleOrder.create({
            'name': 'SO01'
        })

        # Criar uma medição mock
        self.medicao = self.FoundationMedicao.create({
            'nome': '001',
            'data': '2021-01-01',
            'sale_order_id': self.sale_order.id
        })

    @patch('odoo.addons.foundation_medicao.models.foundation_medicao._compute_invoice_id')
    def test_compute_valor_total(self, mock_compute_invoice_id):
        """
        Testa a computação do valor total das estacas medidas.
        """
        # Simulando estacas com preços para teste
        self.env['foundation.estacas'].create({
            'nome_estaca': 'Estaca 1',
            'total_price': 100.00,
            'medicao_id': self.medicao.id
        })
        self.env['foundation.estacas'].create({
            'nome_estaca': 'Estaca 2',
            'total_price': 200.00,
            'medicao_id': self.medicao.id
        })

        self.medicao._compute_valor_total()
        self.assertEqual(self.medicao.valor_total, 300.00)

    def test_action_create_invoice(self):
        """
        Testa a criação de fatura a partir das estacas medidas.
        """
        product = self.Product.create({'name': 'Produto Teste'})
        estaca = self.env['foundation.estacas'].create({
            'nome_estaca': 'Estaca 1',
            'profundidade': 10,
            'sale_order_line_id': self.sale_order.id,
            'total_price': 100.00,
            'medicao_id': self.medicao.id
        })

        with patch.object(self.env['account.move'], 'create') as mock_create:
            mock_create.return_value = self.AccountMove.create({'name': 'INV01'})
            self.medicao.action_create_invoice()
            mock_create.assert_called_once()

    def test_action_view_invoice(self):
        """
        Testa a ação para visualizar a fatura relacionada.
        """
        # Configurar uma fatura mock
        invoice = self.AccountMove.create({'name': 'INV01'})
        self.medicao.invoice_id = invoice.id

        result = self.medicao.action_view_invoice()
        self.assertEqual(result['res_id'], invoice.id)


if __name__ == '__main__':
    unittest.main()
