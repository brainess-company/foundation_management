from datetime import date
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class FoundationMaquinaRegistro(models.Model):
    """
    ESSA TABELA TEM REGISTROS INSERIDOS AUTOMATICAMENTE
    PARA CADA MAQUINA QUE ESTÁ RELACIONADA A UM SERVIÇO DE UMA OBRA
    ENTÃO AQUI EU TENHO UMA TABELA COM REGISTRO COMPOSTO POR CADA MAQUINA RELACIONADA A CADA SERVIÇO
    """
    _name = 'foundation.maquina.registro'
    _description = 'Registro de Máquinas para Serviços'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Herdar de mail.thread e mail.activity.mixin
    #_rec_name = 'nome_maquina'

    data_registro = fields.Date(string="Data de Registro", default=fields.Date.context_today)



    # RELACIONA ESSA TABELA COM A DE SERVIÇO
    service_id = fields.Many2one('foundation.obra.service', string="Serviço")
    nome_servico = fields.Char(related='service_id.service_name', string="Nome do Serviço",readonly=True, store=True)
    obra_id = fields.Many2one('foundation.obra', related='service_id.obra_id', string="Obra id", readonly=True,store=True)
    sale_order_id = fields.Many2one('sale.order', related='service_id.sale_order_id',string="Ordem de Venda", readonly=True, store=True)
    nome_obra = fields.Char(related='service_id.nome_obra', string="Nome da Obra",readonly=True,store=True)
    endereco = fields.Char(related='service_id.endereco', string="Endereço", readonly=True,  store=True)

    # Campos relacionados à definição de produto/serviço
    variante_id = fields.Many2one('product.product', related='service_id.variante_id',string="Variante", readonly=True, store=True)
    service_template_id = fields.Many2one('product.template',related='service_id.service_template_id', string="Template do Serviço",readonly=True, store=True)


    maquina_id = fields.Many2one('foundation.maquina', string="Máquina")
    operador_id = fields.Many2one('res.partner', string="Operador", compute='_compute_operador', store=True)


    # CAMPO INVERSO PARA MOSTRAR ESTACA RELACIONADA COM ESSE SERVIÇO
    estacas_ids = fields.One2many('foundation.estacas', 'foundation_maquina_registro_id', string="Estacas")  # tracking=True
    has_today_chamada = fields.Boolean(string="Tem Chamada Hoje", compute="_compute_has_today_chamada", store=False)
    display_has_today_chamada = fields.Char(string="Chamada Hoje?", compute='_compute_display_has_today_chamada',
                                            store=False)

    product_id = fields.Many2one('product.product', string="Produto Associado")
    product_template_id = fields.Many2one('product.template', string="Template do Produto",
                                          related='product_id.product_tmpl_id', readonly=True, store=True)

    @api.depends('has_today_chamada')
    def _compute_display_has_today_chamada(self):
        for record in self:
            record.display_has_today_chamada = "Sim" if record.has_today_chamada else "Não"

    def _compute_has_today_chamada(self):
        for record in self:
            today_chamadas = self.env['foundation.chamada'].search([
                ('foundation_maquina_registro_id', '=', record.id),
                ('data', '=', date.today())
            ])
            record.has_today_chamada = bool(today_chamadas)
            _logger.info(f"Computing has_today_chamada for record {record.id}: {record.has_today_chamada}")
    @api.depends('maquina_id')
    def _compute_operador(self):
        for record in self:
            # Assumindo que 'operador' é um campo em 'foundation.maquina'
            record.operador_id = record.maquina_id.operador if record.maquina_id else False


