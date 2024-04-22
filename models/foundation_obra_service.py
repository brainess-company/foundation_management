from odoo import models, fields

class FoundationObraService(models.Model):
    """
    ESSA CLASSE SERVE PRINCIPALMENTE PARA RELACIONAR UMA MÁQUINA À UM SERVIÇO
    O SERVIÇO NA VERDADE SÃO OS PRODUCT TEMPLATES DISTINTOS DA SALE ORDER
    """
    _name = 'foundation.obra.service'
    _description = 'Serviços em uma obra'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Herdar de mail.thread e mail.activity.mixin
    _rec_name = 'service_name'

    # RELACIONA ESSA TABELA COM A DE PRODUTOS
    variante_id = fields.Many2one('product.product', string="Variante")
    service_template_id = fields.Many2one('product.template', string="Template do Serviço", related='variante_id.product_tmpl_id', readonly=True, store=True) #produto
    service_name = fields.Char("Nome do Serviço", related='variante_id.name', store=True)  # variante

    # RELACIONA ESSE SERVIÇO COM UMA MÁQUINA
    foundation_maquina_id = fields.Many2one('foundation.maquina', string="Máquina Associada", required=False)
    operador_id = fields.Many2one('res.partner', string="Operador", related='foundation_maquina_id.operador',readonly=True, store=True)
    nome_maquina = fields.Char("Nome da Máquina", related='foundation_maquina_id.nome_maquina', readonly=True, store=True, tracking=True)

    # RELACIONA COM A TABELA DE OBRA (foundation.obra)
    obra_id = fields.Many2one('foundation.obra', string="Obra")
    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", related='obra_id.sale_order_id',readonly=True, store=True)
    nome_obra = fields.Char("Nome da Obra", related='obra_id.nome_obra', readonly=True, store=True)
    endereco = fields.Char("Endereço", related='obra_id.endereco', readonly=True, store=True)

    # CAMPO INVERSO PARA MOSTRAR ESTACA RELACIONADA COM ESSE SERVIÇO
    estacas_ids = fields.One2many('foundation.estacas', 'foundation_obra_service_id', string="Estacas") # tracking=True
