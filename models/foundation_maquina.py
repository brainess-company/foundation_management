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
    maquina_engenharia = fields.Boolean("Maquina de engenharia?", default=True, tracking=False)
    chamada_automatica = fields.Boolean("Chamada Automática", default=False)
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

    obra_id = fields.Many2one(
        'foundation.obra',
        string="Obra Atual",
        ondelete='set null',
        help="A obra atual associada à máquina.",  tracking=True
    )

    department_id = fields.Many2one('hr.department', string='Departamento')
    #maintenance_equipment_id = fields.Many2one('maintenance.equipment',string="Equipamento de Manutenção", readonly=True)
    active = fields.Boolean(string="Ativo", default=True)

    #foundation_obra_maquina_id = fields.Many2many('foundation.obra.maquina', string="Ativo", default=True)

    def toggle_active(self):
        for record in self:
            record.active = not record.active

    @api.model
    def create(self, vals):
        machine = super(FoundationMaquina, self).create(vals)
        machine._create_department()
        machine._log_historico(vals.get('obra_id'), vals.get('status_maquina'))
        return machine

    def write(self, vals):
        for record in self:
            previous_obra_id = record.obra_id.id
            previous_status = record.status_maquina

            # Chama o método original
            result = super(FoundationMaquina, record).write(vals)

            # Rastrear alterações em obra_id e status_maquina
            new_obra_id = vals.get('obra_id', record.obra_id.id)
            new_status = vals.get('status_maquina', record.status_maquina)

            if previous_obra_id != new_obra_id or previous_status != new_status:
                record._log_historico(new_obra_id, new_status)

        return result

    def _log_historico(self, obra_id, status_maquina):
        """
        Cria um registro no histórico de máquina.
        """
        # Obtém a data atual no formato de data
        data_atual = fields.Date.today()

        # Determina a observação
        observacao = self.observacao if self.observacao else "Mudança de obra/status."

        # Busca o registro completo da obra, se necessário
        obra = self.env['foundation.obra'].browse(obra_id) if obra_id else None

        self.env['foundation.maquina.obra.rel'].create({
            'maquina_id': self.id,
            'obra_id': obra_id,
            'sale_order_id': obra.sale_order_id.id if obra and obra.sale_order_id else False,
            'status_maquina': status_maquina,
            'data_registro': data_atual,  # Apenas a data
            'observacao': observacao,  # Observação condicional
        })

    def _create_department(self):
        """Cria um novo departamento para a máquina."""
        department = self.env['hr.department'].create({
            'name': self.nome_maquina + ' Department',
            'maquina_id': self.id,  # Referência à máquina criada
        })
        self.department_id = department.id



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


    def action_view_maquina_equipments(self):
        """Método para visualizar equipamentos relacionados a uma máquina."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Equipamentos',
            'view_mode': 'kanban,tree,form',
            'res_model': 'maintenance.equipment',
            'domain': [('department_id', '=', self.department_id.id)],
            'context': {'default_department_id': self.department_id.id},
            'target': 'current',
        }

    @api.onchange('requer_chamada')
    def _onchange_requer_chamada(self):
        if self.requer_chamada:
            self.chamada_automatica = False

    """@api.onchange('obra_id')
    def _onchange_obra_id(self):
        for record in self:
            now = fields.Datetime.now()

            # Criar registro no histórico com a obra anterior
            self.env['foundation.maquina.obra.rel'].create({
                'maquina_id': record.id,
                'obra_id': record.obra_id.id if record.obra_id else False,
                'data_registro': now,
                'observacao': "Mudança de obra associada."
            })"""


