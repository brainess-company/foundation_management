from odoo import models, fields, api


class ResUsers(models.Model):
    """
    Cria um registro na tabela foundation obra vinculado com a sale order
    Cria vários registros em foundation obra service, um para cada serviço
    """
    _inherit = 'res.users'