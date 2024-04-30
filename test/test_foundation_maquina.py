import unittest
from unittest.mock import patch
from odoo.tests.common import TransactionCase

class TestFoundationMaquina(TransactionCase):
    """
    Classe de teste para FoundationMaquina para verificar a integridade
    e o comportamento esperado das operações do modelo.
    """

    def setUp(self):
        """
        Configuração inicial para cada teste.
        """
        super(TestFoundationMaquina, self).setUp()
        self.FoundationMaquina = self.env['foundation.maquina']
        self.ResPartner = self.env['res.partner']
        self.FoundationTeam = self.env['foundation.team']

        # Criar operador mock
        self.operador = self.ResPartner.create({
            'name': 'Operador Teste'
        })

        # Criar empregados mock
        self.employee1 = self.ResPartner.create({'name': 'Empregado 1'})
        self.employee2 = self.ResPartner.create({'name': 'Empregado 2'})

        # Criar máquina mock
        self.maquina = self.FoundationMaquina.create({
            'nome_maquina': 'Escavadeira X1',
            'operador': self.operador.id,
            'status_maquina': 'disponivel'
        })

        # Criar equipe mock
        self.team = self.FoundationTeam.create({
            'machine_id': self.maquina.id,
            'employee_ids': [(6, 0, [self.employee1.id, self.employee2.id])]
        })

    def test_compute_current_team_employees(self):
        """
        Testa o cálculo dos empregados da equipe atual com base no último registro de equipe.
        """
        self.maquina._compute_current_team_employees()
        current_employees_ids = self.maquina.current_team_employees.ids

        # Verificar se os empregados da última equipe são atribuídos corretamente
        self.assertIn(self.employee1.id, current_employees_ids)
        self.assertIn(self.employee2.id, current_employees_ids)

if __name__ == '__main__':
    unittest.main()
