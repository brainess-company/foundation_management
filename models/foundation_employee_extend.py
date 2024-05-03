from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    team_id = fields.Many2one('foundation.team', string="Equipe Atual", ondelete="set null")
    machine_id = fields.Many2one('foundation.maquina', string="Máquina Alocada",
                                 help="Máquina a qual o funcionário está atualmente alocado.")