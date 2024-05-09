import logging
from odoo.exceptions import ValidationError, UserError
from odoo.tests import common

_logger = logging.getLogger(__name__)


class TestFoundationEstacas(common.TransactionCase):

    def setUp(self):
        super(TestFoundationEstacas, self).setUp()

        # Criação de uma empresa
        self.company = self.env['res.company'].create({
            'name': 'Empresa Teste',
            'currency_id': self.env.ref('base.USD').id,
            'fiscalyear_last_day': 31,
            'fiscalyear_last_month': 12,
        })

        # Criação de um parceiro e usuário associado
        self.partner = self.env['res.partner'].create({
            'name': 'Parceiro Teste',
            'company_id': self.company.id,
        })

        self.user = self.env['res.users'].create({
            'login': 'test_environment_demo',
            'partner_id': self.partner.id,
            'notification_type': 'email',  # Define diretamente a seleção 'email'
            'company_id': self.company.id,
        })

        # Criação de um serviço de obra
        self.sale_order = self.env['sale.order'].create({
            'name': 'SO Teste',
            'company_id': self.company.id,
        })

        self.obra_service = self.env['foundation.obra.service'].create({
            'name': 'Serviço Teste',
            'sale_order_id': self.sale_order.id,
        })

        self.sale_order_line = self.env['sale.order.line'].create({
            'order_id': self.sale_order.id,
            'product_id': self.env['product.product'].create({
                'name': 'Produto Teste'
            }).id,
            'price_unit': 10.0,
        })

        self.medicao = self.env['foundation.medicao'].create({
            'nome': '1',
            'sale_order_id': self.sale_order.id,
        })

        self.maquina_registro = self.env['foundation.maquina.registro'].create({
            'name': 'Registro Teste',
        })

        # Dados da estaca
        self.estaca_vals = {
            'nome_estaca': 'Estaca Teste',
            'profundidade': 10.0,
            'service_id': self.obra_service.id,
            'sale_order_line_id': self.sale_order_line.id,
            'foundation_maquina_registro_id': self.maquina_registro.id,
        }

    def test_create_estaca(self):
        """Testa a criação de uma estaca e valida se a quantidade entregue é atualizada."""
        estaca = self.env['foundation.estacas'].create(self.estaca_vals)
        self.assertEqual(estaca.sale_order_line_id.qty_delivered, 10.0)
        self.assertEqual(estaca.total_price, 100.0)

    def test_write_estaca(self):
        """Testa a atualização da profundidade de uma estaca e valida se a quantidade entregue é atualizada."""
        estaca = self.env['foundation.estacas'].create(self.estaca_vals)
        estaca.write({'profundidade': 20.0})
        self.assertEqual(estaca.sale_order_line_id.qty_delivered, 20.0)
        self.assertEqual(estaca.total_price, 200.0)

    def test_create_estaca_invalid_profundidade(self):
        """Testa a criação de uma estaca com profundidade inválida."""
        with self.assertRaises(ValidationError):
            self.env['foundation.estacas'].create({**self.estaca_vals, 'profundidade': 50.0})

    def test_action_generate_medicao(self):
        """Testa a geração de uma nova medição a partir das estacas selecionadas."""
        estaca1 = self.env['foundation.estacas'].create({**self.estaca_vals, 'medicao_id': False})
        estaca2 = self.env['foundation.estacas'].create({**self.estaca_vals, 'medicao_id': False})

        action = estaca1.action_generate_medicao()
        new_medicao = self.env['foundation.medicao'].browse(action['res_id'])

        self.assertEqual(new_medicao.situacao, 'aguardando')
        self.assertEqual(estaca1.medicao_id, new_medicao)
        self.assertEqual(estaca2.medicao_id, new_medicao)

    def test_action_generate_medicao_with_existing_medicao(self):
        """Testa a tentativa de medir novamente uma estaca já medida."""
        estaca = self.env['foundation.estacas'].create({**self.estaca_vals, 'medicao_id': self.medicao.id})
        with self.assertRaises(UserError):
            estaca.action_generate_medicao()

    def test_toggle_active(self):
        """Testa o método toggle_active para ativar/desativar uma estaca."""
        estaca = self.env['foundation.estacas'].create(self.estaca_vals)
        estaca.toggle_active()
        self.assertFalse(estaca.active)
        estaca.toggle_active()
        self.assertTrue(estaca.active)

    def test_display_medicao(self):
        """Testa o cálculo do campo computado display_medicao."""
        estaca = self.env['foundation.estacas'].create({**self.estaca_vals, 'medicao_id': self.medicao.id})
        self.assertEqual(estaca.display_medicao, "Medição 1")

        estaca.write({'medicao_id': False})
        self.assertEqual(estaca.display_medicao, "")

    def test_compute_line_values(self):
        """Testa o cálculo dos campos computados unit_price e total_price."""
        estaca = self.env['foundation.estacas'].create(self.estaca_vals)
        self.assertEqual(estaca.unit_price, 10.0)
        self.assertEqual(estaca.total_price, 100.0)

        estaca.write({'profundidade': 20.0})
        self.assertEqual(estaca.total_price, 200.0)
