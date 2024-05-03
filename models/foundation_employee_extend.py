from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    machine_id = fields.Many2one('foundation.maquina', string="Máquina Alocada",
                                 help="Máquina a qual o funcionário está atualmente alocado.")