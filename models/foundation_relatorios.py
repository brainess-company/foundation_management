"""Lançamento em lote de estacas"""
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import translate

_logger = logging.getLogger(__name__)


class FoundationRelatorios(models.Model):
    """FALTA CRIAR AS OUTRAS ACTIONS PARA OS STATUS E INCLUIR BOTOUS NO FORMULARIO"""
    _name = 'foundation.relatorios'
    _description = 'Relatórios de Fundação'
    _rec_name = 'display_relatorio_name'

    # CAMPOS PROPRIOS
    data = fields.Date("Data do Relatório",
                       default=fields.Date.context_today, required=True, store=True)
    estacas_ids = fields.One2many('foundation.estacas', 'relatorio_id',
                                  string="Estacas Incluídas")
    assinatura = fields.Binary("Assinatura do Responsável",
                               help="Assinatura digital do responsável pelo relatório")
    state = fields.Selection([
        ('rascunho', 'Rascunho'),
        ('conferencia', 'Aguardando Conferencia'),
        ('em_analise', 'Em Análise'),
        ('cancelado', 'Cancelado'),
        ('conferido', 'Conferido')
    ], default='rascunho', string="Status", required=True)
    # todo verificar as implicações disso

    # Campos adicionais relacionados ao serviço
    nome_servico = fields.Char(related='foundation_maquina_registro_id.nome_servico',
                               string="Nome do Serviço",
                               readonly=True, store=True)
    maquina_id = fields.Many2one('foundation.maquina',
                                 related='foundation_maquina_registro_id.maquina_id',
                                 string="Máquina Associada",
                                 readonly=True, store=True)
    nome_obra = fields.Char(related='foundation_maquina_registro_id.nome_obra',
                            string="Nome da Obra", readonly=True, store=True)
    endereco_obra = fields.Char(related='foundation_maquina_registro_id.endereco',
                                string="Endereço da Obra", readonly=True, store=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order",
                                    related='foundation_maquina_registro_id.sale_order_id',
                                    readonly=True, store=True)
    service_template_id = fields.Many2one('product.template',
                                          string="Template do Serviço",
                                          related='service_id.service_template_id',
                                          readonly=True, store=True, required=True)
    service_id = fields.Many2one('foundation.obra.service',
                                 related='foundation_maquina_registro_id.service_id',
                                 string="Serivice id", readonly=True, store=True)
    variante_id = fields.Many2one('product.product', string="Variante")
    foundation_maquina_registro_id = fields.Many2one(
        'foundation.maquina.registro', dstring='Registro de Máquina',
        required=True, help='Referência ao registro de máquina associado.')
    operador_id = fields.Many2one(related='foundation_maquina_registro_id.operador_id',
                                  string="Operador", readonly=True, store=True)

    relatorio_number = fields.Char(string="Nome do Relatório")
    display_relatorio_name = fields.Char(compute="_compute_display_relatorio_name",
                                         string="Nome de Exibição do Relatório", store=True)

    # Adicionar o campo relacionado requer_chamada
    requer_chamada_maquina = fields.Boolean(string="Requer Chamada?",
                                            related='maquina_id.requer_chamada',
                                            readonly=True, store=True)

    @api.depends('relatorio_number', 'service_id', 'nome_obra')
    def _compute_display_relatorio_name(self):
        """computa o nome do relatorio"""
        for record in self:
            if record.relatorio_number and record.service_id and record.nome_obra:
                record.display_relatorio_name = f"REL{record.relatorio_number} - \
                    {record.service_id.service_name} - {record.nome_obra}"

    @api.model
    def create(self, vals):
        if not vals.get('assinatura'):
            raise UserError("A assinatura é obrigatória para a criação de um relatório.")

        # Verificar o último número de relatório para o registro de máquina específico
        last_report = self.search([
            ('foundation_maquina_registro_id', '=', vals.get('foundation_maquina_registro_id'))
        ], order='id desc', limit=1)
        next_number = 1
        if last_report:
            # Ajustar para obter o número do último relatório e incrementar
            if last_report.relatorio_number.isdigit():
                next_number = int(last_report.relatorio_number) + 1
        vals['relatorio_number'] = str(next_number)

        new_record = super(FoundationRelatorios, self).create(vals)

        # Obter o registro de máquina associado para verificar se requer chamada
        maquina_registro = new_record.foundation_maquina_registro_id

        # Corrigindo a verificação de 'requer_chamada'
        if maquina_registro.maquina_id and not maquina_registro.maquina_id.requer_chamada:
            # Se a máquina não requer chamada, criar uma nova chamada
            chamada_vals = {
                'foundation_maquina_registro_id': maquina_registro.id,
                'data': fields.Date.today(),
                'foundation_obra_service_id': maquina_registro.service_id.id,
                'maquina_id': maquina_registro.maquina_id.id,
                'obra_id': maquina_registro.service_id.obra_id.id,
                'nome_obra': maquina_registro.nome_obra,
                'endereco': maquina_registro.endereco,
            }
            nova_chamada = self.env['foundation.chamada'].create(chamada_vals)

            # Adicionar o operador da máquina à chamada, se disponível
            if maquina_registro.maquina_id.operador_id:
                self.env['foundation.lista.presenca'].create({
                    'chamada_id': nova_chamada.id,
                    'funcionario_id': maquina_registro.maquina_id.operador_id.id,
                    'data': fields.Date.today(),
                })

        return new_record

    def action_confirm(self):
        """action confirm relatorio"""
        self.write({'state': 'conferido'})

    def action_cancel(self):
        """action cancel relatorio"""
        self.write({'state': 'cancelado'})

    def action_draft(self):
        """action draft relatorio"""
        self.write({'state': 'rascunho'})

    @api.constrains('estacas_ids')
    def _check_estacas(self):
        """verifica profundidade das estacas"""
        if any(not estaca.profundidade for estaca in self.estacas_ids):
            raise UserError("Todas as estacas devem ter a profundidade definida.")

    def action_save(self):
        """action save relatorio"""
        _logger.info('CONTEXTO ATUAL ACTION SAVE DE FOUNDATION RL: %s', self.env.context)
        self.ensure_one()
        if not self.assinatura:
            # raise UserError("A assinatura é necessária para salvar o relatório.")
            raise UserError(
                translate._("A assinatura é obrigatória para a criação de um relatório."))
        _logger.info('CONTEXTO ATUAL ATUAL PARA CRIAR RELATORIO 2: %s', self.env.context)
        self.state = 'conferencia'
        # Supondo que haja um campo de estado para controlar a confirmação do relatório
        return {
            'type': 'ir.actions.act_window',
            'name': 'Relatório Confirmado',
            'view_mode': 'form',
            'res_model': 'foundation.relatorios',
            'res_id': self.id,
            'target': 'current'
        }
