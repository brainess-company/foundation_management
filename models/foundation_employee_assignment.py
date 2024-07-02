from odoo import models, fields, api
from odoo.exceptions import UserError

class FoundationEmployeeAssignment(models.Model):
    _name = 'foundation.employee.assignment'
    _description = 'Atribuição de funcionários às máquinas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    date = fields.Date("Data", required=True, default=fields.Date.context_today, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Funcionário", required=False, tracking=True)
    machine_id = fields.Many2one('foundation.maquina', string="Máquina", required=False, tracking=True)
    operador_id = fields.Many2one('hr.employee', related='machine_id.operador_id', string="Operador", readonly=True)
    machine_status = fields.Selection(related='machine_id.status_maquina', string="Status da Máquina", readonly=True)
    is_present = fields.Boolean("Presente Hoje", compute='_compute_is_present', store=True)
    company_id = fields.Many2one('res.company', string="Empresa", related='employee_id.company_id',
                                 store=True, readonly=True)

    @api.depends('employee_id', 'date')
    def _compute_is_present(self):
        """ Verifica se o funcionário está presente na lista de presença na data especificada. """
        for record in self:
            presence = self.env['foundation.lista.presenca'].search([
                ('funcionario_id', '=', record.employee_id.id),
                ('data', '=', record.date)
            ], limit=1)
            record.is_present = bool(presence)

    @api.model
    def create_daily_assignments(self):
        """ Criar registros diários de atribuição para cada funcionário ativo em uma máquina. """
        today = fields.Date.today()
        assignments = self.search([('date', '=', today)])
        if not assignments:
            employees = self.env['hr.employee'].search([('active', '=', True)])
            for employee in employees:
                self.create({
                    'date': today,
                    'employee_id': employee.id,
                    'machine_id': employee.machine_id.id  # Assumindo que 'machine_id' é um campo em 'hr.employee'
                })

    @api.model
    def unlink(self):
        """ Personalize a exclusão para evitar a exclusão de registros de dias anteriores. """
        for record in self:
            if record.date < fields.Date.today():
                raise UserError("Não é possível excluir registros de atribuições de dias anteriores.")
        return super(FoundationEmployeeAssignment, self).unlink()
