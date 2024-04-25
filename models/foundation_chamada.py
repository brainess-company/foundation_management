from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Chamada(models.Model):
    """
    chamada contem lista de presencas
    UM REGISTRO DE CHAMADA AQUI TEM MUITOS LISTA DE PRESENÇA
    UMA CHAMADA É UM GRUPO DE REGISTROS EM LISTA DE PRESENÇA
    """
    _name = 'foundation.chamada'
    _description = 'Registro de Chamada'

    lista_presenca_ids = fields.One2many('foundation.lista.presenca', 'chamada_id', string="Lista de Presença")
    foundation_obra_service_id = fields.Many2one('foundation.obra.service', string="Serviço na Obra", required=True)

    obra_id = fields.Many2one('foundation.obra', string="Obra")
    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", related='obra_id.sale_order_id',
                                    readonly=True, store=True)
    nome_obra = fields.Char("Nome da Obra", related='obra_id.nome_obra', readonly=True, store=True)
    endereco = fields.Char("Endereço", related='obra_id.endereco', readonly=True, store=True)

    foundation_maquina_ids = fields.Many2many('foundation.maquina', string="Máquina Associada")
    #nome_maquina = fields.Char("Nome da Máquina", related='foundation_maquina_id.nome_maquina', readonly=True,store=True)
    data = fields.Date(string="Data", default=fields.Date.today, required=True)
    # Novo campo computado:


    # Adiciona um campo Many2one para vincular a Foundation Obra Service
    foundation_service_id = fields.Many2one('foundation.obra.service', string="Serviço Relacionado")
    has_today_chamada = fields.Boolean(string="Tem Chamada Hoje", compute="_compute_has_today_chamada", store=False)
    display_has_today_chamada = fields.Char(string="Chamada Hoje?", compute='_compute_display_has_today_chamada',
                                            store=False)
    # This field now relates to FoundationMaquinaRegistro instead of FoundationObraService
    foundation_maquina_registro_id = fields.Many2one(
        'foundation.maquina.registro',
        string='Registro de Máquina',
        required=True,  # Assuming this field is required
        help='Referência ao registro de máquina associado.'
    )


    has_chamada_today = fields.Boolean(
        string="Tem Chamada Hoje",
        compute="_compute_has_chamada_today",
        store=False
    )

    @api.depends('foundation_maquina_registro_id', 'data')
    def _compute_has_chamada_today(self):
        for record in self:
            today_chamadas = self.env['foundation.chamada'].search([
                ('foundation_maquina_registro_id', '=', record.foundation_maquina_registro_id.id),
                ('data', '=', date.today())
            ])
            record.has_chamada_today = bool(today_chamadas)


    def action_save(self):
        self.ensure_one()  # Garantir que está sendo chamado em um único registro
        return {'type': 'ir.actions.act_window_close'}
