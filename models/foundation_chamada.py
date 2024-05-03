"""
 Gerencia registros de chamadas para listas de presença em obras.
 Este modelo serve como um meio de documentar a presença de equipes
 e o uso de equipamentos em locais de obras específicos.
"""
from odoo import models, fields, api


class Chamada(models.Model):
    """
    Gerencia registros de chamadas para listas de presença em obras. Este modelo serve como
    um meio de documentar a presença de equipes e
    o uso de equipamentos em locais de obras específicos.

    Atributos:
        lista_presenca_ids (One2many): Registros de presença associados a esta chamada.
        foundation_obra_service_id (Many2one): Serviço na obra associado à chamada.
        obra_id (Many2one): Obra relacionada à chamada.
        sale_order_id (Many2one): Ordem de venda relacionada à obra.
        nome_obra (Char): Nome da obra, obtido da relação com a obra.
        endereco (Char): Endereço da obra, também derivado da relação.
        data (Date): Data da chamada.
    """

    _name = 'foundation.chamada'
    _description = 'Registro de Chamada'

    lista_presenca_ids = fields.One2many('foundation.lista.presenca', 'chamada_id',
                                         string="Lista de Presença")
    foundation_obra_service_id = fields.Many2one('foundation.obra.service',
                                                 string="Serviço na Obra", required=True)

    obra_id = fields.Many2one('foundation.obra', string="Obra")
    sale_order_id = fields.Many2one('sale.order',
                                    string="Ordem de Venda", related='obra_id.sale_order_id',
                                    readonly=True, store=True)
    nome_obra = fields.Char("Nome da Obra",
                            related='obra_id.nome_obra', readonly=True, store=True)
    endereco = fields.Char("Endereço", related='obra_id.endereco', readonly=True, store=True)


    data = fields.Date(string="Data da chamada", default=fields.Date.today, required=True, store=True)

    foundation_service_id = fields.Many2one('foundation.obra.service', string="Serviço Relacionado")

    foundation_maquina_registro_id = fields.Many2one(
        'foundation.maquina.registro',
        string='Registro de Máquina',
        required=True,  # Assuming this field is required
        help='Referência ao registro de máquina associado.'
    )

    # Adicionando campo para selecionar a máquina e mostrar o operador
    maquina_id = fields.Many2one('foundation.maquina', string="Máquina Associada")
    operador_id = fields.Many2one('hr.employee', string="Operador da Máquina",
                                  related='maquina_id.operador_id', readonly=True)
    funcionario_ids = fields.Many2many('hr.employee', compute='_compute_funcionario_ids')

    @api.depends('lista_presenca_ids.funcionario_id')
    def _compute_funcionario_ids(self):
        for rec in self:
            rec.funcionario_ids = [(6, 0, rec.lista_presenca_ids.mapped('funcionario_id').ids)]

    def action_save(self):
        """
            Fecha a janela de ação atual.
            Este método garante que a ação seja chamada em um único registro.
        """
        self.ensure_one()  # Garantir que está sendo chamado em um único registro
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def default_get(self, fields_list):
        res = super(Chamada, self).default_get(fields_list)
        default_maquina_id = self._context.get('default_maquina_id')

        if default_maquina_id:
            maquina = self.env['foundation.maquina'].browse(default_maquina_id)
            if maquina and maquina.operador_id:
                # Preparar a entrada da lista de presença para o operador da máquina
                res['lista_presenca_ids'] = [(0, 0, {
                    'funcionario_id': maquina.operador_id.id,
                    'data': fields.Date.today(),
                })]
        return res
