from odoo import models, fields, api
from odoo.exceptions import UserError


class FoundationEstacas(models.Model):
    _name = 'foundation.estacas'
    _description = 'Estacas utilizadas na obra'

    foundation_obra_service_id = fields.Many2one(
        'foundation.obra.service', string="Serviço na Obra", required=True)
    nome_estaca = fields.Char("Nome da Estaca", required=True)
    diametro = fields.Float("Diâmetro (cm)")
    profundidade = fields.Float("Profundidade (m)", required=True)
    data = fields.Date("Data")
    observacao = fields.Char("Observação")
    medicao_id = fields.Many2one('foundation.medicao', string="Medição Relacionada")
    # Adicionando o campo relacionado para Sale Order ID
    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda",
                                    related='foundation_obra_service_id.sale_order_id', readonly=True, store=True)
    # Novo campo para relacionar diretamente com uma linha de pedido de venda
    sale_order_line_id = fields.Many2one('sale.order.line', string="Linha de Pedido de Venda",
                                         domain="[('order_id', '=', sale_order_id), ('product_id.product_tmpl_id', '=', service_template_id)]",
                                         required=False)
    # Related field to access service_id from FoundationObraService #vaeiante de produto
    service_id = fields.Many2one(
        'product.product', string="Variante",
        related='foundation_obra_service_id.service_id', readonly=True, store=True
    )
    service_template_id = fields.Many2one('product.template', string="Template do Serviço",
                                          related='foundation_obra_service_id.service_template_id', readonly=True,
                                          store=True)



    def action_generate_medicao(self):
        Medicao = self.env['foundation.medicao']

        if not self:
            return {'type': 'ir.actions.act_window_close'}

        # Verifica se todas as estacas selecionadas são da mesma sale_order
        sale_orders = self.mapped('foundation_obra_service_id.sale_order_id')
        if len(sale_orders) > 1:
            raise UserError("Todas as estacas selecionadas devem pertencer à mesma Ordem de Venda.")

        sale_order = sale_orders[0]
        if not sale_order:
            return {'type': 'ir.actions.act_window_close'}

        # Encontrar a última medição para essa sale_order e preparar o nome para a próxima medição
        last_medicao = Medicao.search([('sale_order_id', '=', sale_order.id)], order='create_date desc', limit=1)
        nome_medicao = "Medição 1" if not last_medicao else f"Medição {int(last_medicao.nome.split(' ')[-1]) + 1}"

        # Criar uma nova medição
        new_medicao = Medicao.create({
            'nome': nome_medicao,
            'sale_order_id': sale_order.id,
            'data': fields.Date.today(),
            'situacao': 'aguardando',
        })

        # Associar cada estaca à nova medição, apenas se não foi previamente medida
        for estaca in self:
            if not estaca.medicao_id:
                estaca.medicao_id = new_medicao.id
            else:
                raise UserError(f"Estaca '{estaca.nome_estaca}' já foi medida e não pode ser medida novamente.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Medições',
            'view_mode': 'form',
            'res_model': 'foundation.medicao',
            'res_id': new_medicao.id,
            'target': 'current'
        }






