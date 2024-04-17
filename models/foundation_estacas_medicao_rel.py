from odoo import models, fields


class FoundationEstacasMedicaoRel(models.Model):
    _name = 'foundation.estacas.medicao.rel'
    _description = 'Relação Estaca-Medição'

    foundation_estacas_id = fields.Many2one('foundation.estacas', string="Estaca", required=True)
    foundation_medicao_id = fields.Many2one('foundation.medicao', string="Medição", required=True)
    valor = fields.Char("Valor")
    #valor = fields.Float("Valor Calculado", compute="_compute_valor")

