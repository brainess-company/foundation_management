from odoo import models, fields, api

class FoundationMaquina(models.Model):
    _name = 'foundation.maquina'
    _description = 'Cadastro de Máquinas'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Herdar de mail.thread e mail.activity.mixin
    _rec_name = 'nome_maquina'

    nome_maquina = fields.Char("Máquina",  tracking=True)
    operador = fields.Many2one('res.partner', string="Operador",  tracking=True)
    observacao = fields.Char("Observação")
    team_ids = fields.One2many('foundation.team', 'machine_id', string="Histórico de Equipes")
    current_team_employees = fields.Many2many('res.partner', string="Equipe Atual",
                                              compute='_compute_current_team_employees',
                                              store=False)
    requer_chamada = fields.Boolean("Requer Lista de Chamada", default=False, tracking=True)
    status_maquina = fields.Selection([
        ('em_mobilizacao', 'Em Mobilização'),
        ('sem_obra', 'Sem Obra'),
        ('parada', 'Máquina Parada'),
        ('em_manutencao', 'Em Manutenção'),
        ('disponivel', 'Disponível')
    ], string="Status da Máquina", default='sem_obra', tracking=True)


    @api.depends('team_ids')
    def _compute_current_team_employees(self):
        for machine in self:
            last_team = self.env['foundation.team'].search([
                ('machine_id', '=', machine.id)],
                order='date desc', limit=1)
            machine.current_team_employees = last_team.employee_ids if last_team else False
