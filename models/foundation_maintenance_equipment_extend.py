from odoo import models, fields

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    maquina_id = fields.Many2one('foundation.maquina', string="Máquina Associada")
