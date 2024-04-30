import unittest

from odoo.tests.common import TransactionCase
from datetime import date
from unittest.mock import patch

class TestFoundationMaquinaRegistro(TransactionCase):
    """
    Classe de teste para verificar a funcionalidade e integridade do modelo
    FoundationMaquinaRegistro.
    """

    def setUp(self):
        """
        Configurações iniciais para os testes, criando instâncias de máquinas,
        operadores e registros associados.
        """
        super(TestFoundationMaquinaRegistro, self).setUp()
        self.Maquina = self.env['foundation.maquina']
        self.MaquinaRegistro = self.env['foundation.maquina.registro']
        self.Chamada = self.env['foundation.chamada']
        self.ResPartner = self.env['res.partner']

        # Criando um operador
        self.operador = self.ResPartner.create({
            'name': 'João'
        })

        # Criando uma máquina
        self.maquina = self.Maquina.create({
            'name': 'Escavadeira',
            'operador': self.operador.id
        })

        # Criando um registro de máquina
        self.registro = self.MaquinaRegistro.create({
            'maquina_id': self.maquina.id,
            'data_registro': date.today()
        })

    def test_compute_operador(self):
        """
        Testa o método computado que determina o operador da máquina.
        """
        self.registro._compute_operador()
        self.assertEqual(self.registro.operador_id.id, self.operador.id)

    @patch('odoo.addons.your_module.models.foundation_maquina_registro.date', autospec=True)
    def test_compute_has_today_chamada(self, mock_date):
        """
        Testa o método computado que verifica se há chamadas registradas para hoje.
        """
        mock_date.today.return_value = date.today()
        chamada = self.Chamada.create({
            'foundation_maquina_registro_id': self.registro.id,
            'data': date.today()
        })
        self.registro._compute_has_today_chamada()
        self.assertTrue(self.registro.has_today_chamada)

    def test_compute_display_has_today_chamada(self):
        """
        Testa a lógica de exibição da chamada do dia, com base se a máquina
        requer chamada e se realmente houve uma chamada.
        """
        self.maquina.requer_chamada = True
        chamada = self.Chamada.create({
            'foundation_maquina_registro_id': self.registro.id,
            'data': date.today()
        })
        self.registro._compute_has_today_chamada()
        self.registro._compute_display_has_today_chamada()
        self.assertEqual(self.registro.display_has_today_chamada, "Sim")

if __name__ == '__main__':
    unittest.main()
