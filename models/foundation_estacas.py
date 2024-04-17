from odoo import models, fields, api

class FoundationEstacas(models.Model):
    _name = 'foundation.estacas'
    _description = 'Estacas utilizadas na obra'

    foundation_obra_service_id = fields.Many2one(
        'foundation.obra.service', string="Serviço na Obra", required=True)
    nome_estaca = fields.Char("Nome da Estaca", required=True)
    diametro = fields.Selection(
        selection='_compute_diametros', string="Diâmetro (cm)",
        help="Diâmetros disponíveis baseados nas variantes do produto na Ordem de Venda relacionada.")
    profundidade = fields.Float("Profundidade (m)", required=True)
    data = fields.Date("Data")
    observacao = fields.Char("Observação")

    @api.depends('foundation_obra_service_id')
    def _compute_diametros(self):
        for record in self:
            res = []
            if record.foundation_obra_service_id and record.foundation_obra_service_id.sale_order_id:
                sale_order = record.foundation_obra_service_id.sale_order_id
                product_ids = sale_order.order_line.mapped('product_id').filtered(lambda p: p.product_tmpl_id == record.foundation_obra_service_id.service_id.product_tmpl_id)
                res = [(str(product.id), product.display_name) for product in product_ids]
            record.diametro = [(0, '')] + res  # add a default empty value


