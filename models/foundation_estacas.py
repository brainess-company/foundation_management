from odoo import models, fields

class FoundationEstacas(models.Model):
    _name = 'foundation.estacas'
    _description = 'Estacas utilizadas na obra'

    foundation_obra_service_id = fields.Many2one('foundation.obra.service', string="Serviço na Obra", required=True)
    nome_estaca = fields.Char("Nome da Estaca", required=True)
    diametro = fields.Float("Diâmetro (cm)")
    profundidade = fields.Float("Profundidade (m)", required=True)
    data = fields.Date("Data")
    observacao = fields.Char("Observação")
