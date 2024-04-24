from odoo import models, fields, api

class FoundationMaquinaRegistro(models.Model):
    _name = 'foundation.maquina.registro'
    _description = 'Registro de Máquinas para Serviços'

    service_id = fields.Many2one('foundation.obra.service', string="Serviço")
    maquina_id = fields.Many2one('foundation.maquina', string="Máquina")
    data_registro = fields.Date(string="Data de Registro", default=fields.Date.context_today)