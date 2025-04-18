from odoo import models, fields, api
from odoo.exceptions import UserError

class FecharMedicaoWizard(models.TransientModel):
    _name = 'fechar.medicao.wizard'
    _description = 'Wizard para Fechar Medições'

    obra_id = fields.Many2one('foundation.obra', string="Obra", required=True)
    estacas_ids = fields.Many2many(
        'foundation.estacas',
        string="Estacas sem Medição",
        compute="_compute_estacas_sem_medicao",
        domain="[('active', '=', True)]"  # Filtra apenas estacas ativas
    )
    valor_total = fields.Float(string="Valor Total", compute="_compute_valor_total")

    company_id = fields.Many2one(
        'res.company',
        string="Empresa",
        default=lambda self: self.env.company,  # Define a empresa ativa no momento
        readonly=True
    )

    @api.depends('obra_id')
    def _compute_estacas_sem_medicao(self):
        for wizard in self:
            if wizard.obra_id:
                estacas = self.env['foundation.estacas'].search([
                    ('service_id.obra_id', '=', wizard.obra_id.id),
                    ('medicao_id', '=', False),
                    ('active', '=', True)  # Filtra apenas estacas ativas
                ])
                wizard.estacas_ids = estacas
            else:
                wizard.estacas_ids = False

    @api.depends('estacas_ids')
    def _compute_valor_total(self):
        for wizard in self:
            wizard.valor_total = sum(estaca.total_price for estaca in wizard.estacas_ids)

    def action_criar_medicao(self):
        """
        Gera uma nova medição para a ordem de venda associada
        a todas as estacas selecionadas que atendem aos critérios:
        - Relatório ativo (fr.active = True)
        - Nome da obra = 'OBRA AUDACE' (so.nome_obra = 'OBRA AUDACE')
        - Estaca ativa (fe.active = True)
        - Status do relatório = 'conferido' (fe.status_relatorio = 'conferido')
        - Estaca ainda não medida (fe.medicao_id = False)

        Returns:
            dict: Ação para abrir a janela de visualização da medição criada.
        """
        if not self:
            return {'type': 'ir.actions.act_window_close'}

        # Filtra as estacas que atendem a todos os critérios necessários
        estacas_filtradas = self.env['foundation.estacas'].search([
            ('active', '=', True),  # fe.active = True
            ('status_relatorio', '=', 'conferido'),  # fe.status_relatorio = 'conferido'
            ('active_relatorio', '=', True),  # fr.active = True
            ('medicao_id', '=', False),  # fe.medicao_id = False (estaca ainda não medida)
        ])  # Ordena por relatorio_id e nome_estaca

        # Verifica se há estacas filtradas
        if not estacas_filtradas:
            raise UserError(
                "Nenhuma estaca válida encontrada. Certifique-se de que todas as estacas "
                "estão com relatório conferido, relatório ativo, estaca ativa "
                "e ainda não foram medidas."
            )

        # Verifica se todas as estacas pertencem à mesma Ordem de Venda
        sale_orders = estacas_filtradas.mapped('sale_order_id')
        if len(sale_orders) > 1:
            raise UserError("Todas as estacas selecionadas devem pertencer à mesma Ordem de Venda.")

        sale_order = sale_orders[0]
        if not sale_order:
            return {'type': 'ir.actions.act_window_close'}

        # Encontrar a última medição para essa sale_order e preparar o nome para a próxima medição
        last_medicao = self.env['foundation.medicao'].search(
            [('sale_order_id', '=', sale_order.id)], order='create_date desc', limit=1
        )
        next_medicao_number = 1 if not last_medicao else int(last_medicao.nome) + 1

        # Criar uma nova medição
        new_medicao = self.env['foundation.medicao'].create({
            'nome': str(next_medicao_number),  # Nome da medição é apenas o número
            'sale_order_id': sale_order.id,
            'data': fields.Date.today(),
            'situacao': 'aguardando',
        })

        # Associar cada estaca à nova medição
        for estaca in estacas_filtradas:
            estaca.medicao_id = new_medicao.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Medições',
            'view_mode': 'form',
            'res_model': 'foundation.medicao',
            'res_id': new_medicao.id,
            'target': 'current'
        }
