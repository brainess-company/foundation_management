import unittest
from unittest.mock import patch
from odoo.tests.common import TransactionCase

class TestFoundationEstacas(TransactionCase):
    """
    Classe de teste para FoundationEstacas para verificar a integridade
    e o comportamento esperado das operações do modelo.
    """

    def setUp(self):
        """
        Configuração inicial para cada teste.
        """
        super(TestFoundationEstacas, self).setUp()
        self.FoundationEstacas = self.env['foundation.estacas']
        self.SaleOrderLine = self.env['sale.order.line']

        # Criar um serviço de obra mock
        self.service = self.env['foundation.obra.service'].create({
            'name': 'Service Test'
        })

        # Criar uma ordem de venda mock
        self.sale_order = self.env['sale.order'].create({
            'name': 'Sale Order Test'
        })

        # Criar uma linha de ordem de venda mock
        self.sale_order_line = self.SaleOrderLine.create({
            'order_id': self.sale_order.id,
            'product_id': 1,  # Assume que existe um produto com id 1
            'price_unit': 100.0,
            'product_uom_qty': 0
        })

    @patch('odoo.addons.foundation_estacas.models.foundation_estacas._logger')
    def test_create_estacas(self, mock_logger):
        """
        Testa a criação de uma estaca garantindo que a profundidade seja ajustada
        corretamente e que os logs sejam registrados como esperado.
        """
        estaca = self.FoundationEstacas.create({
            'nome_estaca': 'Estaca 1',
            'profundidade': 10,
            'data': '2021-01-01',
            'observacao': 'Nenhuma',
            'service_id': self.service.id,
            'sale_order_line_id': self.sale_order_line.id
        })

        # Verificar se a estaca foi criada corretamente
        self.assertEqual(estaca.profundidade, 10)
        self.assertEqual(estaca.sale_order_line_id.qty_delivered, 10)
        mock_logger.info.assert_called_with("VALORES ENVVIADOS PARA CRIAR ESTACAS: %s", any())

if __name__ == '__main__':
    unittest.main()
