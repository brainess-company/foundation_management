from odoo import models, fields

class FoundationObraService(models.Model):
    _name = 'foundation.obra.service'
    _description = 'Serviços em uma obra'
    _rec_name = 'service_name'
    #ESSa tela spo serve para a adriana relacionar um serviço a uma máquina

    service_name = fields.Char("Nome do Serviço", related='variante_id.name', store=True) #variante
    service_template_id = fields.Many2one('product.template', string="Template do Serviço",
                                          related='variante_id.product_tmpl_id', readonly=True, store=True) #produto
    variante_id = fields.Many2one('product.product', string="Variante")
    foundation_maquina_id = fields.Many2one('foundation.maquina', string="Máquina Associada", required=False)
    obra_id = fields.Many2one('foundation.obra', string="Obra")
    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", related='obra_id.sale_order_id', readonly=True, store=True)
    nome_obra = fields.Char("Nome da Obra", related='obra_id.nome_obra', readonly=True, store=True)
    endereco = fields.Char("Endereço", related='obra_id.endereco', readonly=True, store=True)
    operador_id = fields.Many2one('res.partner', string="Operador", related='foundation_maquina_id.operador',
                                  readonly=True, store=True)
    nome_maquina = fields.Char("Nome da Máquina", related='foundation_maquina_id.nome_maquina', readonly=True,
                               store=True)
    estacas_ids = fields.One2many('foundation.estacas', 'foundation_obra_service_id', string="Estacas")
