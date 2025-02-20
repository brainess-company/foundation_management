from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    medicao_id = fields.Many2one('foundation.medicao', string="Medição Relacionada", ondelete="set null")

    @api.onchange('state')
    def _onchange_state(self):
        """Quando a fatura for confirmada (estado 'posted'), a situação da medição muda para 'emissao'."""
        if self.state == 'posted' and self.medicao_id:
            self.medicao_id.situacao = 'emissao'