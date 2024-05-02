"""
modulo de gerenciamento de equipes
"""

from odoo import models, fields, api
from odoo.tools.translate import _


class FoundationTeam(models.Model):
    """gerencia os funcionarios relacionados a determinadas maquinas"""
    _name = 'foundation.team'
    _description = 'Registro de equipe de máquinas'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Herdar de mail.thread e mail.activity.mixin
    _rec_name = 'machine_id'

    date = fields.Date("Data", required=True, default=fields.Date.context_today, tracking=True)
    machine_id = fields.Many2one('foundation.maquina',
                                 string="Máquina",
                                 required=True,
                                 tracking=True)
    employee_ids = fields.Many2many('hr.employee',
                                    string="Funcionários",
                                    tracking=True)
    note = fields.Text("Notas", tracking=True)
    machine_status = fields.Selection(related='machine_id.status_maquina',
                                      string="Status da Máquina",
                                      readonly=True, tracking=True)

    @api.model
    def create_daily_team_records(self):
        """registra diariamente um registro de equipes no db, isso se chama job alguma coisa"""
        today = fields.Date.today()
        teams = self.search([])  # Pesquisar todos os registros de equipe
        for team in teams:
            # Verifica se já existe um registro para hoje
            existing_today = self.search(
                [('date', '=', today), ('machine_id', '=', team.machine_id.id)])
            if not existing_today:
                # Cria um novo registro com a mesma configuração do último registro ativo
                last_record = self.search(
                    [('machine_id', '=', team.machine_id.id)], limit=1, order='date desc')
                if last_record:
                    self.create({
                        'date': today,
                        'machine_id': team.machine_id.id,
                        'employee_ids': [(6, 0, last_record.employee_ids.ids)],
                        'note': last_record.note
                    })

    def write(self, vals):
        """Define o método write para verificar se houve modificações de funcionários em equipes."""
        if 'employee_ids' in vals:
            old_employees = self.mapped('employee_ids')
            super().write(vals)
            new_employees = self.mapped('employee_ids')
            added = new_employees - old_employees
            removed = old_employees - new_employees

            if added:
                message = _("Adicionados: %s") % (', '.join(added.mapped('name')),)
                self.message_post(body=message)
            if removed:
                message = _("Removidos: %s") % (', '.join(removed.mapped('name')),)
                self.message_post(body=message)
        else:
            super().write(vals)
        return True
