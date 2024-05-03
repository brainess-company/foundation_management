from odoo import models, fields, api


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    maquina_id = fields.Many2one('foundation.maquina', string='Máquina')