from odoo import models, fields

class FoundationMaquina(models.Model):
    _name = 'foundation.maquina'
    _description = 'Cadastro de Máquinas'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Herdar de mail.thread e mail.activity.mixin
    _rec_name = 'nome_maquina'

    nome_maquina = fields.Char("Máquina",  tracking=True)
    operador = fields.Many2one('res.partner', string="Operador",  tracking=True)
    observacao = fields.Char("Observação")
