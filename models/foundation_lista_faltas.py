from odoo import models, fields, api

class FoundationListaFaltas(models.Model):
    _name = 'foundation.lista.faltas'
    _description = 'Lista de Faltas'

    chamada_id = fields.Many2one('foundation.chamada', string="Chamada", required=True, ondelete="cascade")
    funcionario_id = fields.Many2one('hr.employee', string="Funcionário", required=True)
    maquina_id = fields.Many2one('foundation.maquina', string="Máquina", related='chamada_id.maquina_id', store=True)
    data = fields.Date(string="Data da Falta", related='chamada_id.data', store=True)
    observacao = fields.Text(string="Observação")  # Novo campo de observação

