from odoo import models, fields, api

class ListaPresenca(models.Model):
    _name = 'foundation.lista.presenca'
    _description = 'Lista de Presença de Funcionários'

    chamada_id = fields.Many2one('foundation.chamada', string="Chamada", required=True)
    funcionario_id = fields.Many2one('res.partner', string="Funcionário", required=True)
    data = fields.Date(string="Data", default=fields.Date.today)
