import unittest
from odoo import models, fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestFoundationEstacas(TransactionCase):

    def setUp(self):
        super(TestFoundationEstacas, self).setUp()
        # Configurar dados necessários para o teste
        self.Empresa = self.env['res.partner'].create({
            'name': 'Empresa Teste'
        })
        self.Obra = self.env['foundation.obra'].create({
            'nome_obra': 'Obra X',
            'endereco': 'Endereço X',
            'partner_id': self.Empresa.id
        })
        self.Servico = self.env['foundation.obra.service'].create({
            'obra_id': self.Obra.id,
            'service_name': 'Serviço Y'
        })
        self.Produto = self.env['product.product'].create({
            'name': 'Produto Z'
        })
        self.OrdemVenda = self.env['sale.order'].create({
            'partner_id': self.Empresa.id
        })
        self.LinhaOrdemVenda = self.env['sale.order.line'].create({
            'order_id': self.OrdemVenda.id,
            'product_id': self.Produto.id,
            'product_uom_qty': 5
        })

    def test_create_estacas(self):
        # Teste para verificar a criação correta de uma estaca
        estaca = self.env['foundation.estacas'].create({
            'nome_estaca': 'Estaca 001',
            'profundidade': 10,
            'data': '2024-01-01',
            'service_id': self.Servico.id,
            'sale_order_line_id': self.LinhaOrdemVenda.id
        })
        self.assertEqual(estaca.profundidade, 10, "A profundidade da estaca deve ser igual a 10.")

    def test_profundidade_constraint(self):
        # Teste para verificar a restrição de profundidade aplicada no modelo
        with self.assertRaises(ValidationError, msg="Deve ser lançada uma ValidationError se a profundidade exceder o limite permitido."):
            self.env['foundation.estacas'].create({
                'nome_estaca': 'Estaca 002',
                'profundidade': 50,  # Supondo que 50 é maior que o limite permitido
                'data': '2024-01-01',
                'service_id': self.Servico.id,
                'sale_order_line_id': self.LinhaOrdemVenda.id
            })

# Parte final para inicialização do teste, se necessário.
if __name__ == '__main__':
    unittest.main()
