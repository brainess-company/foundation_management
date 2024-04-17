from odoo import models, fields

class FoundationMaquina(models.Model):
    _name = 'foundation.maquina'
    _description = 'Cadastro de Máquinas'
    _rec_name = 'nome_maquina'

    nome_maquina = fields.Char("Máquina")
    operador = fields.Many2one('res.partner', string="Operador")
    observacao = fields.Char("Observação")
