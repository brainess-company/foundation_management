from odoo import models, fields, api
from odoo.exceptions import UserError

class FoundationRelatorios(models.Model):
    _name = 'foundation.relatorios'
    _description = 'Relatórios de Fundação'

    # Campos básicos
    data = fields.Date("Data do Relatório", default=fields.Date.context_today, required=True)
    foundation_obra_service_id = fields.Many2one('foundation.obra.service', string="Serviço na Obra", required=True)
    estacas_ids = fields.One2many('foundation.estacas', 'relatorio_id', string="Estacas Incluídas")
    assinatura = fields.Binary("Assinatura do Responsável", help="Assinatura digital do responsável pelo relatório")
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado')
    ], default='draft', string="Status", required=True)

    # Campos adicionais relacionados ao serviço
    nome_servico = fields.Char(related='foundation_obra_service_id.service_name', string="Nome do Serviço",
                               readonly=True, store=True)
    nome_maquina = fields.Char(related='foundation_obra_service_id.nome_maquina', string="Máquina Associada",
                               readonly=True, store=True)
    nome_operador = fields.Char(related='foundation_obra_service_id.operador_id.name', string="Operador", readonly=True,
                                store=True)
    nome_obra = fields.Char(related='foundation_obra_service_id.nome_obra', string="Nome da Obra", readonly=True,
                            store=True)
    endereco_obra = fields.Char(related='foundation_obra_service_id.endereco', string="Endereço da Obra", readonly=True,
                                store=True)


    @api.model
    def create(self, vals):
        if not vals.get('assinatura'):
            raise UserError("A assinatura é obrigatória para a criação de um relatório.")
        return super(FoundationRelatorios, self).create(vals)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    @api.constrains('estacas_ids')
    def _check_estacas(self):
        if any(not estaca.profundidade for estaca in self.estacas_ids):
            raise UserError("Todas as estacas devem ter a profundidade definida.")

    def action_save(self):
        self.ensure_one()
        if not self.assinatura:
            raise UserError("A assinatura é necessária para salvar o relatório.")
        self.state = 'confirmed'  # Supondo que haja um campo de estado para controlar a confirmação do relatório
        return {
            'type': 'ir.actions.act_window',
            'name': 'Relatório Confirmado',
            'view_mode': 'form',
            'res_model': 'foundation.relatorios',
            'res_id': self.id,
            'target': 'current'
        }
