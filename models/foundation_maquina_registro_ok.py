"""
Gerencia registros automáticos de máquinas associadas
    a serviços específicos em obras.
    Este modelo serve como uma ligação entre máquinas e os serviços da sale order

"""
import logging
from datetime import date
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class FoundationMaquinaRegistro(models.Model):
    """
    Gerencia registros automáticos de máquinas associadas
    a serviços específicos em obras.
    Este modelo serve como uma ligação entre máquinas e os serviços realizados,


    Cada registro nesta tabela representa uma associação única entre uma máquina e um serviço
    dentro de uma obra


    """

    _name = 'foundation.maquina.registro'
    _description = 'Registro de Máquinas para Serviços'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Herdar de mail.thread e mail.activity.mixin
    # _rec_name = 'nome_maquina'

    data_registro = fields.Date(string="Data de Registro", default=fields.Date.context_today)

    # RELACIONA ESSA TABELA COM A DE SERVIÇO
    service_id = fields.Many2one('foundation.obra.service', string="Serviço")
    nome_servico = fields.Char(related='service_id.service_name',
                               string="Nome do Serviço", readonly=True, store=True)
    obra_id = fields.Many2one('foundation.obra', related='service_id.obra_id',
                              string="Obra id", readonly=True, store=True)
    sale_order_id = fields.Many2one('sale.order', related='service_id.sale_order_id',
                                    string="Ordem de Venda", readonly=True, store=True)
    nome_obra = fields.Char(related='service_id.nome_obra',
                            string="Nome da Obra", readonly=True, store=True)
    cod_sale_order = fields.Char(related='sale_order_id.name',
                                 store=True, readonly=True, string="Ordem de Venda")
    endereco = fields.Char(related='service_id.endereco',
                           string="Endereço", readonly=True,  store=True)

    # Campos relacionados à definição de produto/serviço
    variante_id = fields.Many2one('product.product', related='service_id.variante_id',
                                  string="Variante", readonly=True, store=True)
    service_template_id = fields.Many2one('product.template',
                                          related='service_id.service_template_id',
                                          string="Template do Serviço", readonly=True, store=True)

    maquina_id = fields.Many2one('foundation.maquina', string="Máquina")
    operador_id = fields.Many2one('hr.employee', string="Operador",
                                  related='maquina_id.operador_id', readonly=True, store=True)
    # Campo related para vincular diretamente ao user_id do operador
    operador_user_id = fields.Many2one('res.users', string="Usuário do Operador",
                                       related='operador_id.user_id', readonly=True, store=True)

    # CAMPO INVERSO PARA MOSTRAR ESTACA RELACIONADA COM ESSE SERVIÇO
    estacas_ids = fields.One2many('foundation.estacas', 'foundation_maquina_registro_id',
                                  string="Estacas")  # tracking=True
    has_today_chamada = fields.Boolean(string="Chamada Hoje?",
                                       compute="_compute_has_today_chamada", store=False)
    display_has_today_chamada = fields.Char(string="Fez Chamada Hoje?",
                                            compute='_compute_display_has_today_chamada',
                                            store=False)

    product_id = fields.Many2one('product.product', string="Produto Associado")
    product_template_id = fields.Many2one('product.template', string="Template do Produto",
                                          related='product_id.product_tmpl_id',
                                          readonly=True, store=True)
    # Adicionar o campo relacionado requer_chamada
    requer_chamada_maquina = fields.Boolean(
        string="Requer Chamada?",
        related='maquina_id.requer_chamada',
        readonly=True,
        store=True
    )


    # Campo active para controlar arquivamento
    active = fields.Boolean(string="Ativo", default=True)


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

    @api.depends('maquina_id')
    def _compute_has_today_chamada(self):
        """Calcula se há chamada registrada hoje para a máquina"""
        for record in self:
            today_chamadas = self.env['foundation.chamada'].search([
                ('maquina_id', '=', record.maquina_id.id),
                ('data', '=', date.today())
            ])
            record.has_today_chamada = bool(today_chamadas)
