import unittest
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tools import mute_logger
from datetime import date
from odoo import fields


class TestFoundationRelatorios(TransactionCase):

    def setUp(self):
        super(TestFoundationRelatorios, self).setUp()
        self.Relatorio = self.env['foundation.relatorios']
        self.Estacas = self.env['foundation.estacas']
        self.MaquinaRegistro = self.env['foundation.maquina.registro']

    @mute_logger('odoo.sql_db')
    def test_create_relatorio(self):
        # Criar um registro de máquina para usar no relatório
        maquina_registro = self.MaquinaRegistro.create({
            'nome_obra': 'Obra Teste',
            'endereco': 'Endereço Teste',
            'service_id': 1,
            'operador_id': 1,
            # Adicione outros campos necessários
        })

        # Crie um relatório com todos os campos necessários preenchidos
        relatorio_vals = {
            'data': date.today(),
            'foundation_maquina_registro_id': maquina_registro.id,
            'assinatura': 'Assinatura Digital',  # Supondo que este seja um campo binário
            'state': 'rascunho',  # Estado inicial
            # Adicione outros campos necessários
        }
        relatorio = self.Relatorio.create(relatorio_vals)

        # Verifique se o relatório foi criado corretamente
        self.assertEqual(relatorio.state, 'rascunho')
        self.assertEqual(relatorio.relatorio_number, '1')  # Assumindo que este é o primeiro relatório
        # Adicione mais verificações conforme necessário

        # Tente criar um relatório sem assinatura
        with self.assertRaises(UserError):
            self.Relatorio.create({'data': date.today(), 'foundation_maquina_registro_id': maquina_registro.id})

    @mute_logger('odoo.sql_db')
    def test_action_confirm_relatorio(self):
        # Criar um registro de máquina e um relatório para usar na ação confirmar
        maquina_registro = self.MaquinaRegistro.create({
            'nome_obra': 'Obra Teste',
            'endereco': 'Endereço Teste',
            'service_id': 1,
            'operador_id': 1,
            # Adicione outros campos necessários
        })

        relatorio_vals = {
            'data': date.today(),
            'foundation_maquina_registro_id': maquina_registro.id,
            'assinatura': 'Assinatura Digital',  # Supondo que este seja um campo binário
            'state': 'rascunho',  # Estado inicial
            # Adicione outros campos necessários
        }
        relatorio = self.Relatorio.create(relatorio_vals)

        # Executar a ação de confirmar relatório
        relatorio.action_confirm()

        # Verificar se o estado do relatório mudou para 'conferido'
        self.assertEqual(relatorio.state, 'conferido')
        # Adicione mais verificações conforme necessário


class TestResUsers(TransactionCase):

    def setUp(self):
        super(TestResUsers, self).setUp()
        self.ResUsers = self.env['res.users']

    @mute_logger('odoo.sql_db')
    def test_notification_type_default_value(self):
        # Criação de usuário sem especificar o campo notification_type
        user = self.ResUsers.create({
            'name': 'Test User',
            'login': 'testuser',
            'notification_type': 'inbox'
            # Adicione outros campos necessários
        })

        # Verifica se o campo notification_type foi preenchido com o valor padrão 'email'
        self.assertEqual(user.notification_type, 'email')


if __name__ == '__main__':
    unittest.main()
