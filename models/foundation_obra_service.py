"""
Este modelo representa os serviços associados a uma obra específica dentro do sistema.
Ele rastreia os detalhes dos serviços oferecidos, as máquinas utilizadas, e as estacas
envolvidas em cada serviço. Este modelo serve como um núcleo para conectar diferentes
aspectos de uma obra, como máquinas, estacas e as informações comerciais associadas.

"""

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class FoundationObraService(models.Model):
    """
        Este modelo representa os serviços associados a uma obra específica dentro do sistema.
        Ele rastreia os detalhes dos serviços oferecidos, as máquinas utilizadas, e as estacas
        envolvidas em cada serviço. Este modelo serve como um núcleo para conectar diferentes
        aspectos de uma obra, como máquinas, estacas e as informações comerciais associadas.

        Atributos:
            variante_id (Many2one): Identificador da variante do produto/serviço utilizado no serviço.
            service_template_id (Many2one): Template do serviço relacionado à variante escolhida.
            service_name (Char): Nome do serviço, extraído da variante do produto.
            foundation_maquina_ids (Many2many): Máquinas associadas a este serviço.
            obra_id (Many2one): Obra na qual o serviço está sendo executado.
            sale_order_id (Many2one): Ordem de venda associada à obra.
            nome_obra (Char): Nome da obra, derivado da referência da obra.
            endereco (Char): Endereço da obra, também derivado da referência da obra.
            estacas_ids (One2many): Estacas relacionadas a este serviço específico.
            maquina_registros_ids (One2many): Registros de máquinas associados a este serviço.
        """
    # Configurações básicas do modelo
    _name = 'foundation.obra.service'
    _description = 'Serviços em uma obra'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'service_name'

    # Definição dos campos
    variante_id = fields.Many2one('product.product', string="Variante")
    service_template_id = fields.Many2one('product.template', string="Template do Serviço", related='variante_id.product_tmpl_id', readonly=True, store=True)
    service_name = fields.Char("Nome do Serviço", related='variante_id.name', store=True)
    foundation_maquina_ids = fields.Many2many('foundation.maquina', string="Máquinas Associadas")
    obra_id = fields.Many2one('foundation.obra', string="Obra")
    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", related='obra_id.sale_order_id', readonly=True, store=True)
    nome_obra = fields.Char("Nome da Obra", related='obra_id.nome_obra', readonly=True, store=True)
    endereco = fields.Char("Endereço", related='obra_id.endereco', readonly=True, store=True)
    estacas_ids = fields.One2many('foundation.estacas', 'service_id', string="Estacas")

    maquina_registros_ids = fields.One2many(
        'foundation.maquina.registro',  # Modelo relacionado
        'service_id',  # Campo inverso em FoundationMaquinaRegistro
        string="Registros de Máquinas"
    )

    @api.model
    def create(self, vals):
        """METODO PARA CRIAR MAQUINA"""
        _logger.debug("Creating new FoundationObraService record with values: %s", vals)
        new_record = super().create(vals)
        self._create_machine_records(new_record, new_record.foundation_maquina_ids)
        return new_record

    def write(self, vals):
        """METODO PARA EDITAR MAQUINA"""
        _logger.debug("Writing to FoundationObraService record with values: %s", vals)
        result = super().write(vals)
        if 'foundation_maquina_ids' in vals:
            self._create_machine_records(self, self.foundation_maquina_ids)
        return result

    def _create_machine_records(self, service, maquinas):
        """METODO PARA CRIAR MAQUINA - PARECE REDUNDANTE"""
        _logger.debug("Creating machine records for service %s", service.id)
        MaquinaRegistro = self.env['foundation.maquina.registro']
        for maquina in maquinas:
            _logger.debug("Processing machine %s", maquina.id)
            existing_record = MaquinaRegistro.search([('service_id', '=', service.id), ('maquina_id', '=', maquina.id)], limit=1)
            if existing_record:
                _logger.info("Updating existing machine record for machine %s", maquina.id)
                existing_record.write({
                    'service_id': service.id,
                    'maquina_id': maquina.id,
                })
            else:
                _logger.info("Creating new machine record for machine %s", maquina.id)
                MaquinaRegistro.create({
                    'service_id': service.id,
                    'maquina_id': maquina.id,
                })

        self._create_or_update_analytic_accounts(service, maquinas)

    def _create_or_update_analytic_accounts(self, service, maquinas):
        """CRUAR OU EDITAR CONTA ANALITICA"""
        MaquinaRegistro = self.env['foundation.maquina.registro']
        AnalyticAccount = self.env['account.analytic.account']
        Plan = self.env['account.analytic.plan']

        _logger.info("Checking for existing 'DESPESAS' plan")
        expense_plan = Plan.search([('name', '=', 'DESPESAS')], limit=1)
        if not expense_plan:
            _logger.info("'DESPESAS' plan not found, creating new one")
            expense_plan = Plan.create({
                'name': 'DESPESAS'
            })

        multiple_machines = len(maquinas) > 1
        _logger.debug(f"Processing {len(maquinas)} machines, multiple_machines={multiple_machines}")

        for maquina in maquinas:
            _logger.debug(f"Processing machine {maquina.id}")
            # Procura por um registro existente ou cria um novo
            maquina_registro = MaquinaRegistro.search(
                [('service_id', '=', service.id), ('maquina_id', '=', maquina.id)], limit=1)
            if not maquina_registro:
                maquina_registro = MaquinaRegistro.create({
                    'service_id': service.id,
                    'maquina_id': maquina.id,
                })

            account_name = f"{service.nome_obra} - {service.service_name} - {maquina.nome_maquina}"
            _logger.debug(f"Looking for existing analytic account for machine {maquina.id}")
            existing_account = AnalyticAccount.search([('foundation_maquina_registro_id', '=', maquina_registro.id)],
                                                      limit=1)

            if existing_account:
                _logger.info(f"Updating existing account {existing_account.id}")
                existing_account.write({
                    'name': account_name
                })
            else:
                _logger.info(f"Creating new analytic account for machine {maquina.id}")
                AnalyticAccount.create({
                    'name': account_name,
                    'partner_id': service.obra_id.partner_id.id if service.obra_id.partner_id else None,
                    'company_id': self.env.company.id,
                    'plan_id': expense_plan.id,
                    'foundation_maquina_registro_id': maquina_registro.id
                })

        if multiple_machines:
            service_account_name = f"{service.nome_obra} - {service.service_name}"
            _logger.debug("Checking for existing service account")
            service_account = AnalyticAccount.search(
                [('name', '=', service_account_name), ('foundation_maquina_registro_id', '=', False)], limit=1)
            if service_account:
                _logger.info("Updating service account")
                service_account.write({'name': service_account_name})
            else:
                _logger.info("Creating new service account")
                AnalyticAccount.create({
                    'name': service_account_name,
                    'partner_id': service.obra_id.partner_id.id if service.obra_id.partner_id else None,
                    'company_id': self.env.company.id,
                    'plan_id': expense_plan.id
                })

        obra_account_name = f"{service.nome_obra}"
        _logger.debug("Checking for existing obra account")
        obra_account = AnalyticAccount.search(
            [('name', '=', obra_account_name), ('foundation_maquina_registro_id', '=', False)], limit=1)
        if obra_account:
            _logger.info("Updating obra account")
            obra_account.write({'name': obra_account_name})
        else:
            _logger.info("Creating new obra account")
            AnalyticAccount.create({
                'name': obra_account_name,
                'partner_id': service.obra_id.partner_id.id if service.obra_id.partner_id else None,
                'company_id': self.env.company.id,
                'plan_id': expense_plan.id
            })

