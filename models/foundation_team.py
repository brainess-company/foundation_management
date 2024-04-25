from odoo import models, fields, api

class FoundationTeam(models.Model):
    _name = 'foundation.team'
    _description = 'Registro de equipe de máquinas'
    _rec_name = 'date'

    date = fields.Date("Data", required=True, default=fields.Date.context_today)
    machine_id = fields.Many2one('foundation.maquina', string="Máquina", required=True)
    employee_ids = fields.Many2many('res.partner', string="Funcionários")
    note = fields.Text("Notas")

    @api.model
    def create_daily_team_records(self):
        today = fields.Date.today()
        teams = self.search([])  # Pesquisar todos os registros de equipe
        for team in teams:
            # Verifica se já existe um registro para hoje
            existing_today = self.search([('date', '=', today), ('machine_id', '=', team.machine_id.id)])
            if not existing_today:
                # Cria um novo registro com a mesma configuração do último registro ativo
                last_record = self.search([('machine_id', '=', team.machine_id.id)], limit=1, order='date desc')
                if last_record:
                    self.create({
                        'date': today,
                        'machine_id': team.machine_id.id,
                        'employee_ids': [(6, 0, last_record.employee_ids.ids)],
                        'note': last_record.note
                    })
