import logging
from datetime import date
from odoo import models, fields, api


class FoundationMaquinaObraRel(models.Model):
    _name = 'foundation.maquina.obra.rel'
    _description = 'Histórico de Relações entre Máquinas e Obras'

    maquina_id = fields.Many2one('foundation.maquina', string="Máquina", required=True, ondelete='cascade')
    obra_id = fields.Many2one('foundation.obra', string="Obra", ondelete='set null', help="Obra associada à máquina. Vazio se a máquina não estiver vinculada a nenhuma obra.")
    sale_order_id = fields.Many2one(
        'sale.order', string="Ordem de Venda",
        related='obra_id.sale_order_id', store=True, readonly=True,
        help="Ordem de Venda associada à obra no momento do registro."
    )
    status_maquina = fields.Selection([
        ('em_mobilizacao', 'Em Mobilização'),
        ('sem_obra', 'Sem Obra'),
        ('parada', 'Máquina Parada'),
        ('em_manutencao', 'Em Manutenção'),
        ('disponivel', 'Disponível')
    ], string="Status da Máquina")
    data_registro = fields.Datetime(string="Data do Registro", required=True, default=fields.Datetime.now)
    observacao = fields.Text(string="Observação", help="Detalhes adicionais sobre o registro.")
