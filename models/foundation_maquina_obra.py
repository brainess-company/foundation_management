"""
Gerencia registros automáticos de máquinas associadas
    a serviços específicos em obras.
    Este modelo serve como uma ligação entre máquinas e os serviços realizados,
    permitindo rastrear a utilização de cada máquina em diferentes fases da obra.
"""
import logging
from datetime import date
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class FoundationMaquinaObra(models.Model):
    """
    Gerencia registros automáticos de máquinas associadas
    a serviços específicos em obras.
    Este modelo serve como uma ligação entre máquinas e os serviços realizados,
    permitindo rastrear
    a utilização de cada máquina em diferentes fases da obra.

    Cada registro nesta tabela representa uma associação única entre uma máquina e um serviço
    dentro de uma obra, com detalhes complementares sobre a obra, serviço,
    e a máquina utilizada.
    Isso facilita o monitoramento e a gestão eficaz dos recursos em projetos de construção.

    Atributos:
        data_registro (Date): Data de criação do registro.
        service_id (Many2one): Referência ao serviço associado na obra.
        nome_servico (Char): Nome do serviço associado, extraído da referência do serviço.
        obra_id (Many2one): Referência à obra associada ao serviço.
        sale_order_id (Many2one): Ordem de venda associada ao serviço.
        nome_obra (Char): Nome da obra associada ao serviço.
        endereco (Char): Endereço da obra associada ao serviço.
        variante_id (Many2one): Variante do produto/serviço utilizado.
        service_template_id (Many2one): Template do serviço associado.
        maquina_id (Many2one): Máquina utilizada no serviço.
        operador_id (Many2one): Operador da máquina, determinado dinamicamente.
        estacas_ids (One2many): Estacas relacionadas a este registro de máquina.
        has_today_chamada (Boolean): Indica se houve uma chamada no dia atual.
        display_has_today_chamada (Char): Descrição textual do status da chamada no dia atual.
        product_id (Many2one): Produto associado à máquina.
        product_template_id (Many2one): Template do produto associado.
        requer_chamada_maquina (Boolean): Indica se a máquina requer chamada,
        baseado nas propriedades da máquina.
    """

    _name = 'foundation.maquina.obra'
    _description = 'Registro de Máquinas para obra'
    # _rec_name = 'nome_maquina'

    # RELACIONA ESSA TABELA COM A DE SERVIÇO
    # CAMPOS PRÓPRIOS
    obra_id = fields.Many2one('foundation.obra', string="Obra")
    nome_obra = fields.Char(related='sale_order_id.nome_obra',
                            store=True, readonly=True, string="Nome da Obra")


    # RELACIONA ESSA TABELA FOUNDATION OBRA COM  UMA SALE ORDER
    sale_order_id = fields.Many2one('sale.order',
                                    string="Ordem de Venda", required=True)
    partner_id = fields.Many2one('res.partner', string="Cliente",
                                 related='sale_order_id.partner_id', readonly=True,
                                 store=True)


    maquina_id = fields.Many2one('foundation.maquina', string="Máquina")
    operador_id = fields.Many2one('hr.employee', string="Operador",
                                  related='maquina_id.operador_id', readonly=True, store=True)
    # Campo related para vincular diretamente ao user_id do operador
    operador_user_id = fields.Many2one('res.users', string="Usuário do Operador",
                                       related='operador_id.user_id', readonly=True, store=True)

    has_today_chamada = fields.Boolean(string="Chamada Hoje?",
                                       compute="_compute_has_today_chamada", store=False)
    display_has_today_chamada = fields.Char(string="Fez Chamada Hoje?",
                                            compute='_compute_display_has_today_chamada',
                                            store=False)


    # Adicionar o campo relacionado requer_chamada
    requer_chamada_maquina = fields.Boolean(
        string="Requer Chamada?",
        related='maquina_id.requer_chamada',
        readonly=True,
        store=True
    )



    @api.depends('has_today_chamada', 'requer_chamada_maquina')
    def _compute_display_has_today_chamada(self):
        for record in self:
            if record.requer_chamada_maquina:  # Verifica se a máquina requer chamada
                if record.has_today_chamada:
                    record.display_has_today_chamada = "Sim"
                else:
                    record.display_has_today_chamada = "Não"
            else:
                record.display_has_today_chamada = ""  # Deixa em branco se não requer chamada

    def _compute_has_today_chamada(self):
        """calcula se tem chamada registrada hoje"""
        for record in self:
            today_chamadas = self.env['foundation.chamada'].search([
                ('foundation_maquina_obra_id', '=', record.id),
                ('data', '=', date.today())
            ])
            record.has_today_chamada = bool(today_chamadas)
            _logger.info(
                f"Computing has_today_chamada for record {record.id}: {record.has_today_chamada}")
