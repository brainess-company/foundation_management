import unittest
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger
from unittest.mock import patch


class TestFoundationRelatorios(TransactionCase):

    def setUp(self):
        super(TestFoundationRelatorios, self).setUp()
        self.Relatorio = self.env['foundation.relatorios']
        self.Estacas = self.env['foundation.estacas']
        self.MaquinaRegistro = self.env['foundation.maquina.registro']

    @mute_logger('odoo.sql_db')
    def test_create_relatorio(self):
        with patch.object(self.MaquinaRegistro, 'create') as mock_create:
            # Simulando a criação de um registro de máquina
            mock_create.return_value = self.MaquinaRegistro()

            # Resto do código do teste...

    @mute_logger('odoo.sql_db')
    def test_action_confirm_relatorio(self):
        with patch.object(self.MaquinaRegistro, 'create') as mock_create:
            # Simulando a criação de um registro de máquina
            mock_create.return_value = self.MaquinaRegistro()

            # Resto do código do teste...


