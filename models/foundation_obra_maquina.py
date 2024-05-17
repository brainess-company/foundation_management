"""
    OBRAS RELACIONADAS COM ORDEM DE VENDAS

    """
import logging
from datetime import date
from odoo import models, fields, api

_logger = logging.getLogger(__name__)  # Configuração do logger


class FoundationObraMaquina(models.Model):
    """
    OBRAS RELACIONADAS COM ORDEM DE VENDAS

    """
    _name = 'foundation.obra.maquina'
    _description = 'Informações sobre a obra e maquina'
    _rec_name = 'nome_obra'

    # RELACIONA ESSA TABELA FOUNDATION OBRA COM  UMA SALE ORDER
    sale_order_id = fields.Many2one('sale.order',
                                    string="Ordem de Venda", required=True)

    maquina_id = fields.Many2one('foundation.maquina',
                                 string="Máquina Associada",
                                 readonly=True, store=True)
    operador_id = fields.Many2one('hr.employee', string="Operador",
                                  related='maquina_id.operador_id', readonly=True, store=True)

    nome_obra = fields.Char(related='sale_order_id.nome_obra',
                            store=True, readonly=True, string="Nome da Obra")

    has_today_chamada = fields.Boolean(string="Chamada Hoje?",
                                       compute="_compute_has_today_chamada", store=False)
    display_has_today_chamada = fields.Char(string="Fez Chamada Hoje?",
                                            compute='_compute_display_has_today_chamada',
                                            store=False)

    # Adicionar o campo relacionado requer_chamada
    requer_chamada_maquina = fields.Boolean(
        string="Requer Chamada?",
        related='maquina_id.requer_chamada',
        readonly=True,
        store=True
    )

    # Adicionando novo campo para armazenar o ID da conta analítica


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



