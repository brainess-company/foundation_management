from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    team_id = fields.Many2one('foundation.team', string="Equipe Fundação")
