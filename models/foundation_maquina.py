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
    operador_id = fields.Many2one(
        'hr.employee',
        string="Nome Operador",
        domain="[('id', 'in', available_employee_ids)]",
        tracking=True
    )
    operador_user_id = fields.Many2one('res.users', string="Usuário do Operador",
                                       related='operador_id.user_id', readonly=True, store=True)
    observacao = fields.Char("Observação")
    employee_ids = fields.One2many('hr.employee', 'machine_id', string="Funcionários", tracking=True)
    available_employee_ids = fields.Many2many('hr.employee', compute='_compute_available_employees',
                                              store=False)
    requer_chamada = fields.Boolean("Requer Lista de Chamada", default=False, tracking=True)
    display_requer_chamada = fields.Char(string="Requer chamada?",
                                            compute='_compute_display_requer_chamada',
                                            store=False)
    status_maquina = fields.Selection([
        ('em_mobilizacao', 'Em Mobilização'),
        ('sem_obra', 'Sem Obra'),
        ('parada', 'Máquina Parada'),
        ('em_manutencao', 'Em Manutenção'),
        ('disponivel', 'Disponível')
    ], string="Status da Máquina", default='sem_obra', tracking=True)

    employee_count = fields.Integer(string="Número de Funcionários",
                                    compute='_compute_employee_count', store=True)

    department_id = fields.Many2one('hr.department', string='Departamento', readonly=True)

    @api.model
    def create(self, vals):
        machine = super(FoundationMaquina, self).create(vals)

        # Criar um novo departamento para a máquina
        department = self.env['hr.department'].create({
            'name': machine.nome_maquina + ' Department',
            'maquina_id': machine.id,  # Referência à máquina criada
        })
        machine.department_id = department.id

        return machine

    # Outros campos...

    @api.depends('employee_ids')
    def _compute_employee_count(self):
        for machine in self:
            machine.employee_count = len(machine.employee_ids)

    @api.depends('employee_ids')
    def _compute_available_employees(self):
        for machine in self:
            machine.available_employee_ids = [(6, 0, machine.employee_ids.ids)]

    @api.depends('requer_chamada')
    def _compute_display_requer_chamada(self):
        for record in self:
            if record.requer_chamada:  # Verifica se a máquina requer chamada
                record.display_requer_chamada = "Sim"
            else:
                record.display_requer_chamada = "Não"
