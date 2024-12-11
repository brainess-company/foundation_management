from odoo import models, fields, api
from odoo.exceptions import UserError
from pytz import timezone, UTC
from datetime import datetime

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
    # Campo relacionado ao sale_order_id da máquina
    sale_order_id = fields.Many2one(
        'sale.order', string="Ordem de Venda",
        help="Ordem de Venda associada à obra no momento do registro."
    )
    obra_name = fields.Char(string="Nome da Obra", readonly=True,
                            help="Nome da obra associada à máquina.")

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
        """ Criar registros diários de atribuição para cada funcionário ativo em uma máquina em cada empresa. """
        companies = self.env['res.company'].search([])
        for company in companies:
            today = fields.Date.today()

            # Verificar se já existem registros para hoje nesta empresa
            assignments = self.search([('date', '=', today), ('company_id', '=', company.id)])
            if not assignments:
                # Buscar funcionários ativos da empresa
                employees = self.env['hr.employee'].search(
                    [('active', '=', True), ('company_id', '=', company.id)]
                )
                for employee in employees:
                    # Obter a máquina associada ao funcionário
                    machine = employee.machine_id
                    sale_order_id = None
                    obra_name = None

                    # Se a máquina estiver associada a uma obra, obtenha os dados
                    if machine and machine.obra_id:
                        sale_order_id = machine.obra_id.sale_order_id.id
                        obra_name = machine.obra_id.sale_order_id.nome_obra if machine.obra_id.sale_order_id else False

                    # Criar o registro de atribuição
                    self.create({
                        'date': today,
                        'employee_id': employee.id,
                        'machine_id': machine.id if machine else False,
                        'company_id': company.id,
                        'sale_order_id': sale_order_id,
                        'obra_name': obra_name,
                    })
    """@api.model
    def unlink(self):


        for record in self:
            if record.date < fields.Date.today():
                raise UserError("Não é possível excluir registros de atribuições de dias anteriores.")
        return super(FoundationEmployeeAssignment, self).unlink()"""
