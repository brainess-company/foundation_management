from odoo import models, fields

class FoundationMaquina(models.Model):
    _name = 'foundation.maquina'
    _description = 'Cadastro de Máquinas'

    operador = fields.Many2one('res.partner', string="Operador")
    observacao = fields.Char("Observação")
