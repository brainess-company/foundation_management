from odoo import models, fields

class FoundationMaquina(models.Model):
    _name = 'foundation.maquina'
    _description = 'Cadastro de Máquinas'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Herdar de mail.thread e mail.activity.mixin
    _rec_name = 'nome_maquina'

    nome_maquina = fields.Char("Máquina", track_visibility='onchange')
    operador = fields.Many2one('res.partner', string="Operador", track_visibility='onchange')
    observacao = fields.Char("Observação")
