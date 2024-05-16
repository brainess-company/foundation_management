from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    nome_obra = fields.Char("Nome da Obra", required=True)
    specific_stock_location_id = fields.Many2one('stock.location',
                                                 string="Local de Estoque Específico",
                                                 readonly=True)
    specific_stock_output_id = fields.Many2one('stock.location', string="Local de Estoque de Saída",
                                               readonly=True)
    analytic_account_ids = fields.One2many('account.analytic.account', 'sale_order_id',
                                           string="Contas Analíticas")



    def _ensure_central_stock_location(self):
        """Verifica e cria um estoque central se não existir."""
        StockLocation = self.env['stock.location']
        central_stock = StockLocation.search([
            ('name', '=', 'ESTOQUE CENTRAL'),
            ('company_id', '=', False),
            ('usage', '=', 'internal')
        ], limit=1)

        if central_stock:
            _logger.info("Estoque Central já existente: %s", central_stock.name)
        else:
            central_stock = StockLocation.create({
                'name': 'ESTOQUE CENTRAL',
                'usage': 'internal',
                'location_id': self.env.ref('stock.stock_location_locations').id,
                # Base physical location
                'company_id': False  # No company to make it shared
            })
            _logger.info("Estoque Central criado: %s", central_stock.name)
        return central_stock



    def _create_specific_stock_location(self):
        """Cria um estoque específico para esta sale.order."""
        stock_name = f"ESTOQUE {self.nome_obra} - {self.name}"
        specific_stock = self.env['stock.location'].create({
            'name': stock_name,
            'usage': 'internal',
            'location_id': False,  # Este estoque não deve ser aninhado
            'company_id': False  # Sem associação de empresa
        })
        _logger.info("Estoque específico criado para a Sale Order %s: %s", self.name, stock_name)
        return specific_stock

    def _create_specific_output_stock_location(self):
        """Cria um estoque de saída aninhado ao estoque específico."""
        output_stock_name = "SAÍDA DE ESTOQUE"
        specific_output_stock = self.env['stock.location'].create({
            'name': output_stock_name,
            'usage': 'production',  # Assume que este estoque será para saída de produção
            'location_id': self.specific_stock_location_id.id,  # Aninhado sob o estoque específico
            'company_id': False
        })
        _logger.info("Estoque de saída criado para a Sale Order %s: %s", self.name, output_stock_name)
        return specific_output_stock

    def _update_specific_output_stock_location_name(self):
        """Atualiza apenas o nome do estoque de saída."""
        output_stock_name = "SAÍDA DE ESTOQUE"
        if self.specific_stock_output_id:
            self.specific_stock_output_id.write({'name': output_stock_name})
            _logger.info("Nome do Estoque de saída atualizado para a Sale Order %s: %s", self.name,
                         output_stock_name)

    def _update_specific_stock_location_name(self):
        """Atualiza apenas o nome do estoque específico."""
        stock_name = f"ESTOQUE {self.nome_obra} - {self.name}"
        if self.specific_stock_location_id:
            self.specific_stock_location_id.write({'name': stock_name})
            _logger.info("Nome do Estoque específico atualizado para a Sale Order %s: %s",
                         self.name, stock_name)
            
    # Exemplo de uso destes métodos em create e write seria adaptado aqui

    def _create_foundation_obra_and_services(self):
        """para cada serviço na sale order cria um registro aqui"""
        foundation_obra = self.env['foundation.obra']
        foundation_obra_service = self.env['foundation.obra.service']
        # Assuming this is how you access the machine model
        plan_model = self.env['account.analytic.plan']

        _logger.info("Checking for existing 'DESPESAS' plan")
        expense_plan = plan_model.search([('name', '=', 'DESPESAS')], limit=1)
        if not expense_plan:
            _logger.info("'DESPESAS' plan not found, creating new one")
            expense_plan = plan_model.create({
                'name': 'DESPESAS'
            })

        for order in self:
            # Ensure there is an 'obra' for the sale order
            obra = foundation_obra.search([('sale_order_id', '=', order.id)], limit=1)
            if not obra:
                obra = foundation_obra.create({
                    'sale_order_id': order.id
                })

            # Create a service for each unique product template
            template_lines = {}
            for line in order.order_line:
                # Verifica se a linha não está em branco
                if line.product_id:
                    template = line.product_id.product_tmpl_id
                    if template not in template_lines:
                        template_lines[template] = line

            for template, line in template_lines.items():
                if not foundation_obra_service.search([
                    ('variante_id', '=', line.product_id.id),
                    ('obra_id', '=', obra.id)
                ], limit=1):
                    foundation_obra_service.create({
                        'variante_id': line.product_id.id,
                        'obra_id': obra.id
                    })

    def _create_or_update_analytic_accounts(self):
        """ Cria ou atualiza contas analíticas baseadas na ordem de venda e em cada template de produto único """
        AnalyticAccount = self.env['account.analytic.account']
        plan_model = self.env['account.analytic.plan']
        expense_plan = plan_model.search([('name', '=', 'DESPESAS')], limit=1)

        if not expense_plan:
            expense_plan = plan_model.create({'name': 'DESPESAS'})
            _logger.info("Plano 'DESPESAS' criado: %s", expense_plan.id)

        # Conta geral para a Sale Order
        general_account_name = f"{self.nome_obra} - {self.name}"
        general_account = AnalyticAccount.search([
            ('name', '=', general_account_name),
            ('sale_order_id', '=', self.id)
        ], limit=1)

        if not general_account:
            general_account = AnalyticAccount.create({
                'name': general_account_name,
                'company_id': self.company_id.id,
                'sale_order_id': self.id,
                'plan_id': expense_plan.id  # Definindo plan_id aqui
            })
            _logger.info("Conta analítica criada para a ordem de venda: %s", general_account.name)
        else:
            _logger.info("Conta analítica geral já existe e foi atualizada: %s",
                         general_account.name)

        # Contas para cada template de produto distinto
        product_templates = {line.product_id.product_tmpl_id for line in self.order_line}
        for template in product_templates:
            account_name = f"{self.nome_obra} - {template.name}"
            analytic_account = AnalyticAccount.search([
                ('name', '=', account_name),
                ('sale_order_id', '=', self.id)
            ], limit=1)

            if not analytic_account:
                analytic_account = AnalyticAccount.create({
                    'name': account_name,
                    'company_id': self.company_id.id,
                    'plan_id': expense_plan.id,  # Definindo plan_id aqui
                    'sale_order_id': self.id
                })
                _logger.info("Conta analítica criada: %s", analytic_account.name)
            else:
                analytic_account.write({
                    'company_id': self.company_id.id,  # Atualize campos relevantes se necessário
                    'plan_id': expense_plan.id  # Assegurar que plan_id é atualizado se necessário
                })
                _logger.info("Conta analítica já existe e foi atualizada: %s",
                             analytic_account.name)

    @api.model
    def create(self, vals):
        order = super().create(vals)

        # Crie e associe um local de estoque específico
        specific_stock_location = order._create_specific_stock_location()
        order.specific_stock_location_id = specific_stock_location.id

        # Crie e associe um local de saída específico
        specific_output_stock_location = order._create_specific_output_stock_location()
        order.specific_stock_output_id = specific_output_stock_location.id

        # Realize outras operações após a criação dos estoques
        order._ensure_central_stock_location()
        order._create_foundation_obra_and_services()
        order._create_or_update_analytic_accounts()

        return order

    def write(self, vals):
        res = super().write(vals)

        for order in self:
            # Atualize apenas os nomes, mantendo os IDs intactos
            order._update_specific_stock_location_name()
            order._update_specific_output_stock_location_name()

            if 'state' in vals and vals.get('state') == 'sale':
                order._ensure_central_stock_location()
                order._create_foundation_obra_and_services()
                order._create_or_update_analytic_accounts()

        return res
