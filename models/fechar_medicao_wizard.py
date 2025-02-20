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
        a todas as estacas selecionadas.
        Valida se todas as estacas pertencem à mesma ordem de venda,
        se todas têm o relatório com status 'conferido' e se o relatório está ativo,
        e se a própria estaca está ativa, antes de criar uma medição,
        associando-a às estacas que ainda não foram medidas.

        Returns:
            dict: Ação para abrir a janela de visualização da medição criada.
        """
        if not self:
            return {'type': 'ir.actions.act_window_close'}

        # Filtra as estacas que têm o relatório com status 'conferido', o campo 'active' igual a True na estaca
        # e o campo 'active_relatorio' igual a True no relatório
        estacas_filtradas = self.filtered(
            lambda
                estaca: estaca.status_relatorio == 'conferido' and estaca.active_relatorio and estaca.active
        )

        # Verifica se todas as estacas selecionadas são da mesma sale_order
        sale_orders = estacas_filtradas.mapped('service_id.sale_order_id')
        if len(sale_orders) > 1:
            raise UserError("Todas as estacas selecionadas devem pertencer à mesma Ordem de Venda.")

        # Verifica se há estacas filtradas
        if not estacas_filtradas:
            raise UserError(
                "Nenhuma estaca com relatório conferido, ativo e estaca ativa foi encontrada.")

        # Verifica se todas as estacas têm relatórios conferidos e estão ativas
        all_conferido = all(
            estaca.status_relatorio == 'conferido' and estaca.active_relatorio and estaca.active for
            estaca in estacas_filtradas)
        if not all_conferido:
            raise UserError(
                "Todas as estacas selecionadas devem ter relatórios com status 'Conferido', ativos e estacas ativas.")

        sale_order = sale_orders[0]
        if not sale_order:
            return {'type': 'ir.actions.act_window_close'}

        # Encontrar a última medição para essa sale_order e preparar o nome para a próxima medição
        last_medicao = self.env['foundation.medicao'].search(
            [('sale_order_id', '=', sale_order.id)], order='create_date desc', limit=1)
        next_medicao_number = 1 if not last_medicao else int(last_medicao.nome) + 1

        # Criar uma nova medição
        new_medicao = self.env['foundation.medicao'].create({
            'nome': str(next_medicao_number),  # Nome da medição é apenas o número
            'sale_order_id': sale_order.id,
            'data': fields.Date.today(),
            'situacao': 'aguardando',
        })

        # Associar cada estaca à nova medição, apenas se não foi previamente medida
        for estaca in estacas_filtradas:
            if not estaca.medicao_id:
                estaca.medicao_id = new_medicao.id
            else:
                raise UserError(
                    f"Estaca '{estaca.nome_estaca}' já foi medida e não pode ser medida novamente.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Medições',
            'view_mode': 'form',
            'res_model': 'foundation.medicao',
            'res_id': new_medicao.id,
            'target': 'current'
        }