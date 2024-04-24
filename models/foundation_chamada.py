from odoo import models, fields, api

class Chamada(models.Model):
    _name = 'foundation.chamada'
    _description = 'Registro de Chamada'

    lista_presenca_ids = fields.One2many('foundation.lista.presenca', 'chamada_id', string="Lista de Presença")
    foundation_obra_service_id = fields.Many2one('foundation.obra.service', string="Serviço na Obra", required=True)

    obra_id = fields.Many2one('foundation.obra', string="Obra")
    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", related='obra_id.sale_order_id',
                                    readonly=True, store=True)
    nome_obra = fields.Char("Nome da Obra", related='obra_id.nome_obra', readonly=True, store=True)
    endereco = fields.Char("Endereço", related='obra_id.endereco', readonly=True, store=True)

    foundation_maquina_id = fields.Many2one('foundation.maquina', string="Máquina Associada")
    nome_maquina = fields.Char("Nome da Máquina", related='foundation_maquina_id.nome_maquina', readonly=True,
                               store=True)
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
