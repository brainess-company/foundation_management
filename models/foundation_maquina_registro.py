"""
Gerencia registros automáticos de máquinas associadas
    a serviços específicos em obras.
    Este modelo serve como uma ligação entre máquinas e os serviços realizados,
    permitindo rastrear a utilização de cada máquina em diferentes fases da obra.
"""
import logging
from datetime import date
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class FoundationMaquinaRegistro(models.Model):
    """
    Gerencia registros automáticos de máquinas associadas
    a serviços específicos em obras.
    Este modelo serve como uma ligação entre máquinas e os serviços realizados,
    permitindo rastrear
    a utilização de cada máquina em diferentes fases da obra.

    Cada registro nesta tabela representa uma associação única entre uma máquina e um serviço
    dentro de uma obra, com detalhes complementares sobre a obra, serviço,
    e a máquina utilizada.
    Isso facilita o monitoramento e a gestão eficaz dos recursos em projetos de construção.

    Atributos:
        data_registro (Date): Data de criação do registro.
        service_id (Many2one): Referência ao serviço associado na obra.
        nome_servico (Char): Nome do serviço associado, extraído da referência do serviço.
        obra_id (Many2one): Referência à obra associada ao serviço.
        sale_order_id (Many2one): Ordem de venda associada ao serviço.
        nome_obra (Char): Nome da obra associada ao serviço.
        endereco (Char): Endereço da obra associada ao serviço.
        variante_id (Many2one): Variante do produto/serviço utilizado.
        service_template_id (Many2one): Template do serviço associado.
        maquina_id (Many2one): Máquina utilizada no serviço.
        operador_id (Many2one): Operador da máquina, determinado dinamicamente.
        estacas_ids (One2many): Estacas relacionadas a este registro de máquina.
        has_today_chamada (Boolean): Indica se houve uma chamada no dia atual.
        display_has_today_chamada (Char): Descrição textual do status da chamada no dia atual.
        product_id (Many2one): Produto associado à máquina.
        product_template_id (Many2one): Template do produto associado.
        requer_chamada_maquina (Boolean): Indica se a máquina requer chamada,
        baseado nas propriedades da máquina.
    """

    _name = 'foundation.maquina.registro'
    _description = 'Registro de Máquinas para Serviços'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Herdar de mail.thread e mail.activity.mixin
    # _rec_name = 'nome_maquina'

    data_registro = fields.Date(string="Data de Registro", default=fields.Date.context_today)

    # RELACIONA ESSA TABELA COM A DE SERVIÇO
    service_id = fields.Many2one('foundation.obra.service', string="Serviço")
    nome_servico = fields.Char(related='service_id.service_name',
                               string="Nome do Serviço", readonly=True, store=True)
    obra_id = fields.Many2one('foundation.obra', related='service_id.obra_id',
                              string="Obra id", readonly=True, store=True)
    sale_order_id = fields.Many2one('sale.order', related='service_id.sale_order_id',
                                    string="Ordem de Venda", readonly=True, store=True)
    nome_obra = fields.Char(related='service_id.nome_obra',
                            string="Nome da Obra", readonly=True, store=True)
    endereco = fields.Char(related='service_id.endereco',
                           string="Endereço", readonly=True,  store=True)

    # Campos relacionados à definição de produto/serviço
    variante_id = fields.Many2one('product.product', related='service_id.variante_id',
                                  string="Variante", readonly=True, store=True)
    service_template_id = fields.Many2one('product.template',
                                          related='service_id.service_template_id',
                                          string="Template do Serviço", readonly=True, store=True)

    maquina_id = fields.Many2one('foundation.maquina', string="Máquina")
    operador_id = fields.Many2one('hr.employee', string="Operador",
                                  compute='_compute_operador', store=True)

    # CAMPO INVERSO PARA MOSTRAR ESTACA RELACIONADA COM ESSE SERVIÇO
    estacas_ids = fields.One2many('foundation.estacas', 'foundation_maquina_registro_id',
                                  string="Estacas")  # tracking=True
    has_today_chamada = fields.Boolean(string="Chamada Hoje?",
                                       compute="_compute_has_today_chamada", store=False)
    display_has_today_chamada = fields.Char(string="Fez Chamada Hoje?",
                                            compute='_compute_display_has_today_chamada',
                                            store=False)

    product_id = fields.Many2one('product.product', string="Produto Associado")
    product_template_id = fields.Many2one('product.template', string="Template do Produto",
                                          related='product_id.product_tmpl_id',
                                          readonly=True, store=True)
    # Adicionar o campo relacionado requer_chamada
    requer_chamada_maquina = fields.Boolean(
        string="Requer Chamada?",
        related='maquina_id.requer_chamada',
        readonly=True,
        store=True
    )

    # Adicionando novo campo para armazenar o ID da conta analítica
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Conta Analítica",
        readonly=True,
        help="Referência à conta analítica criada para este registro de máquina."
    )

    # Novos campos para locais de estoque específicos e de saída
    specific_stock_location_id = fields.Many2one('stock.location',
                                                 related='sale_order_id.specific_stock_location_id',
                                                 string="Local de Estoque Específico",
                                                 readonly=True)
    specific_stock_output_id = fields.Many2one('stock.location',
                                               related='sale_order_id.specific_stock_output_id',
                                               string="Local de Estoque de Saída", readonly=True)

    def _create_or_update_analytic_accounts(self, service, maquinas):
        """CRUAR OU EDITAR CONTA ANALITICA"""
        maquina_registro_model = self.env['foundation.maquina.registro']
        analytic_account_model = self.env['account.analytic.account']
        plan_model = self.env['account.analytic.plan']

        _logger.info("Checking for existing 'DESPESAS' plan")
        expense_plan = plan_model.search([('name', '=', 'DESPESAS')], limit=1)
        if not expense_plan:
            _logger.info("'DESPESAS' plan not found, creating new one")
            expense_plan = plan_model.create({
                'name': 'DESPESAS'
            })

        multiple_machines = len(maquinas) > 1
        _logger.debug("Processing %d machines, multiple_machines=%s", len(maquinas),
                      multiple_machines)

        # sua lógica existente...
        for maquina in maquinas:
            maquina_registro = self.env['foundation.maquina.registro'].search(
                [('service_id', '=', service.id), ('maquina_id', '=', maquina.id)], limit=1)
            if not maquina_registro:
                maquina_registro = self.env['foundation.maquina.registro'].create({
                    'service_id': service.id,
                    'maquina_id': maquina.id,
                })

            account_name = f"{service.nome_obra} - {service.service_name} - {maquina.nome_maquina}"

            existing_account = self.env['account.analytic.account'].search(
                [('foundation_maquina_registro_id', '=', maquina_registro.id)], limit=1)

            if existing_account:
                existing_account.write({
                    'name': account_name
                })
            else:
                new_account = self.env['account.analytic.account'].create({
                    'name': account_name,
                    'partner_id': service.obra_id.partner_id.id if service.obra_id.partner_id else None,
                    'company_id': self.env.company.id,
                    'plan_id': expense_plan.id,
                    'foundation_maquina_registro_id': maquina_registro.id
                })
                maquina_registro.analytic_account_id = new_account.id

    @api.depends('has_today_chamada', 'requer_chamada_maquina')
    def _compute_display_has_today_chamada(self):
        for record in self:
            if record.requer_chamada_maquina:  # Verifica se a máquina requer chamada
                if record.has_today_chamada:
                    record.display_has_today_chamada = "Sim"
                else:
                    record.display_has_today_chamada = "Não"
            else:
                record.display_has_today_chamada = ""  # Deixa em branco se não requer chamada

    def _compute_has_today_chamada(self):
        """calcula se tem chamada registrada hoje"""
        for record in self:
            today_chamadas = self.env['foundation.chamada'].search([
                ('foundation_maquina_registro_id', '=', record.id),
                ('data', '=', date.today())
            ])
            record.has_today_chamada = bool(today_chamadas)
            _logger.info(
                f"Computing has_today_chamada for record {record.id}: {record.has_today_chamada}")

    @api.depends('maquina_id')
    def _compute_operador(self):
        """conputa o nome do operador associado"""
        for record in self:
            # Assumindo que 'operador' é um campo em 'foundation.maquina'
            record.operador_id = record.maquina_id.operador if record.maquina_id else False
