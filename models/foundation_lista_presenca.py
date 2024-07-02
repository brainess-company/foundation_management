""" CADA UM FUNCIONARIO AQUI ESTA RELACIONADO COM UMA CHAMADA
    """
from odoo import models, fields, api


class ListaPresenca(models.Model):
    """ CADA UM FUNCIONARIO AQUI ESTA RELACIONADO COM UMA CHAMADA
    """
    _name = 'foundation.lista.presenca'
    _description = 'Lista de Presença de Funcionários'

    chamada_id = fields.Many2one('foundation.chamada', string="Chamada", required=True)
    funcionario_id = fields.Many2one('hr.employee', string="Funcionário", required=True)
    data = fields.Date(string="Data da Lista de Presença", related='chamada_id.data', store=True, readonly=True)
    maquina_id = fields.Many2one('foundation.maquina', string="Máquina Alocada",
                                 compute='_compute_maquina_id', store=True)
    company_id = fields.Many2one('res.company', string="Empresa", related='funcionario_id.company_id',
                                 store=True, readonly=True)

    @api.depends('funcionario_id')
    def _compute_maquina_id(self):
        for record in self:
            record.maquina_id = record.funcionario_id.machine_id if record.funcionario_id else False
