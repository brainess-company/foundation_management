import unittest
from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase
from odoo import fields

class TestFoundationTeam(TransactionCase):

    def setUp(self):
        super(TestFoundationTeam, self).setUp()
        # Criando instâncias mock para os registros de máquina e funcionário
        self.machine = MagicMock()
        self.machine.id = 1  # ID simulado para máquina
        self.employee = MagicMock()
        self.employee.ids = [1, 2]  # IDs simulados para funcionários

        # Configurando a classe FoundationTeam para uso nos testes
        self.FoundationTeam = self.env['foundation.team']

        # Mock das funções search e create do FoundationTeam
        self.foundation_team_search = patch('odoo.addons.your_module_name.models.foundation_team.FoundationTeam.search')
        self.foundation_team_create = patch('odoo.addons.your_module_name.models.foundation_team.FoundationTeam.create')

    @patch('odoo.fields.Date.today')
    def test_create_daily_team_records(self, mock_date):
        """
        Testa o método create_daily_team_records para garantir que ele cria registros de forma adequada.
        """
        mock_date.return_value = '2021-01-01'
        mock_search = self.foundation_team_search.start()
        mock_create = self.foundation_team_create.start()

        # Configurando o retorno do search para simular nenhum registro existente
        mock_search.side_effect = [[], [self.FoundationTeam]]

        # Chama o método que estamos testando
        self.FoundationTeam.create_daily_team_records()

        # Verifica se o create foi chamado uma vez, já que não há registros existentes
        mock_create.assert_called_once_with({
            'date': '2021-01-01',
            'machine_id': 1,
            'employee_ids': [(6, 0, [1, 2])],
            'note': None
        })

        self.foundation_team_search.stop()
        self.foundation_team_create.stop()

    def test_write_changes_to_employees(self):
        """
        Testa se o método write registra corretamente alterações na lista de funcionários.
        """
        with patch.object(self.FoundationTeam, 'write') as mock_write, \
             patch.object(self.FoundationTeam, 'message_post') as mock_message_post:
            team = self.FoundationTeam.create({
                'date': fields.Date.today(),
                'machine_id': self.machine.id,
                'employee_ids': [(6, 0, [1])]
            })

            # Simulando a escrita com novos funcionários
            mock_write.return_value = True
            team.write({'employee_ids': [(6, 0, [2])]})

            # Deve postar uma mensagem de mudança
            mock_message_post.assert_called()
            self.assertTrue(mock_message_post.call_args[1]['body'].startswith("Adicionados:"))

if __name__ == '__main__':
    unittest.main()
