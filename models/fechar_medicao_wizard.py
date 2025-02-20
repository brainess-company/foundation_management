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
        self.ensure_one()
        if not self.estacas_ids:
            raise UserError("Não há estacas sem medição para a obra selecionada.")
        #todo como o campo de relatorio ativo está gravado na tabela de estacas  ele acaba não
        # sendo atualizado conforme o dado real

        # 1ª Verificação: Todas as estacas devem ter relatórios ativos (active = True)
        if not all(estaca.status_relatorio.active for estaca in self.estacas_ids):
            raise UserError("Todas as estacas selecionadas devem ter relatórios ativos.")

        # Verifica se todas as estacas têm o status do relatório como 'conferido'
        if not all(estaca.status_relatorio == 'conferido' for estaca in self.estacas_ids):
            raise UserError("Todas as estacas selecionadas devem ter relatórios com status 'Conferido'.")

        # Encontrar a última medição para essa sale_order e preparar o nome para a próxima medição
        last_medicao = self.env['foundation.medicao'].search(
            [('sale_order_id', '=', self.obra_id.sale_order_id.id)], order='nome desc', limit=1
        )

        # Extrai o número da última medição ou define como 1 se não houver medições anteriores
        if last_medicao and last_medicao.nome.isdigit():
            next_medicao_number = int(last_medicao.nome) + 1
        else:
            next_medicao_number = 1

        # Cria uma nova medição com o número correto
        medicao = self.env['foundation.medicao'].create({
            'nome': str(next_medicao_number),  # Nome da medição é o número sequencial
            'data': fields.Date.today(),
            'situacao': 'aguardando',
            'sale_order_id': self.obra_id.sale_order_id.id,
        })

        # Associar cada estaca à nova medição, apenas se não foi previamente medida
        for estaca in self.estacas_ids:
            if not estaca.medicao_id:
                estaca.medicao_id = medicao.id
            else:
                raise UserError(
                    f"Estaca '{estaca.nome_estaca}' já foi medida e não pode ser medida novamente."
                )

        # Redireciona para a view da medição criada
        return {
            'type': 'ir.actions.act_window',
            'name': 'Medição',
            'view_mode': 'form',
            'res_model': 'foundation.medicao',
            'res_id': medicao.id,
            'target': 'current'
        }