"""
    Gerencia registros de estacas usadas em obras.
    Este modelo é essencial para rastrear as especificações
    e a utilização de estacas em projetos de construção.
    """
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class FoundationEstacas(models.Model):
    """
    Gerencia registros de estacas usadas em obras. Este modelo é essencial para rastrear as especificações
    e a utilização de estacas em projetos de construção.

    Atributos:
        nome_estaca (Char): Nome ou identificador da estaca.
        profundidade (Float): Profundidade da estaca em metros, com validação para estar entre 1 e 40 metros.
        data (Date): Data de registro da estaca.
        observacao (Char): Observações adicionais sobre a estaca.
        service_id (Many2one): Serviço na obra associado à estaca.
        sale_order_id (Many2one): Ordem de venda associada ao serviço da estaca.
        sale_order_line_id (Many2one): Linha da ordem de venda relacionada à estaca.
    """

    _name = 'foundation.estacas'
    _description = 'Estacas utilizadas na obra'
    _rec_name = 'nome_estaca'

    # CAMPOS PROPRIOS
    nome_estaca = fields.Char("Nome da Estaca", required=True)
    profundidade = fields.Float("Profundidade (m)",
                                required=True,
                                help="o numero deve estar entre 1 e 40",
                                default=1.0)
    data = fields.Date("Data",
                       default=lambda self: fields.Date.context_today(self),
                       required=True)
    observacao = fields.Char("Observação")

    # RELACIONA ESSA ESTACA COM O SERVIÇO
    service_id = fields.Many2one('foundation.obra.service',
                                 string="Serviço na Obra",
                                 required=True)
    sale_order_id = fields.Many2one('sale.order',
                                    string="Ordem de Venda",
                                    related='service_id.sale_order_id',
                                    readonly=True, store=True, required=False)
    sale_order_line_id = fields.Many2one('sale.order.line',
                                         string="Linha de Pedido de Venda",
                                         domain="[('order_id', '=', sale_order_id), "
                                                "('product_id.product_tmpl_id', '=', service_template_id)]",
                                         required=True)
    variante_id = fields.Many2one('product.product', string="Variante",
                                  related='service_id.variante_id',
                                  readonly=True, store=True)  # ,required=True)

    service_template_id = fields.Many2one('product.template',
                                          string="Template do Serviço",
                                          related='service_id.service_template_id',
                                          readonly=True, store=True)  # , required=True)

    # RELACIONA ESSA ESTACA COM a tabela nova de SERVIÇO ()FOUNDATION MAQUINA REGISTRO
    foundation_maquina_registro_id = fields.Many2one('foundation.maquina.registro',
                                                     string="Foundation Maquina registro", required=True)

    # RELACIONA ESSA TABELA COM A DE MEDIÇÃO
    medicao_id = fields.Many2one('foundation.medicao',
                                 string="Medição Relacionada")
    nome_medicao = fields.Char(related='medicao_id.nome',
                               string="Numero Medicao", readonly=True)

    # Campos relacionados para mostrar no calendário
    nome_obra = fields.Char(related='service_id.obra_id.nome_obra',
                            string="Obra", readonly=True)

    relatorio_id = fields.Many2one('foundation.relatorios',
                                   string="Relatório Associado")

    # CAMPOS CALCULADOS
    unit_price = fields.Float("Preço Unitário",
                              compute="_compute_line_values", store=True)
    total_price = fields.Float("Preço Total",
                               compute="_compute_line_values", store=True)
    # Campo computado para exibir o nome formatado da medição
    display_medicao = fields.Char(string="Nome da Medição",
                                  compute='_compute_display_medicao')

    @api.depends('nome_medicao')
    def _compute_display_medicao(self):
        """gera o nome correto da medicao"""
        for record in self:
            # Certifique-se de que nome_medicao é uma string e contém apenas números antes de formatar
            if isinstance(record.nome_medicao, str) and record.nome_medicao.isdigit():
                record.display_medicao = f"Medição {record.nome_medicao}"
            else:
                record.display_medicao = ""  # Um valor padrão ou erro se o nome_medicao não for válido

    @api.model
    def create(self, vals):
        """
            Sobrescreve o método create para adicionar
            funcionalidades específicas ao criar estacas.
            Registra a criação no log e ajusta a
            quantidade entregue na linha de pedido de venda
            baseada na profundidade da estaca criada.

            Args:
                vals (dict): Dicionário contendo os valores
                dos campos para criar o registro.

            Returns:
                record: Objeto da estaca recém-criada.
            """
        _logger.info("VALORES ENVVIADOS PARA CRIAR ESTACAS: %s", vals)
        if 'sale_order_id' not in vals:
            _logger.error("sale_order_id ESTA FALTANDO PARA CRIAR ESTACAS!")
        record = super(FoundationEstacas, self).create(vals)
        if record.sale_order_line_id:
            record.sale_order_line_id.qty_delivered += record.profundidade
        return record

    def write(self, vals):
        """
            Sobrescreve o método write para atualizar dinamicamente a quantidade entregue
            na linha de pedido de venda associada, com base na profundidade da estaca.

            Args:
                vals (dict): Dicionário de valores para atualizar.

            Returns:
                res: Resultado da operação de escrita.
            """
        res = super(FoundationEstacas, self).write(vals)
        for record in self:
            if record.sale_order_line_id:
                # Atualiza o delivered_qty somente se a profundidade foi alterada,
                # ou uma linha de pedido de venda foi associada após a criação da estaca
                if 'profundidade' in vals or 'sale_order_line_id' in vals:
                    record.sale_order_line_id.qty_delivered += vals.get('profundidade', record.profundidade)
        return res

    @api.depends('sale_order_line_id.price_unit', 'profundidade')
    def _compute_line_values(self):
        """
            Calcula o preço unitário e o preço total para cada estaca baseado na unidade de preço
            da linha de pedido de venda associada e na profundidade da estaca.

            Este método é um campo computado que atualiza 'unit_price' e 'total_price'.
            """
        for record in self:
            record.unit_price = record.sale_order_line_id.price_unit if record.sale_order_line_id else 0
            record.total_price = record.unit_price * record.profundidade

    @api.model
    def action_generate_medicao(self):
        """
           Gera uma nova medição para a ordem de venda associada
           a todas as estacas selecionadas.
           Valida se todas as estacas pertencem à mesma
           ordem de venda e cria uma medição,
           associando-a às estacas que ainda não foram medidas.

           Returns:
               dict: Ação para abrir a janela de visualização da medição criada.
           """
        Medicao = self.env['foundation.medicao']

        if not self:
            return {'type': 'ir.actions.act_window_close'}

        # Verifica se todas as estacas selecionadas são da mesma sale_order
        sale_orders = self.mapped('service_id.sale_order_id')
        if len(sale_orders) > 1:
            raise UserError("Todas as estacas selecionadas devem pertencer à mesma Ordem de Venda.")

        sale_order = sale_orders[0]
        if not sale_order:
            return {'type': 'ir.actions.act_window_close'}

        # Encontrar a última medição para essa sale_order e preparar o nome para a próxima medição
        last_medicao = Medicao.search([('sale_order_id', '=', sale_order.id)],
                                      order='create_date desc', limit=1)
        next_medicao_number = 1 if not last_medicao else int(
            last_medicao.nome) + 1  # Ajustado para usar apenas o número

        # Criar uma nova medição
        new_medicao = Medicao.create({
            'nome': str(next_medicao_number),  # Nome da medição é apenas o número
            'sale_order_id': sale_order.id,
            'data': fields.Date.today(),
            'situacao': 'aguardando',
        })

        # Associar cada estaca à nova medição, apenas se não foi previamente medida
        for estaca in self:
            if not estaca.medicao_id:
                estaca.medicao_id = new_medicao.id
            else:
                raise UserError(f"Estaca '{estaca.nome_estaca}"
                                f"' já foi medida e não pode ser medida novamente.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Medições',
            'view_mode': 'form',
            'res_model': 'foundation.medicao',
            'res_id': new_medicao.id,
            'target': 'current'
        }

    @api.constrains('profundidade')
    def _check_profundidade(self):
        """
                Valida a profundidade da estaca para garantir que
                 esteja dentro dos limites aceitáveis (1 a 40 metros).
                """
        for record in self:
            if not (1 <= record.profundidade <= 40):
                raise ValidationError("A profundidade deve ser entre 1 e 40 metros.")
            # _logger.info(f"Validated profundidade for record {record.id}: {record.profundidade}")
