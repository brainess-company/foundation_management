"""
    OBRAS RELACIONADAS COM ORDEM DE VENDAS

    """
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)  # Configuração do logger


class FoundationObra(models.Model):
    """
    OBRAS RELACIONADAS COM ORDEM DE VENDAS

    """
    _name = 'foundation.obra'
    _description = 'Informações sobre a obra'
    _rec_name = 'nome_obra'

    # CAMPOS PRÓPRIOS
    nome_obra = fields.Char(related='sale_order_id.nome_obra',
                            store=True, readonly=True, string="Nome da Obra")
    endereco = fields.Char("Endereço")

    # RELACIONA ESSA TABELA FOUNDATION OBRA COM  UMA SALE ORDER
    sale_order_id = fields.Many2one('sale.order',
                                    string="Ordem de Venda", required=True)
    partner_id = fields.Many2one('res.partner', string="Cliente",
                                 related='sale_order_id.partner_id', readonly=True,
                                 store=True)
    # todo remover um campo
    cliente_id = fields.Many2one('res.partner',
                                 string="Cliente 2", related='sale_order_id.partner_id',
                                 readonly=True, store=True)
    valor_total = fields.Monetary("Valor Total", related='sale_order_id.amount_total',
                                  readonly=True)
    invoice_address = fields.Char("Endereço de Faturamento",
                                  related='sale_order_id.partner_invoice_id.street',
                                  readonly=True)
    currency_id = fields.Many2one('res.currency',
                                  related='sale_order_id.currency_id',
                                  readonly=True, store=True)

    # CAMPOS CALCULADOS
    valor_faturado = fields.Monetary(compute="_compute_valor_faturado",
                                     string="Valor ja Faturado", readonly=True)
    valor_a_faturar = fields.Monetary(compute="_compute_valor_a_faturar",
                                      string="Valores a Faturar", readonly=True)
    # Campo active para controlar arquivamento
    active = fields.Boolean(string="Ativo", default=True)

    @api.depends('sale_order_id.invoice_ids', 'sale_order_id.invoice_ids.state')
    def _compute_valor_faturado(self):
        """
        CALCULA O VALOR DE FORMA DINÂMICA
        """
        for record in self:
            valor_faturado = sum(
                invoice.amount_untaxed for invoice in record.sale_order_id.invoice_ids
                if invoice.state == 'posted')
            record.valor_faturado = valor_faturado
            _logger.info(
                f"Computed 'valor_faturado' for FoundationObra {record.id}: {valor_faturado}")

    @api.depends('sale_order_id.order_line.qty_delivered',
                 'sale_order_id.order_line.qty_invoiced',
                 'sale_order_id.order_line.price_unit')
    def _compute_valor_a_faturar(self):
        """
        Calcula o valor a faturar com base na diferença entre quantidade entregue e quantidade faturada,
        multiplicada pelo preço unitário de cada linha da ordem de venda.
        """
        for record in self:
            valor_a_faturar = 0.0
            for line in record.sale_order_id.order_line:
                quantidade_a_faturar = line.qty_delivered - line.qty_invoiced
                if quantidade_a_faturar > 0:
                    valor_a_faturar += quantidade_a_faturar * line.price_unit
            record.valor_a_faturar = valor_a_faturar
            _logger.info(
                f"Computed 'valor_a_faturar' for FoundationObra {record.id}: {valor_a_faturar}")

    def toggle_active(self):
        for record in self:
            if record.valor_a_faturar != 0:
                raise UserError(
                    "A obra não pode ser arquivada porque ainda há valores a faturar.")

            # Verifica se o estoque específico está vazio
            sale_order = record.sale_order_id
            if sale_order.specific_stock_location_id and sale_order.specific_stock_location_id.quant_ids:
                raise UserError(
                    "A obra não pode ser arquivada porque o estoque específico da ordem de venda ainda não está vazio.")

            related_models = [
                'foundation.relatorios',
                'foundation.maquina.registro',
                'foundation.medicao',
                'foundation.estacas',
                'foundation.chamada',
                'account.analytic.account',
                'foundation.obra.service'
            ]

            # Arquivar/Restaurar a obra e os registros relacionados
            record.active = not record.active

            # Atualiza a visibilidade dos estoques específicos
            if sale_order.specific_stock_location_id:
                sale_order.specific_stock_location_id.write({'active': record.active})
            if sale_order.specific_stock_output_id:
                sale_order.specific_stock_output_id.write({'active': record.active})

            for model in related_models:
                related_records = self.env[model].search(
                    [('sale_order_id', '=', record.sale_order_id.id)])
                related_records.write({'active': record.active})
