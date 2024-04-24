from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

    foundation_maquina_ids = fields.Many2many('foundation.maquina', string="Máquina Associada")
    #nome_maquina = fields.Char("Nome da Máquina", related='foundation_maquina_id.nome_maquina', readonly=True,store=True)
    data = fields.Date(string="Data", default=fields.Date.today, required=True)
    # Novo campo computado:
    has_chamada_today = fields.Boolean(string="Tem Chamada Hoje", compute="_compute_has_chamada_today", store=False)
    foundation_maquina_registro_id = fields.Many2one(
        'foundation.maquina.registro',
        string='Registro de Máquina',
        help='Referência ao registro de máquina associado.'
    )

    # Adiciona um campo Many2one para vincular a Foundation Obra Service
    foundation_service_id = fields.Many2one('foundation.obra.service', string="Serviço Relacionado")
    has_today_chamada = fields.Boolean(string="Tem Chamada Hoje", compute="_compute_has_today_chamada", store=False)
    display_has_today_chamada = fields.Char(string="Chamada Hoje?", compute='_compute_display_has_today_chamada',
                                            store=False)

    @api.depends('has_today_chamada')
    def _compute_display_has_today_chamada(self):
        for record in self:
            record.display_has_today_chamada = "Sim" if record.has_today_chamada else "Não"

    def _compute_has_today_chamada(self):
        for record in self:
            today_chamadas = self.env['foundation.chamada'].search([
                ('foundation_maquina_registro_id', '=', record.id),
                ('data', '=', date.today())
            ])
            record.has_today_chamada = bool(today_chamadas)

    @api.constrains('foundation_maquina_registro_id', 'data')
    def _check_unique_chamada_per_day(self):
        for record in self:
            existing_chamada = self.search([
                ('foundation_maquina_registro_id', '=', record.foundation_maquina_registro_id.id),
                ('data', '=', record.data),
                ('id', '!=', record.id)
            ])
            if existing_chamada:
                raise ValidationError("Já existe uma chamada registrada para este registro de máquina neste dia.")
    def action_save(self):
        # Lógica para salvar os dados aqui
        self.ensure_one()  # Garantir que está sendo chamado em um único registro
        self.write(
            {})  # Este método escreve os dados no banco, já está implicitamente incluído pelo Odoo no botão salvar.
        return {'type': 'ir.actions.act_window_close'}
