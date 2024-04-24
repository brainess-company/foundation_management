from odoo import models, fields, api

class Chamada(models.Model):
    _name = 'foundation.chamada'
    _description = 'Registro de Chamada'

    funcionario_id = fields.Many2one('res.partner', string="Funcionário")
    data = fields.Date(string="Data", default=fields.Date.today)

    # RELACIONA COM A TABELA DE OBRA (foundation.obra)
    obra_id = fields.Many2one('foundation.obra', string="Obra")
    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", related='obra_id.sale_order_id',
                                    readonly=True, store=True)
    nome_obra = fields.Char("Nome da Obra", related='obra_id.nome_obra', readonly=True, store=True)
    endereco = fields.Char("Endereço", related='obra_id.endereco', readonly=True, store=True)
    foundation_obra_service_id = fields.Many2one('foundation.obra.service', string="Serviço na Obra", required=True)

    # RELACIONA ESSA TABELA COM A DE PRODUTOS
    variante_id = fields.Many2one('product.product', string="Variante")
    service_template_id = fields.Many2one('product.template', string="Template do Serviço",
                                          related='variante_id.product_tmpl_id', readonly=True, store=True)  # produto
    service_name = fields.Char("Nome do Serviço", related='variante_id.name', store=True)  # variante

    # RELACIONA ESSE SERVIÇO COM UMA MÁQUINA
    foundation_maquina_id = fields.Many2one('foundation.maquina', string="Máquina Associada", required=False)
    operador_id = fields.Many2one('res.partner', string="Operador", related='foundation_maquina_id.operador',
                                  readonly=True, store=True)
    nome_maquina = fields.Char("Nome da Máquina", related='foundation_maquina_id.nome_maquina', readonly=True,
                               store=True, tracking=True)

    def action_save(self):
        # Lógica para salvar os dados aqui
        # Exemplo: salvar os dados e retornar uma mensagem de sucesso
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sucesso',
                'message': 'Dados salvos com sucesso!',
                'type': 'success',  # Pode ser 'success', 'danger', 'warning', 'info'
            }
        }
