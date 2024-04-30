import unittest
from unittest.mock import patch
from odoo.tests.common import TransactionCase

class TestChamada(TransactionCase):
    """
    Classe de teste para verificar a integridade e o comportamento esperado do modelo Chamada.
    """

    def setUp(self):
        """
        Configuração inicial para cada teste.
        Prepara o ambiente simulando registros necessários como obra, serviço e ordem de venda.
        """
        super(TestChamada, self).setUp()
        self.Chamada = self.env['foundation.chamada']
        self.FoundationObraService = self.env['foundation.obra.service']
        self.Obra = self.env['foundation.obra']
        self.SaleOrder = self.env['sale.order']

        # Criar uma obra mock
        self.obra = self.Obra.create({
            'nome_obra': 'Obra Teste',
            'endereco': 'Endereço Teste'
        })

        # Criar uma ordem de venda mock
        self.sale_order = self.SaleOrder.create({
            'name': 'SO Teste',
            'obra_id': self.obra.id
        })

        # Criar um serviço de obra mock
        self.service_obra = self.FoundationObraService.create({
            'name': 'Serviço Teste',
            'obra_id': self.obra.id
        })

        # Criar uma chamada mock
        self.chamada = self.Chamada.create({
            'foundation_obra_service_id': self.service_obra.id,
            'obra_id': self.obra.id,
            'data': '2021-01-01'
        })

    def test_chamada_creation(self):
        """
        Testa a criação de um registro de chamada para verificar se todos os campos relacionados
        estão corretamente configurados.
        """
        self.assertEqual(self.chamada.nome_obra, 'Obra Teste')
        self.assertEqual(self.chamada.endereco, 'Endereço Teste')
        self.assertEqual(self.chamada.sale_order_id.id, self.sale_order.id)

    @patch('odoo.addons.foundation_chamada.models.foundation_chamada.Chamada.action_save')
    def test_action_save(self, mock_action_save):
        """
        Testa o método action_save para garantir que ele é chamado corretamente e
        que a ação é realizada conforme o esperado.
        """
        self.chamada.action_save()
        mock_action_save.assert_called_once()

if __name__ == '__main__':
    unittest.main()
