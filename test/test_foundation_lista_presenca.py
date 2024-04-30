import unittest

from unittest.mock import Mock, patch
from odoo.tests.common import TransactionCase
from odoo import fields


class TestListaPresencaMock(TransactionCase):

    def setUp(self):
        super(TestListaPresencaMock, self).setUp()
        # Patching os modelos que são usados como dependência para isolar o teste
        self.chamada_mock = Mock()
        self.funcionario_mock = Mock()

        # Criando um objeto do modelo 'foundation.lista.presenca'
        self.ListaPresenca = self.env['foundation.lista.presenca']

        # Configurando o mock dos campos que serão usados no teste
        self.ListaPresenca.chamada_id = self.chamada_mock
        self.ListaPresenca.funcionario_id = self.funcionario_mock
        self.ListaPresenca.data = fields.Date.today()

    @patch('odoo.fields.Date.today')
    def test_criacao_lista_presenca(self, mock_date):
        """
        Testa se a criação da lista de presença está configurando corretamente seus atributos.
        """
        mock_date.return_value = '2021-01-01'

        lista_presenca = self.ListaPresenca.create({
            'chamada_id': self.chamada_mock.id,
            'funcionario_id': self.funcionario_mock.id,
            'data': mock_date.return_value
        })

        # Verifica se a data está sendo atribuída corretamente
        self.assertEqual(lista_presenca.data, '2021-01-01', "A data deve ser a retornada pelo mock.")

        # Verifica se os mocks estão sendo usados corretamente
        self.assertEqual(lista_presenca.chamada_id, self.chamada_mock, "O mock da chamada deve ser usado.")
        self.assertEqual(lista_presenca.funcionario_id, self.funcionario_mock, "O mock do funcionário deve ser usado.")

if __name__ == '__main__':
    unittest.main()
