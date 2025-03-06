from odoo import models, fields, api


class FoundationMaquinaObraRel(models.Model):
    _name = 'foundation.maquina.obra.rel'
    _description = 'Histórico de Relações entre Máquinas e Obras'

    maquina_id = fields.Many2one('foundation.maquina', string="Máquina", required=True, ondelete='cascade')
    obra_id = fields.Many2one('foundation.obra', string="Obra", ondelete='set null', help="Obra associada à máquina. Vazio se a máquina não estiver vinculada a nenhuma obra.")
    sale_order_id = fields.Many2one(
        'sale.order', string="Ordem de Venda",
        help="Ordem de Venda associada à obra no momento do registro."
    )
    status_maquina = fields.Selection([
        ('em_mobilizacao', 'Em Mobilização'),
        ('sem_obra', 'Sem Obra'),
        ('parada', 'Máquina Parada'),
        ('em_manutencao', 'Em Manutenção'),
        ('disponivel', 'Disponível')
    ], string="Status da Máquina")
    data_registro = fields.Datetime(string="Data do Registro", required=True, default=fields.Datetime.now)
    observacao = fields.Text(string="Observação", help="Detalhes adicionais sobre o registro.")

    company_id = fields.Many2one('res.company', string="Empresa",
                                 related="sale_order_id.company_id", store=True, index=True)

    @api.model
    def create(self, vals):
        """
        Sobrescreve o método `create` para evitar recursão infinita.
        """
        record = super(FoundationMaquinaObraRel, self).create(vals)

        # Verifica se a criação do histórico já está sendo feita
        if 'maquina_id' in vals and vals.get('obra_id') and vals.get('status_maquina'):
            # Garante que não haja duplicação
            if not self.search([
                ('maquina_id', '=', vals['maquina_id']),
                ('obra_id', '=', vals['obra_id']),
                ('status_maquina', '=', vals['status_maquina']),
            ]):
                self.env['foundation.maquina.obra.rel'].sudo().create({
                    'maquina_id': vals['maquina_id'],
                    'obra_id': vals['obra_id'],
                    'status_maquina': vals['status_maquina'],
                    'data_registro': fields.Datetime.now(),
                    'observacao': vals.get('observacao', ''),
                })

        return record
