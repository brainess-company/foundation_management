import unittest

from odoo.tests.common import TransactionCase

class TestFoundationObraService(TransactionCase):
    """
    Classe de teste para verificar a funcionalidade e a integridade do modelo
    FoundationObraService.
    """

    def setUp(self):
        """
        Configurações iniciais para os testes, criando instâncias necessárias
        de obras, serviços, máquinas e produtos.
        """
        super(TestFoundationObraService, self).setUp()
        self.ProductProduct = self.env['product.product']
        self.FoundationObra = self.env['foundation.obra']
        self.FoundationMaquina = self.env['foundation.maquina']
        self.FoundationObraService = self.env['foundation.obra.service']
        self.FoundationMaquinaRegistro = self.env['foundation.maquina.registro']
        self.AccountAnalyticAccount = self.env['account.analytic.account']

        # Criando registros necessários
        self.obra = self.FoundationObra.create({
            'nome_obra': 'Nova Obra',
            'endereco': 'Rua Principal, 1000'
        })
        self.variante = self.ProductProduct.create({'name': 'Escavadora'})
        self.maquina = self.FoundationMaquina.create({
            'name': 'Maquina 001'
        })

    def test_create_and_update_service(self):
        """
        Testa a criação e atualização de um serviço de obra, verificando se os registros de máquinas
        e contas analíticas são gerados e atualizados corretamente.
        """
        service = self.FoundationObraService.create({
            'variante_id': self.variante.id,
            'obra_id': self.obra.id,
            'foundation_maquina_ids': [(4, self.maquina.id)]
        })

        # Verificando a criação do registro de máquina
        maquina_registro = self.FoundationMaquinaRegistro.search([
            ('service_id', '=', service.id),
            ('maquina_id', '=', self.maquina.id)
        ])
        self.assertTrue(maquina_registro, "Deveria ter criado um registro de máquina.")

        # Verificando a criação da conta analítica
        analytic_account = self.AccountAnalyticAccount.search([
            ('foundation_maquina_registro_id', '=', maquina_registro.id)
        ])
        self.assertTrue(analytic_account, "Deveria ter criado uma conta analítica.")

        # Atualizando o serviço e verificando a atualização
        new_maquina = self.FoundationMaquina.create({'name': 'Maquina 002'})
        service.write({
            'foundation_maquina_ids': [(4, new_maquina.id)]
        })
        new_maquina_registro = self.FoundationMaquinaRegistro.search([
            ('service_id', '=', service.id),
            ('maquina_id', '=', new_maquina.id)
        ])
        self.assertTrue(new_maquina_registro, "Deveria ter atualizado com um novo registro de máquina.")
        new_analytic_account = self.AccountAnalyticAccount.search([
            ('foundation_maquina_registro_id', '=', new_maquina_registro.id)
        ])
        self.assertTrue(new_analytic_account, "Deveria ter atualizado com uma nova conta analítica.")

if __name__ == '__main__':
    unittest.main()
