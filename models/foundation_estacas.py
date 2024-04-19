from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


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
    variante_id = fields.Many2one(
        'product.product', string="Variante",
        related='foundation_obra_service_id.variante_id', readonly=True, store=True
    )
    service_template_id = fields.Many2one('product.template', string="Template do Serviço",
                                          related='foundation_obra_service_id.service_template_id', readonly=True,
                                          store=True)
    unit_price = fields.Float("Preço Unitário", compute="_compute_line_values", store=True)
    total_price = fields.Float("Preço Total", compute="_compute_line_values", store=True)

    # Novo campo de assinatura
    signature = fields.Binary("Assinatura", help="Assinatura do responsável pela estaca")
    image = fields.Binary("Imagem da Estaca", attachment=True, help="Imagem relacionada à estaca")


    @api.model
    def create(self, vals):
        record = super(FoundationEstacas, self).create(vals)
        if record.sale_order_line_id:
            record.sale_order_line_id.qty_delivered += record.profundidade
        return record

    def write(self, vals):
        res = super(FoundationEstacas, self).write(vals)
        for record in self:
            if record.sale_order_line_id:
                # Atualiza o delivered_qty somente se a profundidade foi alterada,
                # ou uma linha de pedido de venda foi associada após a criação da estaca
                if 'profundidade' in vals or 'sale_order_line_id' in vals:
                    record.sale_order_line_id.qty_delivered += vals.get('profundidade', record.profundidade)
        return res

    @api.depends('sale_order_line_id.price_unit', 'profundidade')
    def _compute_line_values(self):
        for record in self:
            record.unit_price = record.sale_order_line_id.price_unit if record.sale_order_line_id else 0
            record.total_price = record.unit_price * record.profundidade


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






