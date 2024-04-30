import unittest

from odoo.tests.common import TransactionCase

class TestSaleOrder(TransactionCase):
    """
    Classe de teste para verificar a funcionalidade do modelo SaleOrder
    estendido para criar automaticamente registros de obra e serviços.
    """

    def setUp(self):
        """
        Prepara o ambiente de testes criando registros necessários e configurando um ambiente de testes.
        """
        super(TestSaleOrder, self).setUp()
        self.SaleOrder = self.env['sale.order']
        self.Product = self.env['product.product']
        self.ProductTemplate = self.env['product.template']
        self.FoundationObra = self.env['foundation.obra']
        self.FoundationObraService = self.env['foundation.obra.service']

        # Criar produto e template de produto
        self.product_template = self.ProductTemplate.create({'name': 'Template 1'})
        self.product = self.Product.create({
            'name': 'Product 1',
            'product_tmpl_id': self.product_template.id
        })

        # Criar uma ordem de venda
        self.sale_order = self.SaleOrder.create({
            'name': 'SO01',
            'state': 'draft',  # Estado inicial
            'nome_obra': 'Obra Teste',
            'order_line': [(0, 0, {'product_id': self.product.id, 'product_uom_qty': 1})]
        })

    def test_create_foundation_obra_and_services(self):
        """
        Testa se a criação de uma sale order com estado 'sale' gera automaticamente
        os registros relacionados de obra e serviço.
        """
        # Alterar estado para 'sale' e verificar se os registros são criados
        self.sale_order.write({'state': 'sale'})
        obra = self.FoundationObra.search([('sale_order_id', '=', self.sale_order.id)])
        obra_service = self.FoundationObraService.search([('obra_id', '=', obra.id)])

        # Verificações
        self.assertTrue(obra, "Deveria ter criado uma obra automaticamente.")
        self.assertTrue(obra_service, "Deveria ter criado um serviço automaticamente.")

        # Verificar se o serviço está relacionado ao produto correto
        self.assertEqual(obra_service.variante_id.id, self.product.id,
                         "O serviço deveria estar relacionado ao produto correto.")

if __name__ == '__main__':
    unittest.main()
