"""
Esse modulo gerencia as maquinas
"""
from odoo import models, fields, api


class FoundationMaquina(models.Model):
    """
        Este modelo gerencia o cadastro e o rastreamento de máquinas usadas nas obras.
        Ele armazena informações como seu operador,
        seu status atual e um histórico das equipes que utilizaram a máquina.

        Atributos:
            nome_maquina (Char): Nome ou identificador da máquina.
            operador (Many2one)
            status_maquina (Selection): Status atual da máquina.
            team_ids (One2many): Histórico das equipes que trabalharam com a máquina.
            current_team_employees (Many2many): conta Empregados da equipe atual,
            calculado dinamicamente.
            requer_chamada (Boolean)
        """
    _name = 'foundation.maquina'
    _description = 'Cadastro de Máquinas'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Herdar de mail.thread e mail.activity.mixin
    _rec_name = 'nome_maquina'

    nome_maquina = fields.Char("Máquina",  required=True, tracking=True)
    operador = fields.Many2one('hr.employee', string="Nome Operador", tracking=True)
    observacao = fields.Char("Observação")
    team_ids = fields.One2many('foundation.team', 'machine_id', string="Histórico de Equipes")
    current_team_employees = fields.Many2many('hr.employee', string="Equipe Atual",
                                              compute='_compute_current_team_employees',
                                              store=False, tracking=True)
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
        """Computa os empregados da equipe atual baseando-se no último registro de equipe
                associado à máquina. Este método procura a equipe mais recente
                e atribui seus empregados ao campo current_team_employees.
                """
        for machine in self:
            last_team = self.env['foundation.team'].search([
                ('machine_id', '=', machine.id)],
                order='date desc', limit=1)
            machine.current_team_employees = last_team.employee_ids if last_team else False
