from odoo import models, fields

class FoundationObraService(models.Model):
    _name = 'foundation.obra.service'
    _description = 'Serviços em uma obra'
    #ESSa tela spo serve para a adriana relacionar um serviço a uma máquina

    service_name = fields.Char("Nome do Serviço", related='service_id.name', store=True)
    service_id = fields.Many2one('product.product', string="Serviço id", domain=[('sale_ok', '=', True)])
    #service = fields.Char("Service", related='sale_order_line_id.product_id.name', store=True)
    foundation_maquina_id = fields.Many2one('foundation.maquina', string="Máquina Associada", required=True)
    obra_id = fields.Many2one('foundation.obra', string="Obra", required=True)
    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", related='obra_id.sale_order_id', readonly=True, store=True)
    nome_obra = fields.Char("Nome da Obra", related='obra_id.nome_obra', readonly=True, store=True)
    endereco = fields.Char("Endereço", related='obra_id.endereco', readonly=True, store=True)
    operador_id = fields.Many2one('res.partner', string="Operador", related='foundation_maquina_id.operador',
                                  readonly=True, store=True)
    nome_maquina = fields.Char("Nome da Máquina", related='foundation_maquina_id.nome_maquina', readonly=True,
                               store=True)
