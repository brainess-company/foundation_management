from odoo import models, fields

class FoundationMedicao(models.Model):
    _name = 'foundation.medicao'
    _description = 'Medições das Estacas'

    nome = fields.Char("Nome da Medição", required=True)
    valor_total = fields.Float("Valor Total", compute="_compute_valor_total", store=True)
    data = fields.Date("Data da Medição")
    situacao = fields.Selection([
        ('aguardando', 'Aguardando Conferência'),
        ('emissao', 'Aguardando Emissão de Nota')
    ], string="Situação", default='aguardando')
